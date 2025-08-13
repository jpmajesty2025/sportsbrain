# Re-Ranking Implementation Plan for SportsBrain RAG System

## Overview
Re-ranking is a post-processing step that improves the relevance of retrieved documents by using more sophisticated models to re-score initial search results.

## Why Re-Ranking?

### Current Limitations
- Vector search returns semantically similar but not always contextually relevant documents
- Embeddings can't capture query-document interaction deeply
- May include irrelevant results in top-K (e.g., "Ja Morant highlights" when asking about keeper value)

### Expected Benefits
- 30-50% improvement in precision@5
- Better context for LLM = more accurate responses
- Reduced token usage by filtering out less relevant documents
- Improved user satisfaction with more targeted answers

## Implementation Strategy

### Phase 1: Core Re-Ranking Service (2 hours)

```python
# backend/services/reranker.py
from typing import List, Tuple, Dict
import cohere
from sentence_transformers import CrossEncoder
import os

class ReRanker:
    def __init__(self, model_type="bge"):  # Start with open-source
        if model_type == "cohere":
            self.client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
            self.model_type = "cohere"
        else:
            # Use open-source BGE-reranker (no API costs)
            self.model = CrossEncoder('BAAI/bge-reranker-large')
            self.model_type = "bge"
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, str]], 
        top_k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Re-rank documents based on relevance to query
        
        Args:
            query: User's question
            documents: List of dicts with 'content' and 'metadata'
            top_k: Number of documents to return
            
        Returns:
            List of (document, score) tuples
        """
        
        if self.model_type == "cohere":
            results = self.client.rerank(
                query=query,
                documents=[doc['content'] for doc in documents],
                top_n=top_k,
                model='rerank-english-v2.0'
            )
            return [(documents[r.index], r.relevance_score) 
                    for r in results]
        else:
            # BGE reranker
            pairs = [[query, doc['content']] for doc in documents]
            scores = self.model.predict(pairs)
            ranked = sorted(
                zip(documents, scores), 
                key=lambda x: x[1], 
                reverse=True
            )
            return ranked[:top_k]
```

### Phase 2: Integration Points (1 hour)

#### 1. Update Vector Search Pipeline
```python
# backend/services/vector_search.py
class EnhancedVectorSearch:
    def __init__(self):
        self.milvus_client = MilvusClient()
        self.reranker = ReRanker()
    
    def search_with_rerank(
        self, 
        query: str, 
        collection: str,
        initial_k: int = 20,  # Retrieve more initially
        final_k: int = 5       # Return fewer after reranking
    ):
        # Step 1: Vector similarity search
        initial_results = self.milvus_client.search(
            collection_name=collection,
            query_vector=embed(query),
            limit=initial_k
        )
        
        # Step 2: Re-rank results
        reranked = self.reranker.rerank(
            query=query,
            documents=initial_results,
            top_k=final_k
        )
        
        return reranked
```

#### 2. Agent Integration
- **DraftPrep Agent**: Re-rank player comparisons, ADP data, keeper values
- **TradeImpact Agent**: Re-rank trade news by actual impact on specific players
- **PredictionAgent**: Re-rank historical patterns by true similarity

### Phase 3: Performance Metrics (30 mins)

#### Metrics to Track
1. **Precision@K**: Percentage of relevant documents in top K
2. **MRR (Mean Reciprocal Rank)**: Position of first relevant result
3. **Response Quality**: A/B test with/without reranking
4. **Latency Impact**: Measure additional processing time

#### Test Scenarios
```python
test_queries = [
    {
        "query": "Should I keep Ja Morant in round 3?",
        "expected_relevant": ["Ja Morant ADP", "Keeper values", "Round 3 strategy"],
        "expected_irrelevant": ["Ja Morant highlights", "Grizzlies schedule"]
    },
    {
        "query": "Punt FT% build with Giannis",
        "expected_relevant": ["Punt FT strategy", "Giannis stats", "Compatible players"],
        "expected_irrelevant": ["Giannis MVP race", "Bucks news"]
    }
]
```

## Implementation Checklist

### Required Dependencies
```python
# Add to requirements.txt
cohere==4.37.0  # Optional: for Cohere API
sentence-transformers==2.2.2  # For BGE reranker
```

### Environment Variables
```bash
# .env (optional for Cohere)
COHERE_API_KEY=your_key_here
RERANKER_MODEL=bge  # or 'cohere'
RERANK_INITIAL_K=20
RERANK_FINAL_K=5
```

### Testing Strategy
1. **Unit Tests**: Test reranker with mock documents
2. **Integration Tests**: Test full pipeline with real Milvus data
3. **A/B Testing**: Compare responses with/without reranking
4. **Performance Tests**: Measure latency impact

## Example Improvement

### Before Re-ranking
```
Query: "Should I trade for Damian Lillard?"
Retrieved:
1. Lillard season stats (0.89)
2. Portland Trail Blazers news (0.85)  ❌ Outdated
3. Lillard highlights (0.83)  ❌ Not relevant
4. Trade rumors (0.82)
5. Bucks roster (0.80)
```

### After Re-ranking
```
Query: "Should I trade for Damian Lillard?"
Re-ranked:
1. Lillard season stats (0.95)
2. Trade impact analysis (0.92)
3. Bucks usage rates (0.88)
4. Fantasy value post-trade (0.85)
5. Similar trades historical performance (0.82)
```

## Success Criteria

1. **Precision@5 improves by >30%** on test queries
2. **Latency increase <200ms** per query
3. **All 5 demo scenarios** show improved relevance
4. **User feedback** indicates better answer quality

## Timeline

- **Hour 1**: Implement ReRanker class with BGE model
- **Hour 2**: Integrate into vector search pipeline
- **Hour 3**: Update all three agents, add tests
- **Hour 4**: Performance testing and optimization
- **Total**: 4 hours implementation + testing

## Notes

- Start with open-source BGE model (no API costs)
- Cohere option available for better quality if needed
- Can cache reranking results for common queries
- Consider async processing for multiple documents

## References

- [BGE Reranker Model](https://huggingface.co/BAAI/bge-reranker-large)
- [Cohere Rerank API](https://docs.cohere.com/docs/reranking)
- [Cross-Encoder vs Bi-Encoder](https://www.sbert.net/examples/applications/cross-encoder/README.html)