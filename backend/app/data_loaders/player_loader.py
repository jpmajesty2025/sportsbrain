"""
NBA Player Data Loader for SportsBrain
Loads player data from NBA API, generates embeddings, and stores in Milvus and Neo4j
"""
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

import mmh3
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, playerprofilev2, commonplayerinfo
from sentence_transformers import SentenceTransformer
from pymilvus import Collection, utility

from app.db.vector_db import vector_db
from app.db.graph_db import graph_db
from app.core.config import settings
from app.data_loaders.fantasy_enrichment import FantasyDataEnricher
import logging

logger = logging.getLogger(__name__)


class PlayerDataLoader:
    def __init__(self):
        # Initialize embedding model - use model that produces 768 dimensions
        # Options: 'all-mpnet-base-v2' (768d) or 'all-MiniLM-L12-v2' (384d)
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # 768 dimensions
        self.collection_name = settings.MILVUS_PLAYERS_COLLECTION
        self.season = "2023-24"  # Most recent completed season
        self.fantasy_enricher = FantasyDataEnricher()
        
    def get_all_active_players(self) -> List[Dict[str, Any]]:
        """Get all active NBA players"""
        try:
            all_players = players.get_active_players()
            logger.info(f"Found {len(all_players)} active players")
            return all_players
        except Exception as e:
            logger.error(f"Failed to fetch players: {e}")
            return []
    
    def get_player_stats(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed stats for a specific player"""
        try:
            # Get career stats
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            career_data = career.get_data_frames()[0]
            
            # Get season stats for 2023-24
            season_stats = career_data[career_data['SEASON_ID'] == self.season]
            
            if season_stats.empty:
                # Try to get most recent season if 2023-24 not available
                season_stats = career_data.iloc[-1:]
            
            if not season_stats.empty:
                stats_dict = season_stats.iloc[0].to_dict()
                
                # Calculate per-game averages
                games_played = stats_dict.get('GP', 1)
                if games_played > 0:
                    return {
                        'season': stats_dict.get('SEASON_ID', self.season),
                        'team': stats_dict.get('TEAM_ABBREVIATION', 'FA'),
                        'games_played': games_played,
                        'ppg': round(stats_dict.get('PTS', 0) / games_played, 1),
                        'rpg': round(stats_dict.get('REB', 0) / games_played, 1),
                        'apg': round(stats_dict.get('AST', 0) / games_played, 1),
                        'spg': round(stats_dict.get('STL', 0) / games_played, 1),
                        'bpg': round(stats_dict.get('BLK', 0) / games_played, 1),
                        'fg_pct': round(stats_dict.get('FG_PCT', 0), 3),
                        'ft_pct': round(stats_dict.get('FT_PCT', 0), 3),
                        'three_pct': round(stats_dict.get('FG3_PCT', 0), 3),
                        'min_per_game': round(stats_dict.get('MIN', 0) / games_played, 1)
                    }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get stats for player {player_id}: {e}")
            return None
    
    def create_player_text_description(self, player_info: Dict, stats: Dict) -> str:
        """Create a rich text description for embedding"""
        position_map = {
            'G': 'Guard', 'F': 'Forward', 'C': 'Center',
            'G-F': 'Guard-Forward', 'F-C': 'Forward-Center',
            'F-G': 'Forward-Guard', 'C-F': 'Center-Forward'
        }
        
        position = position_map.get(player_info.get('position', 'G'), 'Guard')
        
        description = f"{player_info['full_name']} is a {position} "
        
        if stats:
            description += f"playing for {stats['team']} in the {stats['season']} season. "
            description += f"Averaging {stats['ppg']} points, {stats['rpg']} rebounds, and {stats['apg']} assists per game. "
            
            # Add shooting description
            if stats['three_pct'] > 0.38:
                description += "Elite three-point shooter. "
            elif stats['three_pct'] > 0.35:
                description += "Good three-point shooter. "
                
            # Add role description based on stats
            if stats['apg'] > 6:
                description += "Primary playmaker and facilitator. "
            elif stats['ppg'] > 20:
                description += "Primary scoring option. "
            elif stats['rpg'] > 8:
                description += "Strong rebounder. "
                
            # Fantasy relevance
            fantasy_score = (stats['ppg'] * 1.0 + stats['rpg'] * 1.2 + 
                           stats['apg'] * 1.5 + stats['spg'] * 3.0 + stats['bpg'] * 3.0)
            
            if fantasy_score > 45:
                description += "Elite fantasy basketball option. "
            elif fantasy_score > 35:
                description += "Strong fantasy basketball contributor. "
            elif fantasy_score > 25:
                description += "Solid fantasy basketball option. "
            else:
                description += "Streaming or deep league fantasy option. "
                
        else:
            description += "Limited recent playing time or rookie. "
            
        return description
    
    def load_players_to_milvus(self, limit: Optional[int] = None):
        """Load player data to Milvus vector database"""
        try:
            # Connect to Milvus
            vector_db.connect()
            collection = Collection(self.collection_name)
            
            # Get all active players
            all_players = self.get_all_active_players()
            
            if limit:
                all_players = all_players[:limit]
                
            logger.info(f"Processing {len(all_players)} players...")
            
            # Prepare batch data
            batch_size = 50
            total_inserted = 0
            
            for i in range(0, len(all_players), batch_size):
                batch_players = all_players[i:i + batch_size]
                
                # Prepare data lists for batch insert
                primary_keys = []
                vectors = []
                texts = []
                metadatas = []
                created_ats = []
                player_names = []
                positions = []
                
                for player in batch_players:
                    # Get player stats
                    stats = self.get_player_stats(player['id'])
                    
                    # Create text description
                    text = self.create_player_text_description(player, stats)
                    
                    # Generate embedding
                    embedding = self.embedding_model.encode(text, convert_to_tensor=False).tolist()
                    
                    # Generate primary key
                    key_string = f"{player['full_name']}_{player['id']}"
                    primary_key = mmh3.hash(key_string, signed=False)
                    
                    # Prepare base metadata
                    base_metadata = {
                        "player_id": player['id'],
                        "team": stats.get('team', 'FA') if stats else 'FA',
                        "season": stats.get('season', self.season) if stats else self.season,
                        "is_active": player.get('is_active', True),
                        "stats": stats if stats else {},
                        "fantasy_relevant": bool(stats and stats.get('games_played', 0) > 20),
                        "age": player.get('age', 25)  # NBA API doesn't always have age
                    }
                    
                    # Enrich with fantasy data
                    metadata = self.fantasy_enricher.enrich_player_metadata(
                        player['full_name'], 
                        base_metadata
                    )
                    
                    # Add to batch
                    primary_keys.append(primary_key)
                    vectors.append(embedding)
                    texts.append(text)
                    metadatas.append(metadata)
                    created_ats.append(int(time.time()))
                    player_names.append(player['full_name'])
                    positions.append(player.get('position', 'G'))
                
                # Insert batch
                data = [
                    primary_keys,
                    vectors,
                    texts,
                    metadatas,
                    created_ats,
                    player_names,
                    positions
                ]
                
                collection.insert(data)
                total_inserted += len(batch_players)
                
                logger.info(f"Inserted batch {i//batch_size + 1}, total: {total_inserted}")
                
                # Sleep to avoid rate limiting
                time.sleep(1)
            
            # Flush to ensure data is persisted
            collection.flush()
            logger.info(f"Successfully loaded {total_inserted} players to Milvus")
            
        except Exception as e:
            logger.error(f"Failed to load players to Milvus: {e}")
            raise
        finally:
            vector_db.disconnect()
    
    def load_players_to_neo4j(self, limit: Optional[int] = None):
        """Load player nodes and relationships to Neo4j"""
        try:
            # Connect to Neo4j
            graph_db.connect()
            
            # Get all active players
            all_players = self.get_all_active_players()
            
            if limit:
                all_players = all_players[:limit]
                
            logger.info(f"Loading {len(all_players)} players to Neo4j...")
            
            # First, create all teams
            all_teams = teams.get_teams()
            for team in all_teams:
                team_data = {
                    "name": team['full_name'],
                    "abbreviation": team['abbreviation'],
                    "city": team['city'],
                    "conference": "",  # Would need additional API call
                    "division": "",  # Would need additional API call
                    "coach": ""  # Would need additional API call
                }
                
                with graph_db.driver.session() as session:
                    query = """
                    MERGE (t:Team {abbreviation: $abbreviation})
                    SET t.name = $name,
                        t.city = $city
                    """
                    session.run(query, **team_data)
            
            # Create player nodes and relationships
            for player in all_players:
                stats = self.get_player_stats(player['id'])
                
                # Create player node
                player_data = {
                    "id": str(player['id']),
                    "name": player['full_name'],
                    "position": player.get('position', 'G'),
                    "is_active": player.get('is_active', True),
                    "stats": json.dumps(stats) if stats else "{}"
                }
                
                with graph_db.driver.session() as session:
                    query = """
                    MERGE (p:Player {id: $id})
                    SET p.name = $name,
                        p.position = $position,
                        p.is_active = $is_active,
                        p.stats = $stats
                    """
                    session.run(query, **player_data)
                    
                    # Create relationship to team
                    if stats and stats.get('team'):
                        team_query = """
                        MATCH (p:Player {id: $player_id})
                        MATCH (t:Team {abbreviation: $team})
                        MERGE (p)-[r:PLAYS_FOR]->(t)
                        SET r.season = $season
                        """
                        session.run(team_query, 
                                  player_id=str(player['id']),
                                  team=stats['team'],
                                  season=stats['season'])
            
            logger.info(f"Successfully loaded {len(all_players)} players to Neo4j")
            
        except Exception as e:
            logger.error(f"Failed to load players to Neo4j: {e}")
            raise
        finally:
            graph_db.disconnect()


# Utility function for running the loader
def load_all_player_data(limit: Optional[int] = None):
    """Load player data to both Milvus and Neo4j"""
    loader = PlayerDataLoader()
    
    logger.info("Starting player data load...")
    
    # Load to Milvus
    logger.info("Loading to Milvus...")
    loader.load_players_to_milvus(limit=limit)
    
    # Load to Neo4j
    logger.info("Loading to Neo4j...")
    loader.load_players_to_neo4j(limit=limit)
    
    logger.info("Player data load complete!")


if __name__ == "__main__":
    # Test with a small batch first
    load_all_player_data(limit=10)