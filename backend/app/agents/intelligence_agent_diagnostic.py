"""Diagnostic version of Intelligence Agent to debug Milvus issues"""

import logging
import time
from typing import Dict, Any, List, Optional
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
from app.services.reranker_service import ReRankerService

logger = logging.getLogger(__name__)

class DiagnosticIntelligenceAgent(IntelligenceAgentEnhanced):
    """Diagnostic version with extensive logging for Milvus debugging"""
    
    def __init__(self):
        super().__init__()
        self.reranker = None
        self._init_reranker()
        # Initialize embedding model for Milvus searches
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # 768 dims to match Milvus
        logger.info("DIAGNOSTIC: Intelligence Agent initialized with embedding model")
        
    def _init_reranker(self):
        """Initialize reranker (lazy loading)"""
        try:
            self.reranker = ReRankerService()
            logger.info("DIAGNOSTIC: Reranker initialized successfully")
        except Exception as e:
            logger.warning(f"DIAGNOSTIC: Could not initialize reranker: {e}")
            self.reranker = None
    
    def _find_sleeper_candidates_enhanced(self, criteria: str = "") -> str:
        """Override to add diagnostic logging for Milvus searches"""
        logger.info(f"DIAGNOSTIC: Starting sleeper search with criteria: {criteria}")
        
        # First get SQL results
        sql_start = time.time()
        sql_response = super()._find_sleeper_candidates_enhanced(criteria)
        logger.info(f"DIAGNOSTIC: SQL query completed in {time.time() - sql_start:.2f}s")
        
        # Check if this is a "players like X" query that might benefit from vector search
        if "like" in criteria.lower():
            logger.info("DIAGNOSTIC: Detected 'like' query - attempting Milvus enhancement")
            
            try:
                from pymilvus import connections, Collection, utility
                from app.core.config import settings
                
                # Log Milvus config status
                logger.info(f"DIAGNOSTIC: MILVUS_HOST present: {bool(settings.MILVUS_HOST)}")
                logger.info(f"DIAGNOSTIC: MILVUS_TOKEN present: {bool(settings.MILVUS_TOKEN)}")
                
                if not settings.MILVUS_HOST or not settings.MILVUS_TOKEN:
                    logger.warning("DIAGNOSTIC: Milvus credentials missing - skipping vector search")
                    return sql_response
                
                # Try to connect
                logger.info("DIAGNOSTIC: Attempting Milvus connection...")
                connections.connect(
                    alias="diagnostic",
                    uri=settings.MILVUS_HOST,
                    token=settings.MILVUS_TOKEN
                )
                logger.info("DIAGNOSTIC: Milvus connection successful")
                
                # List collections
                collections = utility.list_collections(using="diagnostic")
                logger.info(f"DIAGNOSTIC: Available collections: {collections}")
                
                if "sportsbrain_players" not in collections:
                    logger.warning("DIAGNOSTIC: sportsbrain_players collection not found!")
                    connections.disconnect("diagnostic")
                    return sql_response
                
                # Load collection
                collection = Collection("sportsbrain_players", using="diagnostic")
                collection.load()
                logger.info(f"DIAGNOSTIC: Collection loaded. Schema: {collection.schema}")
                logger.info(f"DIAGNOSTIC: Collection has {collection.num_entities} entities")
                
                # Create embedding
                query = f"players similar to {criteria} sleepers fantasy basketball"
                logger.info(f"DIAGNOSTIC: Creating embedding for query: {query}")
                query_embedding = self.embedding_model.encode(query).tolist()
                logger.info(f"DIAGNOSTIC: Embedding created, dimension: {len(query_embedding)}")
                
                # Search
                search_params = {
                    "metric_type": "IP",
                    "params": {"nprobe": 10}
                }
                
                logger.info("DIAGNOSTIC: Executing Milvus search...")
                search_start = time.time()
                results = collection.search(
                    data=[query_embedding],
                    anns_field="vector",
                    param=search_params,
                    limit=10,
                    output_fields=["text", "metadata"]
                )
                logger.info(f"DIAGNOSTIC: Search completed in {time.time() - search_start:.2f}s")
                
                if results and results[0]:
                    logger.info(f"DIAGNOSTIC: Found {len(results[0])} results from Milvus")
                    
                    # Log first result details
                    if len(results[0]) > 0:
                        first_hit = results[0][0]
                        logger.info(f"DIAGNOSTIC: First hit score: {first_hit.score}")
                        text_field = first_hit.entity.get('text')
                        logger.info(f"DIAGNOSTIC: First hit has text: {bool(text_field)}")
                        if text_field:
                            logger.info(f"DIAGNOSTIC: Text preview: {str(text_field)[:100]}...")
                    
                    # Only proceed with reranking if we have results
                    if self.reranker and len(results[0]) > 1:
                        logger.info("DIAGNOSTIC: Proceeding with reranking...")
                        # [Rest of reranking logic would go here]
                    else:
                        logger.info(f"DIAGNOSTIC: Skipping reranking (reranker={bool(self.reranker)}, results={len(results[0])})")
                else:
                    logger.warning("DIAGNOSTIC: Milvus search returned no results!")
                
                connections.disconnect("diagnostic")
                
            except Exception as e:
                logger.error(f"DIAGNOSTIC: Milvus operation failed: {e}", exc_info=True)
                try:
                    connections.disconnect("diagnostic")
                except:
                    pass
        else:
            logger.info("DIAGNOSTIC: Not a 'like' query - skipping Milvus")
        
        return sql_response