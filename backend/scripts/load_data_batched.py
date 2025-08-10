"""
Batch load players to avoid timeouts
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from app.data_loaders.player_loader import PlayerDataLoader
from app.db.vector_db import vector_db
from pymilvus import Collection
from app.core.config import settings

def check_current_count():
    """Check how many players are already loaded"""
    try:
        vector_db.connect()
        collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
        count = collection.num_entities
        vector_db.disconnect()
        return count
    except:
        return 0

def load_players_in_batches():
    """Load players in smaller batches to avoid timeouts"""
    loader = PlayerDataLoader()
    
    # Get all players
    all_players = loader.get_all_active_players()
    print(f"Total players to load: {len(all_players)}")
    
    # Check current count
    current_count = check_current_count()
    print(f"Current players in Milvus: {current_count}")
    
    if current_count >= len(all_players):
        print("All players already loaded!")
        return
    
    # Load in batches of 100
    batch_size = 100
    start_index = current_count  # Resume from where we left off
    
    for i in range(start_index, len(all_players), batch_size):
        end_index = min(i + batch_size, len(all_players))
        print(f"\nLoading batch {i//batch_size + 1}: players {i} to {end_index-1}")
        
        try:
            # Load this batch
            loader.load_players_to_milvus(limit=end_index)
            
            # Also load to Neo4j
            loader.load_players_to_neo4j(limit=end_index)
            
            print(f"Batch complete. Total loaded: {end_index}")
            
            # Short pause between batches
            if end_index < len(all_players):
                print("Pausing 5 seconds before next batch...")
                time.sleep(5)
                
        except Exception as e:
            print(f"Error loading batch: {e}")
            print(f"Stopped at index {i}. You can resume by running this script again.")
            break
    
    # Final count
    final_count = check_current_count()
    print(f"\nLoad complete! Total players in Milvus: {final_count}")

if __name__ == "__main__":
    load_players_in_batches()