"""
DraftPrep Agent - Enhanced with real PostgreSQL tools for draft preparation
Handles: Keeper decisions, ADP analysis, punt strategies, mock drafts
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
import re
import unicodedata
import asyncio
import logging

logger = logging.getLogger(__name__)

def clean_unicode(text: str) -> str:
    """Remove or replace problematic Unicode characters"""
    if not text:
        return text
    # Replace common problematic characters
    replacements = {
        'ć': 'c', 'Ć': 'C', 'č': 'c', 'Č': 'C',
        'ž': 'z', 'Ž': 'Z', 'š': 's', 'Š': 'S',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U',
        'ö': 'o', 'Ö': 'O', 'ä': 'a', 'Ä': 'A',
        'é': 'e', 'É': 'E', 'è': 'e', 'È': 'E',
        'ê': 'e', 'Ê': 'E', 'à': 'a', 'À': 'A',
        'á': 'a', 'Á': 'A', 'í': 'i', 'Í': 'I',
        'ó': 'o', 'Ó': 'O', 'ú': 'u', 'Ú': 'U'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Remove any remaining non-ASCII characters
    return ''.join(char if ord(char) < 128 else '' for char in text)

class DraftPrepAgent(BaseAgent):
    """
    Draft preparation specialist with real database tools.
    Focuses on keeper value, ADP analysis, and punt strategies.
    """
    
    def __init__(self):
        tools = [
            # Keeper Decision Tools
            Tool(
                name="calculate_keeper_value",
                description=(
                    "Calculate keeper value, should I keep player X in round Y, is player worth keeping, "
                    "keeper decision analysis, retention value, keep or drop decision. "
                    "Use for: keep, keeper, retain, worth keeping, should I keep, keeper round, "
                    "keeper value, retention, hold, preserve. "
                    "Answers: Should I keep Ja Morant in round 3? Is LaMelo worth keeping in round 4? "
                    "Keep or drop player X? Keeper advice for player Y?"
                ),
                func=self._calculate_keeper_value
            ),
            
            # ADP Analysis Tools
            Tool(
                name="analyze_adp_value",
                description=(
                    "Find ADP value picks, players falling in drafts, overvalued/undervalued by ADP, "
                    "draft steals, reaches to avoid, value relative to ranking. "
                    "Use for: ADP value, falling, rising, overvalued, undervalued, draft steal, "
                    "reach, value pick, ADP bargain, mispriced. "
                    "Answers: Who offers good ADP value? Undervalued players? Overvalued to avoid?"
                ),
                func=self._analyze_adp_value
            ),
            Tool(
                name="get_adp_rankings",
                description=(
                    "Get current ADP rankings, draft rankings, where players are being drafted, "
                    "consensus rankings, mock draft data, average draft position. "
                    "Use for: ADP, rankings, draft position, where drafted, consensus rank, "
                    "mock draft results, typical draft spot. "
                    "Answers: What's the ADP? Current rankings? Where is player going? Draft board?"
                ),
                func=self._get_adp_rankings
            ),
            
            # Punt Strategy Tools
            Tool(
                name="build_punt_strategy",
                description=(
                    "Build punt strategy team. Handles: punt FT%, punt FG%, punt assists, punt 3s, punt points, "
                    "punt rebounds, punt steals, punt blocks, build team around Giannis, build around any player. "
                    "ALWAYS use this for any query containing: 'punt', 'punting', 'build team around', "
                    "'build around', 'ignore category', 'sacrifice stat'. "
                    "Example queries: 'Build a punt FT% team around Giannis', 'Build punt FT% team', "
                    "'punt assists build', 'best punt for Giannis', 'punt strategy around player X'"
                ),
                func=self._build_punt_strategy
            ),
            Tool(
                name="find_punt_fits",
                description=(
                    "Find players for punt builds, who fits punt FT%, punt FG% targets, "
                    "punt assist players, category specialists, punt build targets. "
                    "Use for: punt fit, category fit, punt target, specialist, fits build, "
                    "punt complement, synergy, categorical fit. "
                    "Answers: Who fits punt FT%? Best centers for punt FT? Punt assist targets?"
                ),
                func=self._find_punt_fits
            ),
            
            # Mock Draft Tools
            Tool(
                name="simulate_draft_pick",
                description=(
                    "Mock draft simulation, best available at pick X, who to draft at pick 12, "
                    "draft board at position, available players, mock draft pick, BPA. "
                    "Use for: mock draft, pick X, draft position, best available, BPA, "
                    "who to draft, draft simulation, pick recommendation. "
                    "Answers: Mock draft for pick 12? Best available at pick 24? "
                    "Who should I take with pick 8? Draft board for round 3?"
                ),
                func=self._simulate_draft_pick
            )
        ]
        
        super().__init__(
            name="DraftPrep Agent",
            description="Draft expert - keeper decisions, ADP analysis, punt strategies with AI-powered reranking.",
            tools=tools
        )
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools"""
        if settings.OPENAI_API_KEY:
            from langchain.agents import ZeroShotAgent, AgentExecutor
            from langchain.chains import LLMChain
            
            # Custom prompt similar to Intelligence Agent
            prefix = """You are an expert fantasy basketball draft strategist for the 2025-26 NBA season.

CRITICAL RULES - VIOLATION MEANS FAILURE:
1. NEVER mention tool names, actions, or "based on the analysis from" in your responses
2. NEVER say "based on my expert analysis using", "using the", "from the X tool", "the tool says", or similar phrases  
3. NEVER write "using the build_punt_strategy tool" or ANY tool name
4. Present information as YOUR expert knowledge and recommendations
5. Start responses with "I recommend" or "Here's my recommendation" NOT "Based on..."
6. Be specific and detailed in your answers
7. IMPORTANT: For keeper questions, ALWAYS include:
   - The player's ADP and typical draft position
   - Whether it's good/poor value to keep at that round
   - The round advantage or disadvantage
   - A clear keep/pass recommendation with reasoning
8. DO NOT summarize - provide complete analysis from the tool output
9. If a question is unrelated to fantasy basketball, politely say "I can only help with fantasy basketball draft questions."

Examples of BAD responses (NEVER DO THIS):
- "Based on my expert analysis using the build_punt_strategy tool..."
- "Based on the analysis from the calculate_keeper_value tool..."
- "The tool recommends..."
- "Using the X tool..."

Examples of GOOD responses:
- "I recommend building a punt FT% team around Giannis by targeting..."
- "For keeper value, Ja Morant in round 3 is excellent value because..."
- "Here's my recommended punt FT% strategy..."

You have access to the following tools:"""
            
            suffix = """Begin! Remember: 
- NEVER mention tools or say "based on the analysis" or "using the X tool"
- NEVER write tool names in your final answer
- Start with "I recommend" or "Here's my recommendation"
- For keeper questions, include full value analysis
- Present this as YOUR expert recommendation

Question: {input}
Thought: {agent_scratchpad}"""
            
            prompt = ZeroShotAgent.create_prompt(
                tools=self.tools,
                prefix=prefix,
                suffix=suffix,
                input_variables=["input", "agent_scratchpad"]
            )
            
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.1)
            llm_chain = LLMChain(llm=llm, prompt=prompt)
            agent = ZeroShotAgent(llm_chain=llm_chain, tools=self.tools)
            
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True
            )
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a draft-related query"""
        
        if not self.agent_executor:
            return AgentResponse(
                content="DraftPrep agent not properly initialized. Please check OpenAI API key.",
                confidence=0.0
            )
        
        try:
            # Let the agent handle all queries with enhanced tool descriptions
            enhanced_message = f"""[Context: Fantasy basketball draft preparation for 2025-26 season]

