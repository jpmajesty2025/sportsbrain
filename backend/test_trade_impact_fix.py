"""Test script to verify TradeImpact agent Milvus fix"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables if not already set
if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

async def test_trade_impact_agent():
    """Test the TradeImpact agent with Porzingis query"""
    print("Testing TradeImpact Agent with Milvus fix...")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    try:
        # Initialize the agent
        agent = FixedTradeImpactAgent()
        print("[OK] Agent initialized successfully")
        
        # Test query that was failing
        test_query = "How does Porzingis trade affect Tatum?"
        print(f"\nTest Query: {test_query}")
        print("-" * 40)
        
        # Process the message
        response = await agent.process_message(test_query)
        
        print("Response:")
        print(response.content if hasattr(response, 'content') else response)
        
        # Check if the error still occurs
        if "Hit.get()" in str(response):
            print("\n[X] ERROR: Hit.get() error still present!")
            return False
        else:
            print("\n[OK] SUCCESS: No Hit.get() error detected!")
            return True
            
    except Exception as e:
        print(f"\n[X] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_direct_milvus_search():
    """Test the _search_trade_documents method directly"""
    print("\n" + "=" * 60)
    print("Testing direct Milvus search method...")
    print("=" * 60)
    
    from app.agents.trade_impact_agent_fixed import FixedTradeImpactAgent
    
    try:
        agent = FixedTradeImpactAgent()
        
        # Test the fixed method directly
        result = agent._search_trade_documents("Porzingis trade impact")
        
        print("Direct search result:")
        print(result[:500] if result else "No results")
        
        if "Error searching Milvus: Hit.get()" in result:
            print("\n[X] ERROR: Hit.get() error in direct search!")
            return False
        else:
            print("\n[OK] SUCCESS: Direct search working!")
            return True
            
    except Exception as e:
        print(f"\n[X] ERROR in direct search: {e}")
        return False

async def main():
    """Run all tests"""
    print("TradeImpact Agent Milvus Fix Test")
    print("=" * 60)
    
    # Test 1: Direct search
    test1_result = await test_direct_milvus_search()
    
    # Test 2: Full agent
    test2_result = await test_trade_impact_agent()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"Direct Milvus Search: {'[OK] PASSED' if test1_result else '[X] FAILED'}")
    print(f"Full Agent Test: {'[OK] PASSED' if test2_result else '[X] FAILED'}")
    print("=" * 60)
    
    if test1_result and test2_result:
        print("\n[SUCCESS] All tests passed! The fix is working!")
        print("\nNext steps:")
        print("1. Deploy to Railway")
        print("2. Monitor logs to confirm no more Hit.get() errors")
        print("3. Update reranking_status.md")
    else:
        print("\n[WARNING] Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    asyncio.run(main())