"""
Test queries to validate player data loading
Run after: python load_data.py --players --limit 10
"""
import sys
import os
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.vector_db import vector_db
from app.db.graph_db import graph_db
from pymilvus import Collection
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Skip these tests in CI as they require Milvus/Neo4j services
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Skipping in CI - requires Milvus and Neo4j services"
)


def test_vector_search():
    """Test vector similarity search"""
    print("\n=== Testing Vector Search ===")
    
    # Connect and get collection
    vector_db.connect()
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    collection.load()
    
    # Initialize embedding model - must match the one used in player_loader.py
    model = SentenceTransformer('all-mpnet-base-v2')  # 768 dimensions
    
    # Test queries
    test_queries = [
        "Elite scorer with good three point shooting",
        "Strong fantasy basketball contributor",
        "Primary playmaker and facilitator",
        "Players similar to LeBron James"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # Generate query embedding
        query_embedding = model.encode(query, convert_to_tensor=False).tolist()
        
        # Search
        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_embedding],
            anns_field="vector",
            param=search_params,
            limit=3,
            output_fields=["player_name", "text", "metadata"]
        )
        
        # Display results
        for i, hit in enumerate(results[0]):
            print(f"  {i+1}. {hit.entity.get('player_name')} (score: {hit.score:.3f})")
            metadata = hit.entity.get('metadata')
            if metadata:
                team = metadata.get('team', 'N/A')
                ppg = metadata.get('stats', {}).get('ppg', 0)
                print(f"     Team: {team}, PPG: {ppg}")
    
    vector_db.disconnect()


def test_graph_queries():
    """Test Neo4j graph queries"""
    print("\n=== Testing Graph Queries ===")
    
    graph_db.connect()
    
    # Test 1: Count players and teams
    with graph_db.driver.session() as session:
        result = session.run("MATCH (p:Player) RETURN count(p) as player_count")
        player_count = result.single()['player_count']
        print(f"\nTotal players in graph: {player_count}")
        
        result = session.run("MATCH (t:Team) RETURN count(t) as team_count")
        team_count = result.single()['team_count']
        print(f"Total teams in graph: {team_count}")
    
    # Test 2: Show player-team relationships
    print("\nPlayer-Team Relationships:")
    with graph_db.driver.session() as session:
        result = session.run("""
            MATCH (p:Player)-[r:PLAYS_FOR]->(t:Team)
            RETURN p.name as player, t.name as team, r.season as season
            LIMIT 5
        """)
        for record in result:
            print(f"  {record['player']} plays for {record['team']} ({record['season']})")
    
    # Test 3: Find players by position
    print("\nPlayers by position:")
    with graph_db.driver.session() as session:
        result = session.run("""
            MATCH (p:Player)
            RETURN p.position as position, count(p) as count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"  {record['position']}: {record['count']} players")
    
    graph_db.disconnect()


def test_combined_query():
    """Test combining vector and graph data"""
    print("\n=== Testing Combined Vector + Graph ===")
    
    # This demonstrates how we might combine both databases
    vector_db.connect()
    graph_db.connect()
    
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    collection.load()
    
    # First, find high scorers via vector search
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode("Elite scorer averaging over 25 points", convert_to_tensor=False).tolist()
    
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_embedding],
        anns_field="vector",
        param=search_params,
        limit=3,
        output_fields=["player_name", "metadata"]
    )
    
    print("\nHigh scorers found via vector search:")
    for hit in results[0]:
        player_name = hit.entity.get('player_name')
        metadata = hit.entity.get('metadata', {})
        player_id = metadata.get('player_id')
        
        # Get team info from graph
        with graph_db.driver.session() as session:
            result = session.run("""
                MATCH (p:Player {id: $player_id})-[:PLAYS_FOR]->(t:Team)
                RETURN t.name as team
            """, player_id=str(player_id))
            
            team = "Free Agent"
            record = result.single()
            if record:
                team = record['team']
        
        print(f"  {player_name} - {team}")
    
    vector_db.disconnect()
    graph_db.disconnect()


def validate_data_quality():
    """Validate the quality of loaded data"""
    print("\n=== Data Quality Validation ===")
    
    vector_db.connect()
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    
    # Check total embeddings
    print(f"\nTotal embeddings in Milvus: {collection.num_entities}")
    
    # Sample some data to check quality
    expr = "primary_key > 0"
    results = collection.query(
        expr=expr,
        limit=5,
        output_fields=["player_name", "position", "text", "metadata"]
    )
    
    print("\nSample player embeddings:")
    for i, result in enumerate(results):
        print(f"\n{i+1}. {result['player_name']} ({result['position']})")
        print(f"   Text preview: {result['text'][:100]}...")
        metadata = result.get('metadata', {})
        if metadata.get('stats'):
            stats = metadata['stats']
            print(f"   Stats: {stats.get('ppg', 0)} PPG, {stats.get('rpg', 0)} RPG, {stats.get('apg', 0)} APG")
    
    vector_db.disconnect()


if __name__ == "__main__":
    print("SportsBrain Player Data Test Queries")
    print("=" * 50)
    
    try:
        test_vector_search()
        test_graph_queries()
        test_combined_query()
        validate_data_quality()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()