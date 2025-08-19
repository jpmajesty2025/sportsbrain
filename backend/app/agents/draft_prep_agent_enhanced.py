"""Enhanced DraftPrep Agent with Reranking Support"""

import logging
import time
from typing import Dict, Any, List, Optional
from app.agents.draft_prep_agent_tools import DraftPrepAgent
from app.agents.base_agent import AgentResponse
from app.services.reranker_service import ReRankerService
from sqlalchemy import text
from app.db.database import get_db

logger = logging.getLogger(__name__)

class EnhancedDraftPrepAgent(DraftPrepAgent):
    """Enhanced version with reranking for better recommendations"""
    
    def __init__(self):
        super().__init__()
        self.reranker = None
        self._init_reranker()
        
        # Initialize embedding model for vector search
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # 768 dims
            logger.info("Enhanced DraftPrep: Embedding model initialized")
        except Exception as e:
            logger.warning(f"Enhanced DraftPrep: Could not initialize embedding model: {e}")
            self.embedding_model = None
    
    def _init_reranker(self):
        """Initialize reranker (lazy loading)"""
        try:
            self.reranker = ReRankerService()
            logger.info("Enhanced DraftPrep: Reranker initialized successfully")
        except Exception as e:
            logger.warning(f"Enhanced DraftPrep: Could not initialize reranker: {e}")
            self.reranker = None
    
    def _search_strategy_documents(self, query: str, top_k: int = 20) -> List[Dict]:
        """Search strategy documents from Milvus with proper field access"""
        try:
            from pymilvus import connections, Collection
            from app.core.config import settings
            
            if not settings.MILVUS_HOST or not settings.MILVUS_TOKEN or not self.embedding_model:
                logger.warning(f"Enhanced DraftPrep: Milvus not configured for query: {query}")
                return []
            
            # Connect to Milvus (disconnect first if already connected)
            try:
                connections.disconnect("draft_prep")
            except:
                pass
            
            connections.connect(
                alias="draft_prep",
                uri=settings.MILVUS_HOST,
                token=settings.MILVUS_TOKEN
            )
            
            # Search strategies collection
            collection = Collection("sportsbrain_strategies", using="draft_prep")
            collection.load()
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            search_params = {
                "metric_type": "IP",  # Inner Product
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
                    # Fixed: Use correct Hit object access pattern
                    text_content = hit.entity.get('text') or ''
                    metadata_content = hit.entity.get('metadata') or {}
                    
                    documents.append({
                        'content': text_content,
                        'score': hit.score,
                        'metadata': metadata_content
                    })
            
            connections.disconnect("draft_prep")
            logger.info(f"Enhanced DraftPrep: Found {len(documents)} strategy documents")
            return documents
            
        except Exception as e:
            logger.error(f"Enhanced DraftPrep: Strategy search error: {e}")
            return []
    
    def _search_player_documents(self, query: str, top_k: int = 20) -> List[Dict]:
        """Search player documents from Milvus with proper field access"""
        try:
            from pymilvus import connections, Collection
            from app.core.config import settings
            
            if not settings.MILVUS_HOST or not settings.MILVUS_TOKEN or not self.embedding_model:
                logger.warning(f"Enhanced DraftPrep: Milvus not configured for query: {query}")
                return []
            
            # Connect to Milvus (disconnect first if already connected)
            try:
                connections.disconnect("draft_prep_players")
            except:
                pass
            
            connections.connect(
                alias="draft_prep_players",
                uri=settings.MILVUS_HOST,
                token=settings.MILVUS_TOKEN
            )
            
            # Search players collection
            collection = Collection("sportsbrain_players", using="draft_prep_players")
            collection.load()
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            search_params = {
                "metric_type": "IP",  # Inner Product
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
                    # Fixed: Use correct Hit object access pattern
                    text_content = hit.entity.get('text') or ''
                    metadata_content = hit.entity.get('metadata') or {}
                    
                    documents.append({
                        'content': text_content,
                        'score': hit.score,
                        'metadata': metadata_content
                    })
            
            connections.disconnect("draft_prep_players")
            logger.info(f"Enhanced DraftPrep: Found {len(documents)} player documents")
            return documents
            
        except Exception as e:
            logger.error(f"Enhanced DraftPrep: Player search error: {e}")
            return []
    
    def _build_punt_strategy(self, query: str) -> str:
        """Enhanced punt strategy with reranking"""
        start_time = time.time()
        logger.info(f"Enhanced DraftPrep: Building punt strategy for: {query}")
        
        # First get base SQL results (parent implementation)
        base_result = super()._build_punt_strategy(query)
        
        # If we have reranker and Milvus, enhance the results
        if self.reranker:
            try:
                # Search for relevant strategy documents
                strategy_docs = self._search_strategy_documents(
                    query=f"punt strategy {query}",
                    top_k=20
                )
                
                if strategy_docs and len(strategy_docs) > 1:
                    logger.info(f"Enhanced DraftPrep: Reranking {len(strategy_docs)} strategy documents")
                    
                    # Apply reranking
                    reranked = self.reranker.rerank(
                        query=query,
                        documents=strategy_docs,
                        top_k=3,
                        log_details=True
                    )
                    
                    # Add reranked insights to response
                    enhanced_response = base_result + "\n\n**📊 Enhanced Strategy Insights (AI-Powered)**:\n\n"
                    
                    for i, result in enumerate(reranked, 1):
                        content = result.content[:200] if result.content else "Strategy insight"
                        content = content.replace('\n', ' ').strip()
                        
                        enhanced_response += f"**{i}. Strategy Recommendation**\n"
                        enhanced_response += f"Relevance: {result.rerank_score:.2f}\n"
                        enhanced_response += f"{content}...\n\n"
                    
                    logger.info(f"Enhanced DraftPrep: Punt strategy completed in {time.time() - start_time:.2f}s")
                    return enhanced_response
                    
            except Exception as e:
                logger.error(f"Enhanced DraftPrep: Error enhancing punt strategy: {e}")
        
        # Return base result if no enhancement available
        return base_result
    
    def _simulate_draft_pick(self, query: str) -> str:
        """Enhanced mock draft with reranking for better recommendations"""
        start_time = time.time()
        logger.info(f"Enhanced DraftPrep: Simulating draft pick for: {query}")
        
        # First get base SQL results (parent implementation)
        base_result = super()._simulate_draft_pick(query)
        
        # If we have reranker and Milvus, enhance the results
        if self.reranker:
            try:
                # Extract pick number from query if present
                import re
                pick_match = re.search(r'pick (\d+)', query.lower())
                pick_context = f"draft pick {pick_match.group(1)}" if pick_match else "mock draft"
                
                # Search for relevant player documents
                player_docs = self._search_player_documents(
                    query=f"{pick_context} best available players fantasy basketball",
                    top_k=20
                )
                
                if player_docs and len(player_docs) > 1:
                    logger.info(f"Enhanced DraftPrep: Reranking {len(player_docs)} player profiles")
                    
                    # Apply reranking
                    reranked = self.reranker.rerank(
                        query=query,
                        documents=player_docs,
                        top_k=5,
                        log_details=True
                    )
                    
                    # Add reranked recommendations to response
                    enhanced_response = base_result + "\n\n**🎯 AI-Enhanced Draft Recommendations**:\n\n"
                    
                    for i, result in enumerate(reranked, 1):
                        # Parse player info from content if available
                        content = result.content if result.content else ""
                        
                        # Extract player name if in metadata
                        player_name = "Player"
                        if isinstance(result.metadata, dict) and 'player_name' in result.metadata:
                            player_name = result.metadata['player_name']
                        elif content:
                            # Try to extract from content (usually starts with player name)
                            player_name = content.split(',')[0].split(':')[0].strip()[:30]
                        
                        enhanced_response += f"**{i}. {player_name}**\n"
                        enhanced_response += f"Match Score: {result.rerank_score:.2f}\n"
                        
                        # Add brief insight
                        if len(content) > 50:
                            insight = content[50:150].replace('\n', ' ').strip()
                            enhanced_response += f"Insight: {insight}...\n"
                        
                        enhanced_response += "\n"
                    
                    logger.info(f"Enhanced DraftPrep: Mock draft completed in {time.time() - start_time:.2f}s")
                    return enhanced_response
                    
            except Exception as e:
                logger.error(f"Enhanced DraftPrep: Error enhancing mock draft: {e}")
        
        # Return base result if no enhancement available
        return base_result
    
    def _calculate_keeper_value(self, query: str) -> str:
        """Enhanced keeper value with strategic insights from vector search"""
        start_time = time.time()
        logger.info(f"Enhanced DraftPrep: Calculating keeper value for: {query}")
        
        # First get base SQL results (parent implementation)
        base_result = super()._calculate_keeper_value(query)
        
        # If we have reranker and Milvus, add strategic insights
        if self.reranker:
            try:
                # Search for keeper strategy insights
                strategy_docs = self._search_strategy_documents(
                    query=f"keeper value strategy {query}",
                    top_k=15
                )
                
                if strategy_docs and len(strategy_docs) > 1:
                    logger.info(f"Enhanced DraftPrep: Reranking {len(strategy_docs)} keeper insights")
                    
                    # Apply reranking
                    reranked = self.reranker.rerank(
                        query=query,
                        documents=strategy_docs,
                        top_k=2,
                        log_details=True
                    )
                    
                    # Add reranked insights to response
                    enhanced_response = base_result + "\n\n**💡 AI-Powered Keeper Insights**:\n\n"
                    
                    for i, result in enumerate(reranked, 1):
                        content = result.content[:250] if result.content else "Keeper strategy insight"
                        content = content.replace('\n', ' ').strip()
                        
                        enhanced_response += f"**Insight {i}** (Relevance: {result.rerank_score:.2f}):\n"
                        enhanced_response += f"{content}...\n\n"
                    
                    logger.info(f"Enhanced DraftPrep: Keeper value completed in {time.time() - start_time:.2f}s")
                    return enhanced_response
                    
            except Exception as e:
                logger.error(f"Enhanced DraftPrep: Error enhancing keeper value: {e}")
        
        # Return base result if no enhancement available
        return base_result
    
    def _get_adp_rankings(self, query: str) -> str:
        """Enhanced ADP rankings with similar player comparisons"""
        start_time = time.time()
        logger.info(f"Enhanced DraftPrep: Getting ADP rankings for: {query}")
        
        # First get base SQL results (parent implementation)
        base_result = super()._get_adp_rankings(query)
        
        # If we have reranker and query mentions specific players, find similar
        if self.reranker and any(word in query.lower() for word in ["compare", "vs", "versus", "similar"]):
            try:
                # Search for similar players
                player_docs = self._search_player_documents(
                    query=query,
                    top_k=15
                )
                
                if player_docs and len(player_docs) > 1:
                    logger.info(f"Enhanced DraftPrep: Reranking {len(player_docs)} similar players")
                    
                    # Apply reranking
                    reranked = self.reranker.rerank(
                        query=query,
                        documents=player_docs,
                        top_k=3,
                        log_details=True
                    )
                    
                    # Add similar players to response
                    enhanced_response = base_result + "\n\n**🔍 Similar Players by ADP (AI-Enhanced)**:\n\n"
                    
                    for i, result in enumerate(reranked, 1):
                        # Extract player info
                        content = result.content if result.content else ""
                        player_name = content.split(',')[0].split(':')[0].strip()[:30] if content else "Player"
                        
                        enhanced_response += f"**{i}. {player_name}**\n"
                        enhanced_response += f"Similarity Score: {result.rerank_score:.2f}\n"
                        
                        # Add ADP context if available
                        if "ADP" in content or "round" in content.lower():
                            adp_info = content[content.find("ADP"):content.find("ADP")+50] if "ADP" in content else ""
                            if adp_info:
                                enhanced_response += f"{adp_info.strip()}\n"
                        
                        enhanced_response += "\n"
                    
                    logger.info(f"Enhanced DraftPrep: ADP rankings completed in {time.time() - start_time:.2f}s")
                    return enhanced_response
                    
            except Exception as e:
                logger.error(f"Enhanced DraftPrep: Error enhancing ADP rankings: {e}")
        
        # Return base result if no enhancement available
        return base_result
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process message with potential reranking enhancements"""
        
        # Log that enhanced version is being used
        logger.info(f"Enhanced DraftPrep processing: {message[:50]}...")
        
        # Call parent's process_message which will route to our enhanced methods
        response = await super().process_message(message, context)
        
        # Add metadata to indicate if reranking was available
        if response.metadata:
            response.metadata["reranking_available"] = self.reranker is not None
        
        return response