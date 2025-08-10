"""Load the final missing players to complete the collection"""
import sys
import os
import io
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.vector_db import vector_db
from pymilvus import Collection
from app.core.config import settings
from app.data_loaders.player_loader import PlayerDataLoader
from app.data_loaders.player_loader_incremental import IncrementalPlayerLoader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_and_load_missing():
    """Find and load only the missing players"""
    
    # Get all NBA players
    loader = PlayerDataLoader()
    all_nba_players = loader.get_all_active_players()
    all_nba_names = {p['full_name'] for p in all_nba_players}
    print(f"Total NBA players: {len(all_nba_names)}")
    
    # Get current players in Milvus
    vector_db.connect()
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    
    # Query all existing players
    results = collection.query(
        expr="player_name != ''",
        output_fields=["player_name"],
        limit=3000
    )
    
    existing_names = {r.get('player_name') for r in results}
    print(f"Players currently in Milvus: {len(existing_names)}")
    
    # Find missing players
    missing_names = all_nba_names - existing_names
    print(f"Missing players: {len(missing_names)}")
    
    if missing_names:
        print("\nMissing players list:")
        for name in sorted(missing_names):
            print(f"  - {name}")
        
        # Get full player data for missing players
        missing_players = [p for p in all_nba_players if p['full_name'] in missing_names]
        
        confirm = input(f"\nLoad {len(missing_players)} missing players? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print(f"\nLoading {len(missing_players)} missing players...")
            
            # Use incremental loader to add them
            incremental_loader = IncrementalPlayerLoader()
            incremental_loader.load_specific_players(missing_players)
            
            # Verify final count
            collection.flush()
            final_count = collection.num_entities
            print(f"\nFinal entity count: {final_count}")
            
            # Re-check unique players
            results = collection.query(
                expr="player_name != ''",
                output_fields=["player_name"],
                limit=3000
            )
            final_unique = len(set(r.get('player_name') for r in results))
            print(f"Final unique players: {final_unique}")
            
            if final_unique == 572:
                print("\n[SUCCESS] All 572 NBA players are now loaded!")
            else:
                print(f"\n[INFO] Loaded {final_unique} players. {572 - final_unique} still missing.")
        else:
            print("\n[CANCELLED] No players loaded.")
    else:
        print("\n[SUCCESS] No missing players - collection is complete!")
    
    vector_db.disconnect()

if __name__ == "__main__":
    find_and_load_missing()