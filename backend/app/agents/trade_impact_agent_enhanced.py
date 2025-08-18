"""Enhanced TradeImpact Agent with reranking and proper logging"""
import logging
import time
from typing import List, Dict, Optional
from app.agents.trade_impact_agent_tools import TradeImpactAgent
from app.services.reranker_service import ReRankerService

logger = logging.getLogger(__name__)

class EnhancedTradeImpactAgent(TradeImpactAgent):
    """Enhanced version with reranking and detailed logging"""
    
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
            logger.info("Reranker initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize reranker: {e}")
            self.reranker = None
    
    def _search_trade_documents_raw(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Get raw search results for reranking
        Returns list of dicts instead of formatted string
        """
        try:
            # Check Milvus configuration
            if not settings.MILVUS_HOST or not settings.MILVUS_TOKEN:
                logger.warning(f"MILVUS FALLBACK: No configuration. Query: {query}")
                return []
            
            connections.connect(
                alias="default",
                uri=settings.MILVUS_HOST,
                token=settings.MILVUS_TOKEN
            )
            
            collection = Collection("sportsbrain_trades")
            collection.load()
            
            query_embedding = self.embedding_model.encode(query).tolist()
            
            search_params = {
                "metric_type": "IP",  # Inner Product - matches collection schema
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[query_embedding],
                anns_field="vector",  # FIXED: Changed from "embedding" to "vector" per schema
                param=search_params,
                limit=top_k,
                output_fields=["text", "metadata"]  # FIXED: Use actual schema fields
            )
            
            documents = []
            if results and results[0]:
                for hit in results[0]:
                    # Extract metadata JSON field which contains trade details
                    metadata = hit.entity.get('metadata', {})
                    documents.append({
                        'content': hit.entity.get('text', ''),
                        'score': hit.score,
                        'metadata': metadata  # Pass through the full metadata JSON
                    })
            
            connections.disconnect("default")
            logger.info(f"Milvus search successful: Found {len(documents)} documents for query: {query}")
            return documents
            
        except Exception as e:
            logger.error(f"MILVUS FALLBACK: Search failed with error: {e}")
            logger.error(f"Query that failed: {query}")
            logger.error(f"This is the schema mismatch issue - field 'embedding' not found")
            connections.disconnect("default")
            return []
    
    def analyze_trade_impact(self, input_str: str) -> str:
        """Enhanced version with reranking and detailed logging"""
        start_time = time.time()
        
        logger.info(f"=== Starting trade impact analysis for: {input_str}")
        
        try:
            # Step 1: Try Milvus search (get more candidates for reranking)
            initial_results = self._search_trade_documents_raw(
                query=input_str,
                top_k=20 if self.reranker else 5
            )
            
            # Step 2: Check if we got Milvus results
            if not initial_results:
                logger.warning(f"MILVUS FALLBACK TRIGGERED for query: {input_str}")
                logger.warning("Reason: No results from Milvus (connection failed or schema mismatch)")
                logger.info("Using PostgreSQL fallback for analysis")
                
                # Track this fallback (in production, this would go to monitoring service)
                self._log_fallback_event(input_str, "milvus_failure")
                
                result = self._fallback_trade_analysis(input_str)
                logger.info(f"Fallback analysis completed in {time.time() - start_time:.2f}s")
                return result
            
            # Step 3: Apply reranking if available
            if self.reranker and len(initial_results) > 1:
                logger.info(f"Applying reranking to {len(initial_results)} documents")
                reranked = self.reranker.rerank(
                    query=input_str,
                    documents=initial_results,
                    top_k=5,
                    log_details=True
                )
                
                # Format reranked results
                result = self._format_reranked_response(reranked)
                logger.info(f"Reranked analysis completed in {time.time() - start_time:.2f}s")
            else:
                # Format without reranking
                result = self._format_documents(initial_results[:5])
                logger.info(f"Standard analysis completed in {time.time() - start_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Trade impact analysis failed: {e}", exc_info=True)
            logger.info("Using final fallback")
            return self._fallback_trade_analysis(input_str)
    
    def _format_reranked_response(self, reranked_results) -> str:
        """Format reranked results for display"""
        response = "**Trade Impact Analysis (Enhanced with Reranking)**:\n\n"
        
        for i, result in enumerate(reranked_results, 1):
            # Show rank change if significant
            rank_indicator = ""
            if result.rank_change > 2:
                rank_indicator = f" ⬆️ (moved up {result.rank_change} positions)"
            elif result.rank_change < -2:
                rank_indicator = f" ⬇️ (moved down {abs(result.rank_change)} positions)"
            
            response += f"**{i}. {result.metadata.get('trade_title', 'Trade Analysis')}{rank_indicator}**\n"
            response += f"Relevance Score: {result.rerank_score:.2f}\n"
            response += f"Fantasy Impact: {result.metadata.get('fantasy_impact', 'N/A')}\n"
            response += f"Affected Players: {result.metadata.get('affected_players', 'N/A')}\n\n"
        
        return response
    
    def _format_documents(self, documents: List[Dict]) -> str:
        """Format documents without reranking"""
        response = "**Trade Impact Analysis**:\n\n"
        
        for i, doc in enumerate(documents, 1):
            response += f"**{i}. {doc['metadata'].get('trade_title', 'Trade Analysis')}**\n"
            response += f"Score: {doc['score']:.2f}\n"
            response += f"Fantasy Impact: {doc['metadata'].get('fantasy_impact', 'N/A')}\n"
            response += f"Affected Players: {doc['metadata'].get('affected_players', 'N/A')}\n\n"
        
        return response
    
    def _log_fallback_event(self, query: str, reason: str):
        """Log fallback event for monitoring"""
        # In production, this would send to monitoring service
        # For now, just log it prominently
        logger.warning("=" * 60)
        logger.warning("FALLBACK EVENT TRACKING")
        logger.warning(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.warning(f"Query: {query}")
        logger.warning(f"Reason: {reason}")
        logger.warning(f"Agent: TradeImpact")
        logger.warning("=" * 60)

# Import required modules at the end to avoid circular imports
from pymilvus import connections, Collection
from app.core.config import settings