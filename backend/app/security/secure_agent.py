"""Secure agent wrapper that applies all security layers"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from ..security.input_validator import InputValidator
from ..security.output_filter import OutputFilter
from ..security.rate_limiter import RateLimiter
from ..security.prompt_guards import wrap_user_query, create_safe_agent_prompt

logger = logging.getLogger(__name__)

class AgentResponse:
    """Standard response format for agents"""
    def __init__(self, content: str, confidence: float = 1.0, metadata: Optional[Dict] = None):
        self.content = content
        self.confidence = confidence
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

class SecureAgentWrapper:
    """Wraps any agent with comprehensive security layers"""
    
    # Shared rate limiter instance across all agents
    _rate_limiter = None
    
    @classmethod
    def get_rate_limiter(cls):
        """Get or create shared rate limiter instance"""
        if cls._rate_limiter is None:
            cls._rate_limiter = RateLimiter()
        return cls._rate_limiter
    
    def __init__(self, agent):
        """Initialize secure wrapper
        
        Args:
            agent: The agent instance to wrap with security
        """
        self.agent = agent
        self.rate_limiter = self.get_rate_limiter()
        
        # Enhance agent's system prompt with security guards
        if hasattr(self.agent, 'system_prompt'):
            original_prompt = getattr(self.agent, 'system_prompt', '')
            self.agent.system_prompt = create_safe_agent_prompt(original_prompt)
            logger.info(f"Enhanced {agent.__class__.__name__} with security prompt guards")
    
    async def process_secure_message(
        self, 
        message: str, 
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process message with full security pipeline
        
        Args:
            message: User's query message
            user_id: Unique user identifier
            context: Optional context dictionary
            
        Returns:
            AgentResponse with filtered content and security metadata
        """
        
        security_metadata = {
            "checks_performed": [],
            "threats_detected": [],
            "security_status": "pending"
        }
        
        try:
            # 1. Rate limiting check
            logger.debug(f"Checking rate limit for user {user_id}")
            allowed, limit_msg = await self.rate_limiter.check_rate_limit(user_id)
            security_metadata["checks_performed"].append("rate_limit")
            
            if not allowed:
                logger.warning(f"Rate limit exceeded for user {user_id}: {limit_msg}")
                security_metadata["security_status"] = "rate_limited"
                return AgentResponse(
                    content=limit_msg or "Too many requests. Please wait before trying again.",
                    confidence=1.0,
                    metadata={"security": security_metadata}
                )
            
            # 2. Input validation and sanitization
            logger.debug(f"Validating input from user {user_id}")
            is_safe, sanitized, threats = InputValidator.validate_input(message)
            security_metadata["checks_performed"].append("input_validation")
            
            if threats:
                security_metadata["threats_detected"].extend(threats)
                
            if not is_safe and threats:
                logger.warning(f"Security threat detected from {user_id}: {threats}")
                await self.rate_limiter.report_threat(user_id, "prompt_injection", {"threats": threats})
                security_metadata["security_status"] = "input_blocked"
                return AgentResponse(
                    content="I can only help with fantasy basketball questions. Please rephrase your query about player stats, drafts, trades, or strategies.",
                    confidence=1.0,
                    metadata={"security": security_metadata}
                )
            
            # 3. Wrap query with security guards
            wrapped_query = wrap_user_query(sanitized)
            security_metadata["checks_performed"].append("query_wrapping")
            
            # 4. Process with the underlying agent
            logger.debug(f"Processing query with {self.agent.__class__.__name__}")
            try:
                # Check if agent has async process_message method
                if hasattr(self.agent, 'process_message'):
                    if asyncio.iscoroutinefunction(self.agent.process_message):
                        response = await self.agent.process_message(wrapped_query, context)
                    else:
                        response = self.agent.process_message(wrapped_query, context)
                # Fallback to invoke method for LangChain agents
                elif hasattr(self.agent, 'invoke'):
                    response_dict = await self.agent.invoke({"input": wrapped_query})
                    response = AgentResponse(
                        content=response_dict.get("output", ""),
                        confidence=0.9,
                        metadata=response_dict.get("metadata", {})
                    )
                else:
                    raise AttributeError(f"Agent {self.agent.__class__.__name__} has no process method")
                    
                # Ensure response is AgentResponse object
                if isinstance(response, str):
                    response = AgentResponse(content=response)
                elif isinstance(response, dict):
                    response = AgentResponse(
                        content=response.get("content", response.get("output", "")),
                        confidence=response.get("confidence", 0.9),
                        metadata=response.get("metadata", {})
                    )
                    
            except Exception as e:
                logger.error(f"Agent processing error for user {user_id}: {e}", exc_info=True)
                security_metadata["security_status"] = "processing_error"
                return AgentResponse(
                    content="I encountered an error processing your fantasy basketball question. Please try rephrasing it or ask about specific players, trades, or strategies.",
                    confidence=0.0,
                    metadata={"security": security_metadata, "error": str(e)}
                )
            
            # 5. Filter output for sensitive information
            logger.debug(f"Filtering output for user {user_id}")
            filtered_content, output_safe, leaks = OutputFilter.filter_output(
                response.content if hasattr(response, 'content') else str(response)
            )
            security_metadata["checks_performed"].append("output_filtering")
            
            if leaks:
                security_metadata["threats_detected"].extend([f"output_leak: {leak}" for leak in leaks])
                
            if not output_safe and leaks:
                logger.critical(f"Output filter caught leaks from {user_id}: {leaks}")
                await self.rate_limiter.report_threat(user_id, "info_extraction", {"leaks": leaks})
                security_metadata["security_status"] = "output_filtered"
                return AgentResponse(
                    content="I can only provide fantasy basketball analysis and recommendations.",
                    confidence=1.0,
                    metadata={"security": security_metadata}
                )
            
            # 6. Return filtered response with security metadata
            security_metadata["security_status"] = "passed"
            
            # Update response content and metadata
            if hasattr(response, 'content'):
                response.content = filtered_content
            else:
                response = AgentResponse(content=filtered_content)
                
            if hasattr(response, 'metadata'):
                if response.metadata:
                    response.metadata["security"] = security_metadata
                else:
                    response.metadata = {"security": security_metadata}
            
            logger.info(f"Successfully processed secure message for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Unexpected error in security pipeline for user {user_id}: {e}", exc_info=True)
            security_metadata["security_status"] = "system_error"
            return AgentResponse(
                content="I'm having trouble processing your request. Please try asking about fantasy basketball topics like player analysis, draft strategies, or trade recommendations.",
                confidence=0.0,
                metadata={"security": security_metadata, "error": str(e)}
            )
    
    async def get_user_security_status(self, user_id: str) -> dict:
        """Get security status for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with security status information
        """
        return await self.rate_limiter.get_user_status(user_id)
    
    async def reset_user_security(self, user_id: str):
        """Reset security status for a user (admin function)
        
        Args:
            user_id: User identifier
        """
        await self.rate_limiter.reset_user(user_id)
        logger.info(f"Reset security status for user {user_id}")

# Import asyncio for async checking
import asyncio