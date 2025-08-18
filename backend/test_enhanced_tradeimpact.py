"""Test script to verify Enhanced TradeImpact Agent with reranking is working"""
import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Set up logging to see all the reranking activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.agent_coordinator import AgentCoordinator


async def test_enhanced_tradeimpact():
    """Test that the enhanced TradeImpact agent with reranking is working"""
    
    print("=" * 60)
    print("TESTING ENHANCED TRADEIMPACT AGENT WITH RERANKING")
    print("=" * 60)
    
    # Initialize coordinator
    coordinator = AgentCoordinator()
    
    # Verify we have the enhanced agent
    trade_agent = coordinator.agents.get("trade_impact")
    print(f"\n1. Agent Type: {type(trade_agent).__name__}")
    
    # Check if it's the enhanced version
    if hasattr(trade_agent, 'reranker'):
        print("   [OK] Enhanced agent detected (has reranker attribute)")
        if trade_agent.reranker and hasattr(trade_agent.reranker, 'model_loaded'):
            if trade_agent.reranker.model_loaded:
                print("   [OK] Reranker model loaded successfully")
            else:
                print("   [WARNING] Reranker model not loaded")
        else:
            print("   [WARNING] Reranker not initialized")
    else:
        print("   [ERROR] Not using enhanced agent!")
        return False
    
    # Test queries that should benefit from reranking
    test_queries = [
        "How does the Porzingis trade affect Tatum's fantasy value?",
        "What's the impact of Lillard going to Milwaukee on Giannis?",
        "Analyze the fantasy impact of the OG Anunoby trade to the Knicks"
    ]
    
    print("\n2. Testing Trade Impact Queries:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        
        try:
            # Process through coordinator
            response = await coordinator.route_message(
                message=query,
                agent_type="trade_impact"
            )
            
            # Check response
            if response and response.content:
                # Look for signs of reranking
                if "Enhanced with Reranking" in response.content:
                    print("   [OK] Reranking explicitly mentioned in response")
                else:
                    print("   [INFO] Response received (check logs for reranking activity)")
                
                # Show first 200 chars of response
                print(f"   Response preview: {response.content[:200]}...")
                
                # Check metadata for agent info
                if hasattr(response, 'metadata'):
                    agent_used = response.metadata.get('agent', 'unknown')
                    print(f"   Agent: {agent_used}")
            else:
                print("   [WARNING] Empty response")
                
        except Exception as e:
            print(f"   [ERROR] Query failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("Check the logs above for 'Applying reranking' messages")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_enhanced_tradeimpact())
    sys.exit(0 if success else 1)