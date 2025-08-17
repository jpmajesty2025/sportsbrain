# Re-Ranking Implementation Plan v2 - Current System Integration

## Executive Summary
This updated plan integrates re-ranking into our existing SportsBrain system, focusing on practical implementation that works with our current agent architecture and addresses known issues like the Milvus fallback scenarios.

## Current System Analysis

### What We Have
- **3 Agents**: Intelligence, DraftPrep, TradeImpact
- **Vector Search**: Milvus with 3 collections (players, strategies, trades)
- **Fallback Mechanism**: PostgreSQL when Milvus fails (needs logging!)
- **17 Tools**: Mix of SQL, vector search, and calculations

### Key Integration Points
1. **TradeImpact Agent**: Uses `_search_trade_documents()` for Milvus queries
2. **Intelligence Agent**: Currently uses only SQL queries (could add vector search)
3. **DraftPrep Agent**: Pure SQL currently (opportunity for vector enhancement)

## Implementation Strategy

### Phase 1: Core Re-Ranking Service (2 hours)

```python
# backend/app/services/reranker_service.py
from typing import List, Tuple, Dict, Optional
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
            self.model = CrossEncoder(model_name)
            self.model_loaded = True
            logger.info(f"Loaded reranking model: {model_name}")
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
        
        start_time = time.time()
        
        try:
            # Create query-document pairs
            pairs = [[query, doc.get('content', '')] for doc in documents]
            
            # Get reranking scores
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
            logger.error(f"Reranking failed: {e}")
            return self._fallback_to_original(documents, top_k)
    
    def _fallback_to_original(self, documents: List[Dict], top_k: int) -> List[RerankResult]:
        """Fallback to original ranking when reranker fails"""
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
        for i, result in enumerate(results):
            if result.rank_change != 0:
                logger.info(f"  Rank {i+1}: Changed by {result.rank_change:+d} positions "
                          f"(original: {result.original_score:.3f}, "
                          f"rerank: {result.rerank_score:.3f})")
```

### Phase 2: Integration with Existing Agents (2 hours)

#### Enhanced TradeImpact Agent
```python
# backend/app/agents/trade_impact_agent_tools.py (additions)

def analyze_trade_impact(self, input_str: str) -> str:
    """Enhanced version with reranking"""
    try:
        # Step 1: Initial Milvus search (retrieve more candidates)
        initial_results = self._search_trade_documents_raw(
            query=input_str,
            top_k=20  # Get more initial candidates
        )
        
        # Step 2: Check if we got Milvus results or fell back
        if "Milvus connection not configured" in initial_results:
            # LOG THIS FALLBACK!
            logger.warning(f"MILVUS FALLBACK TRIGGERED for query: {input_str}")
            logger.warning("Falling back to PostgreSQL - vector search unavailable")
            return self._fallback_trade_analysis(input_str)
        
        # Step 3: Rerank the results
        reranker = ReRankerService()
        reranked = reranker.rerank(
            query=input_str,
            documents=initial_results,
            top_k=5,
            log_details=True  # Enable logging for monitoring
        )
        
        # Step 4: Format response with reranked results
        return self._format_reranked_response(reranked)
        
    except Exception as e:
        logger.error(f"Trade impact analysis failed: {e}")
        return self._fallback_trade_analysis(input_str)

def _search_trade_documents_raw(self, query: str, top_k: int = 20) -> List[Dict]:
    """Get raw search results for reranking"""
    # Modified version of existing _search_trade_documents
    # Returns list of dicts instead of formatted string
    pass
```

#### Add Vector Search to Intelligence Agent
```python
# backend/app/agents/intelligence_agent_tools.py (additions)

def find_similar_players_enhanced(self, player_name: str) -> str:
    """Find similar players using vector search + reranking"""
    try:
        # Step 1: Get player embedding from Milvus
        player_embedding = self._get_player_embedding(player_name)
        
        if not player_embedding:
            # Fallback to SQL-based similarity
            return self._sql_similarity_search(player_name)
        
        # Step 2: Vector similarity search
        similar_players = self._search_similar_players(
            embedding=player_embedding,
            top_k=15
        )
        
        # Step 3: Rerank based on query context
        query = f"Players similar to {player_name} for fantasy basketball"
        reranker = ReRankerService()
        reranked = reranker.rerank(
            query=query,
            documents=similar_players,
            top_k=5
        )
        
        return self._format_similar_players(reranked)
        
    except Exception as e:
        logger.error(f"Similar player search failed: {e}")
        return self._sql_similarity_search(player_name)
```

### Phase 3: Monitoring and Testing (1 hour)

