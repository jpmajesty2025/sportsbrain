"""Fixed TradeImpact Agent with correct Milvus Hit access"""

import logging
import time
from typing import List, Dict, Optional
from app.agents.trade_impact_agent_tools import TradeImpactAgent
from app.services.reranker_service import ReRankerService

logger = logging.getLogger(__name__)

class FixedTradeImpactAgent(TradeImpactAgent):
    """Fixed version with correct Milvus Hit object access"""
    
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
            logger.info("Fixed Agent: Reranker initialized successfully")
        except Exception as e:
            logger.warning(f"Fixed Agent: Could not initialize reranker: {e}")
            self.reranker = None
    
    def _search_trade_documents_raw(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Get raw search results for reranking
        Fixed: Correct access to Hit object fields
        """
        try:
            from pymilvus import connections, Collection
            from app.core.config import settings
            
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
                anns_field="vector",  # Correct field name per schema
                param=search_params,
                limit=top_k,
                output_fields=["text", "metadata"]  # Request these fields
            )
            
            documents = []
            if results and results[0]:
                for hit in results[0]:
                    # FIXED: hit.entity.get() doesn't accept default value as 2nd argument
                    # Must use get() without default or check membership first
                    text_content = hit.entity.get('text') or ''
                    metadata_content = hit.entity.get('metadata') or {}
                    
                    documents.append({
                        'content': text_content,
                        'score': hit.score,
                        'metadata': metadata_content
                    })
            
            connections.disconnect("default")
            logger.info(f"Milvus search successful: Found {len(documents)} documents for query: {query}")
            return documents
            
        except Exception as e:
            logger.error(f"MILVUS SEARCH ERROR: {e}")
            logger.error(f"Query that failed: {query}")
            try:
                connections.disconnect("default")
            except:
                pass
            return []
    
    def analyze_trade_impact(self, input_str: str) -> str:
        """Enhanced version with reranking and fixed Milvus access"""
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
                logger.info("Using PostgreSQL fallback for analysis")
                
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
                rank_indicator = f" (moved up {result.rank_change} positions)"
            elif result.rank_change < -2:
                rank_indicator = f" (moved down {abs(result.rank_change)} positions)"
            
            # Extract title from content or metadata
            content_preview = result.content[:150] if result.content else "Trade Analysis"
            # Remove newlines for cleaner display
            content_preview = content_preview.replace('\n', ' ').strip()
            
            response += f"**{i}. Analysis{rank_indicator}**\n"
            response += f"Relevance Score: {result.rerank_score:.2f}\n"
            response += f"Content: {content_preview}...\n"
            
            # If metadata is a dict and has relevant fields, show them
            if isinstance(result.metadata, dict):
                if 'players_mentioned' in result.metadata:
                    response += f"Players: {', '.join(result.metadata['players_mentioned'][:3])}\n"
                if 'teams_involved' in result.metadata:
                    response += f"Teams: {', '.join(result.metadata['teams_involved'][:2])}\n"
            
            response += "\n"
        
        return response
    
    def _format_documents(self, documents: List[Dict]) -> str:
        """Format documents without reranking"""
        response = "**Trade Impact Analysis**:\n\n"
        
        for i, doc in enumerate(documents, 1):
            # Extract content preview
            content_preview = doc.get('content', '')[:150]
            content_preview = content_preview.replace('\n', ' ').strip()
            
            response += f"**{i}. Analysis**\n"
            response += f"Score: {doc.get('score', 0):.2f}\n"
            response += f"Content: {content_preview}...\n"
            
            # If metadata is available and has relevant fields
            metadata = doc.get('metadata', {})
            if isinstance(metadata, dict):
                if 'players_mentioned' in metadata:
                    response += f"Players: {', '.join(metadata['players_mentioned'][:3])}\n"
                if 'teams_involved' in metadata:
                    response += f"Teams: {', '.join(metadata['teams_involved'][:2])}\n"
            
            response += "\n"
        
        return response