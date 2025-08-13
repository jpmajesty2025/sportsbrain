#!/usr/bin/env python3
"""Test punt FT% strategy"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_punt_ft():
    agent = DraftPrepAgent()
    
    # Test just the tool directly first
    print("Testing build_punt_strategy tool directly...")
    result = agent._build_punt_strategy("punt FT%")
    print(f"Tool result: {result[:500]}...\n")
    
    # Now test through the agent
    print("Testing through agent...")
    response = await agent.process_message("Best punt FT% build")
    print(f"Agent response: {response.content[:500]}...")

if __name__ == "__main__":
    asyncio.run(test_punt_ft())