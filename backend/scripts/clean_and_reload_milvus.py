"""
Clean and reload Milvus collection - nuclear option to fix duplicates
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from root .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymilvus import Collection, utility
from app.db.vector_db import vector_db
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_collection():
    """Delete ALL entities from the collection"""
    try:
        vector_db.connect()
        collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
        
        # Get initial count
        initial_count = collection.num_entities
        print(f"\n[INFO] Current entity count: {initial_count}")
        
        if initial_count == 0:
            print("[INFO] Collection is already empty")
            return True
            
        print("[CLEANING] Deleting ALL entities from collection...")
        
        # Delete everything using a broad expression
        # This matches all entities since id is always >= 0
        expr = "id >= 0"
        collection.delete(expr)
        collection.flush()
        
        # Verify deletion
        final_count = collection.num_entities
        print(f"[SUCCESS] Deleted {initial_count - final_count} entities")
        print(f"[INFO] Final entity count: {final_count}")
        
        vector_db.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"Error cleaning collection: {e}")
        return False


def reload_players():
    """Reload all players using the incremental loader"""
    try:
        from app.data_loaders.player_loader import PlayerDataLoader
        from app.data_loaders.player_loader_incremental import IncrementalPlayerLoader
        
        # Get all active players
        loader = PlayerDataLoader()
        all_players = loader.get_all_active_players()
        print(f"\n[INFO] Found {len(all_players)} active players to load")
        
        # Use incremental loader to load them (it checks for duplicates)
        incremental_loader = IncrementalPlayerLoader()
        incremental_loader.load_specific_players(all_players)
        
        # Verify final count
        vector_db.connect()
        collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
        final_count = collection.num_entities
        vector_db.disconnect()
        
        print(f"\n[SUCCESS] Collection now has {final_count} entities")
        return True
        
    except Exception as e:
        logger.error(f"Error reloading players: {e}")
        return False


def main():
    """Main function to clean and reload the collection"""
    print("=" * 60)
    print("SportsBrain Milvus Collection Clean & Reload")
    print("=" * 60)
    print("\n[WARNING] This will DELETE ALL data and reload from scratch!")
    print("This is the nuclear option to fix duplicate issues.")
    
    # Check current state
    try:
        vector_db.connect()
        collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
        current_count = collection.num_entities
        vector_db.disconnect()
        
        print(f"\nCurrent entity count: {current_count}")
        
        if current_count == 572:
            print("[INFO] Collection already has exactly 572 entities (correct count)")
            confirm = input("Do you still want to clean and reload? (y/n): ").strip().lower()
        else:
            print(f"[WARNING] Expected 572 entities but found {current_count}")
            confirm = input("\nProceed with clean and reload? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("[EXIT] Operation cancelled")
            return
            
        # Step 1: Clean the collection
        print("\n" + "=" * 40)
        print("Step 1: Cleaning collection...")
        if not clean_collection():
            print("[ERROR] Failed to clean collection")
            return
            
        # Step 2: Reload players
        print("\n" + "=" * 40)
        print("Step 2: Reloading players...")
        if not reload_players():
            print("[ERROR] Failed to reload players")
            return
            
        print("\n" + "=" * 60)
        print("[SUCCESS] Collection cleaned and reloaded successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"[ERROR] Operation failed: {e}")


if __name__ == "__main__":
    main()