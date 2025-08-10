"""
DraftPrep Agent - Async version for keeper decisions and draft preparation
"""
from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent, AgentResponse
from langchain.tools import Tool
from pymilvus import Collection
from sentence_transformers import SentenceTransformer

from app.db.vector_db import vector_db
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class DraftPrepAgent(BaseAgent):
    """Agent specialized in draft preparation and keeper decisions"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        # Define tools
        tools = [
            Tool(
                name="analyze_keeper_value",
                func=self._analyze_keeper_value,
                description="Analyze if a player should be kept in a specific round"
            ),
            Tool(
                name="find_value_picks",
                func=self._find_value_picks,
                description="Find players with good value relative to their ADP"
            ),
            Tool(
                name="compare_players",
                func=self._compare_players,
                description="Compare two players for draft/keeper decisions"
            )
        ]
        
        super().__init__(
            name="DraftPrep",
            description="Expert in keeper league decisions, ADP analysis, and draft strategy",
            tools=tools
        )
    
    def _initialize_agent(self):
        """Initialize agent - required by base class but we'll handle queries directly"""
        pass
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a draft-related query"""
        try:
            message_lower = message.lower()
            
            # Route to appropriate tool based on message content
            if "keep" in message_lower and ("round" in message_lower or "keeper" in message_lower):
                # Extract player name - look for quoted names or known players
                player_name = None
                round_num = None
                
                # Check for specific players
                if "ja morant" in message_lower:
                    player_name = "Ja Morant"
                elif "jayson tatum" in message_lower:
                    player_name = "Jayson Tatum"
                elif "giannis" in message_lower:
                    player_name = "Giannis Antetokounmpo"
                elif "lebron" in message_lower:
                    player_name = "LeBron James"
                elif "luka" in message_lower:
                    player_name = "Luka Dončić"
                
                # Extract round number - look for "round X" or just a number
                import re
                round_match = re.search(r'round\s*(\d+)|in\s*(\d+)', message_lower)
                if round_match:
                    round_num = int(round_match.group(1) or round_match.group(2))
                else:
                    # Look for standalone number
                    for word in message.split():
                        if word.replace('?', '').replace('.', '').isdigit():
                            round_num = int(word.replace('?', '').replace('.', ''))
                            break
                
                if player_name and round_num:
                    result = self._analyze_keeper_value(player_name, round_num)
                    return AgentResponse(
                        content=result,
                        metadata={"tool": "analyze_keeper_value", "player": player_name, "round": round_num},
                        tools_used=["analyze_keeper_value"],
                        confidence=0.9
                    )
                else:
                    return AgentResponse(
                        content="Please specify both the player name and the round number for keeper analysis.",
                        confidence=0.5
                    )
            
            elif "value" in message_lower or "sleeper" in message_lower:
                # Find value picks
                result = self._find_value_picks()
                return AgentResponse(
                    content=result,
                    metadata={"tool": "find_value_picks"},
                    tools_used=["find_value_picks"],
                    confidence=0.8
                )
            
            elif "compare" in message_lower or " vs " in message_lower or " or " in message_lower:
                # Compare players
                return AgentResponse(
                    content="Please specify two players to compare. For example: 'Compare Tatum vs Brown'",
                    confidence=0.5
                )
            
            else:
                # General draft advice
                return AgentResponse(
                    content="I can help with keeper decisions, finding value picks, and comparing players. What would you like to know?",
                    confidence=0.6
                )
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return AgentResponse(
                content=f"Error processing draft query: {str(e)}",
                confidence=0.0
            )
    
    def _analyze_keeper_value(self, player_name: str, target_round: int) -> str:
        """Analyze if a player should be kept in a specific round"""
        try:
            # Connect to Milvus
            vector_db.connect()
            collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
            
            # Find player
            expr = f'player_name == "{player_name}"'
            results = collection.query(
                expr=expr,
                output_fields=["player_name", "metadata"],
                limit=1
            )
            
            if not results:
                vector_db.disconnect()
                return f"Player {player_name} not found in database"
            
            player_data = results[0]
            metadata = player_data.get('metadata', {})
            fantasy = metadata.get('fantasy', {})
            stats = metadata.get('stats', {})
            
            adp = fantasy.get('adp', 999)
            keeper_round = fantasy.get('keeper_round_value', 15)
            
            # Analyze keeper decision
            if keeper_round <= target_round:
                value_diff = target_round - keeper_round
                if value_diff >= 2:
                    recommendation = "STRONG YES - Excellent keeper value! 🔥"
                elif value_diff >= 1:
                    recommendation = "YES - Good keeper value"
                else:
                    recommendation = "MAYBE - Slight value, consider other options"
            else:
                recommendation = "NO - Better options likely available"
            
            analysis = f"""
