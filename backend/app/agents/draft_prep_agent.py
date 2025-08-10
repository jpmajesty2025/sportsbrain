"""
DraftPrep Agent - Handles keeper decisions and draft preparation
"""
from typing import Dict, Any, List
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from pymilvus import Collection
from sentence_transformers import SentenceTransformer

from app.db.vector_db import vector_db
from app.db.graph_db import graph_db
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class DraftPrepAgent:
    """Agent specialized in draft preparation and keeper decisions"""
    
    def __init__(self):
        self.name = "DraftPrep"
        self.description = "Expert in keeper league decisions, ADP analysis, and draft strategy"
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        # Initialize tools
        self.tools = [
            Tool(
                name="analyze_keeper_value",
                func=self.analyze_keeper_value,
                description="Analyze if a player should be kept in a specific round. Input: 'player_name,round'"
            ),
            Tool(
                name="find_value_picks",
                func=self.find_value_picks,
                description="Find players with good value relative to their ADP. Input: 'round_range' (e.g., '5-7')"
            ),
            Tool(
                name="compare_players",
                func=self.compare_players,
                description="Compare two players for draft/keeper decisions. Input: 'player1,player2'"
            ),
            Tool(
                name="get_player_stats",
                func=self.get_player_stats,
                description="Get detailed stats and fantasy info for a player. Input: 'player_name'"
            )
        ]
        
        # Initialize LLM and agent
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
            self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            self.agent = initialize_agent(
                self.tools,
                self.llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                memory=self.memory,
                verbose=True
            )
        else:
            logger.warning("No OpenAI API key found - agent will use direct tool calls only")
            self.agent = None
    
    def analyze_keeper_value(self, input_str: str) -> str:
        """Analyze if a player should be kept in a specific round"""
        try:
            parts = input_str.split(',')
            player_name = parts[0].strip()
            target_round = int(parts[1].strip())
            
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
                    recommendation = "STRONG YES - Excellent value!"
                elif value_diff >= 1:
                    recommendation = "YES - Good value"
                else:
                    recommendation = "MAYBE - Slight value"
            else:
                recommendation = "NO - Better options available"
            
            analysis = f"""
Keeper Analysis for {player_name}:
- Current ADP: {adp} (Round {int(adp/12) + 1})
- Keeper Round Value: {keeper_round}
- Target Round: {target_round}
- Stats: {stats.get('ppg', 0)} PPG, {stats.get('rpg', 0)} RPG, {stats.get('apg', 0)} APG

Recommendation: {recommendation}
"""
            
            vector_db.disconnect()
            return analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_keeper_value: {e}")
            return f"Error analyzing keeper value: {str(e)}"
    
    def find_value_picks(self, round_range: str) -> str:
        """Find players with good value in a specific round range"""
        try:
            # Parse round range
            parts = round_range.split('-')
            start_round = int(parts[0])
            end_round = int(parts[1]) if len(parts) > 1 else start_round
            
            start_adp = (start_round - 1) * 12 + 1
            end_adp = end_round * 12
            
            # Connect to Milvus
            vector_db.connect()
            collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
            
            # Query players in ADP range
            expr = f"metadata['fantasy']['adp'] >= {start_adp} and metadata['fantasy']['adp'] <= {end_adp}"
            results = collection.query(
                expr=expr,
                output_fields=["player_name", "position", "metadata"],
                limit=20
            )
            
            # Sort by value (comparing ADP to projected performance)
            value_picks = []
            for player in results:
                metadata = player.get('metadata', {})
                fantasy = metadata.get('fantasy', {})
                stats = metadata.get('stats', {})
                
                adp = fantasy.get('adp', 999)
                fantasy_score = (stats.get('ppg', 0) * 1.0 + 
                               stats.get('rpg', 0) * 1.2 + 
                               stats.get('apg', 0) * 1.5 + 
                               stats.get('spg', 0) * 3.0 + 
                               stats.get('bpg', 0) * 3.0)
                
                value_picks.append({
                    'name': player['player_name'],
                    'position': player['position'],
                    'adp': adp,
                    'round': int(adp/12) + 1,
                    'fantasy_score': fantasy_score,
                    'stats': stats
                })
            
            # Sort by fantasy score (higher is better)
            value_picks.sort(key=lambda x: x['fantasy_score'], reverse=True)
            
            response = f"Value Picks for Rounds {start_round}-{end_round}:\n\n"
            for i, pick in enumerate(value_picks[:10]):
                response += f"{i+1}. {pick['name']} ({pick['position']}) - ADP {pick['adp']:.1f}\n"
                response += f"   Stats: {pick['stats'].get('ppg', 0)} PPG, "
                response += f"{pick['stats'].get('rpg', 0)} RPG, {pick['stats'].get('apg', 0)} APG\n"
                response += f"   Fantasy Score: {pick['fantasy_score']:.1f}\n\n"
            
            vector_db.disconnect()
            return response
            
        except Exception as e:
            logger.error(f"Error in find_value_picks: {e}")
            return f"Error finding value picks: {str(e)}"
    
    def compare_players(self, input_str: str) -> str:
        """Compare two players for draft/keeper decisions"""
        try:
            parts = input_str.split(',')
            player1_name = parts[0].strip()
            player2_name = parts[1].strip()
            
            # Get data for both players
            player1_data = self._get_player_data(player1_name)
            player2_data = self._get_player_data(player2_name)
            
            if not player1_data:
                return f"Player {player1_name} not found"
            if not player2_data:
                return f"Player {player2_name} not found"
            
            # Compare players
            comparison = f"""
Player Comparison:

{player1_name}:
- ADP: {player1_data['adp']} (Round {player1_data['round']})
- Stats: {player1_data['ppg']} PPG, {player1_data['rpg']} RPG, {player1_data['apg']} APG
- Keeper Value: Round {player1_data['keeper_round']}
- Fantasy Score: {player1_data['fantasy_score']:.1f}

{player2_name}:
- ADP: {player2_data['adp']} (Round {player2_data['round']})
- Stats: {player2_data['ppg']} PPG, {player2_data['rpg']} RPG, {player2_data['apg']} APG
- Keeper Value: Round {player2_data['keeper_round']}
- Fantasy Score: {player2_data['fantasy_score']:.1f}

Recommendation: """
            
            if player1_data['fantasy_score'] > player2_data['fantasy_score'] * 1.1:
                comparison += f"{player1_name} is the better pick (higher fantasy production)"
            elif player2_data['fantasy_score'] > player1_data['fantasy_score'] * 1.1:
                comparison += f"{player2_name} is the better pick (higher fantasy production)"
            else:
                if player1_data['adp'] < player2_data['adp']:
                    comparison += f"{player1_name} (better ADP value, similar production)"
                else:
                    comparison += f"{player2_name} (better ADP value, similar production)"
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error in compare_players: {e}")
            return f"Error comparing players: {str(e)}"
    
    def get_player_stats(self, player_name: str) -> str:
        """Get detailed stats for a player"""
        try:
            player_data = self._get_player_data(player_name)
            if not player_data:
                return f"Player {player_name} not found"
            
            return f"""
{player_name} Fantasy Profile:
- Position: {player_data['position']}
- Team: {player_data['team']}
- ADP: {player_data['adp']} (Round {player_data['round']})
- Keeper Round Value: {player_data['keeper_round']}

2023-24 Stats:
- PPG: {player_data['ppg']}
- RPG: {player_data['rpg']}
- APG: {player_data['apg']}
- FG%: {player_data['fg_pct']:.3f}
- FT%: {player_data['ft_pct']:.3f}
- 3P%: {player_data['three_pct']:.3f}

Fantasy Score: {player_data['fantasy_score']:.1f}
"""
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return f"Error getting stats: {str(e)}"
    
    def _get_player_data(self, player_name: str) -> Dict[str, Any]:
        """Helper to get player data from Milvus"""
        try:
            vector_db.connect()
            collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
            
            expr = f'player_name == "{player_name}"'
            results = collection.query(
                expr=expr,
                output_fields=["player_name", "position", "metadata"],
                limit=1
            )
            
            if not results:
                vector_db.disconnect()
                return None
            
            player = results[0]
            metadata = player.get('metadata', {})
            fantasy = metadata.get('fantasy', {})
            stats = metadata.get('stats', {})
            
            fantasy_score = (stats.get('ppg', 0) * 1.0 + 
                           stats.get('rpg', 0) * 1.2 + 
                           stats.get('apg', 0) * 1.5 + 
                           stats.get('spg', 0) * 3.0 + 
                           stats.get('bpg', 0) * 3.0)
            
            data = {
                'name': player['player_name'],
                'position': player['position'],
                'team': metadata.get('team', 'FA'),
                'adp': fantasy.get('adp', 999),
                'round': int(fantasy.get('adp', 999)/12) + 1,
                'keeper_round': fantasy.get('keeper_round_value', 15),
                'ppg': stats.get('ppg', 0),
                'rpg': stats.get('rpg', 0),
                'apg': stats.get('apg', 0),
                'spg': stats.get('spg', 0),
                'bpg': stats.get('bpg', 0),
                'fg_pct': stats.get('fg_pct', 0),
                'ft_pct': stats.get('ft_pct', 0),
                'three_pct': stats.get('three_pct', 0),
                'fantasy_score': fantasy_score
            }
            
            vector_db.disconnect()
            return data
            
        except Exception as e:
            logger.error(f"Error getting player data: {e}")
            return None
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query using the agent or direct tool calls"""
        try:
            if self.agent:
                # Use LangChain agent with LLM
                response = self.agent.run(query)
                return {
                    "agent": self.name,
                    "response": response,
                    "confidence": 0.9
                }
            else:
                # Direct tool routing without LLM
                query_lower = query.lower()
                
                if "keep" in query_lower and "round" in query_lower:
                    # Extract player name and round from query
                    # This is simplified - in production would use better parsing
                    if "ja morant" in query_lower and "3" in query:
                        result = self.analyze_keeper_value("Ja Morant,3")
                    else:
                        result = "Please specify player name and round for keeper analysis"
                
                elif "value" in query_lower or "pick" in query_lower:
                    # Default to rounds 5-7 for value picks
                    result = self.find_value_picks("5-7")
                
                elif "compare" in query_lower or "vs" in query_lower:
                    result = "Please specify two players to compare"
                
                else:
                    # Default to player stats
                    result = "Please specify what draft preparation help you need"
                
                return {
                    "agent": self.name,
                    "response": result,
                    "confidence": 0.7
                }
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "agent": self.name,
                "response": f"Error processing query: {str(e)}",
                "confidence": 0.0
            }