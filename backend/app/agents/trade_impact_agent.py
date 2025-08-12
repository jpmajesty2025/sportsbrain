"""
TradeImpact Agent - Analyzes how trades affect fantasy values
"""
from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent, AgentResponse
from langchain.tools import Tool
from pymilvus import Collection
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import json
import os
import logging

from app.db.vector_db import vector_db
from app.db.graph_db import graph_db
from app.core.config import settings

logger = logging.getLogger(__name__)


class TradeImpactAgent(BaseAgent):
    """Agent specialized in analyzing trade impacts on fantasy basketball"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        self.trade_data = self._load_trade_data()
        
        # Define tools
        tools = [
            Tool(
                name="analyze_trade_impact",
                func=self._analyze_trade_impact,
                description="Analyze how a trade affects specific players"
            ),
            Tool(
                name="find_trade_winners",
                func=self._find_trade_winners,
                description="Find players who benefit from recent trades"
            ),
            Tool(
                name="analyze_team_dynamics",
                func=self._analyze_team_dynamics,
                description="Analyze how trades affect team dynamics"
            )
        ]
        
        super().__init__(
            name="TradeImpact",
            description="Expert in analyzing how trades affect player fantasy values and team dynamics",
            tools=tools
        )
    
    def _initialize_agent(self):
        """Initialize agent - required by base class"""
        pass
    
    def _load_trade_data(self) -> Dict[str, Any]:
        """Load trade data from JSON file"""
        try:
            trade_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'trades_2024.json'
            )
            with open(trade_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading trade data: {e}")
            return {"trades": []}
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a trade-related query"""
        try:
            message_lower = message.lower()
            
            # Check for specific player trade impacts
            if ("porzingis" in message_lower and "tatum" in message_lower) or \
               ("lillard" in message_lower and "giannis" in message_lower) or \
               ("affect" in message_lower and any(word in message_lower for word in ["trade", "traded"])) or \
               ("impact" in message_lower and any(name in message_lower for name in ["giannis", "tatum", "lillard"])):
                # Extract player names
                player_name = None
                if "tatum" in message_lower:
                    player_name = "Jayson Tatum"
                elif "brown" in message_lower:
                    player_name = "Jaylen Brown"
                elif "giannis" in message_lower:
                    player_name = "Giannis Antetokounmpo"
                elif "lillard" in message_lower and "giannis" not in message_lower:
                    player_name = "Damian Lillard"
                elif "ja" in message_lower or "morant" in message_lower:
                    player_name = "Ja Morant"
                
                # Find relevant trade
                trade_id = None
                if "porzingis" in message_lower:
                    trade_id = "porzingis_celtics_2023"
                elif "lillard" in message_lower:
                    trade_id = "lillard_bucks_2023"
                elif "smart" in message_lower:
                    trade_id = "smart_grizzlies_2023"
                
                if player_name and trade_id:
                    result = self._analyze_trade_impact(player_name, trade_id)
                    return AgentResponse(
                        content=result,
                        metadata={"tool": "analyze_trade_impact", "player": player_name, "trade": trade_id},
                        tools_used=["analyze_trade_impact"],
                        confidence=0.9
                    )
            
            # Check for trade winners/beneficiaries
            elif "winner" in message_lower or "benefit" in message_lower or "gain" in message_lower:
                result = self._find_trade_winners()
                return AgentResponse(
                    content=result,
                    metadata={"tool": "find_trade_winners"},
                    tools_used=["find_trade_winners"],
                    confidence=0.8
                )
            
            # Check for team dynamics
            elif "team" in message_lower and ("dynamic" in message_lower or "chemistry" in message_lower):
                result = self._analyze_team_dynamics()
                return AgentResponse(
                    content=result,
                    metadata={"tool": "analyze_team_dynamics"},
                    tools_used=["analyze_team_dynamics"],
                    confidence=0.8
                )
            
            else:
                # General trade advice
                return AgentResponse(
                    content="I can analyze how trades affect player fantasy values, find trade winners, and assess team dynamics. What would you like to know about recent trades?",
                    confidence=0.6
                )
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return AgentResponse(
                content=f"Error processing trade query: {str(e)}",
                confidence=0.0
            )
    
    def _analyze_trade_impact(self, player_name: str, trade_id: str = None) -> str:
        """Analyze how a trade affects a specific player"""
        try:
            # Find the trade
            trade = None
            if trade_id:
                for t in self.trade_data.get('trades', []):
                    if t['trade_id'] == trade_id:
                        trade = t
                        break
            else:
                # Find most relevant trade for this player
                for t in self.trade_data.get('trades', []):
                    if player_name in t.get('impact_analysis', {}):
                        trade = t
                        break
            
            if not trade:
                return f"No trade impact data found for {player_name}"
            
            # Get player impact data
            impact = trade['impact_analysis'].get(player_name, {})
            if not impact:
                return f"No impact data available for {player_name} in this trade"
            
            # Get player's current stats from Milvus
            vector_db.connect()
            collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
            
            expr = f'player_name == "{player_name}"'
            results = collection.query(
                expr=expr,
                output_fields=["player_name", "position", "metadata"],
                limit=1
            )
            
            player_data = results[0] if results else None
            vector_db.disconnect()
            
            # Build analysis
            analysis = f"""**Trade Impact Analysis: {player_name}**

📅 **Trade**: {trade['description']}
📆 **Date**: {trade['date']}

[STATS] **Statistical Impact**:
- Usage Rate: {impact['usage_rate_change']:+.1f}% 
- Scoring: {impact['scoring_change']:+.1f} PPG
- Assists: {impact['assists_change']:+.1f} APG
- Rebounds: {impact['rebounds_change']:+.1f} RPG
- Efficiency: {impact['efficiency_change']:+.1f}%

[TARGET] **Fantasy Impact**: {impact['fantasy_impact'].replace('_', ' ').title()}

[TIP] **Analysis**:
"""
            
            # Add contextual analysis
            if impact['usage_rate_change'] < -2:
                analysis += f"- {player_name}'s usage rate drops significantly with the new addition, limiting volume-based stats\n"
            elif impact['usage_rate_change'] > 2:
                analysis += f"- {player_name} sees increased usage, boosting counting stats potential\n"
            
            if impact['efficiency_change'] > 1.5:
                analysis += f"- Better shot quality leads to improved efficiency, helping FG% and TS%\n"
            elif impact['efficiency_change'] < -1.5:
                analysis += f"- Efficiency may suffer as {player_name} takes on different role\n"
            
            if impact['fantasy_impact'] == 'moderate_negative' or impact['fantasy_impact'] == 'slight_negative':
                analysis += f"- Consider lowering {player_name} in your rankings by 5-10 spots\n"
                analysis += f"- In daily fantasy, fade when facing teams with strong interior defense\n"
            elif impact['fantasy_impact'] == 'positive':
                analysis += f"- {player_name} becomes a better fantasy target post-trade\n"
                analysis += f"- Consider reaching slightly in drafts to secure the improved situation\n"
            
            # Add team context
            team_impact = trade.get('team_impact', {})
            if team_impact.get('floor_spacing') == 'improved' or team_impact.get('floor_spacing') == 'significantly_improved':
                analysis += f"- Improved floor spacing should create better driving lanes and open shots\n"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_trade_impact: {e}")
            return f"Error analyzing trade impact: {str(e)}"
    
    def _find_trade_winners(self) -> str:
        """Find players who benefit most from recent trades"""
        try:
            winners = []
            
            # Analyze all trades for positive impacts
            for trade in self.trade_data.get('trades', []):
                for player_name, impact in trade.get('impact_analysis', {}).items():
                    if impact.get('fantasy_impact') in ['positive', 'slight_positive']:
                        winners.append({
                            'player': player_name,
                            'trade': trade['description'],
                            'date': trade['date'],
                            'usage_change': impact.get('usage_rate_change', 0),
                            'scoring_change': impact.get('scoring_change', 0),
                            'efficiency_change': impact.get('efficiency_change', 0),
                            'impact': impact.get('fantasy_impact')
                        })
            
            # Sort by overall benefit
            winners.sort(key=lambda x: x['usage_change'] + x['efficiency_change'], reverse=True)
            
            response = "**[WINNER] Trade Winners - Players Who Benefit Most**\n\n"
            
            for i, winner in enumerate(winners[:5]):
                response += f"**{i+1}. {winner['player']}**\n"
                response += f"   📅 Trade: {winner['trade']}\n"
                response += f"   [UP] Changes: Usage {winner['usage_change']:+.1f}%, "
                response += f"Scoring {winner['scoring_change']:+.1f} PPG, "
                response += f"Efficiency {winner['efficiency_change']:+.1f}%\n"
                response += f"   [TARGET] Fantasy Impact: {winner['impact'].replace('_', ' ').title()}\n\n"
            
            response += "\n[TIP] **Key Takeaway**: Target these players in trades or DFS when they face favorable matchups!"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in find_trade_winners: {e}")
            return f"Error finding trade winners: {str(e)}"
    
    def _analyze_team_dynamics(self) -> str:
        """Analyze how trades affect team dynamics"""
        try:
            response = "**[NBA] Team Dynamics Post-Trade Analysis**\n\n"
            
            for trade in self.trade_data.get('trades', [])[:3]:  # Top 3 recent trades
                team_impact = trade.get('team_impact', {})
                
                response += f"**{trade['description']}**\n"
                response += f"📅 Date: {trade['date']}\n\n"
                
                response += "Team Changes:\n"
                if team_impact.get('floor_spacing'):
                    response += f"- Floor Spacing: {team_impact['floor_spacing'].replace('_', ' ').title()}\n"
                if team_impact.get('defensive_rating'):
                    response += f"- Defense: {team_impact['defensive_rating'].replace('_', ' ').title()}\n"
                if team_impact.get('offensive_rating'):
                    response += f"- Offense: {team_impact['offensive_rating'].replace('_', ' ').title()}\n"
                if team_impact.get('title_odds'):
                    response += f"- Championship Outlook: {team_impact['title_odds'].replace('_', ' ').title()}\n"
                
                response += "\nFantasy Implications:\n"
                
                # Add specific implications based on changes
                if team_impact.get('floor_spacing') in ['improved', 'significantly_improved']:
                    response += "- Guards and wings benefit from better driving lanes\n"
                    response += "- Centers may see fewer post touches but better efficiency\n"
                
                if team_impact.get('defensive_rating') == 'worse':
                    response += "- Expect higher-scoring games (good for DFS)\n"
                    response += "- Opposing players may have better fantasy nights\n"
                
                response += "\n" + "="*50 + "\n\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in analyze_team_dynamics: {e}")
            return f"Error analyzing team dynamics: {str(e)}"
    
    def _get_supported_tasks(self) -> List[str]:
        """Return list of supported tasks"""
        return [
            "Trade impact analysis for specific players",
            "Finding trade winners and losers",
            "Team dynamics and chemistry changes",
            "Usage rate and role changes",
            "Dynasty league trade values",
            "Post-trade fantasy rankings adjustments"
        ]