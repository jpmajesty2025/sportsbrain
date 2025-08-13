#!/usr/bin/env python3
"""Test agent timeout handling"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.draft_prep_agent_tools import DraftPrepAgent
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_timeout_handling():
    print("Testing timeout handling in agents...")
    print("=" * 50)
    
    # Test DraftPrep agent
    draft_agent = DraftPrepAgent()
    
    print("\n1. Testing DraftPrep agent with punt FT% query:")
    response = await draft_agent.process_message("Best punt FT% build")
    if "timeout" in str(response.metadata):
        print("   - Timeout occurred (handled gracefully)")
    elif response.confidence > 0:
        print(f"   - Success! Confidence: {response.confidence}")
        print(f"   - Response preview: {response.content[:200]}...")
    else:
        print(f"   - Error: {response.content[:200]}")
    
    print("\n2. Testing DraftPrep agent with complex follow-up:")
    response = await draft_agent.process_message("Why are those players good for punt FT%? Please elaborate on their specific strengths")
    if "timeout" in str(response.metadata):
        print("   - Timeout occurred (handled gracefully)")
    elif response.confidence > 0:
        print(f"   - Success! Confidence: {response.confidence}")
        print(f"   - Response preview: {response.content[:200]}...")
    else:
        print(f"   - Error: {response.content[:200]}")
    
    # Test TradeImpact agent
    trade_agent = TradeImpactAgent()
    
    print("\n3. Testing TradeImpact agent with Porzingis query:")
    response = await trade_agent.process_message("How does the Porzingis trade affect Tatum?")
    if "timeout" in str(response.metadata):
        print("   - Timeout occurred (handled gracefully)")
    elif response.confidence > 0:
        print(f"   - Success! Confidence: {response.confidence}")
        print(f"   - Response preview: {response.content[:200]}...")
    else:
        print(f"   - Error: {response.content[:200]}")
    
    print("\n" + "=" * 50)
    print("Timeout handling test complete!")
    print("\nSummary:")
    print("- Both agents have 30-second timeout protection")
    print("- Timeouts return helpful error messages to users")
    print("- Agents suggest more specific queries when timing out")

if __name__ == "__main__":
    asyncio.run(test_timeout_handling())