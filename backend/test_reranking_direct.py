"""Direct test of reranking functionality in TradeImpact agent"""
import logging
import sys
import os
from dotenv import load_dotenv

# Set up logging to see reranking activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.trade_impact_agent_enhanced import EnhancedTradeImpactAgent


def test_direct_reranking():
    """Test reranking directly without going through LangChain"""
    
    print("=" * 60)
    print("DIRECT TEST OF RERANKING IN TRADEIMPACT AGENT")
    print("=" * 60)
    
    # Initialize enhanced agent
    agent = EnhancedTradeImpactAgent()
    
    # Check reranker status
    print(f"\n1. Reranker Status:")
    print(f"   - Reranker initialized: {agent.reranker is not None}")
    if agent.reranker:
        print(f"   - Model loaded: {agent.reranker.model_loaded}")
    
    # Test the analyze_trade_impact method directly
    query = "How does the Porzingis trade affect Tatum's fantasy value?"
    
    print(f"\n2. Testing query: {query}")
    print("-" * 40)
    
    try:
        # Call the enhanced analyze_trade_impact method
        result = agent.analyze_trade_impact(query)
        
        # Check if reranking was mentioned
        if "Enhanced with Reranking" in result:
            print("   [OK] Reranking was applied!")
        else:
            print("   [INFO] Check logs for reranking activity")
        
        # Show result preview
        print(f"\n3. Result preview (first 500 chars):")
        print("-" * 40)
        print(result[:500])
        
    except Exception as e:
        print(f"   [ERROR] Query failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_direct_reranking()