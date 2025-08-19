from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResponse
from .intelligence_agent_clean import CleanIntelligenceAgent as IntelligenceAgent  # Clean formatting + extended reranking
from .chat_agent import ChatAgent

# Try to import enhanced DraftPrep agent, fall back to base if needed
try:
    from .draft_prep_agent_enhanced import EnhancedDraftPrepAgent as DraftPrepAgent  # Enhanced with reranking
except ImportError:
    from .draft_prep_agent_tools import DraftPrepAgent  # Fallback to base version

from .trade_impact_agent_fixed import FixedTradeImpactAgent as TradeImpactAgent  # Fixed Milvus Hit access issue

class AgentCoordinator:
    def __init__(self) -> None:
        self.agents: Dict[str, BaseAgent] = {
            "draft_prep": DraftPrepAgent(),
            "trade_impact": TradeImpactAgent(),
            "intelligence": IntelligenceAgent(),  # Replaces analytics + prediction
            "chat": ChatAgent()
        }
        self.conversation_history: List[Dict[str, Any]] = []
    
    async def route_message(self, message: str, agent_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        if agent_type and agent_type in self.agents:
            selected_agent = self.agents[agent_type]
        else:
            selected_agent = self._select_best_agent(message)
        
        response = await selected_agent.process_message(message, context)
        
        # Store conversation history
        self.conversation_history.append({
            "message": message,
            "agent": selected_agent.name,
            "response": response.content,
            "timestamp": context.get("timestamp") if context else None
        })
        
        return response
    
    def _select_best_agent(self, message: str) -> BaseAgent:
        message_lower = message.lower()
        
        # Keywords for draft prep agent
        draft_keywords = [
            "draft", "keep", "keeper", "round", "adp", "value", "pick",
            "bust", "target", "avoid", "mock", "punt", "punting", "build"
        ]
        
        # Keywords for trade impact agent
        trade_keywords = [
            "trade", "traded", "affect", "impact", "porzingis", "lillard",
            "acquire", "deal", "swap", "move", "transaction", "usage"
        ]
        
        # Keywords for intelligence agent (analytics + prediction combined)
        intelligence_keywords = [
            "analyze", "statistics", "stats", "performance", "compare",
            "metrics", "data", "trend", "breakdown", "predict", "forecast",
            "odds", "probability", "outcome", "future", "likely", "expect",
            "projection", "breakout", "sophomore", "consistency",
            "risk", "upside", "potential", "sleeper", "sleepers", "find"
        ]
        
        # Score each agent based on keyword presence
        draft_score = sum(1 for keyword in draft_keywords if keyword in message_lower)
        trade_score = sum(1 for keyword in trade_keywords if keyword in message_lower)
        intelligence_score = sum(1 for keyword in intelligence_keywords if keyword in message_lower)
        
        # Special cases for common queries
        if "find" in message_lower and "sleeper" in message_lower:
            # "Find sleepers" should go to Intelligence
            return self.agents["intelligence"]
        elif "punt" in message_lower and any(word in message_lower for word in ["strategy", "build", "ft", "fg", "assist"]):
            # Punt strategies should go to DraftPrep
            return self.agents["draft_prep"]
        
        # Select agent with highest score
        if trade_score > max(draft_score, intelligence_score):
            return self.agents["trade_impact"]
        elif draft_score >= intelligence_score and draft_score > 0:
            return self.agents["draft_prep"]
        else:
            # Default to Intelligence agent for analysis/general questions
            return self.agents["intelligence"]
    
    def get_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        return {
            agent_name: agent.get_capabilities() 
            for agent_name, agent in self.agents.items()
        }
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.conversation_history[-limit:]
    
    def clear_conversation_history(self) -> None:
        self.conversation_history.clear()
    
    def add_custom_agent(self, name: str, agent: BaseAgent) -> None:
        self.agents[name] = agent