#!/usr/bin/env python3
"""Test DraftPrep Agent parsing fix"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.draft_prep_agent_tools import DraftPrepAgent

async def test_punt_ast():
    agent = DraftPrepAgent()
    
    # First query
    print("Query 1: Best punt AST build")
    response1 = await agent.process_message("Best punt AST build")
    print(f"Response: {response1.content[:500]}...\n")
    
    # Follow-up query that was causing the error
    print("Query 2: Why are each of those players good choices for a punt AST build? Please elaborate a bit")
    response2 = await agent.process_message("Why are each of those players good choices for a punt AST build? Please elaborate a bit")
    print(f"Response: {response2.content[:500]}...")

if __name__ == "__main__":
    asyncio.run(test_punt_ast())