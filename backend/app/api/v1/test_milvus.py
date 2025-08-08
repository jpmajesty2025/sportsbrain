"""
Test endpoints for Milvus connectivity and operations
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.db.vector_db import vector_db
from pymilvus import utility, Collection
import mmh3
import time
import random

router = APIRouter()


@router.get("/test/milvus/connection")
async def test_milvus_connection() -> Dict[str, Any]:
    """Test basic Milvus connection"""
    try:
        vector_db.connect()
        
        # List all collections
        collections = utility.list_collections()
        
        return {
            "status": "connected",
            "collections": collections,
            "host": vector_db.milvus_host[:30] + "..." if vector_db.milvus_host else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")
    finally:
        vector_db.disconnect()


@router.get("/test/milvus/collection/{collection_name}")
async def test_collection_info(collection_name: str) -> Dict[str, Any]:
    """Get collection information"""
    try:
        vector_db.connect()
        
        # Check if collection exists
        if collection_name not in utility.list_collections():
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        # Get collection
        collection = Collection(name=collection_name)
        collection.load()
        
        # Get collection info
        info = {
            "name": collection_name,
            "description": collection.description,
            "num_entities": collection.num_entities,
            "schema": {
                "fields": [
                    {
                        "name": field.name,
                        "type": str(field.dtype),
                        "is_primary": field.is_primary,
                        "max_length": getattr(field, 'max_length', None),
                        "dim": getattr(field, 'dim', None)
                    }
                    for field in collection.schema.fields
                ]
            }
        }
        
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        vector_db.disconnect()


@router.post("/test/milvus/insert")
async def test_insert_data() -> Dict[str, Any]:
    """Insert test data into players collection"""
    try:
        vector_db.connect()
        
        collection_name = "sportsbrain_players"
        if collection_name not in utility.list_collections():
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        collection = Collection(name=collection_name)
        
        # Create test data
        test_player = {
            "name": "Test Player",
            "position": "PG",
            "text": "Test Player is a point guard known for excellent court vision and three-point shooting. Averaging 20 points and 8 assists per game."
        }
        
        # Generate primary key using mmh3
        key_string = f"{test_player['name']}_{int(time.time())}"
        primary_key = mmh3.hash(key_string, signed=False)
        
        # Create random vector (in real app, this would come from embedding model)
        vector = [random.random() for _ in range(768)]
        
        # Prepare data for insertion
        data = [
            [primary_key],  # primary_key
            [vector],  # vector
            [test_player['text']],  # text
            [test_player['name']],  # player_name
            [test_player['position']],  # position
            [{
                "team": "Test Team",
                "season": "2023-24",
                "stats": {"ppg": 20.0, "apg": 8.0},
                "test_data": True
            }],  # metadata
            [int(time.time())]  # created_at
        ]
        
        # Insert data
        insert_result = collection.insert(data)
        
        # Flush to ensure data is persisted
        collection.flush()
        
        return {
            "status": "success",
            "inserted_count": len(insert_result.primary_keys),
            "primary_key": primary_key,
            "collection_count": collection.num_entities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        vector_db.disconnect()


@router.post("/test/milvus/search")
async def test_search() -> Dict[str, Any]:
    """Test vector search in players collection"""
    try:
        vector_db.connect()
        
        collection_name = "sportsbrain_players"
        if collection_name not in utility.list_collections():
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        collection = Collection(name=collection_name)
        collection.load()
        
        # Create random query vector (in real app, this would be from query embedding)
        query_vector = [random.random() for _ in range(768)]
        
        # Search parameters
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }
        
        # Perform search
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=5,
            output_fields=["player_name", "position", "text", "metadata"]
        )
        
        # Format results
        formatted_results = []
        for hit in results[0]:
            formatted_results.append({
                "id": hit.id,
                "distance": hit.distance,
                "player_name": hit.entity.get("player_name"),
                "position": hit.entity.get("position"),
                "text": hit.entity.get("text")[:100] + "...",
                "metadata": hit.entity.get("metadata")
            })
        
        return {
            "status": "success",
            "num_results": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        vector_db.disconnect()


@router.delete("/test/milvus/cleanup")
async def cleanup_test_data() -> Dict[str, Any]:
    """Remove test data from collections"""
    try:
        vector_db.connect()
        
        collection_name = "sportsbrain_players"
        if collection_name not in utility.list_collections():
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        collection = Collection(name=collection_name)
        
        # Delete test data using expression
        expr = 'metadata["test_data"] == true'
        collection.delete(expr)
        
        return {
            "status": "success",
            "message": "Test data cleaned up",
            "remaining_entities": collection.num_entities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        vector_db.disconnect()