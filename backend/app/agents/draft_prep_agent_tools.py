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
                description="Calculate if a player should be kept in a specific round",
                func=self._calculate_keeper_value
            ),
            
            # ADP Analysis Tools
            Tool(
                name="analyze_adp_value",
                description="Find players with good value relative to their ADP",
                func=self._analyze_adp_value
            ),
            Tool(
                name="get_adp_rankings",
                description="Get current ADP rankings for players",
                func=self._get_adp_rankings
            ),
            
            # Punt Strategy Tools
            Tool(
                name="build_punt_strategy",
                description="Build a punt strategy team around a specific category",
                func=self._build_punt_strategy
            ),
            Tool(
                name="find_punt_fits",
                description="Find players that fit a specific punt build",
                func=self._find_punt_fits
            ),
            
            # Mock Draft Tools
            Tool(
                name="simulate_draft_pick",
                description="Simulate best available players at a draft position",
                func=self._simulate_draft_pick
            )
        ]
        
        super().__init__(
            name="DraftPrep Agent",
            description="Expert in keeper leagues, ADP analysis, punt strategies, and mock drafts",
            tools=tools
        )
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools"""
        if settings.OPENAI_API_KEY:
            from langchain.prompts import PromptTemplate
            
            # Custom prompt to ensure agent returns tool output
            prefix = """You are a fantasy basketball draft expert. Answer the following questions as best you can using the available tools.

When you use a tool and get results, your Final Answer should BE those results, not a description of what tool you used.
For example, if someone asks for a punt strategy and you use build_punt_strategy, return the actual player recommendations and tips, not "I used the build_punt_strategy function".

