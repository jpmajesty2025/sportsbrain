"""
Load enhanced data into Neo4j including injuries, performances, and relationships
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from backend/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

from app.db.graph_db import graph_db
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jDataLoader:
    """Load additional data into Neo4j graph database"""
    
    def __init__(self):
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data'
        )
        self.stats = {
            'injuries_created': 0,
            'performances_created': 0,
            'trades_created': 0,
            'relationships_created': 0
        }
    
    def load_injury_data(self) -> int:
        """Load injury history into Neo4j"""
        logger.info("\n" + "="*60)
        logger.info("Loading Injury Data into Neo4j")
        logger.info("="*60)
        
        # Load injury data
        injury_file = os.path.join(self.data_dir, 'injuries', 'injury_history_2024_25.json')
        
        if not os.path.exists(injury_file):
            logger.error(f"Injury file not found: {injury_file}")
            return 0
        
        with open(injury_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            injuries = data.get('injuries', [])
        
        logger.info(f"Found {len(injuries)} injury records to load")
        
        try:
            graph_db.connect()
            
            # Create Injury nodes and relationships in batches
            batch_size = 50
            for i in range(0, len(injuries), batch_size):
                batch = injuries[i:i+batch_size]
                
                with graph_db.driver.session() as session:
                    # Create injury nodes and relationships
                    query = """
                    UNWIND $injuries as injury
                    MATCH (p:Player {name: injury.player_name})
                    CREATE (inj:Injury {
                        injury_id: injury.injury_id,
                        type: injury.injury_type,
                        severity: injury.severity,
                        injury_date: injury.injury_date,
                        return_date: injury.return_date,
                        games_missed: injury.games_missed,
                        season: injury.season,
                        description: injury.description,
                        fantasy_impact: injury.fantasy_impact
                    })
                    CREATE (p)-[:HAD_INJURY {
                        date: injury.injury_date,
                        games_missed: injury.games_missed
                    }]->(inj)
                    RETURN count(inj) as created
                    """
                    
                    result = session.run(query, injuries=batch)
                    created = result.single()['created']
                    self.stats['injuries_created'] += created
                    logger.info(f"  Batch {i//batch_size + 1}: Created {created} injury nodes")
            
            graph_db.disconnect()
            logger.info(f"Total injuries loaded: {self.stats['injuries_created']}")
            
        except Exception as e:
            logger.error(f"Error loading injuries: {e}")
            graph_db.disconnect()
        
        return self.stats['injuries_created']
    
    def load_performance_data(self) -> int:
        """Load player performance data into Neo4j"""
        logger.info("\n" + "="*60)
        logger.info("Loading Performance Data into Neo4j")
        logger.info("="*60)
        
        # We would load from real NBA data if we had fetched it
        # For now, create sample performance nodes
        
        try:
            graph_db.connect()
            
            # Create sample high-performance game nodes
            sample_performances = [
                {
                    'player_name': 'Nikola Jokić',
                    'game_date': '2024-01-15',
                    'opponent': 'LAL',
                    'points': 32,
                    'rebounds': 12,
                    'assists': 15,
                    'fantasy_points': 67.5
                },
                {
                    'player_name': 'Giannis Antetokounmpo',
                    'game_date': '2024-01-20',
                    'opponent': 'BOS',
                    'points': 42,
                    'rebounds': 12,
                    'assists': 6,
                    'fantasy_points': 64.2
                },
                {
                    'player_name': 'Luka Dončić',
                    'game_date': '2024-02-01',
                    'opponent': 'GSW',
                    'points': 39,
                    'rebounds': 8,
                    'assists': 12,
                    'fantasy_points': 63.1
                },
                {
                    'player_name': 'Jayson Tatum',
                    'game_date': '2024-02-10',
                    'opponent': 'MIA',
                    'points': 41,
                    'rebounds': 11,
                    'assists': 5,
                    'fantasy_points': 58.7
                },
                {
                    'player_name': 'Joel Embiid',
                    'game_date': '2024-01-25',
                    'opponent': 'DEN',
                    'points': 38,
                    'rebounds': 14,
                    'assists': 3,
                    'fantasy_points': 59.3
                }
            ]
            
            with graph_db.driver.session() as session:
                query = """
                UNWIND $performances as perf
                MATCH (p:Player {name: perf.player_name})
                CREATE (g:Performance {
                    game_date: perf.game_date,
                    opponent: perf.opponent,
                    points: perf.points,
                    rebounds: perf.rebounds,
                    assists: perf.assists,
                    fantasy_points: perf.fantasy_points
                })
                CREATE (p)-[:HAD_PERFORMANCE {
                    date: perf.game_date,
                    fantasy_points: perf.fantasy_points
                }]->(g)
                RETURN count(g) as created
                """
                
                result = session.run(query, performances=sample_performances)
                created = result.single()['created']
                self.stats['performances_created'] = created
                logger.info(f"Created {created} performance nodes")
            
            graph_db.disconnect()
            
        except Exception as e:
            logger.error(f"Error loading performances: {e}")
            graph_db.disconnect()
        
        return self.stats['performances_created']
    
    def load_trade_data(self) -> int:
        """Load trade data into Neo4j"""
        logger.info("\n" + "="*60)
        logger.info("Loading Trade Data into Neo4j")
        logger.info("="*60)
        
        # Load trade documents
        trade_file = os.path.join(self.data_dir, 'mock_trades', 'trade_documents_2024_25.json')
        
        if not os.path.exists(trade_file):
            logger.error(f"Trade file not found: {trade_file}")
            return 0
        
        with open(trade_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            trades = data.get('documents', [])
        
        # Extract unique base trades
        unique_trades = {}
        for doc in trades:
            trade_id = doc.get('trade_id')
            if trade_id not in unique_trades:
                unique_trades[trade_id] = {
                    'trade_id': trade_id,
                    'date': doc.get('trade_date'),
                    'headline': doc.get('headline'),
                    'teams': doc.get('teams_involved', [])
                }
        
        logger.info(f"Found {len(unique_trades)} unique trades to load")
        
        try:
            graph_db.connect()
            
            with graph_db.driver.session() as session:
                # Create Trade nodes
                query = """
                UNWIND $trades as trade
                CREATE (t:Trade {
                    trade_id: trade.trade_id,
                    date: trade.date,
                    headline: trade.headline,
                    teams: trade.teams
                })
                RETURN count(t) as created
                """
                
                result = session.run(query, trades=list(unique_trades.values()))
                created = result.single()['created']
                self.stats['trades_created'] = created
                logger.info(f"Created {created} trade nodes")
            
            graph_db.disconnect()
            
        except Exception as e:
            logger.error(f"Error loading trades: {e}")
            graph_db.disconnect()
        
        return self.stats['trades_created']
    
    def create_similarity_relationships(self) -> int:
        """Create SIMILAR_TO relationships between players based on stats"""
        logger.info("\n" + "="*60)
        logger.info("Creating Player Similarity Relationships")
        logger.info("="*60)
        
        try:
            graph_db.connect()
            
            with graph_db.driver.session() as session:
                # Create similarity relationships based on position and stats
                # This is a simplified version - in production would use vector similarity
                
                queries = [
                    # Similar guards
                    """
                    MATCH (p1:Player), (p2:Player)
                    WHERE p1.name IN ['Stephen Curry', 'Damian Lillard'] 
                    AND p2.name IN ['Trae Young', 'Kyrie Irving']
                    AND p1 <> p2
                    AND NOT EXISTS((p1)-[:SIMILAR_TO]-(p2))
                    CREATE (p1)-[:SIMILAR_TO {similarity_score: 0.85}]->(p2)
                    RETURN count(*) as created
                    """,
                    
                    # Similar forwards
                    """
                    MATCH (p1:Player), (p2:Player)
                    WHERE p1.name IN ['Jayson Tatum', 'Jaylen Brown'] 
                    AND p2.name IN ['Paul George', 'Kawhi Leonard']
                    AND p1 <> p2
                    AND NOT EXISTS((p1)-[:SIMILAR_TO]-(p2))
                    CREATE (p1)-[:SIMILAR_TO {similarity_score: 0.82}]->(p2)
                    RETURN count(*) as created
                    """,
                    
                    # Similar bigs
                    """
                    MATCH (p1:Player), (p2:Player)
                    WHERE p1.name IN ['Nikola Jokić', 'Domantas Sabonis'] 
                    AND p2.name IN ['Alperen Sengun', 'Bam Adebayo']
                    AND p1 <> p2
                    AND NOT EXISTS((p1)-[:SIMILAR_TO]-(p2))
                    CREATE (p1)-[:SIMILAR_TO {similarity_score: 0.79}]->(p2)
                    RETURN count(*) as created
                    """,
                    
                    # Young players similar to stars
                    """
                    MATCH (p1:Player), (p2:Player)
                    WHERE p1.name = 'Paolo Banchero' 
                    AND p2.name = 'Jayson Tatum'
                    AND NOT EXISTS((p1)-[:SIMILAR_TO]-(p2))
                    CREATE (p1)-[:SIMILAR_TO {
                        similarity_score: 0.76,
                        note: 'Similar playstyle and trajectory'
                    }]->(p2)
                    RETURN count(*) as created
                    """
                ]
                
                total_created = 0
                for query in queries:
                    result = session.run(query)
                    created = result.single()['created']
                    total_created += created
                
                logger.info(f"Created {total_created} similarity relationships")
                self.stats['relationships_created'] += total_created
            
            graph_db.disconnect()
            
        except Exception as e:
            logger.error(f"Error creating similarity relationships: {e}")
            graph_db.disconnect()
        
        return self.stats['relationships_created']
    
    def create_trade_impact_relationships(self) -> int:
        """Create IMPACTED_BY relationships between players and trades"""
        logger.info("\n" + "="*60)
        logger.info("Creating Trade Impact Relationships")
        logger.info("="*60)
        
        try:
            graph_db.connect()
            
            with graph_db.driver.session() as session:
                # Create relationships showing how trades impact players
                query = """
                // Damian Lillard trade impacts
                MATCH (t:Trade {trade_id: 'trade_2024_001'})
                MATCH (p:Player)
                WHERE p.name IN ['Damian Lillard', 'Tyler Herro', 'Jimmy Butler', 'Bam Adebayo']
                CREATE (p)-[:IMPACTED_BY {
                    impact_type: CASE p.name
                        WHEN 'Damian Lillard' THEN 'positive_usage'
                        WHEN 'Tyler Herro' THEN 'increased_role'
                        WHEN 'Jimmy Butler' THEN 'decreased_usage'
                        ELSE 'neutral'
                    END,
                    fantasy_impact: CASE p.name
                        WHEN 'Damian Lillard' THEN 0.05
                        WHEN 'Tyler Herro' THEN 0.15
                        WHEN 'Jimmy Butler' THEN -0.10
                        ELSE 0.0
                    END
                }]->(t)
                RETURN count(*) as created
                """
                
                result = session.run(query)
                created = result.single()['created'] if result.single() else 0
                
                logger.info(f"Created {created} trade impact relationships")
                self.stats['relationships_created'] += created
            
            graph_db.disconnect()
            
        except Exception as e:
            logger.error(f"Error creating trade impact relationships: {e}")
            graph_db.disconnect()
        
        return self.stats['relationships_created']
    
    def verify_graph_data(self):
        """Verify the graph data was loaded correctly"""
        logger.info("\n" + "="*60)
        logger.info("Verifying Neo4j Graph Data")
        logger.info("="*60)
        
        try:
            graph_db.connect()
            
            with graph_db.driver.session() as session:
                # Count all node types
                node_query = """
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
                """
                
                result = session.run(node_query)
                logger.info("\nNode counts:")
                for record in result:
                    logger.info(f"  {record['label']}: {record['count']}")
                
                # Count all relationship types
                rel_query = """
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
                """
                
                result = session.run(rel_query)
                logger.info("\nRelationship counts:")
                for record in result:
                    logger.info(f"  {record['type']}: {record['count']}")
                
                # Sample multi-hop query
                sample_query = """
                MATCH (p:Player {name: 'Damian Lillard'})-[:IMPACTED_BY]->(t:Trade)
                RETURN p.name as player, t.headline as trade
                LIMIT 1
                """
                
                result = session.run(sample_query)
                for record in result:
                    logger.info(f"\nSample query result:")
                    logger.info(f"  {record['player']} impacted by: {record['trade']}")
            
            graph_db.disconnect()
            
        except Exception as e:
            logger.error(f"Error verifying graph data: {e}")
            graph_db.disconnect()
    
    def get_loading_summary(self) -> Dict:
        """Get summary of loading operation"""
        return {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'success': sum(self.stats.values()) > 0
        }


def main():
    """Main function to load all enhanced data into Neo4j"""
    print("="*60)
    print("NEO4J ENHANCED DATA LOADING")
    print("="*60)
    
    loader = Neo4jDataLoader()
    
    # Load injury data
    print("\n[1/5] Loading injury data...")
    injuries = loader.load_injury_data()
    
    # Load performance data
    print("\n[2/5] Loading performance data...")
    performances = loader.load_performance_data()
    
    # Load trade data
    print("\n[3/5] Loading trade data...")
    trades = loader.load_trade_data()
    
    # Create similarity relationships
    print("\n[4/5] Creating similarity relationships...")
    similarities = loader.create_similarity_relationships()
    
    # Create trade impact relationships
    print("\n[5/5] Creating trade impact relationships...")
    impacts = loader.create_trade_impact_relationships()
    
    # Verify the data
    loader.verify_graph_data()
    
    # Print summary
    summary = loader.get_loading_summary()
    print("\n" + "="*60)
    print("LOADING COMPLETE")
    print("="*60)
    print(f"Injuries loaded: {summary['stats']['injuries_created']}")
    print(f"Performances loaded: {summary['stats']['performances_created']}")
    print(f"Trades loaded: {summary['stats']['trades_created']}")
    print(f"Relationships created: {summary['stats']['relationships_created']}")
    print("="*60)


if __name__ == "__main__":
    main()