"""Test friendly error messages"""
import asyncio
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
from app.agents.draft_prep_agent_tools import DraftPrepAgent
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_friendly_errors():
    print("Testing friendly error messages for timeouts/iteration limits\n")
    print("=" * 80)
    
    # Test queries that often cause timeouts or iteration limits
    test_cases = [
        {
            "agent": IntelligenceAgentEnhanced(),
            "query": "Compare all point guards and shooting guards from last season and find the best sleepers",
            "name": "Intelligence Agent - Complex Multi-Player Query"
        },
        {
            "agent": DraftPrepAgent(),
            "query": "Give me a complete mock draft for all 10 rounds with analysis",
            "name": "DraftPrep Agent - Complex Mock Draft"
        },
        {
            "agent": TradeImpactAgent(),
            "query": "Analyze all hypothetical trades between all teams",
            "name": "TradeImpact Agent - Overly Broad Query"
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 80)
        print(f"Query: {test['query']}\n")
        
        # Set a short timeout to force error messages
        try:
            response = await asyncio.wait_for(
                test['agent'].process_message(test['query']),
                timeout=5.0  # 5 second timeout to trigger error
            )
            print(f"Response: {response.content}\n")
        except asyncio.TimeoutError:
            print("Timed out as expected - checking error message from agent...\n")
            # Now let the agent handle it normally
            response = await test['agent'].process_message(test['query'])
            print(f"Error Message: {response.content}\n")
            print(f"Metadata: {response.metadata}\n")

if __name__ == "__main__":
    asyncio.run(test_friendly_errors())