"""Verify that there are no duplicate players in the collection"""
import sys
import os
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.vector_db import vector_db
from pymilvus import Collection
from app.core.config import settings

def check_for_duplicates():
    """Check if there are any duplicate player names in the collection"""
    
    vector_db.connect()
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    
    print("=" * 60)
    print("Duplicate Check for Milvus Collection")
    print("=" * 60)
    
    # Get entity count
    entity_count = collection.num_entities
    print(f"\nTotal entities in collection: {entity_count}")
    
    # Query ALL records - use high limit to ensure we get everything
    results = collection.query(
        expr="player_name != ''",
        output_fields=["player_name", "created_at"],
        limit=5000  # High limit to get all records
    )
    
    print(f"Total records retrieved: {len(results)}")
    
    # Count occurrences of each player name
    player_names = [r.get('player_name', 'Unknown') for r in results]
    name_counts = Counter(player_names)
    
    # Find duplicates
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    # Get unique count
    unique_players = len(name_counts)
    
    print(f"\nUnique player names: {unique_players}")
    print(f"Players with duplicates: {len(duplicates)}")
    
    if duplicates:
        print("\n[WARNING] Found duplicate players:")
        print("-" * 40)
        # Sort by count (most duplicated first)
        sorted_dupes = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)
        for name, count in sorted_dupes[:20]:  # Show top 20
            print(f"  {name}: {count} copies")
        
        if len(duplicates) > 20:
            print(f"  ... and {len(duplicates) - 20} more players with duplicates")
        
        # Calculate total duplicate entries
        total_duplicate_entries = sum(count - 1 for count in duplicates.values())
        print(f"\nTotal duplicate entries to remove: {total_duplicate_entries}")
        print(f"After deduplication, would have: {len(results) - total_duplicate_entries} entities")
    else:
        print("\n[SUCCESS] No duplicates found!")
        print(f"All {unique_players} players are unique")
        
        # Additional verification
        if entity_count != len(results):
            print(f"\n[INFO] Entity count ({entity_count}) differs from query results ({len(results)})")
            print("This might indicate:")
            print("  1. Some entities don't have player_name field")
            print("  2. Collection statistics need to be refreshed")
            print("  3. There are pending operations not yet flushed")
        
        if unique_players != entity_count:
            print(f"\n[INFO] Unique players ({unique_players}) differs from entity count ({entity_count})")
    
    # Show some sample data
    if results:
        print("\n" + "-" * 40)
        print("Sample of first 5 players:")
        seen = set()
        count = 0
        for r in results:
            name = r.get('player_name')
            if name and name not in seen:
                seen.add(name)
                print(f"  - {name}")
                count += 1
                if count >= 5:
                    break
    
    vector_db.disconnect()
    return unique_players, duplicates

if __name__ == "__main__":
    unique_count, dupes = check_for_duplicates()
    
    if not dupes:
        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETE")
        print(f"✓ Collection has {unique_count} unique players")
        print("✓ No duplicates detected")
        print("=" * 60)