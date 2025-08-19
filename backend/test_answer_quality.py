"""Test that TradeImpact agent gives focused, consistent answers"""

import os
import sys
import asyncio
import pytest
from pathlib import Path

# Skip this test file in CI to avoid downloading models
if os.getenv("CI") == "true":
    pytest.skip("Skipping model test in CI environment", allow_module_level=True)

sys.path.insert(0, str(Path(__file__).parent))

if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

async def check_query_with_detail(query: str):
    """Test a single query and analyze the response"""
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    agent = FixedTradeImpactAgent()
    
    # Reduce verbosity
    if hasattr(agent, 'agent_executor'):
        agent.agent_executor.verbose = False
    
    print(f"\n[QUERY]: {query}")
    print("-" * 60)
    
    try:
        response = await agent.process_message(query)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Clean for Windows display
        clean_content = content.encode('ascii', 'ignore').decode('ascii')
        
        print("RESPONSE:")
        print(clean_content)
        
        # Analyze response quality
        print("\n[ANALYSIS]:")
        
        # Check for specific player focus in "affect" queries
        if "affect" in query.lower():
            affected_player = query.lower().split("affect")[1].strip().split("?")[0].strip()
            if affected_player in content.lower():
                print(f"  [OK] Focuses on {affected_player}")
            else:
                print(f"  [ISSUE] Doesn't focus on {affected_player}")
        
        # Check for contradictions
        if "positive" in content.lower() and "negative" in content.lower():
            if "positive impact" in content.lower() and "negative impact" in content.lower():
                print("  [ISSUE] Contains contradictory assessments")
            else:
                print("  [OK] No major contradictions")
        else:
            print("  [OK] Consistent assessment")
        
        # Check for specific numbers
        has_percentage = "%" in content
        has_fantasy_points = "FP" in content or "fantasy point" in content.lower()
        
        if has_percentage:
            print("  [OK] Includes usage rate percentages")
        else:
            print("  [ISSUE] Missing specific percentages")
            
        if has_fantasy_points:
            print("  [OK] Includes fantasy point impacts")
        else:
            print("  [ISSUE] Missing fantasy point numbers")
        
        return content
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

async def main():
    print("=" * 60)
    print("TRADEIMPACT AGENT ANSWER QUALITY TEST")
    print("=" * 60)
    
    # Test the three problematic queries
    test_queries = [
        "How does Porzingis trade affect Tatum?",
        "Which players benefited from the Lillard to Bucks trade?",
        "How did Lillard trade affect Giannis usage rate?"
    ]
    
    for query in test_queries:
        await check_query_with_detail(query)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nThe agent should now:")
    print("1. Focus on the specific player being asked about")
    print("2. Give consistent assessments (not contradictory)")
    print("3. Include specific numbers (percentages and fantasy points)")
    print("4. Provide clear, focused answers")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    asyncio.run(main())