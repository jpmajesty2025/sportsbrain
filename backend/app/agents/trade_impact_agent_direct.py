"""Direct TradeImpact Agent that bypasses LangChain summarization"""

import logging
from typing import Optional, Dict, Any
from app.agents.trade_impact_agent_enhanced import EnhancedTradeImpactAgent
from app.agents.base_agent import AgentResponse

logger = logging.getLogger(__name__)

class DirectTradeImpactAgent(EnhancedTradeImpactAgent):
    """TradeImpact Agent that returns tool output directly without LangChain summarization"""
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process message and return the tool output directly"""
        
        # For trade impact queries, bypass LangChain and call the tool directly
        try:
            # Directly call the analyze_trade_impact tool
            result = self.analyze_trade_impact(message)
            
            # Return the full result without LangChain processing
            return AgentResponse(
                content=result,
                metadata={
                    "agent": "trade_impact_direct",
                    "bypassed_langchain": True,
                    "context": context
                },
                confidence=0.95
            )
        except Exception as e:
            logger.error(f"Direct trade impact failed: {e}, falling back to LangChain")
            # Fall back to parent's LangChain-based processing
            return await super().process_message(message, context)