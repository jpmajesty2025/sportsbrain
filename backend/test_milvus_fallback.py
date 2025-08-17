"""Test script to verify Milvus fallback behavior"""
import os
import sys
import logging

# Set up logging to see all output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force Milvus to fail by setting invalid host
print("\n=== Testing Milvus Fallback Behavior ===\n")
print("1. First, testing with VALID Milvus connection...")

# Import after path setup
from app.agents.trade_impact_agent_tools import TradeImpactAgent

# Test 1: With valid connection (if configured)
agent = TradeImpactAgent()
result1 = agent._search_trade_documents("Porzingis trade impact")
print(f"Result with valid config: {result1[:200]}...")

# Test 2: Force fallback
print("\n2. Now forcing Milvus to fail...")
os.environ['MILVUS_HOST'] = 'invalid_host_to_force_failure'
os.environ['MILVUS_TOKEN'] = 'invalid_token'

# Create new agent with invalid config
agent2 = TradeImpactAgent()
result2 = agent2._search_trade_documents("Porzingis trade impact")
print(f"Result with invalid config: {result2[:200]}...")

# Check if we got fallback message
if "Milvus connection not configured" in result2:
    print("\n[SUCCESS] CONFIRMED: Milvus fallback is triggered!")
    print("The agent returns 'Milvus connection not configured' message")
    print("This is happening SILENTLY in production without any logging!")
else:
    print("\n[UNEXPECTED] Milvus might be working or different fallback message")

# Test 3: Test the actual analyze_trade_impact method
print("\n3. Testing full analyze_trade_impact method...")
try:
    full_result = agent2.analyze_trade_impact("How does Porzingis trade affect Tatum?")
    print(f"Full analysis result: {full_result[:300]}...")
    
    # Check if it used fallback
    if "Based on PostgreSQL data" in full_result or "historical patterns" in full_result:
        print("\n[SUCCESS] The agent is using PostgreSQL fallback for analysis")
    else:
        print("\n[INFO] Cannot determine if fallback was used from the response")
        
except Exception as e:
    print(f"\n[ERROR] Error during full analysis: {e}")

print("\n=== Test Complete ===")
print("\nNext Steps:")
print("1. Add logging to track when fallbacks occur")
print("2. Implement reranking for better results")
print("3. Monitor fallback frequency in production")