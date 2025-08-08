"""
Milvus/Zilliz Cloud vector database connection and operations
"""
from typing import List, Dict, Any, Optional
from pymilvus import connections, Collection, utility
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)


class VectorDB:
    """Wrapper for Milvus/Zilliz Cloud operations"""
    
    def __init__(self):
        # Collection names
        self.players_collection = os.getenv("MILVUS_PLAYERS_COLLECTION", settings.MILVUS_PLAYERS_COLLECTION)
        self.strategies_collection = os.getenv("MILVUS_DRAFT_STRATEGIES_COLLECTION", settings.MILVUS_DRAFT_STRATEGIES_COLLECTION)
        self.trades_collection = os.getenv("MILVUS_TRADE_NEWS_COLLECTION", settings.MILVUS_TRADE_NEWS_COLLECTION)
        
        # Store active collections
        self.collections: Dict[str, Optional[Collection]] = {}
        
        # Get credentials from environment variables first (Railway), then settings (.env file)
        self.milvus_host = os.getenv("MILVUS_HOST") or settings.MILVUS_HOST
        self.milvus_token = os.getenv("MILVUS_TOKEN") or settings.MILVUS_TOKEN
        
    def connect(self):
        """Connect to Zilliz Cloud"""
        try:
            if self.milvus_host and self.milvus_token:
                # Connect to Zilliz Cloud
                connections.connect(
                    uri=self.milvus_host,
                    token=self.milvus_token
                )
                logger.info("Connected to Zilliz Cloud")
            else:
                # Fallback to local Milvus for development
                logger.warning("No Zilliz Cloud credentials, attempting local connection")
                connections.connect(
                    alias="default",
                    host="localhost",
                    port="19530"
                )
                
        except Exception as e:
            logger.error(f"Failed to connect to vector database: {e}")
            raise
            
    def create_collection(self, dim: int = 768):
        """Create collection for player embeddings"""
        # Collection schema will be implemented based on embedding model
        pass
        
    def insert_embeddings(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]):
        """Insert player embeddings with metadata"""
        pass
        
    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar players/content"""
        pass
        
    def disconnect(self):
        """Disconnect from Milvus"""
        connections.disconnect("default")


# Singleton instance
vector_db = VectorDB()


def get_vector_db() -> VectorDB:
    """Get vector database instance"""
    return vector_db