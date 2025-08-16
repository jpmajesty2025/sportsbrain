"""Enhanced Intelligence Agent with detailed reasoning and analysis"""

import logging
import asyncio
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
INTELLIGENCE_PROMPT = """You are an elite NBA fantasy basketball analyst preparing for the 2025-26 season.

When analyzing players or making recommendations, you MUST:
1. Provide specific statistical evidence
2. Explain year-over-year changes
3. Consider team context and role changes
4. Give 2-3 concrete reasons for each recommendation

IMPORTANT: When users ask for players "like" someone (e.g., "Find sleepers like Jordan Poole"):
- First identify the reference player's KEY characteristics (play style, stats, role)
- Explain what makes them notable (3PT volume, scoring patterns, team situation)
- Find players with SIMILAR characteristics, not just any sleepers
- Explicitly compare each recommendation to the reference player
- Include statistical evidence showing the similarities

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
                description=(
                    "Analyze detailed player statistics, performance trends, and projections. "
                    "Use for: player stats, performance analysis, statistical trends, player data, "
                    "season stats, career stats, recent performance, stats comparison. "
                    "Answers questions like: How did player X perform? What are player's stats? "
                    "Show me player's numbers. Player analysis. Statistical breakdown."
                ),
                func=self._analyze_player_stats_enhanced
            ),
            Tool(
                name="find_sleepers",
                description=(
                    "Find sleeper candidates, undervalued players, hidden gems, late-round targets, "
                    "draft steals, value picks, under-the-radar players, cheap DFS plays. "
                    "Use for: sleepers, undervalued, hidden gems, late rounds, value, cheap, steals, "
                    "deep league targets, waiver wire adds, unknown players, upside plays. "
                    "Answers: Find sleepers, sleeper centers, sleepers like X, underrated players, "
                    "who to target late, value picks, best late-round players. "
                    "RETURNS COMPLETE ANALYSIS - DO NOT SUMMARIZE."
                ),
                func=self._find_sleeper_candidates_enhanced
            ),
            Tool(
                name="identify_breakouts", 
                description=(
                    "Identify breakout candidates, sophomore leap players, third-year jumps, "
                    "most improved candidates, players ready to explode, ascending players. "
                    "Use for: breakout, sophomore, second-year, third-year, improvement, "
                    "leap, explosion, ascending, rising, emerging, developing players. "
                    "Answers: Which sophomores will break out? Breakout candidates? "
                    "Who will improve most? Rising stars? Players to watch? MIP candidates?"
                ),
                func=self._identify_breakout_candidates_enhanced
            ),
            Tool(
                name="project_performance",
                description=(
                    "Project future performance, season projections, statistical forecasts, "
                    "2025-26 predictions, expected stats, outlook, ceiling and floor. "
                    "Use for: projections, predictions, forecast, outlook, expected, "
                    "will player X score, next season stats, 2025-26 numbers. "
                    "Answers: Project player's stats, what will player average? "
                    "Season predictions? Expected performance? Statistical projections?"
                ),
                func=self._project_player_performance_enhanced
            ),
            Tool(
                name="compare_players",
                description=(
                    "Compare two or more players head-to-head, versus analysis, player battles, "
                    "who is better, side-by-side comparison, player A vs player B analysis. "
                    "Use for: compare, versus, vs, better than, comparison, head-to-head, "
                    "player A or B, choose between, pick one, who to draft. "
                    "Answers: Compare X vs Y, who is better? Player A or Player B? "
                    "Barnes vs Banchero? Which player to choose?"
                ),
                func=self._compare_players_enhanced
            ),
            Tool(
                name="analyze_consistency",
                description=(
                    "Analyze consistency, reliability, injury risk, volatility, floor/ceiling, "
                    "boom/bust potential, risk assessment, durability, health concerns. "
                    "Use for: consistency, reliable, injury, risk, volatile, boom/bust, "
                    "floor, ceiling, durability, health, games played, availability. "
                    "Answers: How consistent is player? Injury risk? Reliable option? "
                    "Boom or bust? High floor? Safe pick? Risky player?"
                ),
                func=self._analyze_consistency_enhanced
            ),
            Tool(
                name="evaluate_player_draft_value",
                description=(
                    "Evaluate if specific player is worth drafting, draft value analysis, "
                    "should I draft player X, is player draftable, worth a pick, draft or pass. "
                    "Use for: worth drafting, should I draft, draft value, draftable, "
                    "worth picking, draft or not, good pick, bad pick, draft advice. "
                    "Answers: Is Gary Trent Jr. worth drafting? Should I draft player X? "
                    "Worth a pick? Draft or pass? Good value? Worth rostering?"
                ),
                func=self._evaluate_player_draft_value
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
            from langchain.agents import ZeroShotAgent
            from langchain.agents import AgentExecutor
            from langchain.prompts import PromptTemplate
            
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.3)
            
            # Custom prompt to avoid mentioning tool names
            prefix = """You are a fantasy basketball expert assistant. Answer the user's questions using the available tools.

CRITICAL RULES:
1. NEVER mention tool names in your responses
2. NEVER say "based on the X tool" or "from the Y analysis"
3. Present information as YOUR expert knowledge
4. Be specific and detailed in your answers

You have access to the following tools:"""
            
            suffix = """Begin! Remember: Do not mention tool names in your final answer.

