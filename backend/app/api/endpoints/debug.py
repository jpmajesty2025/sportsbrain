"""Debug endpoint to check reranking status"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/reranking-status")
async def check_reranking_status() -> Dict[str, Any]:
    """Check if reranking is properly initialized"""
    
    status = {
        "reranking_available": False,
        "agents_checked": {},
        "milvus_status": "unknown",
        "model_status": "unknown",
        "errors": []
    }
    
    try:
        # Check if we can import the enhanced agents
        try:
            from app.agents.intelligence_agent_enhanced_with_reranking import IntelligenceAgentWithReranking
            status["agents_checked"]["intelligence_enhanced"] = "imported"
            
            # Try to instantiate
            intel_agent = IntelligenceAgentWithReranking()
            if hasattr(intel_agent, 'reranker') and intel_agent.reranker is not None:
                status["agents_checked"]["intelligence_reranker"] = "initialized"
                if hasattr(intel_agent.reranker, 'model_loaded'):
                    status["agents_checked"]["intelligence_model"] = "loaded" if intel_agent.reranker.model_loaded else "failed"
            else:
                status["agents_checked"]["intelligence_reranker"] = "not initialized"
        except Exception as e:
            status["errors"].append(f"Intelligence agent: {str(e)}")
            
        try:
            from app.agents.trade_impact_agent_enhanced import EnhancedTradeImpactAgent
            status["agents_checked"]["trade_enhanced"] = "imported"
            
            # Try to instantiate
            trade_agent = EnhancedTradeImpactAgent()
            if hasattr(trade_agent, 'reranker') and trade_agent.reranker is not None:
                status["agents_checked"]["trade_reranker"] = "initialized"
                if hasattr(trade_agent.reranker, 'model_loaded'):
                    status["agents_checked"]["trade_model"] = "loaded" if trade_agent.reranker.model_loaded else "failed"
            else:
                status["agents_checked"]["trade_reranker"] = "not initialized"
        except Exception as e:
            status["errors"].append(f"Trade agent: {str(e)}")
        
        # Check if reranker service can be imported
        try:
            from app.services.reranker_service import ReRankerService
            status["agents_checked"]["reranker_service"] = "imported"
            
            # Try to instantiate
            reranker = ReRankerService()
            if reranker.model_loaded:
                status["model_status"] = "loaded"
                status["reranking_available"] = True
            else:
                status["model_status"] = "failed to load"
        except Exception as e:
            status["errors"].append(f"Reranker service: {str(e)}")
            
        # Check Milvus
        try:
            from pymilvus import connections, Collection
            from app.core.config import settings
            
            if settings.MILVUS_HOST and settings.MILVUS_TOKEN:
                connections.connect(
                    alias="test",
                    uri=settings.MILVUS_HOST,
                    token=settings.MILVUS_TOKEN
                )
                
                # Try to list collections
                from pymilvus import utility
                collections = utility.list_collections(using="test")
                status["milvus_status"] = f"connected ({len(collections)} collections)"
                
                # Check specific collections
                expected = ["sportsbrain_players", "sportsbrain_strategies", "sportsbrain_trades"]
                for coll_name in expected:
                    if coll_name in collections:
                        status["agents_checked"][f"milvus_{coll_name}"] = "exists"
                    else:
                        status["agents_checked"][f"milvus_{coll_name}"] = "missing"
                
                connections.disconnect("test")
            else:
                status["milvus_status"] = "no credentials"
        except Exception as e:
            status["milvus_status"] = f"error: {str(e)}"
            status["errors"].append(f"Milvus: {str(e)}")
            
        # Check current coordinator
        try:
            from app.agents.agent_coordinator import AgentCoordinator
            coord = AgentCoordinator()
            
            # Check what agents are loaded
            for agent_name, agent in coord.agents.items():
                agent_class = type(agent).__name__
                status["agents_checked"][f"coordinator_{agent_name}"] = agent_class
                
                # Check if they have rerankers
                if hasattr(agent, 'reranker'):
                    status["agents_checked"][f"{agent_name}_has_reranker"] = agent.reranker is not None
        except Exception as e:
            status["errors"].append(f"Coordinator: {str(e)}")
            
    except Exception as e:
        status["errors"].append(f"General error: {str(e)}")
    
    # Summary
    status["summary"] = {
        "reranking_enabled": status["reranking_available"],
        "issues_found": len(status["errors"]),
        "recommendation": ""
    }
    
    if not status["reranking_available"]:
        if "failed to load" in status["model_status"]:
            status["summary"]["recommendation"] = "BGE model failed to load - check if sentence-transformers is installed"
        elif status["milvus_status"] == "no credentials":
            status["summary"]["recommendation"] = "Milvus credentials not found in environment"
        elif status["errors"]:
            status["summary"]["recommendation"] = "Check errors list for specific issues"
        else:
            status["summary"]["recommendation"] = "Reranking components not properly initialized"
    else:
        status["summary"]["recommendation"] = "Reranking should be working - check agent responses"
    
    return status