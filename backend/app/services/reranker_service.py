"""Re-ranking service for SportsBrain RAG system"""
from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder
import logging
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class RerankResult:
    """Result from reranking with metadata"""
    content: str
    original_score: float
    rerank_score: float
    metadata: Dict
    rank_change: int  # How much the rank changed

class ReRankerService:
    """Re-ranking service for SportsBrain RAG system"""
    
    def __init__(self, model_name: str = 'BAAI/bge-reranker-large'):
        """Initialize with BGE reranker (open-source, no API costs)"""
        try:
            logger.info(f"Loading reranking model: {model_name}")
            self.model = CrossEncoder(model_name)
            self.model_loaded = True
            logger.info(f"Successfully loaded reranking model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load reranking model: {e}")
            self.model_loaded = False
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict], 
        top_k: int = 5,
        log_details: bool = True
    ) -> List[RerankResult]:
        """
        Re-rank documents based on relevance to query
        
        Args:
            query: User's question
            documents: List of dicts with 'content', 'score', and 'metadata'
            top_k: Number of documents to return
            log_details: Whether to log reranking details (for debugging)
            
        Returns:
            List of RerankResult objects
        """
        if not self.model_loaded:
            logger.warning("Reranker not loaded, returning original order")
            return self._fallback_to_original(documents, top_k)
        
        if not documents:
            logger.warning("No documents to rerank")
            return []
        
        start_time = time.time()
        
        try:
            # Create query-document pairs
            pairs = [[query, doc.get('content', '')] for doc in documents]
            
            # Get reranking scores
            logger.debug(f"Reranking {len(pairs)} documents for query: {query[:50]}...")
            scores = self.model.predict(pairs)
            
            # Combine with original rankings
            results = []
            for i, (doc, rerank_score) in enumerate(zip(documents, scores)):
                results.append({
                    'document': doc,
                    'original_rank': i,
                    'original_score': doc.get('score', 0.0),
                    'rerank_score': float(rerank_score)
                })
            
            # Sort by rerank score
            results.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # Create RerankResult objects
            reranked = []
            for new_rank, item in enumerate(results[:top_k]):
                rank_change = item['original_rank'] - new_rank
                reranked.append(RerankResult(
                    content=item['document'].get('content', ''),
                    original_score=item['original_score'],
                    rerank_score=item['rerank_score'],
                    metadata=item['document'].get('metadata', {}),
                    rank_change=rank_change
                ))
            
            # Log reranking details if requested
            if log_details:
                self._log_reranking_details(query, reranked, time.time() - start_time)
            
            return reranked
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}", exc_info=True)
            return self._fallback_to_original(documents, top_k)
    
    def _fallback_to_original(self, documents: List[Dict], top_k: int) -> List[RerankResult]:
        """Fallback to original ranking when reranker fails"""
        logger.info("Using fallback - returning original document order")
        results = []
        for i, doc in enumerate(documents[:top_k]):
            results.append(RerankResult(
                content=doc.get('content', ''),
                original_score=doc.get('score', 0.0),
                rerank_score=doc.get('score', 0.0),  # Use original score
                metadata=doc.get('metadata', {}),
                rank_change=0  # No change
            ))
        return results
    
    def _log_reranking_details(self, query: str, results: List[RerankResult], duration: float):
        """Log reranking details for monitoring"""
        logger.info(f"Reranking for query: '{query[:50]}...' took {duration:.3f}s")
        
        # Count significant rank changes
        significant_changes = sum(1 for r in results if abs(r.rank_change) > 2)
        if significant_changes > 0:
            logger.info(f"  {significant_changes} documents had significant rank changes (>2 positions)")
        
        # Log top results with changes
        for i, result in enumerate(results[:3]):  # Log top 3
            if result.rank_change != 0:
                logger.info(
                    f"  Rank {i+1}: Changed by {result.rank_change:+d} positions "
                    f"(original: {result.original_score:.3f}, "
                    f"rerank: {result.rerank_score:.3f})"
                )
        
        # Log average scores
        if results:
            avg_original = sum(r.original_score for r in results) / len(results)
            avg_rerank = sum(r.rerank_score for r in results) / len(results)
            logger.info(
                f"  Average scores - Original: {avg_original:.3f}, "
                f"Rerank: {avg_rerank:.3f}"
            )