from typing import Dict, Any, List, Optional
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import Tool
from .base_agent import BaseAgent, AgentResponse
from app.core.config import settings

class PredictionAgent(BaseAgent):
    def __init__(self):
        tools = [
            Tool(
                name="game_outcome_predictor",
                description="Predict game outcomes based on historical data and current form",
                func=self._predict_game_outcome
            ),
            Tool(
                name="player_performance_predictor",
                description="Predict individual player performance for upcoming games",
                func=self._predict_player_performance
            ),
            Tool(
                name="season_predictor",
                description="Predict season outcomes and playoff probabilities",
                func=self._predict_season_outcomes
            )
        ]
        super().__init__(
            name="Prediction Agent",
            description="Specialized agent for sports predictions and forecasting",
            tools=tools
        )
    
    def _initialize_agent(self):
        if settings.OPENAI_API_KEY:
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.3)
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        if not self.agent_executor:
            return AgentResponse(
                content="Prediction agent not properly initialized. Please check OpenAI API key.",
                confidence=0.0
            )
        
        try:
            result = await self.agent_executor.arun(input=message)
            return AgentResponse(
                content=result,
                metadata={"context": context, "prediction_type": "sports_forecast"},
                tools_used=[tool.name for tool in self.tools],
                confidence=0.7  # Predictions inherently less certain
            )
        except Exception as e:
            return AgentResponse(
                content=f"Error processing prediction request: {str(e)}",
                confidence=0.0
            )
    
    def _get_supported_tasks(self) -> List[str]:
        return [
            "game_outcome_prediction",
            "player_performance_forecast",
            "season_predictions",
            "playoff_probability",
            "injury_risk_assessment"
        ]
    
    def _predict_game_outcome(self, game_info: str) -> str:
        # Placeholder for game outcome prediction
        return f"Predicting outcome for game: {game_info}. This would use ML models trained on historical data to predict win probabilities."
    
    def _predict_player_performance(self, player_info: str) -> str:
        # Placeholder for player performance prediction
        return f"Predicting performance for player: {player_info}. This would forecast statistics based on recent form and matchup analysis."
    
    def _predict_season_outcomes(self, season_info: str) -> str:
        # Placeholder for season prediction
        return f"Predicting season outcomes for: {season_info}. This would project final standings and playoff probabilities."