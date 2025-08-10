"""
Demo queries to showcase SportsBrain's capabilities
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.vector_db import vector_db
from app.db.graph_db import graph_db
from pymilvus import Collection
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import json


def run_vector_searches():
    """Run various vector similarity searches"""
    print("\n" + "="*60)
    print("SPORTSBRAIN DEMO QUERIES - VECTOR SEARCH")
    print("="*60)
    
    # Connect to Milvus
    vector_db.connect()
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    collection.load()
    
    # Initialize embedding model
    model = SentenceTransformer('all-mpnet-base-v2')
    
    # Demo queries aligned with claude.md scenarios
    queries = [
        {
            "query": "Elite point guards with great three point shooting for fantasy basketball",
            "context": "Finding PGs for punt FG% strategy"
        },
        {
            "query": "High scoring forwards who are consistent fantasy performers",
            "context": "Looking for reliable fantasy options"
        },
        {
            "query": "Young players with breakout potential and good keeper value",
            "context": "Dynasty/keeper league targets"
        },
        {
            "query": "Centers who get blocks and rebounds but poor free throw shooters",
            "context": "Punt FT% build targets"
        },
        {
            "query": "Players similar to Jayson Tatum elite scoring forward",
            "context": "Finding comparable players"
        }
    ]
    
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    
    for q in queries:
        print(f"\n{'='*60}")
        print(f"Query: {q['query']}")
        print(f"Context: {q['context']}")
        print("-"*60)
        
        # Generate embedding
        query_embedding = model.encode(q['query'], convert_to_tensor=False).tolist()
        
        # Search
        results = collection.search(
            data=[query_embedding],
            anns_field="vector",
            param=search_params,
            limit=5,
            output_fields=["player_name", "position", "text", "metadata"]
        )
        
        # Display results
        for i, hit in enumerate(results[0]):
            player_name = hit.entity.get('player_name')
            position = hit.entity.get('position')
            score = hit.score
            metadata = hit.entity.get('metadata', {})
            
            # Extract key stats
            stats = metadata.get('stats', {})
            fantasy = metadata.get('fantasy', {})
            
            print(f"\n{i+1}. {player_name} ({position}) - Similarity: {score:.3f}")
            print(f"   Team: {metadata.get('team', 'N/A')}")
            print(f"   Stats: {stats.get('ppg', 0)} PPG, {stats.get('rpg', 0)} RPG, {stats.get('apg', 0)} APG")
            print(f"   3P%: {stats.get('three_pct', 0):.3f}, FT%: {stats.get('ft_pct', 0):.3f}")
            print(f"   Fantasy: ADP {fantasy.get('adp', 999)}, Keeper Round {fantasy.get('keeper_round_value', 15)}")
            
            # Show a snippet of the text description
            text = hit.entity.get('text', '')
            if text:
                print(f"   Description: {text[:150]}...")
    
    vector_db.disconnect()


def run_graph_queries():
    """Run Neo4j graph queries"""
    print("\n" + "="*60)
    print("SPORTSBRAIN DEMO QUERIES - GRAPH DATABASE")
    print("="*60)
    
    graph_db.connect()
    
    # Query 1: Team roster analysis
    print("\n1. Top Fantasy Players by Team:")
    with graph_db.driver.session() as session:
        result = session.run("""
            MATCH (p:Player)-[:PLAYS_FOR]->(t:Team)
            WHERE p.ppg > 20
            RETURN t.name as team, collect(p.name) as star_players, count(p) as count
            ORDER BY count DESC
            LIMIT 5
        """)
        for record in result:
            print(f"   {record['team']}: {record['count']} stars - {', '.join(record['star_players'][:3])}")
    
    # Query 2: Position distribution
    print("\n2. Player Distribution by Position:")
    with graph_db.driver.session() as session:
        result = session.run("""
            MATCH (p:Player)
            RETURN p.position as position, count(p) as count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"   {record['position']}: {record['count']} players")
    
    # Query 3: High-value keepers
    print("\n3. Best Keeper Values (Low ADP, High Performance):")
    with graph_db.driver.session() as session:
        result = session.run("""
            MATCH (p:Player)
            WHERE p.ppg > 15
            RETURN p.name as player, p.position as position, 
                   p.ppg as ppg, p.keeper_round_value as keeper_round
            ORDER BY p.keeper_round_value DESC, p.ppg DESC
            LIMIT 10
        """)
        for record in result:
            print(f"   {record['player']} ({record['position']}): {record['ppg']} PPG, Keep in Round {record['keeper_round']}")
    
    graph_db.disconnect()


