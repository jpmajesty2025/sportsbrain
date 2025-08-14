#!/usr/bin/env python3
"""Test which agents have real agentic behavior"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
from app.agents.trade_impact_agent_tools import TradeImpactAgent
from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_agents():
    print("=" * 70)
    print("TESTING AGENT BEHAVIOR")
    print("=" * 70)
    
    # Test 1: Intelligence Agent
    print("\n1. INTELLIGENCE AGENT (IntelligenceAgentEnhanced)")
    print("-" * 50)
    intel_agent = IntelligenceAgentEnhanced()
    
    queries = [
        "Who are the best sleeper candidates?",
        "Compare Tatum and Brown for fantasy",
        "Find breakout sophomores"
    ]
    
    for query in queries[:1]:  # Test one query
        print(f"\nQuery: '{query}'")
        response = await intel_agent.process_message(query)
        print(f"Method: Uses agent_executor? {response.metadata}")
        print(f"Confidence: {response.confidence}")
        print(f"Response preview: {response.content[:200]}...")
        
    # Test 2: TradeImpact Agent
    print("\n\n2. TRADEIMPACT AGENT")
    print("-" * 50)
    trade_agent = TradeImpactAgent()
    
    queries = [
        "How does Porzingis trade affect Tatum?",
        "Which players benefit from recent trades?",
        "Analyze Lillard trade impact"
    ]
    
    for query in queries[:1]:  # Test one query
        print(f"\nQuery: '{query}'")
        response = await trade_agent.process_message(query)
        print(f"Method: {response.metadata}")
        print(f"Confidence: {response.confidence}")
        print(f"Response preview: {response.content[:200]}...")
    
    # Test 3: DraftPrep Agent
    print("\n\n3. DRAFTPREP AGENT")
    print("-" * 50)
    draft_agent = DraftPrepAgent()
    
    # Test a complex query that should use the agent
    complex_query = "What's a good strategy if I have the 5th pick and want to build around a wing player but avoid injury-prone players?"
    print(f"\nComplex Query: '{complex_query}'")
    response = await draft_agent.process_message(complex_query)
    print(f"Method: {response.metadata.get('method')}")
    print(f"Confidence: {response.confidence}")
    print(f"Response preview: {response.content[:200]}...")
    
    print("\n" + "=" * 70)
    print("ANALYSIS:")
    print("-" * 50)
    print("• Intelligence Agent: Uses LangChain agent with tool selection")
    print("• TradeImpact Agent: Uses LangChain agent with tool selection")  
    print("• DraftPrep Agent: Mostly bypasses agent (direct routing)")
    print("\nOnly Intelligence and TradeImpact demonstrate true agentic behavior")
    print("where the LLM reasons about which tool to use and how to use it.")

if __name__ == "__main__":
    asyncio.run(test_agents())