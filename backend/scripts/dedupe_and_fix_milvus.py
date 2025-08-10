"""
Deduplicate Milvus collection and ensure all active players are loaded
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from root .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
from typing import List, Dict, Set, Any
from app.data_loaders.player_loader import PlayerDataLoader
from app.db.vector_db import vector_db
from pymilvus import Collection, utility
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_collection():
    """Analyze the current state of the collection"""
    try:
        vector_db.connect()
        collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
        
        # Get total count
        total_entities = collection.num_entities
        print(f"\n[ANALYSIS] Collection Analysis:")
        print(f"Total entities in collection: {total_entities}")
        
        # Query all player names to find duplicates
        print("\nFetching all player data for analysis...")
        limit = 3000  # Fetch more than we need
        results = collection.query(
            expr="player_name != ''",
            output_fields=["player_name", "metadata"],
            limit=limit
        )
        
        # Analyze duplicates
        player_counts = {}
        unique_players = set()
        
        for entity in results:
            player_name = entity.get('player_name', 'Unknown')
            unique_players.add(player_name)
            player_counts[player_name] = player_counts.get(player_name, 0) + 1
        
        # Find duplicates
        duplicates = {name: count for name, count in player_counts.items() if count > 1}
        
        print(f"\n[RESULTS] Analysis Results:")
        print(f"Unique players found: {len(unique_players)}")
        print(f"Players with duplicates: {len(duplicates)}")
        
        if duplicates:
            print(f"\n[DUPLICATES] Top 10 Most Duplicated Players:")
            sorted_dupes = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]
            for name, count in sorted_dupes:
                print(f"  - {name}: {count} copies")
        
        vector_db.disconnect()
        return unique_players, duplicates, total_entities
        
    except Exception as e:
        logger.error(f"Error analyzing collection: {e}")
        return set(), {}, 0


def get_all_active_player_names():
    """Get list of all active NBA players"""
    loader = PlayerDataLoader()
    all_players = loader.get_all_active_players()
    player_names = {player['full_name'] for player in all_players}
    print(f"\n[NBA API] Reports: {len(player_names)} active players")
    return player_names


def deduplicate_collection(keep_latest=True):
    """Remove duplicate entries from the collection"""
    try:
        vector_db.connect()
        collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
        
        print("\n[DEDUP] Starting deduplication process...")
        
        # Get total count
        total_before = collection.num_entities
        print(f"Total entities before deduplication: {total_before}")
        
        # Query ALL data - increase limit to handle all entities
        limit = 5000  # Increased to handle all 2132 entities
        results = collection.query(
            expr="player_name != ''",
            output_fields=["player_name", "metadata", "created_at"],
            limit=limit
        )
        
        print(f"Fetched {len(results)} records for analysis")
        
        # Group by player name to find duplicates
        players_data = {}
        for entity in results:
            player_name = entity.get('player_name', 'Unknown')
            if player_name not in players_data:
                players_data[player_name] = []
            players_data[player_name].append(entity)
        
        # Count duplicates
        duplicate_count = sum(len(entries) - 1 for entries in players_data.values() if len(entries) > 1)
        unique_count = len(players_data)
        
        print(f"Found {unique_count} unique players")
        print(f"Found {duplicate_count} duplicate records to remove")
        
        if duplicate_count == 0 and total_before > unique_count:
            # If we still have more entities than unique players, do a more aggressive cleanup
            print(f"[WARNING] Entity count ({total_before}) exceeds unique players ({unique_count})")
            print("Performing comprehensive cleanup...")
            
            # Keep only one record per player name
            for player_name, entries in players_data.items():
                if len(entries) > 1:
                    # Sort by created_at to keep the latest
                    sorted_entries = sorted(entries, key=lambda x: x.get('created_at', 0), reverse=keep_latest)
                    
                    # Delete all but the first
                    for i, entry in enumerate(sorted_entries[1:]):
                        # Delete by player_name and created_at combination
                        expr = f'player_name == "{player_name}"'
                        # Get all entries for this player
                        all_player_entries = collection.query(
                            expr=expr,
                            output_fields=["created_at"],
                            limit=100
                        )
                        
                        # Keep only the latest/earliest based on preference
                        if len(all_player_entries) > 1:
                            created_ats = [e['created_at'] for e in all_player_entries]
                            created_ats.sort(reverse=keep_latest)
                            # Delete all but the first
                            for created_at in created_ats[1:]:
                                delete_expr = f'player_name == "{player_name}" and created_at == {created_at}'
                                collection.delete(delete_expr)
                                duplicate_count += 1
            
            collection.flush()
            print(f"[SUCCESS] Cleanup complete! Removed approximately {duplicate_count} duplicates")
        
        elif duplicate_count > 0:
            # Standard deduplication for found duplicates
            for player_name, entries in players_data.items():
                if len(entries) > 1:
                    # Sort by created_at to keep the latest (or earliest)
                    sorted_entries = sorted(entries, key=lambda x: x.get('created_at', 0), reverse=keep_latest)
                    
                    # Keep the first one, delete others
                    for entry in sorted_entries[1:]:
                        # Delete by player_name and created_at
                        expr = f'player_name == "{player_name}" and created_at == {entry.get("created_at", 0)}'
                        collection.delete(expr)
            
            collection.flush()
            print(f"[SUCCESS] Deduplication complete! Removed {duplicate_count} duplicates")
        else:
            print("[SUCCESS] No duplicates found!")
        
        # Get final count
        total_after = collection.num_entities
        print(f"Total entities after deduplication: {total_after}")
        
        vector_db.disconnect()
        return unique_count
        
    except Exception as e:
        logger.error(f"Error during deduplication: {e}")
        return 0


def identify_missing_players(existing_players: Set[str], all_nba_players: Set[str]):
    """Identify which players are missing from Milvus"""
    missing = all_nba_players - existing_players
    extra = existing_players - all_nba_players
    
    print(f"\n[COVERAGE] Player Coverage Analysis:")
    print(f"Players in NBA API: {len(all_nba_players)}")
    print(f"Players in Milvus: {len(existing_players)}")
    print(f"Missing players: {len(missing)}")
    print(f"Extra/Inactive players in Milvus: {len(extra)}")
    
    if missing and len(missing) <= 20:
        print(f"\n[MISSING] Missing players list:")
        for player in sorted(missing)[:20]:
            print(f"  - {player}")
    elif missing:
        print(f"\n[MISSING] First 20 missing players:")
        for player in sorted(missing)[:20]:
            print(f"  - {player}")
        print(f"  ... and {len(missing) - 20} more")
    
    return missing, extra


def load_missing_players(missing_players: Set[str]):
    """Load only the missing players to Milvus"""
    if not missing_players:
        print("\n[SUCCESS] No missing players to load!")
        return
    
    print(f"\n[LOADING] Loading {len(missing_players)} missing players...")
    
    try:
        loader = PlayerDataLoader()
        all_players = loader.get_all_active_players()
        
        # Filter to only missing players
        players_to_load = [p for p in all_players if p['full_name'] in missing_players]
        
        if not players_to_load:
            print("[WARNING] Could not find missing players in NBA API")
            return
        
        # Create a custom loader that only loads specific players
        from app.data_loaders.player_loader_incremental import IncrementalPlayerLoader
        incremental_loader = IncrementalPlayerLoader()
        incremental_loader.load_specific_players(players_to_load)
        
        print(f"[SUCCESS] Successfully loaded {len(players_to_load)} missing players")
        
    except ImportError:
        print("[INFO] Creating incremental loader...")
        # Create the incremental loader file
        create_incremental_loader()
        print("[SUCCESS] Incremental loader created. Please run this script again to load missing players.")
    except Exception as e:
        logger.error(f"Error loading missing players: {e}")


def create_incremental_loader():
    """Create an incremental loader that can load specific players"""
    loader_code = '''"""
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
'''
    
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'app', 'data_loaders', 'player_loader_incremental.py'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(loader_code)
    
    print(f"[SUCCESS] Created incremental loader at: {file_path}")


def main():
    """Main function to dedupe and fix the Milvus collection"""
    # Set UTF-8 encoding for Windows
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("SportsBrain Milvus Collection Deduplication Tool")
    print("=" * 60)
    
    # Step 1: Analyze current state
    existing_players, duplicates, total_entities = analyze_collection()
    
    # Step 2: Get all NBA players
    all_nba_players = get_all_active_player_names()
    
    # Step 3: Identify missing players
    missing, extra = identify_missing_players(existing_players, all_nba_players)
    
    # Step 4: Ask user what to do
    print("\n" + "=" * 60)
    print("[MENU] Available Actions:")
    print("1. Deduplicate collection (remove duplicates)")
    print("2. Load missing players only")
    print("3. Both (dedupe then load missing)")
    print("4. Just analyze (no changes)")
    print("0. Exit")
    
    choice = input("\nSelect action (0-4): ").strip()
    
    if choice == "1" or choice == "3":
        deduplicate_collection()
        if choice == "3":
            # Re-analyze after deduplication
            existing_players, _, _ = analyze_collection()
            missing, _ = identify_missing_players(existing_players, all_nba_players)
            load_missing_players(missing)
    elif choice == "2":
        load_missing_players(missing)
    elif choice == "4":
        print("\n[SUCCESS] Analysis complete. No changes made.")
    else:
        print("\n[EXIT] Exiting without changes.")
    
    # Final analysis
    if choice in ["1", "2", "3"]:
        print("\n" + "=" * 60)
        print("[FINAL] Final State:")
        analyze_collection()


if __name__ == "__main__":
    main()