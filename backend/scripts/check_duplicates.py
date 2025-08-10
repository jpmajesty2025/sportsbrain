"""
Check for duplicate players in Milvus
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.vector_db import vector_db
from pymilvus import Collection
from app.core.config import settings
from collections import Counter

def check_duplicates():
    """Check for duplicate players in Milvus"""
    vector_db.connect()
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    
    print(f"Total entities in collection: {collection.num_entities}")
    
    # Query all players
    results = collection.query(
        expr="primary_key > 0",
        output_fields=["primary_key", "player_name"],
        limit=1000
    )
    
    # Count duplicates
    player_names = [r['player_name'] for r in results]
    name_counts = Counter(player_names)
    
    # Find duplicates
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    print(f"\nTotal unique players: {len(name_counts)}")
    print(f"Players with duplicates: {len(duplicates)}")
    
    if duplicates:
        print("\nDuplicate players:")
        for name, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {name}: {count} copies")
    
    # Show sample of players
    print("\nSample players:")
    for i, (name, count) in enumerate(name_counts.most_common(10)):
        print(f"  {i+1}. {name}: {count} entries")
    
    vector_db.disconnect()

if __name__ == "__main__":
    check_duplicates()