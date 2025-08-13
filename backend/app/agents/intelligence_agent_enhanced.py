"""Enhanced Intelligence Agent with detailed reasoning and analysis"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.config import settings
from app.db.database import get_db

logger = logging.getLogger(__name__)

# Enhanced prompt template that forces reasoning
INTELLIGENCE_PROMPT = """You are an elite NBA fantasy basketball analyst preparing for the 2024-25 season.

When analyzing players or making recommendations, you MUST:
1. Provide specific statistical evidence
2. Explain year-over-year changes
3. Consider team context and role changes
4. Give 2-3 concrete reasons for each recommendation

Current date: August 2025 (off-season, preparing for drafts)

User Question: {question}
Data Available: {data}

Provide a detailed, analytical response with specific reasoning for each recommendation.
"""

class IntelligenceAgentEnhanced(BaseAgent):
    """Enhanced Intelligence Agent with detailed statistical analysis and reasoning"""
    
    def __init__(self):
        """Initialize the enhanced Intelligence Agent"""
        # Define enhanced tools with reasoning
        tools = [
            Tool(
                name="analyze_player_stats",
                description="Analyze detailed player statistics with trends",
                func=self._analyze_player_stats_enhanced
            ),
            Tool(
                name="find_sleepers",
                description="Find sleeper candidates with detailed reasoning",
                func=self._find_sleeper_candidates_enhanced
            ),
            Tool(
                name="identify_breakouts", 
                description="Identify breakout candidates with statistical support",
                func=self._identify_breakout_candidates_enhanced
            ),
            Tool(
                name="project_performance",
                description="Project player performance with context",
                func=self._project_player_performance_enhanced
            ),
            Tool(
                name="compare_players",
                description="Compare players with detailed analysis",
                func=self._compare_players_enhanced
            ),
            Tool(
                name="analyze_consistency",
                description="Analyze player consistency and risk factors",
                func=self._analyze_consistency_enhanced
            )
        ]
        
        super().__init__(
            name="Intelligence Agent Enhanced",
            description="Advanced analytics and predictions with detailed reasoning",
            tools=tools
        )
        
        # Initialize chain-of-thought prompt
        if settings.OPENAI_API_KEY:
            self.llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.3)
            self.reasoning_chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["question", "data"],
                    template=INTELLIGENCE_PROMPT
                )
            )
    
    def _initialize_agent(self):
        """Initialize the enhanced agent with reasoning capabilities"""
        if settings.OPENAI_API_KEY:
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.3)
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True
            )
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process message with enhanced reasoning"""
        if not self.agent_executor:
            return AgentResponse(
                content="Intelligence agent not properly initialized. Please check OpenAI API key.",
                confidence=0.0
            )
        
        try:
            # Add context about current date and enhance the query
            enhanced_message = f"""[Context: August 2025, NBA off-season, preparing for 2024-25 fantasy drafts]
            
            User Query: {message}
            
            Instructions: Provide detailed analysis with specific statistics and reasoning for each recommendation.
            Include year-over-year comparisons where relevant."""
            
            result = await self.agent_executor.arun(input=enhanced_message)
            
            return AgentResponse(
                content=result,
                metadata={
                    "context": context,
                    "agent_type": "intelligence_enhanced",
                    "capabilities": ["detailed_analysis", "statistical_reasoning", "trend_identification"]
                },
                tools_used=[tool.name for tool in self.tools],
                confidence=0.90
            )
        except Exception as e:
            logger.error(f"Error in enhanced intelligence agent: {str(e)}")
            return AgentResponse(
                content=f"Error processing intelligence request: {str(e)}",
                confidence=0.0
            )
    
    # ENHANCED TOOL IMPLEMENTATIONS WITH REASONING
    
    def _analyze_player_stats_enhanced(self, player_name: str) -> str:
        """Analyze player stats with detailed context and reasoning"""
        try:
            db = next(get_db())
            
            # Get comprehensive player data including historical context
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team, p.age,
                    f.adp_rank, f.adp_round,
                    f.projected_ppg, f.projected_rpg, f.projected_apg,
                    f.projected_spg, f.projected_bpg,
                    f.projected_fg_pct, f.projected_ft_pct, f.projected_3pm,
                    f.projected_fantasy_ppg,
                    f.consistency_rating, f.injury_risk,
                    f.breakout_candidate, f.sleeper_score,
                    gs.ppg as last_season_ppg,
                    gs.rpg as last_season_rpg,
                    gs.apg as last_season_apg
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                LEFT JOIN (
                    SELECT player_id, 
                           AVG(points) as ppg,
                           AVG(rebounds) as rpg, 
                           AVG(assists) as apg
                    FROM game_stats
                    WHERE season_year = 2024
                    GROUP BY player_id
                ) gs ON p.id = gs.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.fetchone()
            if player:
                response = f"**{player.name}** ({player.position}, {player.team}) - Detailed Analysis:\n\n"
                
                # Age and career stage context
                response += f"**Profile**: {player.age} years old, "
                if player.age < 25:
                    response += "entering prime development years\n"
                elif player.age <= 29:
                    response += "in statistical prime\n"
                else:
                    response += "veteran with established role\n"
                
                # Draft value analysis
                response += f"\n**Draft Value**:\n"
                response += f"• ADP: #{player.adp_rank} (Round {player.adp_round})\n"
                
                # Statistical projections with reasoning
                response += f"\n**2024-25 Projections with Analysis**:\n"
                
                # Points analysis
                if player.last_season_ppg:
                    ppg_change = ((player.projected_ppg - player.last_season_ppg) / player.last_season_ppg * 100)
                    response += f"• Points: {player.projected_ppg:.1f} PPG "
                    response += f"({ppg_change:+.1f}% from last season's {player.last_season_ppg:.1f})\n"
                    if ppg_change > 10:
                        response += f"  → Significant scoring increase expected due to expanded role\n"
                    elif ppg_change < -10:
                        response += f"  → Scoring decrease likely due to roster changes\n"
                else:
                    response += f"• Points: {player.projected_ppg:.1f} PPG (rookie/no prior data)\n"
                
                # Rebounds and assists
                response += f"• Rebounds: {player.projected_rpg:.1f} RPG\n"
                response += f"• Assists: {player.projected_apg:.1f} APG\n"
                
                # Defensive stats
                if player.projected_spg >= 1.0 or player.projected_bpg >= 1.0:
                    response += f"• Defensive Impact: {player.projected_spg:.1f} STL, {player.projected_bpg:.1f} BLK\n"
                    if player.projected_bpg >= 1.5:
                        response += f"  → Elite shot-blocking provides significant fantasy value\n"
                
                # Shooting efficiency
                response += f"• Shooting: {player.projected_fg_pct:.1%} FG%, {player.projected_ft_pct:.1%} FT%, {player.projected_3pm:.1f} 3PM\n"
                
                # Fantasy impact assessment
                response += f"\n**Fantasy Impact**:\n"
                response += f"• Projected Fantasy Points: {player.projected_fantasy_ppg:.1f} per game\n"
                response += f"• Consistency Rating: {player.consistency_rating:.2f}/1.0\n"
                
                if player.consistency_rating > 0.7:
                    response += "  → High consistency makes them a reliable fantasy starter\n"
                elif player.consistency_rating < 0.5:
                    response += "  → Volatility suggests streaming candidate or bench player\n"
                
                # Risk factors
                if player.injury_risk and player.injury_risk > 0.3:
                    response += f"• Injury Risk: {player.injury_risk:.1%} - Monitor health closely\n"
                
                # Special designations
                if player.breakout_candidate:
                    response += "\n**🎯 BREAKOUT CANDIDATE**: Poised for statistical leap\n"
                if player.sleeper_score and player.sleeper_score > 0.6:
                    response += f"**💎 SLEEPER ALERT**: Score {player.sleeper_score:.2f} - Undervalued at current ADP\n"
                
                return response
            else:
                return f"No data found for player matching '{player_name}'"
                
        except Exception as e:
            logger.error(f"Error analyzing player stats: {str(e)}")
            return f"Error analyzing player: {str(e)}"
    
    def _find_sleeper_candidates_enhanced(self, criteria: str = "") -> str:
        """Find sleeper candidates with detailed reasoning for each"""
        try:
            db = next(get_db())
            
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team, p.age,
                    f.adp_rank, f.adp_round,
                    f.sleeper_score, 
                    f.projected_fantasy_ppg,
                    f.consistency_rating,
                    f.projected_ppg, f.projected_rpg, f.projected_apg,
                    CASE 
                        WHEN p.age < 24 THEN 'Young player development'
                        WHEN f.adp_rank > 100 THEN 'Late-round value'
                        WHEN p.team IN ('DET', 'HOU', 'ORL', 'OKC') THEN 'Improving team context'
                        ELSE 'Opportunity increase'
                    END as sleeper_reason
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE f.sleeper_score > 0.6
                ORDER BY f.sleeper_score DESC
                LIMIT 8
            """))
            
            sleepers = result.fetchall()
            if sleepers:
                response = "**Top Sleeper Candidates for 2024-25** (with detailed analysis):\n\n"
                
                for idx, s in enumerate(sleepers[:5], 1):
                    response += f"**{idx}. {s.name}** ({s.position}, {s.team})\n"
                    response += f"• **Current ADP**: #{s.adp_rank} (Round {s.adp_round})\n"
                    response += f"• **Sleeper Score**: {s.sleeper_score:.2f}/1.0\n"
                    response += f"• **Projected Stats**: {s.projected_ppg:.1f} PPG, {s.projected_rpg:.1f} RPG, {s.projected_apg:.1f} APG\n"
                    response += f"• **Fantasy Projection**: {s.projected_fantasy_ppg:.1f} FP/game\n"
                    response += f"• **Why They're a Sleeper**: {s.sleeper_reason}\n"
                    
                    # Add specific reasoning based on data
                    if s.age < 24:
                        response += f"  → At age {s.age}, entering prime development window\n"
                    if s.adp_rank > 100:
                        response += f"  → Available after round 8, exceptional value potential\n"
                    if s.consistency_rating > 0.65:
                        response += f"  → Consistency rating {s.consistency_rating:.2f} suggests reliable production\n"
                    
                    response += "\n"
                
                response += "\n**Strategy Tip**: Target these players 1-2 rounds before their ADP to ensure you get them"
                
                return response
            else:
                return "No sleeper candidates identified in current data"
                
        except Exception as e:
            logger.error(f"Error finding sleepers: {str(e)}")
            return f"Error finding sleepers: {str(e)}"
    
    def _identify_breakout_candidates_enhanced(self, criteria: str = "") -> str:
        """Identify breakout candidates with detailed statistical reasoning"""
        try:
            db = next(get_db())
            
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team, p.age,
                    f.adp_rank, f.adp_round,
                    f.projected_fantasy_ppg,
                    f.projected_ppg, f.projected_rpg, f.projected_apg,
                    f.sleeper_score, f.consistency_rating,
                    gs.ppg as last_season_ppg,
                    gs.games_played as last_season_games,
                    CASE
                        WHEN p.age BETWEEN 22 AND 25 THEN 'Sophomore/Junior leap expected'
                        WHEN gs.ppg IS NULL THEN 'Rookie with high upside'
                        WHEN f.projected_ppg > gs.ppg * 1.2 THEN 'Major role expansion'
                        ELSE 'System/coaching change benefit'
                    END as breakout_reason
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                LEFT JOIN (
                    SELECT player_id,
                           AVG(points) as ppg,
                           COUNT(*) as games_played
                    FROM game_stats
                    WHERE season_year = 2024
                    GROUP BY player_id
                ) gs ON p.id = gs.player_id
                WHERE f.breakout_candidate = true
                ORDER BY f.projected_fantasy_ppg DESC
                LIMIT 10
            """))
            
            breakouts = result.fetchall()
            if breakouts:
                response = "**2024-25 Breakout Candidates** (with statistical evidence):\n\n"
                
                # Top tier breakouts with detailed analysis
                response += "**ELITE BREAKOUT TARGETS**:\n\n"
                for idx, b in enumerate(breakouts[:3], 1):
                    response += f"**{idx}. {b.name}** ({b.position}, {b.team})\n"
                    response += f"• **Age**: {b.age} years old\n"
                    response += f"• **ADP**: #{b.adp_rank} (Round {b.adp_round})\n"
                    
                    # Year-over-year comparison if available
                    if b.last_season_ppg:
                        improvement = ((b.projected_ppg - b.last_season_ppg) / b.last_season_ppg * 100)
                        response += f"• **Scoring Projection**: {b.projected_ppg:.1f} PPG "
                        response += f"(+{improvement:.1f}% from {b.last_season_ppg:.1f} last season)\n"
                    else:
                        response += f"• **Scoring Projection**: {b.projected_ppg:.1f} PPG (rookie season)\n"
                    
                    response += f"• **Full Projection**: {b.projected_rpg:.1f} RPG, {b.projected_apg:.1f} APG\n"
                    response += f"• **Fantasy Impact**: {b.projected_fantasy_ppg:.1f} FP/game\n"
                    response += f"• **Breakout Catalyst**: {b.breakout_reason}\n"
                    
                    # Age-specific analysis
                    if b.age <= 23:
                        response += f"  → Young player trajectory suggests continued growth\n"
                    elif b.age <= 26:
                        response += f"  → Entering statistical prime years\n"
                    
                    response += "\n"
                
                # Additional candidates
                if len(breakouts) > 3:
                    response += "**ADDITIONAL BREAKOUT CANDIDATES**:\n"
                    for b in breakouts[3:7]:
                        response += f"• **{b.name}** ({b.team}): "
                        response += f"{b.projected_ppg:.1f}/{b.projected_rpg:.1f}/{b.projected_apg:.1f}, "
                        response += f"ADP #{b.adp_rank}\n"
                        response += f"  → {b.breakout_reason}\n"
                
                return response
            else:
                return "No breakout candidates identified in current data"
                
        except Exception as e:
            logger.error(f"Error identifying breakouts: {str(e)}")
            return f"Error identifying breakouts: {str(e)}"
    
    def _project_player_performance_enhanced(self, player_name: str) -> str:
        """Project performance with detailed context and comparisons"""
        try:
            db = next(get_db())
            
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team, p.age,
                    f.*,
                    gs.ppg as last_ppg,
                    gs.rpg as last_rpg,
                    gs.apg as last_apg,
                    gs.games_played
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                LEFT JOIN (
                    SELECT player_id,
                           AVG(points) as ppg,
                           AVG(rebounds) as rpg,
                           AVG(assists) as apg,
                           COUNT(*) as games_played
                    FROM game_stats
                    WHERE season_year = 2024
                    GROUP BY player_id
                ) gs ON p.id = gs.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.fetchone()
            if player:
                response = f"**2024-25 Projection for {player.name}**:\n\n"
                response += f"**Player Context**:\n"
                response += f"• Team: {player.team}\n"
                response += f"• Position: {player.position}\n"
                response += f"• Age: {player.age} years old\n"
                
                if player.games_played:
                    response += f"• Last Season: {player.games_played} games played\n"
                
                response += f"\n**Statistical Projections**:\n"
                response += f"• Scoring: {player.projected_ppg:.1f} PPG"
                if player.last_ppg:
                    diff = player.projected_ppg - player.last_ppg
                    response += f" ({diff:+.1f} from last season)\n"
                else:
                    response += " (no prior season data)\n"
                    
                response += f"• Rebounding: {player.projected_rpg:.1f} RPG\n"
                response += f"• Assists: {player.projected_apg:.1f} APG\n"
                response += f"• Stocks: {player.projected_spg:.1f} STL, {player.projected_bpg:.1f} BLK\n"
                response += f"• Shooting: {player.projected_3pm:.1f} 3PM at {player.projected_fg_pct:.1%} FG%\n"
                
                response += f"\n**Fantasy Outlook**:\n"
                response += f"• Fantasy Points: {player.projected_fantasy_ppg:.1f} per game\n"
                response += f"• Draft Position: ADP #{player.adp_rank} (Round {player.adp_round})\n"
                
                # Provide actionable advice
                if player.adp_rank <= 20:
                    response += "• Elite first/second round pick - cornerstone player\n"
                elif player.adp_rank <= 50:
                    response += "• Solid early-mid round selection\n"
                elif player.adp_rank <= 100:
                    response += "• Good mid-round value\n"
                else:
                    response += "• Late-round upside pick\n"
                
                return response
            else:
                return f"No projection data found for '{player_name}'"
                
        except Exception as e:
            logger.error(f"Error projecting performance: {str(e)}")
            return f"Error projecting performance: {str(e)}"
    
    def _compare_players_enhanced(self, players: str) -> str:
        """Compare players with detailed statistical analysis"""
        try:
            # Parse player names (expecting format: "Player1 vs Player2")
            if " vs " in players.lower():
                names = players.split(" vs ")
            elif " or " in players.lower():
                names = players.split(" or ")
            else:
                return "Please provide two players to compare (e.g., 'LeBron vs Durant')"
            
            if len(names) != 2:
                return "Please provide exactly two players to compare"
            
            db = next(get_db())
            
            comparison_data = []
            for name in names:
                result = db.execute(text("""
                    SELECT 
                        p.name, p.position, p.team, p.age,
                        f.*
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE LOWER(p.name) LIKE LOWER(:name)
                    LIMIT 1
                """), {"name": f"%{name.strip()}%"})
                
                player = result.fetchone()
                if player:
                    comparison_data.append(player)
            
            if len(comparison_data) == 2:
                p1, p2 = comparison_data
                
                response = f"**Player Comparison: {p1.name} vs {p2.name}**\n\n"
                
                # Basic info
                response += "**Player Profiles**:\n"
                response += f"• {p1.name}: {p1.position}, {p1.team}, Age {p1.age}\n"
                response += f"• {p2.name}: {p2.position}, {p2.team}, Age {p2.age}\n"
                
                # Draft value
                response += "\n**Draft Value**:\n"
                response += f"• {p1.name}: ADP #{p1.adp_rank} (Round {p1.adp_round})\n"
                response += f"• {p2.name}: ADP #{p2.adp_rank} (Round {p2.adp_round})\n"
                if abs(p1.adp_rank - p2.adp_rank) <= 10:
                    response += "→ Similar draft cost, choice depends on team needs\n"
                elif p1.adp_rank < p2.adp_rank:
                    response += f"→ {p1.name} is drafted {p2.adp_rank - p1.adp_rank} spots earlier on average\n"
                else:
                    response += f"→ {p2.name} is drafted {p1.adp_rank - p2.adp_rank} spots earlier on average\n"
                
                # Statistical comparison
                response += "\n**Projected Stats (2024-25)**:\n"
                response += f"• Scoring: {p1.name} ({p1.projected_ppg:.1f}) vs {p2.name} ({p2.projected_ppg:.1f})\n"
                response += f"• Rebounding: {p1.name} ({p1.projected_rpg:.1f}) vs {p2.name} ({p2.projected_rpg:.1f})\n"
                response += f"• Assists: {p1.name} ({p1.projected_apg:.1f}) vs {p2.name} ({p2.projected_apg:.1f})\n"
                response += f"• Fantasy Points: {p1.name} ({p1.projected_fantasy_ppg:.1f}) vs {p2.name} ({p2.projected_fantasy_ppg:.1f})\n"
                
                # Winner recommendation
                response += "\n**Recommendation**:\n"
                p1_score = p1.projected_fantasy_ppg / max(p1.adp_rank, 1)
                p2_score = p2.projected_fantasy_ppg / max(p2.adp_rank, 1)
                
                if p1_score > p2_score * 1.1:
                    response += f"✅ **{p1.name}** provides better value\n"
                    response += f"• Higher fantasy output relative to draft cost\n"
                elif p2_score > p1_score * 1.1:
                    response += f"✅ **{p2.name}** provides better value\n"
                    response += f"• Higher fantasy output relative to draft cost\n"
                else:
                    response += "↔️ **Similar value** - choose based on:\n"
                    response += f"• Team needs (position scarcity)\n"
                    response += f"• Risk tolerance (consistency vs upside)\n"
                
                return response
            else:
                return f"Could not find data for both players"
                
        except Exception as e:
            logger.error(f"Error comparing players: {str(e)}")
            return f"Error comparing players: {str(e)}"
    
    def _analyze_consistency_enhanced(self, player_name: str) -> str:
        """Analyze player consistency with risk assessment"""
        try:
            db = next(get_db())
            
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.consistency_rating,
                    f.injury_risk,
                    f.projected_fantasy_ppg,
                    f.adp_rank,
                    COUNT(gs.id) as games_played,
                    STDDEV(gs.points) as points_stddev,
                    AVG(gs.points) as avg_points,
                    MIN(gs.points) as min_points,
                    MAX(gs.points) as max_points
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                LEFT JOIN game_stats gs ON p.id = gs.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                GROUP BY p.id, p.name, p.position, p.team, 
                         f.consistency_rating, f.injury_risk, 
                         f.projected_fantasy_ppg, f.adp_rank
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.fetchone()
            if player:
                response = f"**Consistency Analysis for {player.name}**:\n\n"
                
                # Consistency rating interpretation
                response += f"**Consistency Rating**: {player.consistency_rating:.2f}/1.0\n"
                if player.consistency_rating >= 0.75:
                    response += "• ✅ Highly consistent - reliable weekly starter\n"
                elif player.consistency_rating >= 0.60:
                    response += "• ⚠️ Moderately consistent - solid but with variance\n"
                else:
                    response += "• ❌ Inconsistent - boom/bust player\n"
                
                # Statistical variance analysis
                if player.points_stddev and player.avg_points:
                    cv = (player.points_stddev / player.avg_points) * 100
                    response += f"\n**Performance Variance**:\n"
                    response += f"• Average: {player.avg_points:.1f} PPG\n"
                    response += f"• Range: {player.min_points:.0f} to {player.max_points:.0f} points\n"
                    response += f"• Coefficient of Variation: {cv:.1f}%\n"
                    
                    if cv < 30:
                        response += "  → Low variance, predictable output\n"
                    elif cv < 50:
                        response += "  → Moderate variance, generally reliable\n"
                    else:
                        response += "  → High variance, volatile production\n"
                
                # Injury risk assessment
                if player.injury_risk:
                    response += f"\n**Injury Risk**: {player.injury_risk:.1%}\n"
                    if player.injury_risk < 0.2:
                        response += "• Low injury concern\n"
                    elif player.injury_risk < 0.4:
                        response += "• Moderate injury history - monitor status\n"
                    else:
                        response += "• ⚠️ Significant injury risk - have backup plan\n"
                
                # Fantasy recommendation
                response += f"\n**Fantasy Recommendation**:\n"
                response += f"• Projected: {player.projected_fantasy_ppg:.1f} fantasy points/game\n"
                response += f"• ADP: #{player.adp_rank}\n"
                
                if player.consistency_rating >= 0.7 and player.injury_risk < 0.3:
                    response += "• **Verdict**: Safe, reliable pick at ADP\n"
                elif player.consistency_rating >= 0.6:
                    response += "• **Verdict**: Solid option with some risk\n"
                else:
                    response += "• **Verdict**: High-risk, high-reward player\n"
                
                return response
            else:
                return f"No consistency data found for '{player_name}'"
                
        except Exception as e:
            logger.error(f"Error analyzing consistency: {str(e)}")
            return f"Error analyzing consistency: {str(e)}"