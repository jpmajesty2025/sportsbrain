"""
Incremental Player Loader - Loads specific players without duplicates
"""
from typing import List, Dict, Any
import time
import mmh3
from sentence_transformers import SentenceTransformer
from pymilvus import Collection
from app.db.vector_db import vector_db
from app.core.config import settings
from app.data_loaders.player_loader import PlayerDataLoader
import logging

logger = logging.getLogger(__name__)


class IncrementalPlayerLoader(PlayerDataLoader):
    """Loader that only loads specific players and checks for duplicates"""
    
    def load_specific_players(self, players_to_load: List[Dict[str, Any]]):
        """Load only specific players, checking for duplicates"""
        try:
            # Connect to Milvus
            vector_db.connect()
            collection = Collection(self.collection_name)
            
            # Check existing players
            existing_players = set()
            results = collection.query(
                expr="player_name != ''",
                output_fields=["player_name"],
                limit=3000
            )
            for r in results:
                existing_players.add(r.get('player_name'))
            
            logger.info(f"Found {len(existing_players)} existing players in Milvus")
            
            # Filter out players that already exist
            new_players = [p for p in players_to_load if p['full_name'] not in existing_players]
            
            if not new_players:
                logger.info("All specified players already exist in Milvus")
                return
            
            logger.info(f"Loading {len(new_players)} new players...")
            
            # Process in small batches to avoid rate limiting
            batch_size = 10
            total_inserted = 0
            
            for i in range(0, len(new_players), batch_size):
                batch_players = new_players[i:i + batch_size]
                
                # Prepare data lists for batch insert
                primary_keys = []
                vectors = []
                texts = []
                metadatas = []
                created_ats = []
                player_names = []
                positions = []
                
                for player in batch_players:
                    try:
                        # Get player stats with retry logic
                        stats = None
                        for attempt in range(3):
                            try:
                                stats = self.get_player_stats(player['id'])
                                break
                            except Exception as e:
                                if attempt < 2:
                                    time.sleep(2)  # Wait before retry
                                else:
                                    logger.warning(f"Failed to get stats for {player['full_name']}: {e}")
                        
                        # Create text description
                        text = self.create_player_text_description(player, stats)
                        
                        # Generate embedding
                        embedding = self.embedding_model.encode(text, convert_to_tensor=False).tolist()
                        
                        # Generate primary key
                        key_string = f"{player['full_name']}_{player['id']}"
                        primary_key = mmh3.hash(key_string, signed=False)
                        
                        # Prepare metadata
                        base_metadata = {
                            "player_id": player['id'],
                            "team": stats.get('team', 'FA') if stats else 'FA',
                            "season": stats.get('season', self.season) if stats else self.season,
                            "is_active": player.get('is_active', True),
                            "stats": stats if stats else {},
                            "fantasy_relevant": bool(stats and stats.get('games_played', 0) > 20)
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
                        
                    except Exception as e:
                        logger.error(f"Error processing player {player['full_name']}: {e}")
                        continue
                
                if primary_keys:  # Only insert if we have data
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
                    total_inserted += len(primary_keys)
                    
                    logger.info(f"Inserted batch {i//batch_size + 1}, total: {total_inserted}")
                
                # Sleep to avoid rate limiting
                time.sleep(3)
            
            # Flush to ensure data is persisted
            collection.flush()
            logger.info(f"Successfully loaded {total_inserted} new players to Milvus")
            
        except Exception as e:
            logger.error(f"Failed to load players to Milvus: {e}")
            raise
        finally:
            vector_db.disconnect()
    
    def upsert_players(self, players_to_upsert: List[Dict[str, Any]]):
        """Upsert players - update if exists, insert if new"""
        try:
            # Connect to Milvus
            vector_db.connect()
            collection = Collection(self.collection_name)
            
            logger.info(f"Upserting {len(players_to_upsert)} players...")
            
            # Process each player
            updated = 0
            inserted = 0
            
            for player in players_to_upsert:
                try:
                    player_name = player['full_name']
                    
                    # Check if player exists
                    expr = f'player_name == "{player_name}"'
                    existing = collection.query(
                        expr=expr,
                        output_fields=["id", "player_name"],
                        limit=1
                    )
                    
                    if existing:
                        # Delete existing entry
                        collection.delete(expr)
                        updated += 1
                    else:
                        inserted += 1
                    
                    # Get fresh stats
                    stats = self.get_player_stats(player['id'])
                    
                    # Create text description
                    text = self.create_player_text_description(player, stats)
                    
                    # Generate embedding
                    embedding = self.embedding_model.encode(text, convert_to_tensor=False).tolist()
                    
                    # Generate primary key
                    key_string = f"{player['full_name']}_{player['id']}"
                    primary_key = mmh3.hash(key_string, signed=False)
                    
                    # Prepare metadata
                    base_metadata = {
                        "player_id": player['id'],
                        "team": stats.get('team', 'FA') if stats else 'FA',
                        "season": stats.get('season', self.season) if stats else self.season,
                        "is_active": player.get('is_active', True),
                        "stats": stats if stats else {},
                        "fantasy_relevant": bool(stats and stats.get('games_played', 0) > 20)
                    }
                    
                    # Enrich with fantasy data
                    metadata = self.fantasy_enricher.enrich_player_metadata(
                        player['full_name'], 
                        base_metadata
                    )
                    
                    # Insert new/updated data
                    data = [
                        [primary_key],
                        [embedding],
                        [text],
                        [metadata],
                        [int(time.time())],
                        [player_name],
                        [player.get('position', 'G')]
                    ]
                    
                    collection.insert(data)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error upserting player {player.get('full_name', 'Unknown')}: {e}")
                    continue
            
            # Flush to ensure data is persisted
            collection.flush()
            logger.info(f"Upsert complete: {updated} updated, {inserted} inserted")
            
        except Exception as e:
            logger.error(f"Failed to upsert players: {e}")
            raise
        finally:
            vector_db.disconnect()