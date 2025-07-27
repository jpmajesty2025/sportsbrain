from typing import Dict, Any, List
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import Tool
from .base_agent import BaseAgent, AgentResponse
from app.core.config import settings

class ChatAgent(BaseAgent):
    def __init__(self):
        tools = [
            Tool(
                name="sports_qa",
                description="Answer general sports questions and provide explanations",
                func=self._answer_sports_question
            ),
            Tool(
                name="rule_explainer",
                description="Explain sports rules and regulations",
                func=self._explain_rules
            ),
            Tool(
                name="historical_lookup",
                description="Look up historical sports facts and records",
                func=self._lookup_historical_data
            )
        ]
        super().__init__(
            name="Chat Agent",
            description="Conversational agent for general sports questions and interactions",
            tools=tools
        )
    
    def _initialize_agent(self):
        if settings.OPENAI_API_KEY:
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.7)
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=True
            )
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        if not self.agent_executor:
            return AgentResponse(
                content="Chat agent not properly initialized. Please check OpenAI API key.",
                confidence=0.0
            )
        
        try:
            result = await self.agent_executor.arun(input=message)
            return AgentResponse(
                content=result,
                metadata={"context": context, "conversation_type": "sports_chat"},
                tools_used=[tool.name for tool in self.tools],
                confidence=0.9
            )
        except Exception as e:
            return AgentResponse(
                content=f"Error processing chat request: {str(e)}",
                confidence=0.0
            )
    
    def _get_supported_tasks(self) -> List[str]:
        return [
            "general_sports_questions",
            "rule_explanations", 
            "historical_facts",
            "player_information",
            "team_information",
            "casual_conversation"
        ]
    
    def _answer_sports_question(self, question: str) -> str:
        # Placeholder for sports Q&A
        return f"Answering sports question: {question}. This would provide comprehensive answers about sports topics."
    
    def _explain_rules(self, rule_query: str) -> str:
        # Placeholder for rule explanations
        return f"Explaining rules for: {rule_query}. This would provide detailed rule explanations with examples."
    
    def _lookup_historical_data(self, lookup_query: str) -> str:
        # Placeholder for historical data lookup
        return f"Looking up historical data: {lookup_query}. This would search historical records and provide relevant information."