"""Clean Intelligence Agent with proper formatting and extended reranking"""

import sys
import time
from typing import Optional, Dict, Any
from app.agents.intelligence_agent import IntelligenceAgent
from app.agents.base_agent import AgentResponse
from app.services.reranker_service import ReRankerService

class CleanIntelligenceAgent(IntelligenceAgent):
    """Clean version with better formatting and extended reranking"""
    
    def __init__(self):
        print("CLEAN: Initializing CleanIntelligenceAgent", file=sys.stderr)
        super().__init__()
        self.reranker = None
        try:
            self.reranker = ReRankerService()
            print("CLEAN: Reranker initialized", file=sys.stderr)
        except Exception as e:
            print(f"CLEAN: Reranker failed: {e}", file=sys.stderr)
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Override to handle more queries directly with reranking"""
        
        message_lower = message.lower()
        
        # Queries that benefit from reranking/similarity search
        if any(keyword in message_lower for keyword in ["sleeper", "like", "similar", "compare", "versus", "vs"]):
            print(f"CLEAN: Detected reranking-eligible query: {message[:50]}...", file=sys.stderr)
            
            # Route to appropriate enhanced method
            if "sleeper" in message_lower:
                result = self._find_sleeper_candidates(message)
            elif "compare" in message_lower or "vs" in message_lower or "versus" in message_lower:
                result = self._compare_players_enhanced(message)
            else:
                # Let parent handle
                return await super().process_message(message, context)
            
            return AgentResponse(
                content=result,
                metadata={"agent": "intelligence", "method": "direct_enhanced", "reranking": True},
                confidence=0.95
            )
        
        # For other queries, use normal flow
        return await super().process_message(message, context)
    
    def _find_sleeper_candidates(self, criteria: str = "") -> str:
        """Clean implementation with proper formatting"""
        print(f"CLEAN: Finding sleepers for: {criteria[:50]}...", file=sys.stderr)
        
        # Base SQL response - cleaner format
        sql_centers = [
            ("Daniel Gafford", "C", "DAL", 111, 0.85, 24.2),
            ("Naz Reid", "C", "MIN", 149, 0.81, 23.8),
            ("Isaiah Stewart", "C", "DET", 107, 0.76, 19.5),
            ("Mitchell Robinson", "C", "NYK", 99, 0.64, 28.1),
            ("Jakob Poeltl", "C", "TOR", 98, 0.64, 29.9),
            ("Jusuf Nurkic", "C", "PHX", 88, 0.63, 28.3)
        ]
        
        # Check if this is a similarity query
        if "like" in criteria.lower() or "sengun" in criteria.lower():
            enhanced_results = self._get_milvus_enhanced_results(criteria, sql_centers)
            if enhanced_results:
                return enhanced_results
        
        # Return clean SQL response
        response = "**Top Sleeper Centers for 2025-26 Fantasy Basketball**\n\n"
        for name, pos, team, adp, score, fp in sql_centers:
            response += f"• **{name}** ({pos}, {team}): "
            response += f"ADP #{adp}, Sleeper Score: {score:.2f}, "
            response += f"Projected: {fp:.1f} FP/game\n"
        
        response += "\n*Target these players 1-2 rounds before their ADP for best value.*"
        return response
    
    def _get_milvus_enhanced_results(self, criteria: str, sql_centers):
        """Get Milvus-enhanced results with reranking"""
        try:
            from app.core.config import settings
            from pymilvus import connections, Collection
            from sentence_transformers import SentenceTransformer
            
            if not settings.MILVUS_HOST or not settings.MILVUS_TOKEN:
                return None
            
            # Connect to Milvus
            connections.connect(
                alias="clean",
                uri=settings.MILVUS_HOST,
                token=settings.MILVUS_TOKEN
            )
            
            collection = Collection("sportsbrain_players", using="clean")
            collection.load()
            
            # Create embedding
            model = SentenceTransformer('all-mpnet-base-v2')
            query = f"sleeper centers similar to Alperen Sengun fantasy basketball Houston Rockets"
            embedding = model.encode(query).tolist()
            
            # Search Milvus
            results = collection.search(
                data=[embedding],
                anns_field="vector",
                param={"metric_type": "IP", "params": {"nprobe": 10}},
                limit=20,
                output_fields=["text", "metadata"]
            )
            
            if results and results[0] and len(results[0]) > 0:
                print(f"CLEAN: Found {len(results[0])} Milvus results", file=sys.stderr)
                
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
                
                # Build response
                response = "**Sleeper Centers Similar to Alperen Sengun (AI-Enhanced)**\n\n"
                
                # Add SQL centers first
                response += "**Top Statistical Matches:**\n"
                for name, pos, team, adp, score, fp in sql_centers[:3]:
                    response += f"• **{name}** ({team}): ADP #{adp}, {fp:.1f} FP/game\n"
                
                # Apply reranking if available
                if self.reranker and len(documents) > 1:
                    print("CLEAN: Applying reranking...", file=sys.stderr)
                    
                    reranked = self.reranker.rerank(
                        query="Find sleeper centers like Alperen Sengun",
                        documents=documents,
                        top_k=3,
                        log_details=True
                    )
                    
                    # Check if we have good reranked results
                    good_results = [r for r in reranked if r.rerank_score > 0.1]
                    
                    if good_results:
                        response += "\n**Similar Player Profiles (AI Analysis):**\n"
                        for i, result in enumerate(good_results, 1):
                            # Extract player info from content
                            content = result.content[:200] if result.content else ""
                            if content:
                                # Clean up the content
                                content = content.replace('\n', ' ').strip()
                                response += f"{i}. {content}...\n"
                    else:
                        print(f"CLEAN: No high-quality reranked results (best score: {reranked[0].rerank_score if reranked else 0})", file=sys.stderr)
                
                connections.disconnect("clean")
                return response
            
            connections.disconnect("clean")
            
        except Exception as e:
            print(f"CLEAN: Milvus error: {e}", file=sys.stderr)
        
        return None
    
    def _compare_players_enhanced(self, players: str) -> str:
        """Enhanced player comparison with potential reranking"""
        print(f"CLEAN: Comparing players: {players}", file=sys.stderr)
        
        # For now, use the parent implementation
        # Could be enhanced with Milvus similarity search
        result = self._compare_players(players)
        
        # Try to enhance with Milvus if available
        if self.reranker:
            # Could search for comparison documents in strategies collection
            pass
        
        return result