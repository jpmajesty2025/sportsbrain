"""
Neo4j Aura graph database connection and operations
"""
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)


class GraphDB:
    """Wrapper for Neo4j Aura operations"""
    
    def __init__(self):
        self.driver = None
        self.graph_db = None
        # Get credentials from environment variables first (Railway), then settings (.env file)
        self.neo4j_uri = os.getenv("NEO4J_URI") or settings.NEO4J_URI
        self.neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j") or settings.NEO4J_USERNAME
        self.neo4j_password = os.getenv("NEO4J_PASSWORD") or settings.NEO4J_PASSWORD
        
    def connect(self):
        """Connect to Neo4j Aura"""
        try:
            if self.neo4j_uri and self.neo4j_password:
                self.driver = GraphDatabase.driver(
                    self.neo4j_uri, 
                    auth=(self.neo4j_username, self.neo4j_password)
                )
                
                # Test connection
                with self.driver.session() as session:
                    session.run("RETURN 1")
                
                # Initialize LangChain Neo4j wrapper for agent use
                self.graph_db = Neo4jGraph(
                    url=self.neo4j_uri,
                    username=self.neo4j_username,
                    password=self.neo4j_password
                )
                
                logger.info("Connected to Neo4j Aura")
            else:
                logger.warning("No Neo4j credentials provided")
                
        except Exception as e:
            logger.error(f"Failed to connect to graph database: {e}")
            raise
            
    def create_player_node(self, player_data: Dict[str, Any]):
        """Create or update a player node"""
        with self.driver.session() as session:
            query = """
            MERGE (p:Player {id: $id})
            SET p.name = $name,
                p.position = $position,
                p.team = $team,
                p.age = $age,
                p.stats_2023_24 = $stats
            RETURN p
            """
            return session.run(query, **player_data)
            
    def create_team_node(self, team_data: Dict[str, Any]):
        """Create or update a team node"""
        with self.driver.session() as session:
            query = """
            MERGE (t:Team {name: $name})
            SET t.conference = $conference,
                t.division = $division,
                t.coach = $coach
            RETURN t
            """
            return session.run(query, **team_data)
            
    def create_trade_relationship(self, trade_data: Dict[str, Any]):
        """Create trade relationships"""
        with self.driver.session() as session:
            query = """
            MATCH (p:Player {id: $player_id})
            MATCH (from:Team {name: $from_team})
            MATCH (to:Team {name: $to_team})
            CREATE (p)-[t:TRADED_FROM {date: $date}]->(from)
            CREATE (p)-[j:JOINED {date: $date}]->(to)
            RETURN p, t, j
            """
            return session.run(query, **trade_data)
            
    def find_similar_players(self, player_id: str, limit: int = 5):
        """Find players with similar stats patterns"""
        with self.driver.session() as session:
            query = """
            MATCH (p1:Player {id: $player_id})
            MATCH (p2:Player)
            WHERE p1 <> p2 AND p1.position = p2.position
            RETURN p2
            ORDER BY abs(p1.stats_2023_24.ppg - p2.stats_2023_24.ppg) +
                     abs(p1.stats_2023_24.rpg - p2.stats_2023_24.rpg) +
                     abs(p1.stats_2023_24.apg - p2.stats_2023_24.apg)
            LIMIT $limit
            """
            return session.run(query, player_id=player_id, limit=limit)
            
    def get_team_roster_changes(self, team_name: str):
        """Get all roster changes for a team"""
        with self.driver.session() as session:
            query = """
            MATCH (t:Team {name: $team_name})
            OPTIONAL MATCH (t)<-[j:JOINED]-(new:Player)
            OPTIONAL MATCH (t)<-[l:TRADED_FROM]-(lost:Player)
            RETURN t, 
                   collect(DISTINCT {player: new.name, action: 'joined', date: j.date}) as additions,
                   collect(DISTINCT {player: lost.name, action: 'left', date: l.date}) as departures
            """
            return session.run(query, team_name=team_name)
            
    def disconnect(self):
        """Disconnect from Neo4j"""
        if self.driver:
            self.driver.close()


# Singleton instance
graph_db = GraphDB()


def get_graph_db() -> GraphDB:
    """Get graph database instance"""
    return graph_db