#### Monitoring Dashboard Data
```python
# backend/app/monitoring/rerank_metrics.py

class RerankingMetrics:
    """Track reranking performance and impact"""
    
    def __init__(self):
        self.metrics = {
            'total_reranks': 0,
            'fallback_count': 0,
            'avg_latency': 0,
            'avg_rank_change': 0,
            'milvus_fallbacks': 0
        }
    
    def log_reranking(self, results: List[RerankResult], latency: float):
        """Log reranking event for metrics"""
        self.metrics['total_reranks'] += 1
        self.metrics['avg_latency'] = self._update_avg(
            self.metrics['avg_latency'], 
            latency, 
            self.metrics['total_reranks']
        )
        
        # Track how much reranking changes results
        avg_change = sum(abs(r.rank_change) for r in results) / len(results)
        self.metrics['avg_rank_change'] = self._update_avg(
            self.metrics['avg_rank_change'],
            avg_change,
            self.metrics['total_reranks']
        )
    
    def log_milvus_fallback(self, query: str):
        """Log when Milvus fails and we fallback"""
        self.metrics['milvus_fallbacks'] += 1
        logger.warning(f"MILVUS FALLBACK #{self.metrics['milvus_fallbacks']}: {query}")
```

#### Test Suite
```python
# backend/tests/test_reranking.py

import pytest
from app.services.reranker_service import ReRankerService

class TestReranking:
    
    def test_reranking_improves_relevance(self):
        """Test that reranking improves result relevance"""
        reranker = ReRankerService()
        
        query = "Should I keep Ja Morant in round 3?"
        
        # Mock documents (what Milvus might return)
        documents = [
            {"content": "Ja Morant highlights reel 2024", "score": 0.89},
            {"content": "Ja Morant ADP is round 2, keeper value analysis", "score": 0.85},
            {"content": "Memphis Grizzlies schedule", "score": 0.83},
            {"content": "Round 3 keeper strategy guide", "score": 0.82},
            {"content": "Ja Morant injury history and risk", "score": 0.80}
        ]
        
        reranked = reranker.rerank(query, documents, top_k=3)
        
        # The keeper value analysis should rank higher
        assert "keeper value" in reranked[0].content.lower()
        
        # Highlights reel should rank lower
        highlights_ranks = [i for i, r in enumerate(reranked) 
                          if "highlights" in r.content.lower()]
        assert not highlights_ranks or highlights_ranks[0] > 1
    
    def test_fallback_when_model_fails(self):
        """Test graceful fallback when reranker fails"""
        reranker = ReRankerService(model_name="invalid_model")
        documents = [{"content": "test", "score": 0.5}]
        
        results = reranker.rerank("query", documents, top_k=1)
        assert len(results) == 1
        assert results[0].rank_change == 0  # No change on fallback
```

## Implementation Timeline

### Day 1 (4 hours)
1. **Hour 1-2**: Implement ReRankerService class
2. **Hour 3**: Integrate with TradeImpact Agent
3. **Hour 4**: Add comprehensive logging for Milvus fallbacks

### Day 2 (3 hours)  
1. **Hour 1**: Add vector search to Intelligence Agent
2. **Hour 2**: Create test suite
3. **Hour 3**: Test with real queries, measure impact

### Day 3 (1 hour)
1. **Hour 1**: Performance optimization and documentation

## Success Metrics

1. **Milvus Fallback Visibility**: 100% of fallbacks logged with context
2. **Relevance Improvement**: 30%+ better ranking for test queries
3. **Latency Impact**: <200ms additional processing time
4. **Agent Success Rate**: Increase from 70-80% to 85-90%

## Key Differences from v1

1. **Focus on Current System**: Works with existing 3 agents, not hypothetical 4
2. **Fallback Monitoring**: Addresses the silent Milvus fallback issue
3. **Incremental Integration**: Can be added without breaking changes
4. **Open Source Only**: Uses BGE model, no API costs
5. **Detailed Logging**: Every reranking decision is traceable

## Next Steps

1. **Immediate**: Implement logging for Milvus fallbacks (even without reranking)
2. **Short-term**: Deploy ReRankerService and integrate with TradeImpact
3. **Medium-term**: Extend to other agents once proven successful
4. **Long-term**: Consider Cohere or custom model training

## Risk Mitigation

- **Model Loading Failure**: Graceful fallback to original ranking
- **Performance Impact**: Cache reranking results for common queries
- **Memory Usage**: Load model once, share across requests
- **Debugging**: Comprehensive logging at every step

## Conclusion

This v2 plan provides a practical path to implementing reranking in our current system while addressing known issues like silent Milvus fallbacks. The implementation is incremental, testable, and focuses on measurable improvements to our existing agents.