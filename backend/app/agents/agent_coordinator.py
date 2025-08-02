from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResponse
from .analytics_agent import AnalyticsAgent
from .prediction_agent import PredictionAgent
from .chat_agent import ChatAgent

class AgentCoordinator:
    def __init__(self) -> None:
        self.agents: Dict[str, BaseAgent] = {
            "analytics": AnalyticsAgent(),
            "prediction": PredictionAgent(),
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
        
        # Keywords for analytics agent
        analytics_keywords = [
            "analyze", "statistics", "stats", "performance", "compare", 
            "metrics", "data", "trend", "breakdown"
        ]
        
        # Keywords for prediction agent
        prediction_keywords = [
            "predict", "forecast", "odds", "probability", "outcome", 
            "future", "likely", "expect", "projection"
        ]
        
        # Score each agent based on keyword presence
        analytics_score = sum(1 for keyword in analytics_keywords if keyword in message_lower)
        prediction_score = sum(1 for keyword in prediction_keywords if keyword in message_lower)
        
        if analytics_score > prediction_score:
            return self.agents["analytics"]
        elif prediction_score > analytics_score:
            return self.agents["prediction"]
        else:
            # Default to chat agent for general questions
            return self.agents["chat"]
    
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