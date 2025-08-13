#!/usr/bin/env python3
"""Test punt FT% to see the actual error"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_punt_ft():
    agent = DraftPrepAgent()
    
    print("Testing: 'Best punt FT% build'")
    print("-" * 40)
    
    # First test the tool directly
    print("\n1. Testing tool directly:")
    try:
        result = agent._build_punt_strategy("punt FT%")
        print(f"Tool works! Result: {result[:200]}...")
    except Exception as e:
        print(f"Tool error: {e}")
    
    # Now test through the agent (this is what's failing)
    print("\n2. Testing through agent:")
    try:
        response = await agent.process_message("Best punt FT% build")
        print(f"Response confidence: {response.confidence}")
        print(f"Response metadata: {response.metadata}")
        print(f"Response content: {response.content}")
    except Exception as e:
        print(f"Agent error: {e}")

if __name__ == "__main__":
    asyncio.run(test_punt_ft())