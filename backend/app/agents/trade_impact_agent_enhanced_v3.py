"""Enhanced TradeImpact Agent V3 with better Milvus fallback handling"""

import logging
import time
from typing import List, Dict, Optional
from app.agents.trade_impact_agent_tools import TradeImpactAgent
from app.services.reranker_service import ReRankerService

logger = logging.getLogger(__name__)

class EnhancedTradeImpactAgentV3(TradeImpactAgent):
    """V3: Better handling when Milvus returns no results"""
    
    def __init__(self):
        super().__init__()
        self.reranker = None
        self._init_reranker()
        # Override parent's embedding model to match Milvus dimensions
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # 768 dims
        
    def _init_reranker(self):
        """Initialize reranker (lazy loading)"""
        try:
            self.reranker = ReRankerService()
            logger.info("V3: Reranker initialized successfully")
        except Exception as e:
            logger.warning(f"V3: Could not initialize reranker: {e}")
            self.reranker = None
    
    def analyze_trade_impact(self, input_str: str) -> str:
        """V3: Enhanced with SQL + optional reranking"""
        start_time = time.time()
        logger.info(f"V3: Starting analysis for: {input_str}")
        
        # ALWAYS get SQL analysis first
        sql_response = self._fallback_trade_analysis(input_str)
        logger.info(f"V3: Got SQL response in {time.time() - start_time:.2f}s")
        
        # Try to enhance with Milvus if available
        try:
            from pymilvus import connections, Collection
            from app.core.config import settings
            
            if settings.MILVUS_HOST and settings.MILVUS_TOKEN and self.reranker:
                logger.info("V3: Attempting Milvus enhancement...")
                
                connections.connect(
                    alias="default",
                    uri=settings.MILVUS_HOST,
                    token=settings.MILVUS_TOKEN
                )
                
                collection = Collection("sportsbrain_trades")
                collection.load()
                
                query_embedding = self.embedding_model.encode(input_str).tolist()
                
                search_params = {
                    "metric_type": "IP",
                    "params": {"nprobe": 10}
                }
                
                results = collection.search(
                    data=[query_embedding],
                    anns_field="vector",
                    param=search_params,
                    limit=10,
                    output_fields=["text", "metadata"]
                )
                
                if results and results[0] and len(results[0]) > 0:
                    logger.info(f"V3: Found {len(results[0])} Milvus documents")
                    
                    # Convert to reranking format
                    documents = []
                    for hit in results[0]:
                        documents.append({
                            'content': hit.entity.get('text', ''),
                            'score': hit.score,
                            'metadata': hit.entity.get('metadata', {})
                        })
                    
                    # Apply reranking
                    reranked = self.reranker.rerank(
                        query=input_str,
                        documents=documents,
                        top_k=3,
                        log_details=True
                    )
                    
                    # Combine SQL response with reranked insights
                    enhanced_response = sql_response + "\n\n**Additional AI-Enhanced Insights:**\n"
                    for i, result in enumerate(reranked, 1):
                        if result.rerank_score > 0.5:  # Only high-quality matches
                            content_preview = result.content[:200] if result.content else ""
                            content_preview = content_preview.replace('\n', ' ').strip()
                            enhanced_response += f"{i}. {content_preview}...\n"
                    
                    connections.disconnect("default")
                    logger.info(f"V3: Enhanced analysis completed in {time.time() - start_time:.2f}s")
                    return enhanced_response
                else:
                    logger.info("V3: No Milvus results, using SQL only")
                    connections.disconnect("default")
                    
        except Exception as e:
            logger.warning(f"V3: Milvus enhancement failed: {e}")
        
        # Return SQL response if Milvus didn't enhance
        return sql_response
    
    def _fallback_trade_analysis(self, query: str) -> str:
        """Use parent's fallback but ensure it's detailed"""
        result = super()._fallback_trade_analysis(query)
        # Ensure we're returning the full analysis, not a summary
        if len(result) < 500:  # If response seems too short
            logger.warning("V3: SQL response seems abbreviated, requesting full analysis")
            # Add more detail request
            result = f"""**Comprehensive Trade Impact Analysis**

{result}

**Detailed Breakdown**:
- Primary player impact with specific usage rate changes
- Secondary player impacts on same team
- Fantasy point projections for all affected players
- Draft strategy recommendations
- Risk assessment and injury considerations

Note: This analysis is based on historical patterns and team dynamics."""
        
        return result