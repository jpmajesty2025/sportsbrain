"""Quick check of Milvus entity count"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.vector_db import vector_db
from pymilvus import Collection
from app.core.config import settings

vector_db.connect()
collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
count = collection.num_entities

print(f"Current entity count in Milvus: {count}")

if count == 572:
    print("[SUCCESS] Collection has exactly 572 entities (correct count)")
else:
    print(f"[WARNING] Expected 572 entities but found {count}")

# Check for unique players
results = collection.query(
    expr="player_name != ''",
    output_fields=["player_name"],
    limit=1000
)

unique_players = set(r.get('player_name') for r in results)
print(f"Unique players found: {len(unique_players)}")

vector_db.disconnect()