def run_combined_analysis():
    """Combine vector and graph for advanced queries"""
    print("\n" + "="*60)
    print("SPORTSBRAIN DEMO - COMBINED VECTOR + GRAPH ANALYSIS")
    print("="*60)
    
    vector_db.connect()
    graph_db.connect()
    
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    collection.load()
    model = SentenceTransformer('all-mpnet-base-v2')
    
    # Find players similar to a query, then check their teams
    print("\n1. Finding Elite Scorers and Their Team Context:")
    
    query = "Elite scoring guards who can carry fantasy teams"
    query_embedding = model.encode(query, convert_to_tensor=False).tolist()
    
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_embedding],
        anns_field="vector",
        param=search_params,
        limit=5,
        output_fields=["player_name", "metadata"]
    )
    
    print(f"Query: '{query}'")
    print("-"*60)
    
    for hit in results[0]:
        player_name = hit.entity.get('player_name')
        metadata = hit.entity.get('metadata', {})
        
        # Get team context from graph
        with graph_db.driver.session() as session:
            result = session.run("""
                MATCH (p:Player {name: $name})-[:PLAYS_FOR]->(t:Team)
                OPTIONAL MATCH (t)<-[:PLAYS_FOR]-(teammate:Player)
                WHERE teammate.ppg > 15 AND teammate.name <> p.name
                RETURN t.name as team, collect(teammate.name) as other_stars
                LIMIT 1
            """, name=player_name)
            
            record = result.single()
            if record:
                team = record['team']
                teammates = record['other_stars']
                
                print(f"\n{player_name}:")
                print(f"  Team: {team}")
                print(f"  Stats: {metadata.get('stats', {}).get('ppg', 0)} PPG")
                print(f"  ADP: {metadata.get('fantasy', {}).get('adp', 999)}")
                print(f"  Other stars on team: {', '.join(teammates[:2]) if teammates else 'None'}")
                print(f"  Usage implications: {'Shared' if teammates else 'Primary option'}")
    
    vector_db.disconnect()
    graph_db.disconnect()


def show_keeper_analysis():
    """Specific analysis for keeper league decisions"""
    print("\n" + "="*60)
    print("SPORTSBRAIN DEMO - KEEPER LEAGUE ANALYSIS")
    print("="*60)
    
    vector_db.connect()
    collection = Collection(settings.MILVUS_PLAYERS_COLLECTION)
    
    # Direct query for specific players
    print("\nAnalyzing specific keeper decisions:")
    
    # Look for Ja Morant specifically
    expr = "player_name in ['Ja Morant', 'Jayson Tatum', 'LeBron James', 'Luka Dončić']"
    results = collection.query(
        expr=expr,
        output_fields=["player_name", "position", "metadata"]
    )
    
    for result in results:
        name = result['player_name']
        metadata = result.get('metadata', {})
        fantasy = metadata.get('fantasy', {})
        stats = metadata.get('stats', {})
        
        print(f"\n{name}:")
        print(f"  Position: {result['position']}")
        print(f"  2023-24 Stats: {stats.get('ppg', 0)} PPG, {stats.get('apg', 0)} APG, {stats.get('rpg', 0)} RPG")
        print(f"  ADP: {fantasy.get('adp', 999)}")
        print(f"  Keeper Round Value: {fantasy.get('keeper_round_value', 15)}")
        print(f"  Keeper Decision: {'KEEP' if fantasy.get('keeper_round_value', 15) <= 3 else 'PASS'} in round 3")
    
    vector_db.disconnect()


if __name__ == "__main__":
    print("SportsBrain Query Demonstration")
    print("With 470 NBA players loaded\n")
    
    try:
        # Run all demo queries
        run_vector_searches()
        run_graph_queries()
        run_combined_analysis()
        show_keeper_analysis()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()