**Keeper Analysis for {player_name}**

📊 **Current Stats**:
- ADP: {adp} (Round {int(adp/12) + 1})
- Keeper Round Value: {keeper_round}
- Your Target Round: {target_round}
- 2023-24 Stats: {stats.get('ppg', 0)} PPG, {stats.get('rpg', 0)} RPG, {stats.get('apg', 0)} APG

🎯 **Recommendation**: {recommendation}

💡 **Analysis**: 
"""
            if keeper_round <= target_round:
                analysis += f"Keeping {player_name} in round {target_round} gives you a player typically drafted in round {int(adp/12) + 1}. "
                analysis += f"That's a {int(adp/12) + 1 - target_round} round advantage!"
            else:
                analysis += f"{player_name}'s ADP suggests they should be available later than round {target_round}. "
                analysis += "Consider targeting them in the draft instead of using a keeper spot."
            
            vector_db.disconnect()
            return analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_keeper_value: {e}")
            return f"Error analyzing keeper value: {str(e)}"
    
    def _find_value_picks(self) -> str:
        """Find players with good value relative to ADP"""
        try:
            # Connect to Milvus
            vector_db.connect()
            collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
            
            # Query players with good fantasy scores relative to ADP
            expr = "metadata['fantasy']['adp'] > 50 and metadata['fantasy']['adp'] < 150"
            results = collection.query(
                expr=expr,
                output_fields=["player_name", "position", "metadata"],
                limit=50
            )
            
            # Calculate value scores
            value_picks = []
            for player in results:
                metadata = player.get('metadata', {})
                fantasy = metadata.get('fantasy', {})
                stats = metadata.get('stats', {})
                
                # Skip if no stats
                if not stats or stats.get('games_played', 0) < 20:
                    continue
                
                adp = fantasy.get('adp', 999)
                
                # Calculate fantasy points per game
                fantasy_ppg = (stats.get('ppg', 0) * 1.0 + 
                             stats.get('rpg', 0) * 1.2 + 
                             stats.get('apg', 0) * 1.5 + 
                             stats.get('spg', 0) * 3.0 + 
                             stats.get('bpg', 0) * 3.0)
                
                # Value score = fantasy production / ADP (higher is better)
                value_score = fantasy_ppg / (adp / 10) if adp > 0 else 0
                
                value_picks.append({
                    'name': player['player_name'],
                    'position': player['position'],
                    'adp': adp,
                    'round': int(adp/12) + 1,
                    'fantasy_ppg': fantasy_ppg,
                    'value_score': value_score,
                    'stats': stats
                })
            
            # Sort by value score
            value_picks.sort(key=lambda x: x['value_score'], reverse=True)
            
            response = "**🎯 Top Value Picks (Sleepers & Undervalued Players)**\n\n"
            
            for i, pick in enumerate(value_picks[:10]):
                response += f"**{i+1}. {pick['name']}** ({pick['position']})\n"
                response += f"   📊 ADP: {pick['adp']:.1f} (Round {pick['round']})\n"
                response += f"   📈 Stats: {pick['stats'].get('ppg', 0)} PPG, "
                response += f"{pick['stats'].get('rpg', 0)} RPG, {pick['stats'].get('apg', 0)} APG\n"
                response += f"   💎 Value Score: {pick['value_score']:.2f}\n\n"
            
            response += "\n💡 **Value Score** = Fantasy production relative to draft position. Higher scores indicate better value!"
            
            vector_db.disconnect()
            return response
            
        except Exception as e:
            logger.error(f"Error in find_value_picks: {e}")
            return f"Error finding value picks: {str(e)}"
    
    def _compare_players(self, player1: str, player2: str) -> str:
        """Compare two players for draft decisions"""
        # Simplified for now
        return f"Comparing {player1} vs {player2} - Feature coming soon!"
    
    def _get_supported_tasks(self) -> List[str]:
        """Return list of supported tasks"""
        return [
            "Keeper league decisions",
            "ADP analysis",
            "Finding value picks/sleepers",
            "Player comparisons for draft",
            "Round-by-round draft strategy"
        ]