"""Test Scoot Henderson directly"""
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

agent = IntelligenceAgentEnhanced()

# Call the tool directly
print("Direct tool call for Scoot Henderson:")
print("-" * 50)
try:
    result = agent._analyze_player_stats_enhanced("Scoot Henderson")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()