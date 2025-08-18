"""Enhanced Intelligence Agent with reranking capabilities"""

import logging
import time
from typing import Dict, Any, List, Optional
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
from app.services.reranker_service import ReRankerService

logger = logging.getLogger(__name__)

class IntelligenceAgentWithReranking(IntelligenceAgentEnhanced):
    """Enhanced Intelligence Agent with BGE reranking for improved search relevance"""
    
    def __init__(self):
        super().__init__()
        self.reranker = None
        self._init_reranker()
        # Initialize embedding model for Milvus searches
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # 768 dims to match Milvus
        
    def _init_reranker(self):
        """Initialize reranker (lazy loading)"""
        try:
            self.reranker = ReRankerService()
            logger.info("Intelligence Agent: Reranker initialized successfully")
        except Exception as e:
            logger.warning(f"Intelligence Agent: Could not initialize reranker: {e}")
            self.reranker = None
    
    def _search_player_embeddings_raw(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Search player embeddings in Milvus and return raw results for reranking
        Returns list of dicts instead of formatted string
        """
        try:
            from pymilvus import connections, Collection
            from app.core.config import settings
            
            # Check Milvus configuration
            if not settings.MILVUS_HOST or not settings.MILVUS_TOKEN:
                logger.warning(f"Intelligence Agent: No Milvus configuration for query: {query}")
                return []
            
            connections.connect(
                alias="default",
                uri=settings.MILVUS_HOST,
                token=settings.MILVUS_TOKEN
            )
            
            collection = Collection("sportsbrain_players")
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
                output_fields=["text", "metadata"]  # Get text and metadata fields
            )
            
            documents = []
            if results and results[0]:
                for hit in results[0]:
                    documents.append({
                        'content': hit.entity.get('text', ''),
                        'score': hit.score,
                        'metadata': hit.entity.get('metadata', {})
                    })
            
            connections.disconnect("default")
            logger.info(f"Intelligence Agent: Milvus search found {len(documents)} documents for query: {query}")
            return documents
            
        except Exception as e:
            logger.error(f"Intelligence Agent: Milvus search failed: {e}")
            logger.error(f"Query that failed: {query}")
            try:
                connections.disconnect("default")
            except:
                pass
            return []
    
    def _search_strategy_embeddings_raw(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Search strategy embeddings in Milvus and return raw results for reranking
        """
        try:
            from pymilvus import connections, Collection
            from app.core.config import settings
            
            if not settings.MILVUS_HOST or not settings.MILVUS_TOKEN:
                logger.warning(f"Intelligence Agent: No Milvus configuration for strategy query: {query}")
                return []
            
            connections.connect(
                alias="default",
                uri=settings.MILVUS_HOST,
                token=settings.MILVUS_TOKEN
            )
            
            collection = Collection("sportsbrain_strategies")
            collection.load()
            
            query_embedding = self.embedding_model.encode(query).tolist()
            
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[query_embedding],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                output_fields=["text", "metadata"]
            )
            
            documents = []
            if results and results[0]:
                for hit in results[0]:
                    documents.append({
                        'content': hit.entity.get('text', ''),
                        'score': hit.score,
                        'metadata': hit.entity.get('metadata', {})
                    })
            
            connections.disconnect("default")
            logger.info(f"Intelligence Agent: Strategy search found {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Intelligence Agent: Strategy search failed: {e}")
            try:
                connections.disconnect("default")
            except:
                pass
            return []
    
    def _find_sleeper_candidates_enhanced(self, criteria: str = "") -> str:
        """Override to add reranking when searching for similar players"""
        # Check if this is a "players like X" query that might benefit from vector search
        if "like" in criteria.lower() and self.reranker:
            import re
            match = re.search(r'like\s+(.+?)(?:\s|$)', criteria.lower())
            if match:
                player_name = match.group(1).strip()
                
                # Search for similar players using embeddings
                query = f"players similar to {player_name} sleepers fantasy basketball"
                initial_results = self._search_player_embeddings_raw(query, top_k=20)
                
                if initial_results:
                    logger.info(f"Intelligence Agent: Applying reranking to {len(initial_results)} player results")
                    
                    # Apply reranking
                    reranked = self.reranker.rerank(
                        query=criteria,
                        documents=initial_results,
                        top_k=5,
                        log_details=True
                    )
                    
                    # Combine reranked vector results with SQL results
                    response = f"**Similar Players to {player_name} (Enhanced with Reranking)**:\n\n"
                    
                    for i, result in enumerate(reranked, 1):
                        response += f"**{i}. Similarity Match**\n"
                        response += f"Relevance Score: {result.rerank_score:.2f}\n"
                        
                        # Extract player info from content
                        content_preview = result.content[:200] if result.content else "Player Analysis"
                        response += f"Analysis: {content_preview}...\n"
                        
                        if isinstance(result.metadata, dict):
                            if 'player_name' in result.metadata:
                                response += f"Player: {result.metadata['player_name']}\n"
                            if 'position' in result.metadata:
                                response += f"Position: {result.metadata['position']}\n"
                        
                        response += "\n"
                    
                    # Also include SQL-based results
                    response += "\n" + super()._find_sleeper_candidates_enhanced(criteria)
                    return response
        
        # Fall back to parent implementation
        return super()._find_sleeper_candidates_enhanced(criteria)
    
    def _analyze_player_stats_enhanced(self, player_name: str) -> str:
        """Override to add reranking for player analysis searches"""
        start_time = time.time()
        
        # First get SQL-based analysis
        sql_response = super()._analyze_player_stats_enhanced(player_name)
        
        # If reranker is available, also search for additional insights
        if self.reranker:
            query = f"{player_name} fantasy basketball analysis stats projections"
            
            # Search both player and strategy collections
            player_docs = self._search_player_embeddings_raw(query, top_k=10)
            strategy_docs = self._search_strategy_embeddings_raw(query, top_k=10)
            
            all_docs = player_docs + strategy_docs
            
            if all_docs:
                logger.info(f"Intelligence Agent: Found {len(all_docs)} documents for {player_name}")
                
                # Apply reranking
                reranked = self.reranker.rerank(
                    query=f"Detailed analysis of {player_name} for fantasy basketball",
                    documents=all_docs,
                    top_k=3,
                    log_details=True
                )
                
                if reranked:
                    sql_response += "\n\n**Additional Insights (AI-Enhanced)**:\n"
                    for i, result in enumerate(reranked, 1):
                        # Only show highly relevant results
                        if result.rerank_score > 0.5:
                            content_preview = result.content[:150] if result.content else ""
                            content_preview = content_preview.replace('\n', ' ').strip()
                            if content_preview:
                                sql_response += f"{i}. {content_preview}...\n"
                
                logger.info(f"Intelligence Agent: Analysis completed in {time.time() - start_time:.2f}s")
        
        return sql_response
    
    def _compare_players_enhanced(self, players: str) -> str:
        """Override to add reranking for player comparisons"""
        start_time = time.time()
        
        # Get SQL-based comparison
        sql_response = super()._compare_players_enhanced(players)
        
        # If reranker is available, search for additional comparison insights
        if self.reranker and "vs" in players.lower() or "versus" in players.lower():
            # Search for comparison documents
            comparison_docs = self._search_strategy_embeddings_raw(
                f"player comparison {players} fantasy basketball",
                top_k=15
            )
            
            if comparison_docs:
                logger.info(f"Intelligence Agent: Found {len(comparison_docs)} comparison documents")
                
                # Apply reranking
                reranked = self.reranker.rerank(
                    query=f"Compare {players} for fantasy basketball",
                    documents=comparison_docs,
                    top_k=2,
                    log_details=True
                )
                
                if reranked:
                    sql_response += "\n\n**Expert Analysis (AI-Enhanced)**:\n"
                    for result in reranked:
                        if result.rerank_score > 0.6:
                            content_preview = result.content[:200] if result.content else ""
                            content_preview = content_preview.replace('\n', ' ').strip()
                            if content_preview:
                                sql_response += f"• {content_preview}...\n"
                
                logger.info(f"Intelligence Agent: Comparison completed in {time.time() - start_time:.2f}s")
        
        return sql_response
    
    def _log_reranking_event(self, query: str, initial_count: int, reranked_count: int):
        """Log reranking event for monitoring"""
        logger.info("=" * 60)
        logger.info("RERANKING EVENT - INTELLIGENCE AGENT")
        logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Query: {query}")
        logger.info(f"Initial Results: {initial_count}")
        logger.info(f"Reranked Results: {reranked_count}")
        logger.info(f"Agent: Intelligence (Enhanced)")
        logger.info("=" * 60)