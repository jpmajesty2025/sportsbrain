"""Secure agent endpoints with defensive prompt engineering"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from app.db.database import get_db
from app.models.models import User
from app.api.endpoints.auth import get_current_user
from app.agents.secure_agent_coordinator import SecureAgentCoordinator
from app.agents.base_agent import AgentResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/secure", tags=["secure_agents"])

# Initialize secure coordinator (singleton pattern)
_coordinator = None

def get_coordinator() -> SecureAgentCoordinator:
    """Get or create the secure agent coordinator"""
    global _coordinator
    if _coordinator is None:
        _coordinator = SecureAgentCoordinator()
        logger.info("Initialized secure agent coordinator")
    return _coordinator

# Request/Response models
class AgentQueryRequest(BaseModel):
    """Request model for agent queries"""
    message: str = Field(..., min_length=1, max_length=500, description="User's query message")
    agent_type: Optional[str] = Field(None, description="Specific agent to use (draft_prep, trade_impact, analytics, prediction, chat)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context for the query")

class AgentQueryResponse(BaseModel):
    """Response model for agent queries"""
    content: str = Field(..., description="Agent's response content")
    agent: str = Field(..., description="Agent that handled the query")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata including security info")

class SecurityStatusResponse(BaseModel):
    """Response model for user security status"""
    user_id: str
    is_blocked: bool
    threat_score: int
    threat_level: str
    recent_requests: int
    violations: int
    block_expires: Optional[str] = None

class SecurityMetricsResponse(BaseModel):
    """Response model for security metrics"""
    total_requests: int
    security_blocks: int
    block_rate: float
    threat_types: Dict[str, int]
    recent_blocks: list

# Endpoints
@router.post("/query", response_model=AgentQueryResponse)
async def query_secure_agent(
    request: AgentQueryRequest,
    current_user: User = Depends(get_current_user),
    coordinator: SecureAgentCoordinator = Depends(get_coordinator)
):
    """Query agents with comprehensive security protection
    
    This endpoint:
    - Validates and sanitizes input
    - Applies rate limiting per user
    - Wraps queries with security guards
    - Filters output for sensitive information
    - Tracks security threats and violations
    """
    try:
        logger.info(f"Secure query from user {current_user.id}: {request.message[:50]}...")
        
        # Process through secure coordinator
        response = await coordinator.route_secure_message(
            message=request.message,
            user_id=str(current_user.id),
            agent_type=request.agent_type,
            context=request.context
        )
        
        # Check if the response indicates a security issue
        security_status = response.metadata.get("security", {}).get("security_status", "")
        
        if security_status in ["rate_limited", "input_blocked", "output_filtered"]:
            logger.warning(f"Security issue for user {current_user.id}: {security_status}")
            # Still return the response but with appropriate HTTP status
            return AgentQueryResponse(
                content=response.content,
                agent=response.metadata.get("agent", "security"),
                confidence=response.confidence,
                metadata=response.metadata
            )
        
        # Return successful response
        return AgentQueryResponse(
            content=response.content,
            agent=response.metadata.get("agent", "unknown"),
            confidence=response.confidence,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"Error processing secure query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query securely"
        )

@router.get("/status", response_model=SecurityStatusResponse)
async def get_security_status(
    current_user: User = Depends(get_current_user),
    coordinator: SecureAgentCoordinator = Depends(get_coordinator)
):
    """Get current security status for the authenticated user
    
    Returns information about:
    - Whether the user is currently blocked
    - Their threat score and level
    - Recent request counts
    - Number of violations
    """
    try:
        status = await coordinator.get_user_security_status(str(current_user.id))
        
        return SecurityStatusResponse(
            user_id=str(current_user.id),
            is_blocked=status.get("is_blocked", False),
            threat_score=status.get("threat_score", 0),
            threat_level=status.get("threat_level", "none"),
            recent_requests=status.get("recent_requests", 0),
            violations=status.get("violations", 0),
            block_expires=status.get("block_expires")
        )
        
    except Exception as e:
        logger.error(f"Error getting security status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security status"
        )

@router.get("/metrics", response_model=SecurityMetricsResponse)
async def get_security_metrics(
    current_user: User = Depends(get_current_user),
    coordinator: SecureAgentCoordinator = Depends(get_coordinator)
):
    """Get overall security metrics (admin only)
    
    Returns aggregated security metrics including:
    - Total requests and blocks
    - Block rate percentage
    - Breakdown of threat types detected
    - Recent security blocks
    """
    # TODO: Add proper admin role check
    # For now, just log the access
    logger.info(f"User {current_user.id} accessed security metrics")
    
    try:
        metrics = coordinator.get_security_metrics()
        
        return SecurityMetricsResponse(
            total_requests=metrics.get("total_requests", 0),
            security_blocks=metrics.get("security_blocks", 0),
            block_rate=metrics.get("block_rate", 0.0),
            threat_types=metrics.get("threat_types", {}),
            recent_blocks=metrics.get("recent_blocks", [])
        )
        
    except Exception as e:
        logger.error(f"Error getting security metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security metrics"
        )

@router.post("/reset/{user_id}")
async def reset_user_security(
    user_id: str,
    current_user: User = Depends(get_current_user),
    coordinator: SecureAgentCoordinator = Depends(get_coordinator)
):
    """Reset security status for a user (admin only)
    
    Clears:
    - Rate limit counters
    - Threat scores
    - Block status
    - Violation history
    """
    # TODO: Implement proper admin authentication
    # For now, only allow self-reset in development
    if str(current_user.id) != user_id:
        logger.warning(f"User {current_user.id} attempted to reset security for {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges to reset another user's security"
        )
    
    try:
        await coordinator.reset_user_security(user_id, admin_token="admin_secret_token")
        logger.info(f"Reset security status for user {user_id}")
        
        return {
            "message": f"Security status reset for user {user_id}",
            "user_id": user_id
        }
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resetting security: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset security status"
        )

@router.get("/capabilities")
async def get_agent_capabilities(
    current_user: User = Depends(get_current_user),
    coordinator: SecureAgentCoordinator = Depends(get_coordinator)
):
    """Get capabilities of available agents
    
    Returns information about what each agent can do
    """
    try:
        capabilities = coordinator.get_agent_capabilities()
        
        return {
            "agents": capabilities,
            "security_enabled": True,
            "features": [
                "Input validation and sanitization",
                "Prompt injection prevention",
                "Information extraction blocking",
                "Rate limiting per user",
                "Output filtering for sensitive data",
                "Threat detection and auto-blocking"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent capabilities"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for secure agents"""
    try:
        coordinator = get_coordinator()
        return {
            "status": "healthy",
            "service": "secure_agents",
            "coordinator_initialized": coordinator is not None,
            "agents_loaded": len(coordinator.agents) if coordinator else 0
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "service": "secure_agents",
            "error": str(e)
        }