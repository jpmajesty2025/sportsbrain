"""Smarter Intelligence Agent that doesn't overthink"""

import sys
from typing import Optional, Dict, Any
from app.agents.intelligence_agent_complete import CompleteIntelligenceAgent
from app.agents.base_agent import AgentResponse

class SmarterIntelligenceAgent(CompleteIntelligenceAgent):
    """Smarter version that answers directly without overthinking"""
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Override to handle sleeper queries more efficiently"""
        
        message_lower = message.lower()
        
        # Direct handling for sleeper queries
        if "sleeper" in message_lower and ("center" in message_lower or "sengun" in message_lower):
            print("SMARTER: Detected sleeper center query, handling directly", file=sys.stderr)
            
            # Call the tool directly and return
            result = self._find_sleeper_candidates(message)
            
            # Don't let LangChain overthink it
            return AgentResponse(
                content=result,
                metadata={
                    "agent": "intelligence",
                    "method": "direct_sleeper_search",
                    "bypassed_chain": True
                },
                confidence=0.95
            )
        
        # For other queries, use normal LangChain flow
        return await super().process_message(message, context)