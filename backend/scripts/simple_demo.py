"""
Simple demo queries avoiding Unicode issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.vector_db import vector_db
from app.db.graph_db import graph_db
from pymilvus import Collection
from app.core.config import settings


def test_milvus_queries():
    """Test some key queries on Milvus"""
    print("\n=== MILVUS QUERY RESULTS ===")
    
    vector_db.connect()
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    
    # Count total entities
    print(f"\nTotal players in Milvus: {collection.num_entities}")
    
    # Query 1: Find specific players
    print("\n1. Checking Key Players (Ja Morant question):")
    expr = "player_name in ['Ja Morant', 'Jayson Tatum', 'Giannis Antetokounmpo']"
    results = collection.query(
        expr=expr,
        output_fields=["player_name", "position", "metadata"],
        limit=10
    )
    
    for result in results:
        name = result['player_name']
        metadata = result.get('metadata', {})
        fantasy = metadata.get('fantasy', {})
        stats = metadata.get('stats', {})
        
        print(f"\n{name}:")
        print(f"  Stats: {stats.get('ppg', 0)} PPG, {stats.get('apg', 0)} APG")
        print(f"  ADP: {fantasy.get('adp', 999)}")
        print(f"  Keeper Round: {fantasy.get('keeper_round_value', 15)}")
        print(f"  Keep in Round 3? {'YES' if fantasy.get('keeper_round_value', 15) <= 3 else 'NO'}")
    
    # Query 2: Find top fantasy players
    print("\n2. Top Fantasy Players by ADP:")
    expr = "metadata['fantasy']['adp'] < 20"
    results = collection.query(
        expr=expr,
        output_fields=["player_name", "metadata"],
        limit=10
    )
    
    # Sort by ADP
    sorted_results = sorted(results, key=lambda x: x['metadata']['fantasy']['adp'])
    
    for result in sorted_results[:5]:
        name = result['player_name']
        adp = result['metadata']['fantasy']['adp']
        print(f"  {name}: ADP {adp}")
    
    vector_db.disconnect()


def test_neo4j_queries():
    """Test Neo4j graph queries"""
    print("\n=== NEO4J QUERY RESULTS ===")
    
    graph_db.connect()
    
    # Query 1: Count players and teams
    with graph_db.driver.session() as session:
        result = session.run("MATCH (p:Player) RETURN count(p) as count")
        player_count = result.single()['count']
        
        result = session.run("MATCH (t:Team) RETURN count(t) as count")
        team_count = result.single()['count']
        
        print(f"\nTotal in Neo4j: {player_count} players, {team_count} teams")
    
    # Query 2: Players by team
    print("\n1. Sample Team Rosters:")
    with graph_db.driver.session() as session:
        result = session.run("""
            MATCH (p:Player)-[:PLAYS_FOR]->(t:Team)
            WITH t.name as team, collect(p.name) as players
            WHERE size(players) > 5
            RETURN team, players[0..5] as sample_players
            LIMIT 3
        """)
        
        for record in result:
            team = record['team']
            players = record['sample_players']
            print(f"\n{team}:")
            for player in players:
                print(f"  - {player}")
    
    graph_db.disconnect()


if __name__ == "__main__":
    print("SportsBrain Simple Demo")
    print("Testing with 470 NBA players")
    
    try:
        test_milvus_queries()
        test_neo4j_queries()
        print("\n=== DEMO COMPLETE ===")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()