Question: {input}
Thought: {agent_scratchpad}"""
            
            prompt = ZeroShotAgent.create_prompt(
                tools=self.tools,
                prefix=prefix,
                suffix=suffix,
                input_variables=["input", "agent_scratchpad"]
            )
            
            llm_chain = LLMChain(llm=llm, prompt=prompt)
            agent = ZeroShotAgent(llm_chain=llm_chain, tools=self.tools)
            
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True
            )
    
    def _get_supported_tasks(self) -> List[str]:
        """Return list of supported tasks"""
        return [
            "analyze player statistics with trends",
            "find sleeper candidates with reasoning",
            "identify breakout candidates with evidence",
            "project player performance with context",
            "compare players with detailed analysis",
            "analyze player consistency and risk"
        ]
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process message with enhanced reasoning"""
        if not self.agent_executor:
            return AgentResponse(
                content="Intelligence agent not properly initialized. Please check OpenAI API key.",
                confidence=0.0
            )
        
        try:
            # Let the agent handle all queries with enhanced tool descriptions
            # Add context to help the agent understand the request better
            enhanced_message = f"""[Context: August 2025, NBA off-season, preparing for 2025-26 fantasy drafts]
            
            User Query: {message}
            
            Instructions: Provide detailed analysis with specific statistics and reasoning.
            IMPORTANT: Do NOT mention tool names or say things like "based on the X tool" or "using the Y tool".
            Simply provide the answer directly as if you have the knowledge. Do not summarize tool outputs."""
            
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
        except asyncio.TimeoutError:
            from .error_messages import get_friendly_error_message
            return AgentResponse(
                content=get_friendly_error_message("intelligence_enhanced", message, "timeout"),
                confidence=0.5,
                metadata={"error": "timeout", "agent_type": "intelligence_enhanced"}
            )
        except Exception as e:
            logger.error(f"Error in enhanced intelligence agent: {str(e)}")
            error_msg = str(e)
            if "iteration limit" in error_msg.lower() or "time limit" in error_msg.lower():
                from .error_messages import get_friendly_error_message
                return AgentResponse(
                    content=get_friendly_error_message("intelligence_enhanced", message, "iteration_limit"),
                    confidence=0.5,
                    metadata={"error": "iteration_limit", "agent_type": "intelligence_enhanced"}
                )
            logger.error(f"Unexpected error - Agent: intelligence_enhanced, Error: {str(e)}, Query: {message}")
            return AgentResponse(
                content=("I apologize for the inconvenience. I am unable to complete your request at this time. "
                        "At SportsBrain, we're always working hard to improve user experience. "
                        "This interaction has been logged for later analysis."),
                confidence=0.0,
                metadata={"error": str(e), "agent_type": "intelligence_enhanced"}
            )
    
    # ENHANCED TOOL IMPLEMENTATIONS WITH REASONING
    
    def _analyze_player_stats_enhanced(self, player_name: str) -> str:
        """Analyze player stats with detailed context and reasoning"""
        try:
            db = next(get_db())
            
            # Get comprehensive player data including historical context
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) as age,
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
                    GROUP BY player_id
                ) gs ON p.id = gs.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.fetchone()
            if player:
                response = f"**{player.name}** ({player.position}, {player.team}) - Detailed Analysis:\n\n"
                
                # Age and career stage context
                if player.age is not None:
                    try:
                        age = int(player.age)
                    except (ValueError, TypeError):
                        age = 0
                    
                    if age > 0:
                        response += f"**Profile**: {age} years old, "
                        if age < 25:
                            response += "entering prime development years\n"
                        elif age <= 29:
                            response += "in statistical prime\n"
                        else:
                            response += "veteran with established role\n"
                    else:
                        response += f"**Profile**: {player.position}, {player.team}\n"
                else:
                    response += f"**Profile**: {player.position}, {player.team}\n"
                
                # Draft value analysis
                response += f"\n**Draft Value**:\n"
                response += f"• ADP: #{player.adp_rank} (Round {player.adp_round})\n"
                
                # Statistical projections with reasoning
                response += f"\n**2025-26 Projections with Analysis**:\n"
                
                # Points analysis
                if player.last_season_ppg is not None:
                    try:
                        proj_ppg = float(player.projected_ppg) if player.projected_ppg else 0
                        last_ppg = float(player.last_season_ppg)
                    except (ValueError, TypeError):
                        proj_ppg = float(player.projected_ppg) if player.projected_ppg else 0
                        last_ppg = 0
                    
                    if last_ppg > 0:
                        ppg_change = ((proj_ppg - last_ppg) / last_ppg * 100)
                        response += f"• Points: {proj_ppg:.1f} PPG "
                        response += f"({ppg_change:+.1f}% from last season's {last_ppg:.1f})\n"
                        if ppg_change > 10:
                            response += f"  → Significant scoring increase expected due to expanded role\n"
                        elif ppg_change < -10:
                            response += f"  → Scoring decrease likely due to roster changes\n"
                    else:
                        response += f"• Points: {proj_ppg:.1f} PPG\n"
                else:
                    proj_ppg = float(player.projected_ppg) if player.projected_ppg else 0
                    response += f"• Points: {proj_ppg:.1f} PPG (rookie/no prior data)\n"
                
                # Rebounds and assists
                proj_rpg = float(player.projected_rpg) if player.projected_rpg else 0
                proj_apg = float(player.projected_apg) if player.projected_apg else 0
                response += f"• Rebounds: {proj_rpg:.1f} RPG\n"
                response += f"• Assists: {proj_apg:.1f} APG\n"
                
                # Defensive stats
                proj_spg = float(player.projected_spg) if player.projected_spg else 0
                proj_bpg = float(player.projected_bpg) if player.projected_bpg else 0
                if proj_spg >= 1.0 or proj_bpg >= 1.0:
                    response += f"• Defensive Impact: {proj_spg:.1f} STL, {proj_bpg:.1f} BLK\n"
                    if proj_bpg >= 1.5:
                        response += f"  → Elite shot-blocking provides significant fantasy value\n"
                
                # Shooting efficiency
                proj_fg_pct = float(player.projected_fg_pct) if player.projected_fg_pct else 0
                proj_ft_pct = float(player.projected_ft_pct) if player.projected_ft_pct else 0
                proj_3pm = float(player.projected_3pm) if player.projected_3pm else 0
                response += f"• Shooting: {proj_fg_pct:.1%} FG%, {proj_ft_pct:.1%} FT%, {proj_3pm:.1f} 3PM\n"
                
                # Fantasy impact assessment
                response += f"\n**Fantasy Impact**:\n"
                proj_fantasy_ppg = float(player.projected_fantasy_ppg) if player.projected_fantasy_ppg else 0
                consistency = float(player.consistency_rating) if player.consistency_rating else 0
                response += f"• Projected Fantasy Points: {proj_fantasy_ppg:.1f} per game\n"
                response += f"• Consistency Rating: {consistency:.2f}/1.0\n"
                
                if consistency > 0.7:
                    response += "  → High consistency makes them a reliable fantasy starter\n"
                elif consistency < 0.5:
                    response += "  → Volatility suggests streaming candidate or bench player\n"
                
                # Risk factors
                if player.injury_risk:
                    try:
                        risk = float(player.injury_risk)
                        if risk > 0.3:
                            response += f"• Injury Risk: {risk:.1%} - Monitor health closely\n"
                    except (ValueError, TypeError):
                        # injury_risk might be a string like "Low", "Medium", "High"
                        response += f"• Injury Risk: {player.injury_risk}\n"
                
                # Special designations
                if player.breakout_candidate:
                    response += "\n**🎯 BREAKOUT CANDIDATE**: Poised for statistical leap\n"
                if player.sleeper_score and player.sleeper_score > 0.6:
                    response += f"**💎 SLEEPER ALERT**: Score {player.sleeper_score:.2f} - Undervalued at current ADP\n"
                
                return response
            else:
                return f"No data found for player matching '{player_name}'"
                
        except Exception as e:
            import traceback
            logger.error(f"Error analyzing player stats: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"Error analyzing player: {str(e)}"
    
    def _find_sleeper_candidates_enhanced(self, criteria: str = "") -> str:
        """Find sleeper candidates with detailed reasoning for each"""
        try:
            db = next(get_db())
            
            # Check if asking about a specific player's draft value
            if criteria and ("worth" in criteria.lower() or "draft" in criteria.lower()):
                # Look for player names in the criteria
                player_check = db.execute(text("""
                    SELECT p.name, f.sleeper_score, f.adp_rank, f.adp_round,
                           f.projected_fantasy_ppg
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE LOWER(p.name) LIKE LOWER(:pattern)
                """), {"pattern": f"%{criteria.replace('worth', '').replace('drafting', '').replace('draft', '').replace('?', '').strip()}%"})
                
                player_result = player_check.fetchone()
                if player_result:
                    if player_result.sleeper_score >= 0.7:
                        return f"Yes, {player_result.name} is definitely worth drafting! Sleeper score: {player_result.sleeper_score:.2f}/1.00, ADP: Round {player_result.adp_round} (#{player_result.adp_rank}). They project for {player_result.projected_fantasy_ppg:.1f} fantasy PPG. Target them 1-2 rounds before their ADP."
                    elif player_result.sleeper_score >= 0.5:
                        return f"{player_result.name} is a decent value at their ADP. Sleeper score: {player_result.sleeper_score:.2f}/1.00, ADP: Round {player_result.adp_round} (#{player_result.adp_rank}). They're worth drafting at or slightly before their ADP."
                    else:
                        return f"{player_result.name} is not a great value. Sleeper score: {player_result.sleeper_score:.2f}/1.00, ADP: Round {player_result.adp_round} (#{player_result.adp_rank}). Consider other options unless they fall 2+ rounds past ADP."
            
            # Check if this is a "players like X" query
            if "like" in criteria.lower():
                # Extract player name after "like"
                import re
                match = re.search(r'like\s+(.+?)(?:\s|$)', criteria.lower())
                if match:
                    player_name = match.group(1).strip()
                    # Clean up common words that might follow
                    for suffix in ['who', 'that', 'with', 'but', 'and']:
                        if player_name.endswith(suffix):
                            player_name = player_name[:-len(suffix)].strip()
                    
                    # Try to find the full player name in our database
                    db = next(get_db())
                    result = db.execute(text("""
                        SELECT name FROM players 
                        WHERE LOWER(name) LIKE LOWER(:name)
                        LIMIT 1
                    """), {"name": f"%{player_name}%"})
                    
                    player = result.fetchone()
                    if player:
                        return self._find_similar_players(player.name)
            
            # Original sleeper finding logic
            db = next(get_db())
            
            # Check for position filtering in criteria
            position_filter = ""
            criteria_lower = criteria.lower() if criteria else ""
            
            # Map position keywords to database positions
            if "point guard" in criteria_lower or "pg" in criteria_lower:
                position_filter = "AND p.position = 'PG'"
            elif "shooting guard" in criteria_lower or "sg" in criteria_lower:
                position_filter = "AND p.position = 'SG'"
            elif "small forward" in criteria_lower or "sf" in criteria_lower:
                position_filter = "AND p.position = 'SF'"
            elif "power forward" in criteria_lower or "pf" in criteria_lower:
                position_filter = "AND p.position = 'PF'"
            elif "center" in criteria_lower or "centers" in criteria_lower:
                position_filter = "AND p.position = 'C'"
            elif "guard" in criteria_lower:
                position_filter = "AND p.position IN ('PG', 'SG')"
            elif "forward" in criteria_lower:
                position_filter = "AND p.position IN ('SF', 'PF')"
            elif "big" in criteria_lower or "bigs" in criteria_lower:
                position_filter = "AND p.position IN ('PF', 'C')"
            
            query = f"""
                SELECT 
                    p.name, p.position, p.team,
                    EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) as age,
                    f.adp_rank, f.adp_round,
                    f.sleeper_score, 
                    f.projected_fantasy_ppg,
                    f.consistency_rating,
                    f.injury_risk,
                    f.projected_ppg, f.projected_rpg, f.projected_apg,
                    f.shot_distribution,
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) < 24 THEN 'Young player development'
                        WHEN f.adp_rank > 100 THEN 'Late-round value'
                        WHEN p.team IN ('DET', 'HOU', 'ORL', 'OKC') THEN 'Improving team context'
                        ELSE 'Opportunity increase'
                    END as sleeper_reason
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE f.sleeper_score > 0.6
                {position_filter}
                ORDER BY f.sleeper_score DESC
                LIMIT 10
            """
            
            result = db.execute(text(query))
            
            sleepers = result.fetchall()
            if sleepers:
                import json
                response = "="*70 + "\n"
                if position_filter:
                    # Extract position from filter for display
                    if "SG" in position_filter:
                        pos_display = "SHOOTING GUARD"
                    elif "PG" in position_filter:
                        pos_display = "POINT GUARD"
                    elif "SF" in position_filter:
                        pos_display = "SMALL FORWARD"
                    elif "PF" in position_filter:
                        pos_display = "POWER FORWARD"
                    elif "C" in position_filter and "(" not in position_filter:
                        pos_display = "CENTER"
                    elif "'PG', 'SG'" in position_filter:
                        pos_display = "GUARD"
                    elif "'SF', 'PF'" in position_filter:
                        pos_display = "FORWARD"
                    elif "'PF', 'C'" in position_filter:
                        pos_display = "BIG MAN"
                    else:
                        pos_display = "FILTERED"
                    response += f"**2025-26 {pos_display} SLEEPER CANDIDATES**\n"
                else:
                    response += "**2025-26 FANTASY BASKETBALL SLEEPER CANDIDATES**\n"
                response += "Complete Statistical Analysis with Shot Distributions\n"
                response += "="*70 + "\n\n"
                
                # Make output so detailed it can't be summarized
                for idx, s in enumerate(sleepers, 1):
                    # Parse shot distribution
                    shot_dist = None
                    if s.shot_distribution:
                        try:
                            shot_dist = json.loads(s.shot_distribution) if isinstance(s.shot_distribution, str) else s.shot_distribution
                        except:
                            shot_dist = None
                    
                    response += f"#{idx}. **{s.name}**\n"
                    response += "-"*40 + "\n"
                    response += f"Position: {s.position} | Team: {s.team} | Age: {s.age if s.age else 'N/A'}\n"
                    response += f"📊 SLEEPER SCORE: {s.sleeper_score:.2f}/1.00\n"
                    response += f"📍 ADP: #{s.adp_rank} (Round {s.adp_round})\n"
                    response += f"\n📈 PROJECTIONS:\n"
                    response += f"  • Points: {s.projected_ppg:.1f} PPG\n"
                    response += f"  • Rebounds: {s.projected_rpg:.1f} RPG\n"
                    response += f"  • Assists: {s.projected_apg:.1f} APG\n"
                    response += f"  • Fantasy Points: {s.projected_fantasy_ppg:.1f} per game\n"
                    
                    if shot_dist:
                        response += f"\n🏀 SHOT DISTRIBUTION:\n"
                        response += f"  • 3-Point: {shot_dist.get('3PT', 0)*100:.0f}%\n"
                        response += f"  • Midrange: {shot_dist.get('midrange', 0)*100:.0f}%\n"
                        response += f"  • Paint: {shot_dist.get('paint', 0)*100:.0f}%\n"
                    
                    response += f"\n📋 ANALYSIS:\n"
                    response += f"  • Sleeper Reason: {s.sleeper_reason}\n"
                    if s.consistency_rating:
                        response += f"  • Consistency Rating: {s.consistency_rating:.2f}\n"
                    if s.injury_risk:
                        response += f"  • Injury Risk: {s.injury_risk}\n"
                    
                    # Enhanced strategic insights
                    response += f"\n🎯 STRATEGIC INSIGHTS:\n"
                    
                    # Draft timing recommendation
                    target_round = max(1, s.adp_round - 1)
                    response += f"  • Optimal Draft Window: Rounds {target_round}-{s.adp_round}\n"
                    response += f"  • Reach Threshold: Round {max(1, s.adp_round - 2)} (aggressive)\n"
                    
                    # Role-based analysis
                    if s.projected_ppg >= 20:
                        response += f"  • Role Profile: Primary Scorer - Build around as core piece\n"
                    elif s.projected_ppg >= 15:
                        response += f"  • Role Profile: Secondary Scorer - Excellent complement to stars\n"
                    elif s.projected_apg >= 5:
                        response += f"  • Role Profile: Playmaker - Boosts team assist totals\n"
                    else:
                        response += f"  • Role Profile: Role Player - Specialist for specific categories\n"
                    
                    # Team fit considerations
                    response += f"  • Best Fit: "
                    if shot_dist and shot_dist.get('3PT', 0) > 0.35:
                        response += "Teams needing 3PT production\n"
                    elif s.projected_rpg >= 8:
                        response += "Teams needing rebounding help\n"
                    elif s.projected_apg >= 5:
                        response += "Teams needing playmaking\n"
                    else:
                        response += "Balanced roster construction\n"
                    
                    # Risk/Reward Score
                    risk_score = 0
                    if s.injury_risk == "High":
                        risk_score += 3
                    elif s.injury_risk == "Medium":
                        risk_score += 2
                    else:
                        risk_score += 1
                    
                    reward_score = min(5, s.sleeper_score * 5)
                    risk_reward_ratio = reward_score / risk_score
                    
                    response += f"  • Risk/Reward Score: {risk_reward_ratio:.2f} "
                    if risk_reward_ratio >= 3:
                        response += "(Excellent value)\n"
                    elif risk_reward_ratio >= 2:
                        response += "(Good value)\n"
                    else:
                        response += "(Moderate value)\n"
                    
                    response += "\n"
                
                response += "="*70 + "\n"
                response += "STRATEGY SUMMARY: Target these players 1-2 rounds before their ADP\n"
                response += "="*70
                
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
            
            # Check if asking about a specific player
            if criteria:
                # Look for player names in the criteria
                player_check = db.execute(text("""
                    SELECT p.name, f.breakout_candidate
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE LOWER(p.name) LIKE LOWER(:pattern)
                """), {"pattern": f"%{criteria}%"})
                
                player_result = player_check.fetchone()
                if player_result:
                    if player_result.breakout_candidate:
                        # Get additional details for a complete answer
                        details = db.execute(text("""
                            SELECT p.name, p.position, p.team,
                                   f.adp_rank, f.adp_round,
                                   f.projected_ppg, f.projected_rpg, f.projected_apg,
                                   f.projected_fantasy_ppg, f.sleeper_score
                            FROM players p
                            JOIN fantasy_data f ON p.id = f.player_id
                            WHERE LOWER(p.name) LIKE LOWER(:pattern)
                        """), {"pattern": f"%{criteria}%"})
                        
                        player_data = details.fetchone()
                        if player_data:
                            return f"""**ANSWER: YES - {player_data.name} IS A BREAKOUT CANDIDATE**

**Player Profile**:
• Position: {player_data.position}
• Team: {player_data.team}
• ADP: #{player_data.adp_rank} (Round {player_data.adp_round})

**2025-26 Projections**:
• Points: {player_data.projected_ppg:.1f} PPG
• Rebounds: {player_data.projected_rpg:.1f} RPG
• Assists: {player_data.projected_apg:.1f} APG
• Fantasy Points: {player_data.projected_fantasy_ppg:.1f} per game

**Breakout Rationale**: Expected to significantly improve fantasy production based on age progression, expanded role, and favorable team situation. Sleeper score: {player_data.sleeper_score:.2f}

**Recommendation**: Target 1-2 rounds before ADP for maximum value."""
                        else:
                            return f"Yes, {player_result.name} is a breakout candidate for 2025-26. They are expected to significantly improve their fantasy production based on age, role expansion, and team situation."
                    else:
                        return f"**ANSWER: NO - {player_result.name} is NOT a breakout candidate**. They are either already established at their ceiling or not expected to have a significant statistical leap in production for the 2025-26 season."
            
            # Default behavior - return all breakout candidates
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) as age,
                    f.adp_rank, f.adp_round,
                    f.projected_fantasy_ppg,
                    f.projected_ppg, f.projected_rpg, f.projected_apg,
                    f.sleeper_score, f.consistency_rating,
                    gs.ppg as last_season_ppg,
                    gs.games_played as last_season_games,
                    CASE
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) BETWEEN 22 AND 25 THEN 'Sophomore/Junior leap expected'
                        WHEN gs.ppg IS NULL THEN 'Rookie with high upside'
                        WHEN f.projected_ppg > CAST(gs.ppg AS FLOAT) * 1.2 THEN 'Major role expansion'
                        ELSE 'System/coaching change benefit'
                    END as breakout_reason
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                LEFT JOIN (
                    SELECT player_id,
                           AVG(points) as ppg,
                           COUNT(*) as games_played
                    FROM game_stats
                    GROUP BY player_id
                ) gs ON p.id = gs.player_id
                WHERE f.breakout_candidate = true
                ORDER BY f.projected_fantasy_ppg DESC
                LIMIT 10
            """))
            
            breakouts = result.fetchall()
            if breakouts:
                response = "**2025-26 Breakout Candidates** (with statistical evidence):\n\n"
                
                # Top tier breakouts with detailed analysis
                response += "**ELITE BREAKOUT TARGETS**:\n\n"
                for idx, b in enumerate(breakouts[:3], 1):
                    response += f"**{idx}. {b.name}** ({b.position}, {b.team})\n"
                    response += f"• **Age**: {b.age} years old\n"
                    response += f"• **ADP**: #{b.adp_rank} (Round {b.adp_round})\n"
                    
                    # Year-over-year comparison if available
                    if b.last_season_ppg:
                        try:
                            last_ppg = float(b.last_season_ppg)
                            proj_ppg = float(b.projected_ppg)
                            improvement = ((proj_ppg - last_ppg) / last_ppg * 100)
                            response += f"• **Scoring Projection**: {proj_ppg:.1f} PPG "
                            response += f"(+{improvement:.1f}% from {last_ppg:.1f} last season)\n"
                        except (ValueError, TypeError, ZeroDivisionError):
                            response += f"• **Scoring Projection**: {b.projected_ppg:.1f} PPG\n"
                    else:
                        response += f"• **Scoring Projection**: {b.projected_ppg:.1f} PPG (rookie season)\n"
                    
                    response += f"• **Full Projection**: {b.projected_rpg:.1f} RPG, {b.projected_apg:.1f} APG\n"
                    response += f"• **Fantasy Impact**: {b.projected_fantasy_ppg:.1f} FP/game\n"
                    response += f"• **Breakout Catalyst**: {b.breakout_reason}\n"
                    
                    # Age-specific analysis
                    if b.age:
                        if b.age <= 23:
                            response += f"  → Young player trajectory suggests continued growth\n"
                        elif b.age <= 26:
                            response += f"  → Entering statistical prime years\n"
                    
                    # Strategic draft recommendations
                    response += f"\n**Draft Strategy**:\n"
                    response += f"  • Target Round: {max(1, b.adp_round - 1)} (before consensus)\n"
                    response += f"  • Pairing Suggestions: "
                    if b.projected_apg >= 6:
                        response += "Pair with elite scorers who need a playmaker\n"
                    elif b.projected_rpg >= 8:
                        response += "Pair with guards to balance rebounding\n"
                    else:
                        response += "Versatile - fits most roster constructions\n"
                    
                    # Risk assessment
                    response += f"  • Breakout Confidence: "
                    if b.sleeper_score >= 0.8:
                        response += "High (80%+ probability)\n"
                    elif b.sleeper_score >= 0.6:
                        response += "Moderate (60-80% probability)\n"
                    else:
                        response += "Speculative (sub-60% probability)\n"
                    
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
                    p.name, p.position, p.team,
                    EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) as age,
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
                    GROUP BY player_id
                ) gs ON p.id = gs.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.fetchone()
            if player:
                response = f"**2025-26 Projection for {player.name}**:\n\n"
                response += f"**Player Context**:\n"
                response += f"• Team: {player.team}\n"
                response += f"• Position: {player.position}\n"
                if player.age:
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
            # Parse player names - handle multiple formats
            players_lower = players.lower()
            if " vs " in players_lower:
                names = players.split(" vs ")
            elif " versus " in players_lower:
                names = players.split(" versus ")
            elif " or " in players_lower:
                names = players.split(" or ")
            elif " and " in players_lower:
                names = players.split(" and ")
            elif ", " in players:
                names = players.split(", ")
            else:
                # Try to extract capitalized names
                import re
                names = re.findall(r'[A-Z][a-z]+(?: [A-Z][a-z]+)*', players)
                if len(names) != 2:
                    return "Please provide two players to compare (e.g., 'LeBron vs Durant' or 'Barnes and Banchero')"
            
            if len(names) != 2:
                return "Please provide exactly two players to compare"
            
            db = next(get_db())
            
            comparison_data = []
            for name in names:
                result = db.execute(text("""
                    SELECT 
                        p.name, p.position, p.team,
                        EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) as age,
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
                response += "\n**Projected Stats (2025-26)**:\n"
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
    
    def _evaluate_player_draft_value(self, player_name: str = "") -> str:
        """Evaluate if a specific player is worth drafting"""
        try:
            if not player_name:
                return "Please specify a player name to evaluate."
            
            db = next(get_db())
            
            # Clean the player name
            clean_name = player_name.replace("?", "").strip()
            
            # Look for the player
            result = db.execute(text("""
                SELECT p.name, f.sleeper_score, f.adp_rank, f.adp_round,
                       f.projected_fantasy_ppg, f.consistency_rating,
                       f.injury_risk
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE LOWER(p.name) LIKE LOWER(:pattern)
                LIMIT 1
            """), {"pattern": f"%{clean_name}%"})
            
            player = result.fetchone()
            if not player:
                return f"Could not find player matching '{player_name}'"
            
            # Evaluate draft value based on sleeper score
            if player.sleeper_score >= 0.8:
                verdict = "EXCELLENT VALUE - Definitely worth drafting!"
                recommendation = f"Target {player.name} 1-2 rounds before their ADP of Round {player.adp_round}."
            elif player.sleeper_score >= 0.7:
                verdict = "GOOD VALUE - Worth drafting"
                recommendation = f"Draft {player.name} at or slightly before their ADP of Round {player.adp_round}."
            elif player.sleeper_score >= 0.5:
                verdict = "FAIR VALUE - Decent pick at ADP"
                recommendation = f"{player.name} is appropriately valued. Draft at ADP (Round {player.adp_round}) if they fit your build."
            else:
                verdict = "POOR VALUE - Better options available"
                recommendation = f"Only draft {player.name} if they fall 2+ rounds past their ADP of Round {player.adp_round}."
            
            response = f"**{player.name} Draft Analysis**\n\n"
            response += f"**Verdict**: {verdict}\n"
            response += f"• **Sleeper Score**: {player.sleeper_score:.2f}/1.00\n"
            response += f"• **ADP**: #{player.adp_rank} (Round {player.adp_round})\n"
            response += f"• **Projected Fantasy PPG**: {player.projected_fantasy_ppg:.1f}\n"
            response += f"• **Consistency**: {player.consistency_rating}\n"
            response += f"• **Injury Risk**: {player.injury_risk}\n\n"
            response += f"**Recommendation**: {recommendation}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error evaluating player draft value: {str(e)}")
            return f"Error evaluating {player_name}: {str(e)}"
    
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
    
    def _characterize_player(self, player_name: str) -> Dict[str, Any]:
        """Create a comprehensive player profile for similarity matching"""
        try:
            db = next(get_db())
            
            # Get comprehensive player data including shot distribution
            result = db.execute(text("""
                SELECT 
                    p.id, p.name, p.position, p.team, p.playing_style,
                    EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) as age,
                    f.adp_rank, f.adp_round, f.keeper_round,
                    f.projected_ppg, f.projected_rpg, f.projected_apg,
                    f.projected_spg, f.projected_bpg, f.projected_3pm,
                    f.projected_fantasy_ppg, f.sleeper_score,
                    f.breakout_candidate, f.consistency_rating,
                    f.shot_distribution,
                    AVG(gs.points) as avg_points,
                    AVG(gs.rebounds) as avg_rebounds,
                    AVG(gs.assists) as avg_assists,
                    AVG(gs.three_pointers_attempted) as avg_3pa,
                    AVG(gs.usage_rate) as avg_usage_rate,
                    COUNT(gs.id) as games_played
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                LEFT JOIN game_stats gs ON p.id = gs.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                GROUP BY p.id, p.name, p.position, p.team, p.playing_style,
                         p.birth_date, f.adp_rank, f.adp_round, f.keeper_round,
                         f.projected_ppg, f.projected_rpg, f.projected_apg,
                         f.projected_spg, f.projected_bpg, f.projected_3pm,
                         f.projected_fantasy_ppg, f.sleeper_score,
                         f.breakout_candidate, f.consistency_rating,
                         f.shot_distribution
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.fetchone()
            
            if not player:
                return None
            
            # Determine player archetype based on stats and style
            avg_3pa = float(player.avg_3pa) if player.avg_3pa else 0
            avg_assists = float(player.avg_assists) if player.avg_assists else player.projected_apg
            avg_usage = float(player.avg_usage_rate) if player.avg_usage_rate else 20
            
            # Classify player characteristics
            is_shooter = avg_3pa > 6 or player.projected_3pm > 2.5
            is_playmaker = avg_assists > 5
            is_high_usage = avg_usage > 28
            is_medium_usage = 22 <= avg_usage <= 28
            is_sleeper = player.sleeper_score > 0.6
            
            # Determine primary role
            if player.position in ['PG', 'SG']:
                if is_shooter and avg_3pa > 7:
                    primary_role = 'volume_shooter'
                elif is_playmaker:
                    primary_role = 'floor_general'
                else:
                    primary_role = 'combo_guard'
            elif player.position in ['SF', 'PF']:
                if is_shooter:
                    primary_role = 'stretch_forward'
                elif player.projected_rpg > 8:
                    primary_role = 'rebounding_forward'
                else:
                    primary_role = 'versatile_forward'
            else:  # Center
                if player.projected_apg > 4:
                    primary_role = 'point_center'
                elif is_shooter:
                    primary_role = 'stretch_center'
                else:
                    primary_role = 'traditional_center'
            
            # Parse shot distribution if available
            shot_distribution = player.shot_distribution if player.shot_distribution else {
                '3PT': 0.35,
                'midrange': 0.30,
                'paint': 0.35
            }
            
            return {
                'player_id': player.id,
                'name': player.name,
                'position': player.position,
                'team': player.team,
                'playing_style': player.playing_style,
                'age': int(player.age) if player.age else None,
                'primary_role': primary_role,
                'adp_rank': player.adp_rank,
                'adp_round': player.adp_round,
                'projections': {
                    'ppg': player.projected_ppg,
                    'rpg': player.projected_rpg,
                    'apg': player.projected_apg,
                    'spg': player.projected_spg,
                    'bpg': player.projected_bpg,
                    '3pm': player.projected_3pm,
                    'fantasy_ppg': player.projected_fantasy_ppg
                },
                'characteristics': {
                    'is_shooter': is_shooter,
                    'is_playmaker': is_playmaker,
                    'is_high_usage': is_high_usage,
                    'is_sleeper': is_sleeper,
                    'is_breakout': player.breakout_candidate,
                    'avg_3pa': avg_3pa,
                    'usage_rate': avg_usage,
                    'consistency': player.consistency_rating
                },
                'shot_distribution': shot_distribution,
                'sleeper_score': player.sleeper_score,
                'games_data_available': player.games_played or 0
            }
            
        except Exception as e:
            logger.error(f"Error characterizing player {player_name}: {str(e)}")
            return None
    
    def _find_similar_players(self, reference_player: str, min_sleeper_score: float = 0.6) -> str:
        """Find players similar to a reference player using shot distributions and playing style"""
        try:
            # First characterize the reference player
            ref_profile = self._characterize_player(reference_player)
            if not ref_profile:
                return f"Could not find player '{reference_player}' in database"
            
            db = next(get_db())
            
            # Get reference player's shot distribution for comparison
            ref_shot_dist = ref_profile['shot_distribution']
            if isinstance(ref_shot_dist, str):
                import json
                ref_shot_dist = json.loads(ref_shot_dist)
            
            # Find similar players based on multiple factors
            result = db.execute(text("""
                WITH similarity_scores AS (
                    SELECT 
                        p.id,
                        p.name,
                        p.position,
                        p.team,
                        p.playing_style,
                        fd.sleeper_score,
                        fd.adp_rank,
                        fd.shot_distribution,
                        fd.projected_fantasy_ppg,
                        -- Calculate similarity based on position and style
                        CASE 
                            WHEN p.position = :ref_position THEN 0.3
                            WHEN p.position IN ('PG', 'SG') AND :ref_position IN ('PG', 'SG') THEN 0.2
                            WHEN p.position IN ('SF', 'PF') AND :ref_position IN ('SF', 'PF') THEN 0.2
                            ELSE 0
                        END as position_similarity,
                        CASE
                            WHEN p.playing_style = :ref_style THEN 0.3
                            ELSE 0
                        END as style_similarity
                    FROM players p
                    JOIN fantasy_data fd ON p.id = fd.player_id
                    WHERE p.name != :ref_name
                        AND fd.sleeper_score >= :min_sleeper
                        AND fd.shot_distribution IS NOT NULL
                )
                SELECT *
                FROM similarity_scores
                ORDER BY (position_similarity + style_similarity + sleeper_score) DESC
                LIMIT 10
            """), {
                "ref_name": ref_profile['name'],
                "ref_position": ref_profile['position'],
                "ref_style": ref_profile['playing_style'],
                "min_sleeper": min_sleeper_score
            })
            
            similar_players = result.fetchall()
            
            if not similar_players:
                return f"No similar sleeper candidates found for {ref_profile['name']}"
            
            # Calculate shot distribution similarity for each player
            import json
            import math
            
            def calculate_shot_similarity(dist1, dist2):
                """Calculate Euclidean distance between shot distributions"""
                if isinstance(dist1, str):
                    dist1 = json.loads(dist1)
                if isinstance(dist2, str):
                    dist2 = json.loads(dist2)
                
                # Calculate Euclidean distance
                distance = math.sqrt(
                    (dist1.get('3PT', 0) - dist2.get('3PT', 0))**2 +
                    (dist1.get('midrange', 0) - dist2.get('midrange', 0))**2 +
                    (dist1.get('paint', 0) - dist2.get('paint', 0))**2
                )
                # Convert to similarity score (0-1, where 1 is identical)
                return max(0, 1 - distance)
            
            # Build response with detailed similarity analysis
            response = f"**Players Similar to {ref_profile['name']}** "
            response += f"({ref_profile['position']}, {ref_profile['playing_style']})\n"
            response += f"Reference Profile: {ref_profile['characteristics']['avg_3pa']:.1f} 3PA/game, "
            response += f"{ref_profile['characteristics']['usage_rate']:.1f}% usage\n\n"
            
            response += "**Top Similar Sleeper Candidates:**\n\n"
            
            for i, player in enumerate(similar_players[:5], 1):
                shot_sim = calculate_shot_similarity(ref_shot_dist, player.shot_distribution)
                
                # Parse player's shot distribution for display
                player_dist = player.shot_distribution
                if isinstance(player_dist, str):
                    player_dist = json.loads(player_dist)
                
                response += f"{i}. **{player.name}** ({player.position}, {player.team})\n"
                response += f"   • Sleeper Score: {player.sleeper_score:.2f} | ADP: #{player.adp_rank}\n"
                response += f"   • Playing Style: {player.playing_style}\n"
                response += f"   • Shot Profile: {player_dist.get('3PT', 0)*100:.0f}% 3PT, "
                response += f"{player_dist.get('midrange', 0)*100:.0f}% Mid, "
                response += f"{player_dist.get('paint', 0)*100:.0f}% Paint\n"
                response += f"   • Shot Similarity: {shot_sim:.0%}\n"
                response += f"   • Fantasy Projection: {player.projected_fantasy_ppg:.1f} FP/game\n"
                
                # Add specific similarity insights
                if player.position == ref_profile['position']:
                    response += f"   • ✓ Same position ({player.position})\n"
                if player.playing_style == ref_profile['playing_style']:
                    response += f"   • ✓ Same playing style ({player.playing_style})\n"
                if shot_sim > 0.8:
                    response += f"   • ✓ Very similar shot distribution\n"
                
                response += "\n"
            
            response += f"\n**Key Insight**: These players share similar profiles to {ref_profile['name']} "
            response += "but may be available later in drafts, offering excellent value.\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error finding similar players: {str(e)}")
            return f"Error finding similar players: {str(e)}"