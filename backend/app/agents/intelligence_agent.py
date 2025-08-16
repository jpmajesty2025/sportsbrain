"""
Intelligence Agent - Merged Analytics + Prediction capabilities
Handles: Historical analysis, future projections, pattern matching
"""
from typing import Dict, Any, List, Optional
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import Tool
from sqlalchemy.orm import Session
from sqlalchemy import text
from .base_agent import BaseAgent, AgentResponse
from app.core.config import settings
from app.db.database import get_db
import json

class IntelligenceAgent(BaseAgent):
    """
    Unified intelligence agent that combines analytics and prediction.
    Specializes in fantasy basketball insights for off-season draft prep.
    """
    
    def __init__(self):
        tools = [
            # Historical Analysis Tools (from Analytics)
            Tool(
                name="analyze_player_stats",
                description="Analyze historical player statistics and performance metrics",
                func=self._analyze_player_stats
            ),
            Tool(
                name="find_sleepers",
                description="Find sleeper candidates based on sleeper scores and projections",
                func=self._find_sleeper_candidates
            ),
            
            # Prediction Tools (from Prediction)
            Tool(
                name="identify_breakouts",
                description="Identify breakout candidates for upcoming season",
                func=self._identify_breakout_candidates
            ),
            Tool(
                name="project_performance",
                description="Project player performance for 2025-26 season",
                func=self._project_player_performance
            ),
            
            # Pattern Matching Tools (New)
            Tool(
                name="compare_players",
                description="Compare players based on stats and fantasy value",
                func=self._compare_players
            ),
            Tool(
                name="analyze_consistency",
                description="Analyze player consistency ratings and injury risk",
                func=self._analyze_consistency
            )
        ]
        
        super().__init__(
            name="Intelligence Agent",
            description="Unified analytics and prediction agent for fantasy basketball intelligence",
            tools=tools
        )
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools"""
        if settings.OPENAI_API_KEY:
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.2)
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a message and return insights"""
        if not self.agent_executor:
            return AgentResponse(
                content="Intelligence agent not properly initialized. Please check OpenAI API key.",
                confidence=0.0
            )
        
        try:
            # Add context about current date (off-season)
            enhanced_message = f"[Context: It's August 2025, NBA off-season, preparing for 2025-26 fantasy drafts]\n{message}"
            
            result = await self.agent_executor.arun(input=enhanced_message)
            
            return AgentResponse(
                content=result,
                metadata={
                    "context": context,
                    "agent_type": "intelligence",
                    "capabilities": ["analysis", "prediction", "pattern_matching"]
                },
                tools_used=[tool.name for tool in self.tools],
                confidence=0.85
            )
        except Exception as e:
            return AgentResponse(
                content=f"Error processing intelligence request: {str(e)}",
                confidence=0.0
            )
    
    def _get_supported_tasks(self) -> List[str]:
        """Return list of supported tasks"""
        return [
            "player_analysis",
            "sleeper_identification", 
            "breakout_prediction",
            "performance_projection",
            "player_comparison",
            "consistency_analysis",
            "historical_trends",
            "statistical_insights"
        ]
    
    # Tool implementations with REAL database queries
    
    def _analyze_player_stats(self, player_name: str) -> str:
        """Analyze player stats from PostgreSQL"""
        try:
            db = next(get_db())
            
            # Query player with fantasy data
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.projected_ppg, f.projected_rpg, f.projected_apg,
                    f.projected_spg, f.projected_bpg, f.projected_fantasy_ppg,
                    f.adp_rank, f.consistency_rating, f.injury_risk
                FROM players p
                LEFT JOIN fantasy_data f ON p.id = f.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.first()
            if player:
                return (f"{player.name} ({player.position}, {player.team}): "
                       f"Projected: {player.projected_ppg:.1f} PPG, {player.projected_rpg:.1f} RPG, "
                       f"{player.projected_apg:.1f} APG. Fantasy: {player.projected_fantasy_ppg:.1f} FP/game. "
                       f"ADP: #{player.adp_rank}. Consistency: {player.consistency_rating:.2f}. "
                       f"Injury Risk: {player.injury_risk}")
            else:
                return f"No stats found for {player_name}"
                
        except Exception as e:
            return f"Error analyzing stats: {str(e)}"
    
    def _find_sleeper_candidates(self, criteria: str = "") -> str:
        """Find sleeper candidates from database"""
        try:
            db = next(get_db())
            
            # Query players with high sleeper scores
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.adp_rank, f.sleeper_score, f.projected_fantasy_ppg,
                    f.consistency_rating
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE f.sleeper_score > 0.6
                ORDER BY f.sleeper_score DESC
                LIMIT 10
            """))
            
            sleepers = result.fetchall()
            if sleepers:
                response = "Top sleeper candidates for 2025-26:\n"
                for s in sleepers[:5]:
                    response += (f"- {s.name} ({s.position}, {s.team}): "
                               f"ADP #{s.adp_rank}, Sleeper Score: {s.sleeper_score:.2f}, "
                               f"Projected: {s.projected_fantasy_ppg:.1f} FP/game\n")
                return response
            else:
                return "No sleeper candidates found"
                
        except Exception as e:
            return f"Error finding sleepers: {str(e)}"
    
    def _identify_breakout_candidates(self, criteria: str = "") -> str:
        """Identify breakout candidates"""
        try:
            db = next(get_db())
            
            # Query breakout candidates
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.adp_rank, f.projected_fantasy_ppg,
                    f.sleeper_score, f.consistency_rating
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE f.breakout_candidate = true
                ORDER BY f.projected_fantasy_ppg DESC
                LIMIT 10
            """))
            
            breakouts = result.fetchall()
            if breakouts:
                response = "Breakout candidates for 2025-26 season:\n"
                for b in breakouts[:7]:
                    response += (f"- {b.name} ({b.position}, {b.team}): "
                               f"ADP #{b.adp_rank}, Projected: {b.projected_fantasy_ppg:.1f} FP/game\n")
                return response
            else:
                return "No breakout candidates identified"
                
        except Exception as e:
            return f"Error identifying breakouts: {str(e)}"
    
    def _project_player_performance(self, player_name: str) -> str:
        """Project player performance for 2025-26"""
        try:
            db = next(get_db())
            
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.projected_ppg, f.projected_rpg, f.projected_apg,
                    f.projected_spg, f.projected_bpg, f.projected_3pm,
                    f.projected_fg_pct, f.projected_ft_pct,
                    f.projected_fantasy_ppg, f.adp_rank
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.first()
            if player:
                return (f"2025-26 Projections for {player.name}:\n"
                       f"Stats: {player.projected_ppg:.1f} PPG, {player.projected_rpg:.1f} RPG, "
                       f"{player.projected_apg:.1f} APG, {player.projected_spg:.1f} SPG, "
                       f"{player.projected_bpg:.1f} BPG, {player.projected_3pm:.1f} 3PM\n"
                       f"Shooting: {player.projected_fg_pct:.1%} FG%, {player.projected_ft_pct:.1%} FT%\n"
                       f"Fantasy: {player.projected_fantasy_ppg:.1f} points per game (ADP: #{player.adp_rank})")
            else:
                return f"No projections found for {player_name}"
                
        except Exception as e:
            return f"Error projecting performance: {str(e)}"
    
    def _compare_players(self, players: str) -> str:
        """Compare two or more players"""
        # Parse player names from input
        player_names = [p.strip() for p in players.split(',')][:3]  # Limit to 3
        
        try:
            db = next(get_db())
            comparisons = []
            
            for name in player_names:
                result = db.execute(text("""
                    SELECT 
                        p.name, p.position, p.team,
                        f.adp_rank, f.projected_fantasy_ppg,
                        f.consistency_rating, f.injury_risk
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE LOWER(p.name) LIKE LOWER(:name)
                    LIMIT 1
                """), {"name": f"%{name}%"})
                
                player = result.first()
                if player:
                    comparisons.append(player)
            
            if comparisons:
                response = "Player Comparison:\n"
                for p in comparisons:
                    response += (f"{p.name} ({p.position}): ADP #{p.adp_rank}, "
                               f"{p.projected_fantasy_ppg:.1f} FP/game, "
                               f"Consistency: {p.consistency_rating:.2f}, Risk: {p.injury_risk}\n")
                return response
            else:
                return "No players found for comparison"
                
        except Exception as e:
            return f"Error comparing players: {str(e)}"
    
    def _analyze_consistency(self, player_name: str) -> str:
        """Analyze player consistency and reliability"""
        try:
            db = next(get_db())
            
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.consistency_rating, f.injury_risk,
                    f.projected_fantasy_ppg, f.adp_rank
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.first()
            if player:
                consistency_desc = "Very High" if player.consistency_rating > 0.85 else \
                                 "High" if player.consistency_rating > 0.7 else \
                                 "Moderate" if player.consistency_rating > 0.5 else "Low"
                
                return (f"{player.name} Consistency Analysis:\n"
                       f"Consistency Rating: {player.consistency_rating:.2f} ({consistency_desc})\n"
                       f"Injury Risk: {player.injury_risk}\n"
                       f"Expected Production: {player.projected_fantasy_ppg:.1f} FP/game\n"
                       f"Draft Position: ADP #{player.adp_rank}")
            else:
                return f"No consistency data found for {player_name}"
                
        except Exception as e:
            return f"Error analyzing consistency: {str(e)}"