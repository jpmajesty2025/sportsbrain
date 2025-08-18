"""Force logging version of Intelligence Agent"""

import logging
from typing import Optional, Dict, Any
from app.agents.intelligence_agent import IntelligenceAgent
from app.agents.base_agent import AgentResponse

# Force logging to always show
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForceLogIntelligenceAgent(IntelligenceAgent):
    """Version that forces logging at every step"""
    
    def __init__(self):
        logger.info("FORCELOG: Initializing ForceLogIntelligenceAgent")
        super().__init__()
        logger.info(f"FORCELOG: Agent initialized with {len(self.tools)} tools")
        
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Override process_message to add logging"""
        logger.info(f"FORCELOG: process_message called with: {message[:100]}")
        
        # Log before calling parent
        logger.info("FORCELOG: Calling parent process_message")
        result = await super().process_message(message, context)
        
        # Log after
        logger.info(f"FORCELOG: Parent returned {len(result.content)} chars")
        
        return result
    
    def _find_sleeper_candidates(self, criteria: str = "") -> str:
        """The actual method that gets called by LangChain"""
        logger.info(f"FORCELOG: _find_sleeper_candidates called with criteria: {criteria}")
        
        # Call parent implementation
        result = super()._find_sleeper_candidates(criteria)
        
        logger.info(f"FORCELOG: Returning {len(result)} characters of sleeper data")
        
        # Check for Milvus
        logger.info("FORCELOG: Checking Milvus configuration...")
        try:
            from app.core.config import settings
            logger.info(f"FORCELOG: MILVUS_HOST = {settings.MILVUS_HOST[:30] if settings.MILVUS_HOST else 'NOT SET'}...")
            logger.info(f"FORCELOG: MILVUS_TOKEN = {'SET' if settings.MILVUS_TOKEN else 'NOT SET'}")
        except Exception as e:
            logger.error(f"FORCELOG: Error checking settings: {e}")
        
        # Add marker to response so we know this version is running
        if "FORCELOG_ACTIVE" not in result:
            result = f"[FORCELOG_ACTIVE]\n{result}"
        
        return result