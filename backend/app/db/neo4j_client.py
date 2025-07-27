from neo4j import GraphDatabase
from app.core.config import settings

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
    
    def close(self):
        self.driver.close()
    
    def create_player_node(self, player_id: int, name: str, position: str, team: str):
        with self.driver.session() as session:
            session.run(
                "MERGE (p:Player {id: $player_id}) "
                "SET p.name = $name, p.position = $position, p.team = $team",
                player_id=player_id, name=name, position=position, team=team
            )
    
    def create_game_node(self, game_id: int, date: str, home_team: str, away_team: str):
        with self.driver.session() as session:
            session.run(
                "MERGE (g:Game {id: $game_id}) "
                "SET g.date = $date, g.home_team = $home_team, g.away_team = $away_team",
                game_id=game_id, date=date, home_team=home_team, away_team=away_team
            )
    
    def create_played_in_relationship(self, player_id: int, game_id: int, stats: dict):
        with self.driver.session() as session:
            session.run(
                "MATCH (p:Player {id: $player_id}) "
                "MATCH (g:Game {id: $game_id}) "
                "MERGE (p)-[r:PLAYED_IN]->(g) "
                "SET r += $stats",
                player_id=player_id, game_id=game_id, stats=stats
            )

neo4j_client = Neo4jClient()