User Query: {message}

Instructions: 
1. Use the appropriate tool based on the query
2. CRITICAL: When you get a tool response with details (stats, analysis, recommendations), include ALL of it in your final answer
3. For keeper questions specifically, your response MUST include:
   - Player's ADP and draft position
   - The value assessment (good/poor value)
   - Round advantage/disadvantage
   - Clear recommendation with reasoning
4. Do NOT condense or summarize the tool output - preserve all the details
5. Never mention tool names or say "based on the analysis"""
            
            result = await asyncio.wait_for(
                self.agent_executor.arun(input=enhanced_message),
                timeout=30.0
            )
            
            return AgentResponse(
                content=result,
                metadata={
                    "context": context,
                    "agent_type": "draft_prep",
                    "method": "agent_reasoning"
                },
                tools_used=[tool.name for tool in self.tools],
                confidence=0.7  # Lower confidence for agent responses
            )
        except asyncio.TimeoutError:
            from .error_messages import get_friendly_error_message
            return AgentResponse(
                content=get_friendly_error_message("draft_prep", message, "timeout"),
                confidence=0.5,
                metadata={"error": "timeout", "agent_type": "draft_prep"}
            )
        except Exception as e:
            error_msg = str(e)
            if "iteration limit" in error_msg.lower() or "time limit" in error_msg.lower():
                from .error_messages import get_friendly_error_message
                return AgentResponse(
                    content=get_friendly_error_message("draft_prep", message, "iteration_limit"),
                    confidence=0.5,
                    metadata={"error": "iteration_limit", "agent_type": "draft_prep"}
                )
            logger.error(f"Unexpected error - Agent: draft_prep, Error: {str(e)}, Query: {message}")
            return AgentResponse(
                content=("I apologize for the inconvenience. I am unable to complete your request at this time. "
                        "At SportsBrain, we're always working hard to improve user experience. "
                        "This interaction has been logged for later analysis."),
                confidence=0.0,
                metadata={"error": str(e), "agent_type": "draft_prep"}
            )
    
    def _get_supported_tasks(self) -> List[str]:
        """Return list of supported tasks"""
        return [
            "keeper_decisions",
            "adp_analysis",
            "value_picks",
            "punt_strategies",
            "mock_drafts",
            "draft_rankings",
            "position_scarcity",
            "sleeper_picks"
        ]
    
    # KEEPER VALUE TOOLS
    
    def _calculate_keeper_value(self, query: str) -> str:
        """Calculate keeper value for a player in a specific round"""
        try:
            # Parse player name and round from query
            player_name = None
            keeper_round = None
            
            # Common player name patterns
            if "ja morant" in query.lower():
                player_name = "Ja Morant"
            elif "giannis" in query.lower():
                player_name = "Giannis Antetokounmpo"
            elif "tatum" in query.lower():
                player_name = "Jayson Tatum"
            else:
                # Try to extract any capitalized names
                name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', query)
                if name_match:
                    player_name = name_match.group(1)
            
            # Extract round number
            round_match = re.search(r'round\s*(\d+)|(\d+)(?:st|nd|rd|th)\s*round', query.lower())
            if round_match:
                keeper_round = int(round_match.group(1) or round_match.group(2))
            
            if not player_name:
                return "Please specify a player name for keeper analysis"
            
            db = next(get_db())
            
            # Query player with fantasy data
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.adp_rank, f.adp_round, f.keeper_round,
                    f.projected_fantasy_ppg, f.consistency_rating,
                    f.injury_risk
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE LOWER(p.name) LIKE LOWER(:name)
                LIMIT 1
            """), {"name": f"%{player_name}%"})
            
            player = result.first()
            if not player:
                return f"Player {player_name} not found in database"
            
            # Calculate keeper value
            if keeper_round:
                # value_diff: How many rounds LATER you get to keep vs their ADP
                # Positive = getting them LATER than ADP (good value)
                # Negative = keeping them EARLIER than ADP (bad value)
                value_diff = keeper_round - player.adp_round
                
                if value_diff >= 3:
                    recommendation = "EXCEPTIONAL VALUE - Must keep!"
                elif value_diff >= 2:
                    recommendation = "GREAT VALUE - Strongly recommend keeping"
                elif value_diff >= 1:
                    recommendation = "GOOD VALUE - Worth keeping"
                elif value_diff == 0:
                    recommendation = "FAIR VALUE - Neutral, consider other options"
                elif value_diff == -1:
                    recommendation = "SLIGHT OVERPAY - Probably pass"
                else:
                    recommendation = "POOR VALUE - Do not keep"
                
                # Format the advantage/disadvantage text correctly
                if value_diff > 0:
                    advantage_text = f"That's a {value_diff} round discount!"
                elif value_diff < 0:
                    advantage_text = f"That's {abs(value_diff)} round(s) too expensive!"
                else:
                    advantage_text = "That's exactly at market value."
                
                response = f"""
