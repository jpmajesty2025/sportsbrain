"""
Test endpoints for Neo4j connectivity and operations
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.db.graph_db import graph_db
import time

router = APIRouter()


@router.get("/connection")
async def check_neo4j_connection() -> Dict[str, Any]:
    """Test basic Neo4j connection"""
    try:
        # Get connection details (without exposing password)
        uri = graph_db.neo4j_uri
        username = graph_db.neo4j_username
        has_password = bool(graph_db.neo4j_password)
        
        # Try to connect
        graph_db.connect()
        
        # If successful, get some basic info
        with graph_db.driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions")
            components = [{"name": record["name"], "version": record["versions"][0]} 
                         for record in result]
        
        return {
            "status": "connected",
            "uri": uri[:30] + "..." if uri else None,
            "username": username,
            "has_password": has_password,
            "components": components
        }
    except Exception as e:
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "uri": graph_db.neo4j_uri[:30] + "..." if graph_db.neo4j_uri else None,
            "has_credentials": bool(graph_db.neo4j_uri and graph_db.neo4j_password)
        }
        raise HTTPException(status_code=500, detail=error_details)
    finally:
        graph_db.disconnect()


@router.get("/stats")
async def get_database_stats() -> Dict[str, Any]:
    """Get Neo4j database statistics"""
    try:
        graph_db.connect()
        
        with graph_db.driver.session() as session:
            # Count nodes by label
            node_counts = {}
            labels_result = session.run("CALL db.labels()")
            for record in labels_result:
                label = record[0]
                count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = count_result.single()["count"]
                node_counts[label] = count
            
            # Count relationships
            rel_counts = {}
            rels_result = session.run("CALL db.relationshipTypes()")
            for record in rels_result:
                rel_type = record[0]
                count_result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
                count = count_result.single()["count"]
                rel_counts[rel_type] = count
        
        return {
            "node_counts": node_counts,
            "relationship_counts": rel_counts,
            "total_nodes": sum(node_counts.values()),
            "total_relationships": sum(rel_counts.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        graph_db.disconnect()


@router.post("/test-data")
async def create_test_data() -> Dict[str, Any]:
    """Create test nodes and relationships"""
    try:
        graph_db.connect()
        
        # Create test player
        test_player = {
            "id": f"test_player_{int(time.time())}",
            "name": "Test Player",
            "position": "PG",
            "team": "Test Team",
            "age": 25,
            "stats": {"ppg": 20.0, "apg": 8.0, "rpg": 4.0}
        }
        
        graph_db.create_player_node(test_player)
        
        # Create test team
        test_team = {
            "name": "Test Team",
            "conference": "Test",
            "division": "Test",
            "coach": "Test Coach"
        }
        
        graph_db.create_team_node(test_team)
        
        # Create relationship
        with graph_db.driver.session() as session:
            query = """
            MATCH (p:Player {id: $player_id})
            MATCH (t:Team {name: $team_name})
            MERGE (p)-[r:PLAYS_FOR]->(t)
            RETURN p, r, t
            """
            result = session.run(query, player_id=test_player["id"], team_name="Test Team")
            
        return {
            "status": "success",
            "message": "Test data created",
            "player_id": test_player["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        graph_db.disconnect()


@router.delete("/cleanup")
async def cleanup_test_data() -> Dict[str, Any]:
    """Remove test data"""
    try:
        graph_db.connect()
        
        with graph_db.driver.session() as session:
            # Delete test nodes and relationships
            query = """
            MATCH (n)
            WHERE n.name STARTS WITH 'Test'
            DETACH DELETE n
            RETURN count(n) as deleted_count
            """
            result = session.run(query)
            deleted_count = result.single()["deleted_count"]
        
        return {
            "status": "success",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        graph_db.disconnect()