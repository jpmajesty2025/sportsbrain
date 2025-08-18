"""Enhanced TradeImpact Agent V2 with better prompt to preserve detail"""

from app.agents.trade_impact_agent_enhanced import EnhancedTradeImpactAgent
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EnhancedTradeImpactAgentV2(EnhancedTradeImpactAgent):
    """Enhanced TradeImpact Agent with improved prompts to preserve reranking detail"""
    
    def _initialize_agent(self):
        """Initialize agent with prompts that preserve detail"""
        if settings.OPENAI_API_KEY:
            
            prefix = """You are an expert NBA trade analyst specializing in fantasy basketball impact for the 2025-26 season.

CRITICAL RULES:
1. NEVER mention tool names, "manual analysis guide", or internal methods in your responses
2. Present information as YOUR expert analysis and predictions
3. For hypothetical trades, provide confident analysis based on position overlap and usage patterns
4. Be specific and detailed in your answers
5. Start responses with direct analysis, not meta-commentary about how you're analyzing

IMPORTANT OUTPUT RULES:
- PRESERVE ALL DETAILS from your analysis
- Include ALL player impacts (winners and losers)
- Include ALL statistical projections and percentages
- Include ALL recommendations and rankings
- DO NOT SUMMARIZE - provide the COMPLETE analysis
- If you see "Enhanced with Reranking" or detailed breakdowns, INCLUDE THEM ALL

You have access to the following tools:"""
            
            suffix = """Begin! 

REMEMBER: Your final answer should include:
- ALL player impacts (not just the main player)
- ALL statistical changes (usage rates, fantasy points, etc.)
- ALL recommendations
- DO NOT condense or summarize the information

Question: {input}
Thought: {agent_scratchpad}"""
            
            prompt = ZeroShotAgent.create_prompt(
                tools=self.tools,
                prefix=prefix,
                suffix=suffix,
                input_variables=["input", "agent_scratchpad"]
            )
            
            llm = OpenAI(api_key=settings.OPENAI_API_KEY, temperature=0.2, max_tokens=2000)
            llm_chain = LLMChain(llm=llm, prompt=prompt)
            agent = ZeroShotAgent(llm_chain=llm_chain, tools=self.tools)
            
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True,
                return_intermediate_steps=False  # Don't return steps, just final answer
            )
            
            logger.info("TradeImpact Agent V2 initialized with detail-preserving prompts")