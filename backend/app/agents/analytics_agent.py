from typing import Dict, Any, List
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import Tool
from .base_agent import BaseAgent, AgentResponse
from app.core.config import settings

class AnalyticsAgent(BaseAgent):
    def __init__(self):
        tools = [
            Tool(
                name="player_stats_analyzer",
                description="Analyze player statistics and performance metrics",
                func=self._analyze_player_stats
            ),
            Tool(
                name="team_performance_analyzer", 
                description="Analyze team performance and trends",
                func=self._analyze_team_performance
            ),
            Tool(
                name="game_analytics",
                description="Provide detailed game analysis and insights",
                func=self._analyze_game
            )
        ]
        super().__init__(
            name="Analytics Agent",
            description="Specialized agent for sports data analysis and statistical insights",
            tools=tools
        )
    
    def _initialize_agent(self):
        if settings.OPENAI_API_KEY:
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.1)
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        if not self.agent_executor:
            return AgentResponse(
                content="Analytics agent not properly initialized. Please check OpenAI API key.",
                confidence=0.0
            )
        
        try:
            result = await self.agent_executor.arun(input=message)
            return AgentResponse(
                content=result,
                metadata={"context": context},
                tools_used=[tool.name for tool in self.tools],
                confidence=0.8
            )
        except Exception as e:
            return AgentResponse(
                content=f"Error processing analytics request: {str(e)}",
                confidence=0.0
            )
    
    def _get_supported_tasks(self) -> List[str]:
        return [
            "player_performance_analysis",
            "team_statistics",
            "comparative_analysis",
            "trend_identification",
            "performance_metrics"
        ]
    
    def _analyze_player_stats(self, player_info: str) -> str:
        # Placeholder for actual player stats analysis
        return f"Analyzing player statistics for: {player_info}. This would connect to the database and perform statistical analysis."
    
    def _analyze_team_performance(self, team_info: str) -> str:
        # Placeholder for team performance analysis
        return f"Analyzing team performance for: {team_info}. This would analyze team metrics, win rates, and performance trends."
    
    def _analyze_game(self, game_info: str) -> str:
        # Placeholder for game analysis
        return f"Analyzing game: {game_info}. This would provide detailed game breakdown and key insights."