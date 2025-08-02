from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain.schema import BaseMessage
from pydantic import BaseModel

class AgentResponse(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    tools_used: Optional[List[str]] = None
    confidence: Optional[float] = None

class BaseAgent(ABC):
    def __init__(self, name: str, description: str, tools: Optional[List[BaseTool]] = None):
        self.name = name
        self.description = description
        self.tools = tools or []
        self.agent_executor: Optional[AgentExecutor] = None
        self._initialize_agent()
    
    @abstractmethod
    def _initialize_agent(self):
        pass
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        pass
    
    def add_tool(self, tool: BaseTool):
        self.tools.append(tool)
        self._initialize_agent()
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tools": [tool.name for tool in self.tools],
            "supported_tasks": self._get_supported_tasks()
        }
    
    @abstractmethod
    def _get_supported_tasks(self) -> List[str]:
        pass