**Keeper Analysis for {clean_unicode(player.name)}**

[STATS] **Player Info**:
- Position: {player.position} | Team: {player.team}
- ADP: #{player.adp_rank} (Round {player.adp_round})
- Typical Keeper Round: {player.keeper_round}
- Your Keeper Round: {keeper_round}

[TARGET] **Recommendation**: {recommendation}

[VALUE] **Value Analysis**:
- You'd be getting a Round {player.adp_round} player in Round {keeper_round}
- {advantage_text}
- Projected Fantasy PPG: {player.projected_fantasy_ppg:.1f}
- Consistency: {player.consistency_rating:.2f} | Injury Risk: {player.injury_risk}

[STRATEGY] **Strategic Insights**:
- Opportunity Cost: {"Low - great value allows flexibility" if value_diff >= 2 else "High - limits draft options" if value_diff <= -1 else "Moderate - standard keeper play"}
- Alternative Strategy: {"Look for better keeper options" if value_diff < 0 else f"Lock this in and build around {player.position} strength"}
- Build Synergy: {"Punt FT% friendly" if player.position in ["C", "PF"] else "Balanced build friendly"}
- Draft Capital Saved: {max(0, value_diff)} rounds of value to invest elsewhere

[TIP] **Bottom Line**: {"Keep him!" if value_diff > 0 else "Pass and draft someone else"}
"""
            else:
                response = f"""
