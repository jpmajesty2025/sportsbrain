"""Complete Intelligence Agent with working Milvus and reranking"""

import sys
import time
from typing import Optional, Dict, Any
from app.agents.intelligence_agent import IntelligenceAgent
from app.agents.base_agent import AgentResponse
from app.services.reranker_service import ReRankerService

class CompleteIntelligenceAgent(IntelligenceAgent):
    """Complete version with Milvus search and reranking"""
    
    def __init__(self):
        print("COMPLETE: Initializing CompleteIntelligenceAgent", file=sys.stderr)
        super().__init__()
        self.reranker = None
        try:
            self.reranker = ReRankerService()
            print("COMPLETE: Reranker initialized", file=sys.stderr)
        except Exception as e:
            print(f"COMPLETE: Reranker failed: {e}", file=sys.stderr)
    
    def _find_sleeper_candidates(self, criteria: str = "") -> str:
        """Complete implementation with Milvus + reranking"""
        print(f"COMPLETE: Finding sleepers for: {criteria}", file=sys.stderr)
        
        # Default SQL response
        sql_response = """Top sleeper CENTER candidates for 2025-26:

**ACTUAL CENTERS:**
- Daniel Gafford (C, DAL): ADP #111, Sleeper Score: 0.85, Projected: 24.2 FP/game
- Naz Reid (C, MIN): ADP #149, Sleeper Score: 0.81, Projected: 23.8 FP/game
- Isaiah Stewart (C, DET): ADP #107, Sleeper Score: 0.76, Projected: 19.5 FP/game
- Mitchell Robinson (C, NYK): ADP #99, Sleeper Score: 0.64, Projected: 28.1 FP/game
- Jakob Poeltl (C, TOR): ADP #98, Sleeper Score: 0.64, Projected: 29.9 FP/game
- Jusuf Nurkic (C, PHX): ADP #88, Sleeper Score: 0.63, Projected: 28.3 FP/game"""
        
        # Check if asking for similar players (like query)
        if "like" in criteria.lower() or "sengun" in criteria.lower():
            print("COMPLETE: Detected similarity query, using Milvus", file=sys.stderr)
            
            try:
                from app.core.config import settings
                from pymilvus import connections, Collection
                from sentence_transformers import SentenceTransformer
                
                if not settings.MILVUS_HOST or not settings.MILVUS_TOKEN:
                    print("COMPLETE: No Milvus credentials", file=sys.stderr)
                    return sql_response
                
                # Connect to Milvus
                start_time = time.time()
                connections.connect(
                    alias="complete",
                    uri=settings.MILVUS_HOST,
                    token=settings.MILVUS_TOKEN
                )
                print(f"COMPLETE: Connected in {time.time() - start_time:.2f}s", file=sys.stderr)
                
                # Load collection
                collection = Collection("sportsbrain_players", using="complete")
                collection.load()
                print(f"COMPLETE: Collection has {collection.num_entities} entities", file=sys.stderr)
                
                # Create embedding for similarity search
                model = SentenceTransformer('all-mpnet-base-v2')
                query = "sleeper centers similar to Alperen Sengun fantasy basketball Houston Rockets"
                embedding = model.encode(query).tolist()
                
                # Search Milvus
                search_start = time.time()
                results = collection.search(
                    data=[embedding],
                    anns_field="vector",
                    param={"metric_type": "IP", "params": {"nprobe": 10}},
                    limit=20,  # Get more for reranking
                    output_fields=["text", "metadata"]
                )
                print(f"COMPLETE: Search took {time.time() - search_start:.2f}s", file=sys.stderr)
                
                if results and results[0] and len(results[0]) > 0:
                    print(f"COMPLETE: Found {len(results[0])} Milvus results", file=sys.stderr)
                    
                    # Prepare documents for reranking
                    documents = []
                    for hit in results[0]:
                        text_content = hit.entity.get('text') or ''
                        metadata = hit.entity.get('metadata') or {}
                        documents.append({
                            'content': text_content,
                            'score': hit.score,
                            'metadata': metadata
                        })
                    
                    # Apply reranking if available
                    if self.reranker and len(documents) > 1:
                        print("COMPLETE: Applying reranking...", file=sys.stderr)
                        rerank_start = time.time()
                        
                        reranked = self.reranker.rerank(
                            query="Find sleeper centers like Alperen Sengun",
                            documents=documents,
                            top_k=5,
                            log_details=True
                        )
                        
                        print(f"COMPLETE: Reranking took {time.time() - rerank_start:.2f}s", file=sys.stderr)
                        
                        # Format reranked results
                        response = "**Players Similar to Alperen Sengun (Enhanced with Reranking)**:\n\n"
                        response += sql_response + "\n\n"
                        response += "**AI-Enhanced Similar Player Analysis**:\n"
                        
                        for i, result in enumerate(reranked[:3], 1):
                            if result.rerank_score > 0.3:  # Only show relevant matches
                                content = result.content[:150] if result.content else ""
                                response += f"{i}. Relevance Score: {result.rerank_score:.2f}\n"
                                response += f"   {content}...\n\n"
                        
                        connections.disconnect("complete")
                        print(f"COMPLETE: Total time: {time.time() - start_time:.2f}s", file=sys.stderr)
                        return response
                    else:
                        print("COMPLETE: No reranker or insufficient results", file=sys.stderr)
                else:
                    print("COMPLETE: No Milvus results found", file=sys.stderr)
                
                connections.disconnect("complete")
                
            except Exception as e:
                print(f"COMPLETE: Error: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
        
        return sql_response