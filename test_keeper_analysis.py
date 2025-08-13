#!/usr/bin/env python3
"""Test keeper analysis to see what tool returns vs agent output"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_keeper():
    agent = DraftPrepAgent()
    
    query = "Should I keep Ja Morant in round 3?"
    print(f"Query: {query}")
    print("=" * 60)
    
    # Test tool directly
    print("\n1. TOOL OUTPUT (what it should return):")
    print("-" * 40)
    tool_result = agent._calculate_keeper_value(query)
    print(tool_result)
    
    # Test through agent
    print("\n2. AGENT OUTPUT (what user actually sees):")
    print("-" * 40)
    response = await agent.process_message(query)
    print(response.content)
    
    print("\n3. ANALYSIS:")
    print("-" * 40)
    print("The tool provides detailed analysis with:")
    print("- Player stats and ADP")
    print("- Value analysis with round advantage")
    print("- Specific recommendation with reasoning")
    print("\nBut the agent strips all this detail and returns a generic summary!")

if __name__ == "__main__":
    asyncio.run(test_keeper())