**{clean_unicode(player.name)} Keeper Info**:
- ADP: #{player.adp_rank} (Round {player.adp_round})
- Recommended Keeper Round: {player.keeper_round} or later
- Projected: {player.projected_fantasy_ppg:.1f} fantasy points/game
"""
            
            return response
            
        except Exception as e:
            return f"Error calculating keeper value: {str(e)}"
    
    # ADP VALUE TOOLS
    
    def _analyze_adp_value(self, criteria: str = "") -> str:
        """Find players with good value relative to ADP"""
        try:
            db = next(get_db())
            
            # Find players where projected value exceeds ADP
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.adp_rank, f.adp_round,
                    f.projected_fantasy_ppg,
                    f.sleeper_score,
                    (f.projected_fantasy_ppg * 82) as total_projection,
                    (f.projected_fantasy_ppg * 82 / f.adp_rank) as value_ratio
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE f.adp_rank BETWEEN 20 AND 100
                ORDER BY value_ratio DESC
                LIMIT 10
            """))
            
            values = result.fetchall()
            
            response = "[TARGET] **Top ADP Value Picks for 2025-26**:\n\n"
            for i, v in enumerate(values[:7], 1):
                response += f"{i}. **{v.name}** ({v.position}, {v.team})\n"
                response += f"   - ADP: #{v.adp_rank} (Round {v.adp_round})\n"
                response += f"   - Projected: {v.projected_fantasy_ppg:.1f} FP/game\n"
                response += f"   - Value Score: {v.value_ratio:.2f}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error analyzing ADP value: {str(e)}"
    
    def _get_adp_rankings(self, position: str = "") -> str:
        """Get current ADP rankings, optionally filtered by position or player"""
        try:
            db = next(get_db())
            
            # Check if asking about a specific player
            position_lower = position.lower()
            if "adp" in position_lower or "ranking" in position_lower:
                # Extract player name from queries like "What's LaMelo Ball's ADP?"
                import re
                # Look for capitalized names
                names = re.findall(r'[A-Z][a-z]+(?: [A-Z][a-z]+)*', position)
                if names:
                    player_name = ' '.join(names)
                    # Look up specific player
                    result = db.execute(text("""
                        SELECT p.name, p.position, p.team, f.adp_rank, f.adp_round, 
                               f.projected_fantasy_ppg
                        FROM players p
                        JOIN fantasy_data f ON p.id = f.player_id
                        WHERE LOWER(p.name) LIKE LOWER(:name)
                        LIMIT 1
                    """), {"name": f"%{player_name}%"})
                    
                    player = result.first()
                    if player:
                        return f"""**{clean_unicode(player.name)} ADP Information**:
                        
• **Current ADP**: #{player.adp_rank} (Round {player.adp_round})
• **Position**: {player.position}
• **Team**: {player.team}
• **Projected Fantasy PPG**: {player.projected_fantasy_ppg:.1f}

[TIP] Draft Window: Target 3-5 picks before ADP#{player.adp_rank}"""
                    else:
                        position = ""  # Fall through to general rankings
            
            # Build query based on position filter
            if position and position.upper() in ['PG', 'SG', 'SF', 'PF', 'C']:
                query = text("""
                    SELECT p.name, p.position, p.team, f.adp_rank, f.adp_round
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE p.position = :position
                    ORDER BY f.adp_rank
                    LIMIT 15
                """)
                result = db.execute(query, {"position": position.upper()})
            else:
                query = text("""
                    SELECT p.name, p.position, p.team, f.adp_rank, f.adp_round
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    ORDER BY f.adp_rank
                    LIMIT 20
                """)
                result = db.execute(query)
            
            players = result.fetchall()
            
            title = f"Top {position.upper()} Rankings" if position else "Top 20 Overall Rankings"
            response = f"[LIST] **{title} (2025-26 ADP)**:\n\n"
            
            for p in players:
                name = clean_unicode(p.name)
                response += f"{p.adp_rank}. {name} ({p.position}, {p.team}) - Round {p.adp_round}\n"
            
            return response
            
        except Exception as e:
            return f"Error getting ADP rankings: {str(e)}"
    
    # PUNT STRATEGY TOOLS
    
    def _build_punt_strategy(self, strategy: str) -> str:
        """Build a complete punt strategy around a category"""
        try:
            # Check if a specific player is mentioned (e.g., "around Giannis")
            player_mentioned = None
            if "giannis" in strategy.lower():
                player_mentioned = "Giannis Antetokounmpo"
                # Giannis is typically associated with punt FT%
                if "ft" not in strategy.lower():
                    strategy = strategy + " FT%"
            elif "simmons" in strategy.lower() or "ben simmons" in strategy.lower():
                player_mentioned = "Ben Simmons"
                if "ft" not in strategy.lower():
                    strategy = strategy + " FT%"
            elif "gobert" in strategy.lower():
                player_mentioned = "Rudy Gobert"
                if "ft" not in strategy.lower():
                    strategy = strategy + " FT%"
            
            # Parse the punt category
            punt_cat = None
            if "ft" in strategy.lower() or "free throw" in strategy.lower():
                punt_cat = "FT%"
                punt_field = "punt_ft_fit"
            elif "fg" in strategy.lower() or "field goal" in strategy.lower():
                punt_field = "punt_fg_fit"
                punt_cat = "FG%"
            elif "ast" in strategy.lower() or "assist" in strategy.lower():
                punt_field = "punt_ast_fit"
                punt_cat = "Assists"
            elif "3" in strategy.lower() or "three" in strategy.lower():
                punt_field = "punt_3pm_fit"
                punt_cat = "3-Pointers"
            elif "reb" in strategy.lower() or "rebound" in strategy.lower():
                punt_field = None  # We'll handle this differently
                punt_cat = "Rebounds"
            elif "pts" in strategy.lower() or "point" in strategy.lower() or "scoring" in strategy.lower():
                punt_field = None
                punt_cat = "Points"
            elif "stl" in strategy.lower() or "steal" in strategy.lower():
                punt_field = None
                punt_cat = "Steals"
            elif "blk" in strategy.lower() or "block" in strategy.lower():
                punt_field = None
                punt_cat = "Blocks"
            else:
                return "Please specify a category to punt (FT%, FG%, Assists, 3PM, Rebounds, Points, Steals, or Blocks)"
            
            db = next(get_db())
            
            # Get players that fit this punt build
            if punt_field:
                # Use existing punt fields for categories we have
                result = db.execute(text(f"""
                    SELECT 
                        p.name, p.position, p.team,
                        f.adp_rank, f.adp_round,
                        f.projected_ppg, f.projected_rpg, f.projected_apg,
                        f.projected_bpg, f.projected_spg,
                        f.projected_fg_pct, f.projected_ft_pct,
                        f.{punt_field} as punt_fit
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE f.{punt_field} = true
                    ORDER BY f.adp_rank
                    LIMIT 15
                """))
            elif punt_cat == "Rebounds":
                # For punt REB, find guards and wings with low rebounds but high other stats
                result = db.execute(text("""
                    SELECT 
                        p.name, p.position, p.team,
                        f.adp_rank, f.adp_round,
                        f.projected_ppg, f.projected_rpg, f.projected_apg,
                        f.projected_bpg, f.projected_spg,
                        f.projected_fg_pct, f.projected_ft_pct
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE p.position IN ('PG', 'SG', 'SF')
                    AND f.projected_rpg < 6.0  -- Low rebounds
                    AND f.projected_fantasy_ppg > 30  -- Still valuable
                    ORDER BY f.adp_rank
                    LIMIT 15
                """))
            elif punt_cat == "Points":
                # For punt PTS, find defensive specialists
                result = db.execute(text("""
                    SELECT 
                        p.name, p.position, p.team,
                        f.adp_rank, f.adp_round,
                        f.projected_ppg, f.projected_rpg, f.projected_apg,
                        f.projected_bpg, f.projected_spg,
                        f.projected_fg_pct, f.projected_ft_pct
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE f.projected_ppg < 15.0  -- Low scoring
                    AND (f.projected_bpg > 1.0 OR f.projected_spg > 1.0)  -- Good defense
                    ORDER BY f.adp_rank
                    LIMIT 15
                """))
            elif punt_cat == "Steals":
                # For punt STL, find bigs with low steals
                result = db.execute(text("""
                    SELECT 
                        p.name, p.position, p.team,
                        f.adp_rank, f.adp_round,
                        f.projected_ppg, f.projected_rpg, f.projected_apg,
                        f.projected_bpg, f.projected_spg,
                        f.projected_fg_pct, f.projected_ft_pct
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE p.position IN ('PF', 'C')
                    AND f.projected_spg < 1.0  -- Low steals
                    AND f.projected_fantasy_ppg > 30  -- Still valuable
                    ORDER BY f.adp_rank
                    LIMIT 15
                """))
            elif punt_cat == "Blocks":
                # For punt BLK, find guards and wings
                result = db.execute(text("""
                    SELECT 
                        p.name, p.position, p.team,
                        f.adp_rank, f.adp_round,
                        f.projected_ppg, f.projected_rpg, f.projected_apg,
                        f.projected_bpg, f.projected_spg,
                        f.projected_fg_pct, f.projected_ft_pct
                    FROM players p
                    JOIN fantasy_data f ON p.id = f.player_id
                    WHERE p.position IN ('PG', 'SG', 'SF')
                    AND f.projected_bpg < 0.5  -- Low blocks
                    AND f.projected_fantasy_ppg > 30  -- Still valuable
                    ORDER BY f.adp_rank
                    LIMIT 15
                """))
            else:
                return f"Error: Unrecognized punt category {punt_cat}"
            
            players = result.fetchall()
            
            # Build response with player-specific mention if applicable
            if player_mentioned:
                response = f"[TARGET] **Punt {punt_cat} Team Build Around {player_mentioned}**:\n\n"
            else:
                response = f"[TARGET] **Punt {punt_cat} Strategy Build**:\n\n"
            
            response += f"**Core Targets** (Players who excel despite weak {punt_cat}):\n\n"
            
            # Group by rounds
            early = [p for p in players if p.adp_round <= 3]
            mid = [p for p in players if 3 < p.adp_round <= 7]
            late = [p for p in players if p.adp_round > 7]
            
            if early:
                response += "**Early Rounds (1-3)**:\n"
                for p in early:
                    name = clean_unicode(p.name)
                    response += f"- {name} ({p.position}) - Round {p.adp_round}\n"
                    response += f"  Stats: {p.projected_ppg:.1f} PPG, {p.projected_rpg:.1f} RPG, {p.projected_apg:.1f} APG\n"
            
            if mid:
                response += "\n**Mid Rounds (4-7)**:\n"
                for p in mid:
                    name = clean_unicode(p.name)
                    response += f"- {name} ({p.position}) - Round {p.adp_round}\n"
            
            if late:
                response += "\n**Late Round Values (8+)**:\n"
                for p in late:
                    name = clean_unicode(p.name)
                    response += f"- {name} ({p.position}) - Round {p.adp_round}\n"
            
            response += f"\n[TIP] **Strategy Tips**:\n"
            if punt_cat == "FT%":
                if player_mentioned == "Giannis Antetokounmpo":
                    response += "- With Giannis as your cornerstone, you're already punting FT%\n"
                    response += "- Target other elite bigs: Gobert, Claxton, Capela\n"
                    response += "- Focus on maximizing FG%, REB, BLK to pair with Giannis' elite scoring\n"
                else:
                    response += "- Target elite big men like Giannis, Gobert\n"
                    response += "- Focus on FG%, REB, BLK, STL\n"
                    response += "- Avoid guards who only provide FT% and 3PM\n"
                response += "\n**Synergistic Categories**: You'll dominate FG%, REB, BLK\n"
                response += "**Complementary Picks**: Look for Centers and PFs with 55%+ FG\n"
                response += "**Round-by-Round**: R1-2: Elite bigs, R3-5: Rebounding wings, R6+: FG% specialists\n"
                response += "**Position Scarcity**: Lock up Centers early (limited pool of elite ones)\n"
            elif punt_cat == "Assists":
                response += "- Target scoring bigs and wings\n"
                response += "- Focus on PTS, REB, stocks (STL+BLK)\n"
                response += "- Avoid traditional point guards\n"
                response += "\n**Synergistic Categories**: Strong in PTS, REB, and defensive stats\n"
                response += "**Complementary Picks**: Scoring forwards and combo guards\n"
                response += "**Round-by-Round**: R1-3: Elite scorers, R4-6: 3&D wings, R7+: Defensive bigs\n"
                response += "**Position Scarcity**: Wings become crucial (need scoring without assists)\n"
            elif punt_cat == "Rebounds":
                response += "- Target elite guards and perimeter players\n"
                response += "- Focus on AST, STL, 3PM, FT%\n"
                response += "- Avoid traditional big men and rebounding specialists\n"
                response += "- Look for guards with high usage rates\n"
                response += "\n**Synergistic Categories**: Excel in AST, STL, 3PM, FT%\n"
                response += "**Complementary Picks**: High-usage guards and stretch forwards\n"
                response += "**Round-by-Round**: R1-2: Elite guards, R3-5: 3PT specialists, R6+: Assist/steals guys\n"
                response += "**Position Scarcity**: PG/SG heavy - grab them early and often\n"
            elif punt_cat == "Points":
                response += "- Target defensive specialists and facilitators\n"
                response += "- Focus on REB, AST, STL, BLK, FG%\n"
                response += "- Look for players like Draymond Green, Marcus Smart\n"
                response += "\n**Synergistic Categories**: Dominate defensive stats and percentages\n"
                response += "**Complementary Picks**: Glue guys and defensive anchors\n"
                response += "**Round-by-Round**: R1-3: Elite defenders, R4-7: Facilitators, R8+: Specialists\n"
                response += "**Position Scarcity**: Very unique build - few players fit perfectly\n"
            elif punt_cat == "Steals":
                response += "- Target traditional big men\n"
                response += "- Focus on REB, BLK, FG%, points in the paint\n"
                response += "- Avoid guard-heavy builds\n"
                response += "\n**Synergistic Categories**: Elite in REB, BLK, FG%\n"
                response += "**Complementary Picks**: Traditional centers and rebounding PFs\n"
                response += "**Round-by-Round**: R1-3: Elite bigs, R4-6: Rebounding specialists, R7+: Block specialists\n"
                response += "**Position Scarcity**: Center-heavy build - secure them early\n"
            elif punt_cat == "Blocks":
                response += "- Target guards and wings\n"
                response += "- Focus on AST, STL, 3PM, FT%\n"
                response += "- Avoid traditional centers\n"
                response += "\n**Synergistic Categories**: Strong in perimeter stats and percentages\n"
                response += "**Complementary Picks**: Ball-handling wings and combo guards\n"
                response += "**Round-by-Round**: R1-3: Elite guards/wings, R4-7: 3&D players, R8+: Assist specialists\n"
                response += "**Position Scarcity**: Guard/Wing focused - balanced availability\n"
            
            return response
            
        except Exception as e:
            return f"Error building punt strategy: {str(e)}"
    
    def _find_punt_fits(self, query: str) -> str:
        """Find players that fit a specific punt build"""
        try:
            db = next(get_db())
            
            # Check what punt strategy they're asking about
            conditions = []
            strategy_name = ""
            
            if "giannis" in query.lower():
                conditions.append("f.punt_ft_fit = true")
                strategy_name = "Giannis build (Punt FT%)"
            elif "ft" in query.lower():
                conditions.append("f.punt_ft_fit = true")
                strategy_name = "Punt FT%"
            elif "fg" in query.lower():
                conditions.append("f.punt_fg_fit = true")
                strategy_name = "Punt FG%"
            elif "ast" in query.lower():
                conditions.append("f.punt_ast_fit = true")
                strategy_name = "Punt Assists"
            elif "3" in query.lower():
                conditions.append("f.punt_3pm_fit = true")
                strategy_name = "Punt 3PM"
            else:
                # Show all punt fits
                conditions.append("(f.punt_ft_fit = true OR f.punt_fg_fit = true OR f.punt_ast_fit = true OR f.punt_3pm_fit = true)")
                strategy_name = "Various Punt Strategies"
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            result = db.execute(text(f"""
                SELECT 
                    p.name, p.position, p.team,
                    f.adp_rank, f.adp_round,
                    f.punt_ft_fit, f.punt_fg_fit, f.punt_ast_fit, f.punt_3pm_fit,
                    f.projected_fantasy_ppg
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE {where_clause}
                ORDER BY f.projected_fantasy_ppg DESC
                LIMIT 10
            """))
            
            players = result.fetchall()
            
            response = f"[NBA] **Best Players for {strategy_name}**:\n\n"
            for p in players:
                punts = []
                if p.punt_ft_fit: punts.append("FT%")
                if p.punt_fg_fit: punts.append("FG%")
                if p.punt_ast_fit: punts.append("AST")
                if p.punt_3pm_fit: punts.append("3PM")
                
                name = clean_unicode(p.name)
                response += f"**{name}** ({p.position}, {p.team})\n"
                response += f"- ADP: #{p.adp_rank} (Round {p.adp_round})\n"
                response += f"- Fantasy PPG: {p.projected_fantasy_ppg:.1f}\n"
                response += f"- Fits: Punt {', '.join(punts)}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error finding punt fits: {str(e)}"
    
    # MOCK DRAFT TOOLS
    
    def _simulate_draft_pick(self, pick_info: str) -> str:
        """Simulate best available players at a draft position"""
        try:
            # Extract round/pick number
            import re
            
            # Check for round range (e.g., "rounds 8-10")
            range_match = re.search(r'rounds?\s*(\d+)\s*[-–]\s*(\d+)', pick_info.lower())
            if range_match:
                start_round = int(range_match.group(1))
                end_round = int(range_match.group(2))
                pick_start = (start_round - 1) * 12 + 1
                pick_end = end_round * 12
                specific_pick = None
            else:
                pick_match = re.search(r'pick\s*(\d+)|round\s*(\d+)', pick_info.lower())
                
                if pick_match:
                    # Check if it explicitly says "round" vs "pick"
                    is_round = 'round' in pick_info.lower() and 'pick' not in pick_info.lower()
                    pick_num = int(pick_match.group(1) or pick_match.group(2))
                    
                    if is_round:
                        # User specified a round number
                        pick_start = (pick_num - 1) * 12 + 1
                        pick_end = pick_num * 12
                        specific_pick = None
                    else:
                        # User specified a specific pick number
                        specific_pick = pick_num
                        # Show players available around that pick
                        pick_start = max(1, pick_num - 2)
                        pick_end = min(150, pick_num + 10)
                else:
                    # Default to first round
                    pick_start = 1
                    pick_end = 15
                    specific_pick = None
            
            db = next(get_db())
            
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.adp_rank, f.adp_round,
                    f.projected_fantasy_ppg,
                    f.consistency_rating,
                    f.projected_ppg, f.projected_rpg, f.projected_apg
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE f.adp_rank BETWEEN :start AND :end
                ORDER BY f.adp_rank
                LIMIT 15
            """), {"start": pick_start, "end": pick_end})
            
            players = result.fetchall()
            
            # Format response based on whether it's a specific pick or range
            if specific_pick:
                response = f"[DICE] **Mock Draft Recommendation for Pick #{specific_pick}**:\n\n"
                
                # Find the best player available around that pick
                best_available = [p for p in players if p.adp_rank >= specific_pick]
                if best_available:
                    top_pick = best_available[0]
                    name = clean_unicode(top_pick.name)
                    response += f"**RECOMMENDED PICK: {name}** ({top_pick.position}, {top_pick.team})\n"
                    response += f"- ADP: #{top_pick.adp_rank} (Round {top_pick.adp_round})\n"
                    response += f"- Projected: {top_pick.projected_fantasy_ppg:.1f} fantasy points/game\n"
                    response += f"- Stats: {top_pick.projected_ppg:.1f} PPG, {top_pick.projected_rpg:.1f} RPG, {top_pick.projected_apg:.1f} APG\n"
                    response += f"- Consistency Rating: {top_pick.consistency_rating:.2f}/1.0\n\n"
                    
                    response += "**Other Available Options**:\n"
                    for p in best_available[1:6]:
                        name = clean_unicode(p.name)
                        response += f"- Pick #{p.adp_rank}: {name} ({p.position}) - {p.projected_fantasy_ppg:.1f} FP/game\n"
                else:
                    # All players already taken, show who was available
                    response += "All typical picks for this position have been selected.\n\n"
                    response += "**Players Who Were Available Before This Pick**:\n"
                    for p in players[:5]:
                        name = clean_unicode(p.name)
                        response += f"- Pick #{p.adp_rank}: {name} ({p.position})\n"
            else:
                response = f"[DICE] **Mock Draft - Best Available (Picks {pick_start}-{pick_end})**:\n\n"
                
                for p in players[:8]:
                    name = clean_unicode(p.name)
                    response += f"**Pick {p.adp_rank}: {name}** ({p.position}, {p.team})\n"
                    response += f"- Projected: {p.projected_fantasy_ppg:.1f} FP/game\n"
                    response += f"- Consistency: {p.consistency_rating:.2f}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error simulating draft: {str(e)}"