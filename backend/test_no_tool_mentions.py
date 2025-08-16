"""Test that agents don't mention tools in responses"""
import asyncio
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
from app.agents.draft_prep_agent_tools import DraftPrepAgent
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_no_tool_mentions():
    print("Testing that agents don't mention tools in responses")
    print("=" * 80)
    
    # Test queries that often result in tool mentions
    test_cases = [
        {
            "agent": IntelligenceAgentEnhanced(),
            "query": "Find sleeper centers like Alperen Sengun",
            "name": "Intelligence Agent - Sleeper Query"
        },
        {
            "agent": DraftPrepAgent(), 
            "query": "Should I keep Ja Morant in round 3?",
            "name": "DraftPrep Agent - Keeper Query"
        },
        {
            "agent": TradeImpactAgent(),
            "query": "How does the Porzingis trade affect Tatum?",
            "name": "TradeImpact Agent - Trade Query"
        }
    ]
    
    # Words that should NOT appear in responses
    forbidden_words = [
        "tool", "action", "function", "using the", "based on my analysis using",
        "from the", "according to the", "the X tool", "my search"
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 80)
        print(f"Query: {test['query']}\n")
        
        response = await test['agent'].process_message(test['query'])
        print(f"Response: {response.content}\n")
        
        # Check for forbidden words
        response_lower = response.content.lower()
        violations = []
        for word in forbidden_words:
            if word in response_lower:
                violations.append(word)
        
        if violations:
            print(f"❌ FAILED: Response mentions: {violations}")
        else:
            print("✅ PASSED: No tool mentions found")

if __name__ == "__main__":
    asyncio.run(test_no_tool_mentions())