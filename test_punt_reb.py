#!/usr/bin/env python3
"""Test punt REB strategy"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_punt_reb():
    agent = DraftPrepAgent()
    
    # Test punt REB
    print("Query: Best punt REB build")
    response = await agent.process_message("Best punt REB build")
    print(f"Response: {response.content}\n")

if __name__ == "__main__":
    asyncio.run(test_punt_reb())