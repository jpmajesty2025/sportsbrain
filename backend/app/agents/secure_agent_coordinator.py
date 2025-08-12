"""Secure agent coordinator with defensive prompt engineering"""

from typing import Dict, Any, List, Optional
import logging

from .agent_coordinator import AgentCoordinator
from .base_agent import AgentResponse
from ..security.secure_agent import SecureAgentWrapper

logger = logging.getLogger(__name__)

class SecureAgentCoordinator(AgentCoordinator):
    """Agent coordinator with comprehensive security layers"""
    
    def __init__(self) -> None:
        """Initialize coordinator with security-wrapped agents"""
        super().__init__()
        
        # Wrap all agents with security layers
        logger.info("Initializing secure agent coordinator with security wrappers")
        for agent_name, agent in self.agents.items():
            self.agents[agent_name] = SecureAgentWrapper(agent)
            logger.info(f"Wrapped {agent_name} agent with security layers")
    
    async def route_secure_message(
        self, 
        message: str, 
        user_id: str,
        agent_type: Optional[str] = None, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Route message through security-enhanced agents
        
        Args:
            message: User's query message
            user_id: Unique user identifier for rate limiting
            agent_type: Optional specific agent to use
            context: Optional context dictionary
            
        Returns:
            AgentResponse with security metadata
        """
        # Select appropriate agent
        if agent_type and agent_type in self.agents:
            selected_agent = self.agents[agent_type]
            agent_name = agent_type
        else:
            # Use parent's selection logic
            base_agent = self._select_best_agent(message)
            # Find the wrapped version
            for name, agent in self.agents.items():
                if isinstance(agent, SecureAgentWrapper) and agent.agent == base_agent:
                    selected_agent = agent
                    agent_name = name
                    break
            else:
                # Fallback to first matching agent
                agent_name = next((name for name, agent in self.agents.items() 
                                  if getattr(agent, 'agent', agent).__class__.__name__ == base_agent.__class__.__name__), 
                                 "intelligence")  # Default to Intelligence agent instead of chat
                selected_agent = self.agents[agent_name]
        
        logger.info(f"Routing message from user {user_id} to {agent_name} agent")
        
        # Process through secure wrapper
        response = await selected_agent.process_secure_message(
            message=message,
            user_id=user_id,
            context=context
        )
        
        # Store conversation history with security metadata
        self.conversation_history.append({
            "message": message,
            "user_id": user_id,
            "agent": agent_name,
            "response": response.content,
            "security": response.metadata.get("security", {}),
            "timestamp": context.get("timestamp") if context else None
        })
        
        # Add agent info to response metadata
        if not response.metadata:
            response.metadata = {}
        response.metadata["agent"] = agent_name
        
        return response
    
    async def get_user_security_status(self, user_id: str) -> Dict[str, Any]:
        """Get security status for a user across all agents
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user's security status
        """
        # Get status from any wrapped agent (they share rate limiter)
        if self.agents:
            first_agent = next(iter(self.agents.values()))
            if isinstance(first_agent, SecureAgentWrapper):
                return await first_agent.get_user_security_status(user_id)
        
        return {
            "user_id": user_id,
            "status": "unknown",
            "message": "Security status unavailable"
        }
    
    async def reset_user_security(self, user_id: str, admin_token: Optional[str] = None):
        """Reset user's security status (requires admin privileges)
        
        Args:
            user_id: User identifier
            admin_token: Optional admin authentication token
        """
        # TODO: Verify admin token before allowing reset
        if admin_token != "admin_secret_token":  # Replace with proper admin auth
            logger.warning(f"Unauthorized attempt to reset security for user {user_id}")
            raise PermissionError("Admin privileges required")
        
        # Reset through any wrapped agent
        if self.agents:
            first_agent = next(iter(self.agents.values()))
            if isinstance(first_agent, SecureAgentWrapper):
                await first_agent.reset_user_security(user_id)
                logger.info(f"Admin reset security status for user {user_id}")
    
    def add_custom_agent(self, name: str, agent: Any) -> None:
        """Add a custom agent with security wrapping
        
        Args:
            name: Agent name
            agent: Agent instance to add
        """
        # Wrap with security before adding
        wrapped_agent = SecureAgentWrapper(agent)
        self.agents[name] = wrapped_agent
        logger.info(f"Added custom agent {name} with security wrapper")
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics from conversation history
        
        Returns:
            Dictionary with security metrics
        """
        total_requests = len(self.conversation_history)
        
        if total_requests == 0:
            return {
                "total_requests": 0,
                "security_blocks": 0,
                "block_rate": 0.0,
                "threat_types": {}
            }
        
        security_blocks = 0
        threat_types = {}
        
        for entry in self.conversation_history:
            security_data = entry.get("security", {})
            status = security_data.get("security_status", "")
            
            if status in ["rate_limited", "input_blocked", "output_filtered"]:
                security_blocks += 1
                
            threats = security_data.get("threats_detected", [])
            for threat in threats:
                threat_type = threat.split(":")[0] if ":" in threat else threat
                threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
        
        return {
            "total_requests": total_requests,
            "security_blocks": security_blocks,
            "block_rate": security_blocks / total_requests,
            "threat_types": threat_types,
            "recent_blocks": [
                {
                    "timestamp": entry.get("timestamp"),
                    "user_id": entry.get("user_id"),
                    "status": entry.get("security", {}).get("security_status"),
                    "threats": entry.get("security", {}).get("threats_detected", [])
                }
                for entry in self.conversation_history[-10:]
                if entry.get("security", {}).get("security_status") in 
                   ["rate_limited", "input_blocked", "output_filtered"]
            ]
        }