You have access to the following tools:"""
            
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.1)
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,
                agent_kwargs={
                    "prefix": prefix
                }
            )
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a draft-related query"""
        
        # DIRECT TOOL ROUTING - bypass agent for common queries
        message_lower = message.lower()
        
        # Keeper queries
        if "keep" in message_lower or "keeper" in message_lower:
            try:
                tool_result = self._calculate_keeper_value(message)
                return AgentResponse(
                    content=tool_result,
                    metadata={
                        "context": context,
                        "agent_type": "draft_prep",
                        "method": "direct_tool_call"
                    },
                    tools_used=["calculate_keeper_value"],
                    confidence=0.95
                )
            except Exception as e:
                pass  # Fall through to agent
        
        # Punt strategy queries
        elif "punt" in message_lower:
            try:
                tool_result = self._build_punt_strategy(message)
                return AgentResponse(
                    content=tool_result,
                    metadata={
                        "context": context,
                        "agent_type": "draft_prep",
                        "method": "direct_tool_call"
                    },
                    tools_used=["build_punt_strategy"],
                    confidence=0.95
                )
            except Exception as e:
                pass  # Fall through to agent
        
        # ADP/value queries  
        elif "adp" in message_lower or "value" in message_lower:
            try:
                tool_result = self._analyze_adp_value(message)
                return AgentResponse(
                    content=tool_result,
                    metadata={
                        "context": context,
                        "agent_type": "draft_prep",
                        "method": "direct_tool_call"
                    },
                    tools_used=["analyze_adp_value"],
                    confidence=0.95
                )
            except Exception as e:
                pass  # Fall through to agent
        
        # Mock draft queries
        elif "mock" in message_lower or "draft" in message_lower or "pick" in message_lower:
            try:
                tool_result = self._simulate_draft_pick(message)
                return AgentResponse(
                    content=tool_result,
                    metadata={
                        "context": context,
                        "agent_type": "draft_prep",
                        "method": "direct_tool_call"
                    },
                    tools_used=["simulate_draft_pick"],
                    confidence=0.95
                )
            except Exception as e:
                pass  # Fall through to agent
        
        # FALLBACK TO AGENT for complex or unclear queries
        if not self.agent_executor:
            return AgentResponse(
                content="DraftPrep agent not properly initialized. Please check OpenAI API key.",
                confidence=0.0
            )
        
        try:
            # Use agent for complex queries that don't match patterns
            enhanced_message = f"""[Context: Fantasy basketball draft preparation for 2024-25 season]
{message}

Pass the COMPLETE user query to the tool, including all details like round numbers, player names, and categories."""
            
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
            # Try to provide a helpful response even if we timeout
            return AgentResponse(
                content="The request took too long to process. For punt strategies, try asking more specific questions like 'Which guards fit a punt FT% build?' or 'What are good targets for punt rebounds strategy?'",
                confidence=0.5,
                metadata={"error": "timeout", "agent_type": "draft_prep"}
            )
        except Exception as e:
            error_msg = str(e)
            if "iteration limit" in error_msg.lower() or "time limit" in error_msg.lower():
                # Agent hit iteration limit - provide helpful response
                return AgentResponse(
                    content="I found relevant information but couldn't complete the full analysis. Try asking a more specific question about your punt strategy, keeper decision, or draft targets.",
                    confidence=0.5,
                    metadata={"error": "iteration_limit", "agent_type": "draft_prep"}
                )
            return AgentResponse(
                content=f"Error processing draft query: {error_msg}",
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
                value_diff = player.adp_round - keeper_round
                
                if value_diff >= 3:
                    recommendation = "EXCEPTIONAL VALUE - Must keep!"
                elif value_diff >= 2:
                    recommendation = "GREAT VALUE - Strongly recommend keeping"
                elif value_diff >= 1:
                    recommendation = "GOOD VALUE - Worth keeping"
                elif value_diff == 0:
                    recommendation = "FAIR VALUE - Consider other options"
                else:
                    recommendation = "POOR VALUE - Do not keep"
                
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
- That's a {value_diff} round advantage!
- Projected Fantasy PPG: {player.projected_fantasy_ppg:.1f}
- Consistency: {player.consistency_rating:.2f} | Injury Risk: {player.injury_risk}

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
            
            response = "[TARGET] **Top ADP Value Picks for 2024-25**:\n\n"
            for i, v in enumerate(values[:7], 1):
                response += f"{i}. **{v.name}** ({v.position}, {v.team})\n"
                response += f"   - ADP: #{v.adp_rank} (Round {v.adp_round})\n"
                response += f"   - Projected: {v.projected_fantasy_ppg:.1f} FP/game\n"
                response += f"   - Value Score: {v.value_ratio:.2f}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error analyzing ADP value: {str(e)}"
    
    def _get_adp_rankings(self, position: str = "") -> str:
        """Get current ADP rankings, optionally filtered by position"""
        try:
            db = next(get_db())
            
            # Build query based on position filter
            if position:
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
            response = f"[LIST] **{title} (2024-25 ADP)**:\n\n"
            
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
                response += "- Target elite big men like Giannis, Gobert\n"
                response += "- Focus on FG%, REB, BLK, STL\n"
                response += "- Avoid guards who only provide FT% and 3PM\n"
            elif punt_cat == "Assists":
                response += "- Target scoring bigs and wings\n"
                response += "- Focus on PTS, REB, stocks (STL+BLK)\n"
                response += "- Avoid traditional point guards\n"
            elif punt_cat == "Rebounds":
                response += "- Target elite guards and perimeter players\n"
                response += "- Focus on AST, STL, 3PM, FT%\n"
                response += "- Avoid traditional big men and rebounding specialists\n"
                response += "- Look for guards with high usage rates\n"
            elif punt_cat == "Points":
                response += "- Target defensive specialists and facilitators\n"
                response += "- Focus on REB, AST, STL, BLK, FG%\n"
                response += "- Look for players like Draymond Green, Marcus Smart\n"
            elif punt_cat == "Steals":
                response += "- Target traditional big men\n"
                response += "- Focus on REB, BLK, FG%, points in the paint\n"
                response += "- Avoid guard-heavy builds\n"
            elif punt_cat == "Blocks":
                response += "- Target guards and wings\n"
                response += "- Focus on AST, STL, 3PM, FT%\n"
                response += "- Avoid traditional centers\n"
            
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
            pick_match = re.search(r'pick\s*(\d+)|round\s*(\d+)', pick_info.lower())
            
            if pick_match:
                pick_num = int(pick_match.group(1) or pick_match.group(2))
                if pick_num <= 15:  # Assume it's a round number
                    # Convert to pick number (assuming 12-team league)
                    pick_start = (pick_num - 1) * 12 + 1
                    pick_end = pick_num * 12
                else:
                    # Direct pick number
                    pick_start = max(1, pick_num - 3)
                    pick_end = pick_num + 8
            else:
                # Default to first round
                pick_start = 1
                pick_end = 15
            
            db = next(get_db())
            
            result = db.execute(text("""
                SELECT 
                    p.name, p.position, p.team,
                    f.adp_rank, f.adp_round,
                    f.projected_fantasy_ppg,
                    f.consistency_rating
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE f.adp_rank BETWEEN :start AND :end
                ORDER BY f.adp_rank
                LIMIT 12
            """), {"start": pick_start, "end": pick_end})
            
            players = result.fetchall()
            
            response = f"[DICE] **Mock Draft - Best Available (Picks {pick_start}-{pick_end})**:\n\n"
            
            for p in players[:8]:
                name = clean_unicode(p.name)
                response += f"**Pick {p.adp_rank}: {name}** ({p.position}, {p.team})\n"
                response += f"- Projected: {p.projected_fantasy_ppg:.1f} FP/game\n"
                response += f"- Consistency: {p.consistency_rating:.2f}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error simulating draft: {str(e)}"