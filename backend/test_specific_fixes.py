"""Test specific fixes for the 5 errors"""
import asyncio
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
from app.agents.draft_prep_agent_tools import DraftPrepAgent
from app.agents.trade_impact_agent_tools import TradeImpactAgent

async def test_fixes():
    print("Testing specific fixes...\n")
    
    # Initialize agents
    intel_agent = IntelligenceAgentEnhanced()
    draft_agent = DraftPrepAgent()
    trade_agent = TradeImpactAgent()
    
    tests = [
        # Error 1: Type error in analyze_player_stats (SHOULD BE FIXED)
        ("Intelligence", intel_agent, "What are Scoot Henderson's stats?"),
        
        # Error 2: Compare players with "and" (SHOULD BE FIXED)
        ("Intelligence", intel_agent, "Compare Scottie Barnes and Paolo Banchero"),
        
        # Error 3: ADP query with full question (SHOULD BE FIXED)
        ("DraftPrep", draft_agent, "What's LaMelo Ball's ADP?"),
        
        # Error 4: Rounds 8-10 (SHOULD BE FIXED)
        ("DraftPrep", draft_agent, "Best sleepers in rounds 8-10"),
        
        # Error 5: OG trade (SHOULD BE FIXED)
        ("TradeImpact", trade_agent, "What's the usage rate change for Brunson after the OG trade?")
    ]
    
    for agent_name, agent, query in tests:
        print(f"\n[{agent_name}] Testing: {query}")
        print("-" * 50)
        try:
            response = await agent.process_message(query)
            if response.content:
                # Check for errors
                if "error" in response.content.lower():
                    print(f"❌ ERROR: {response.content[:200]}")
                else:
                    print(f"✅ SUCCESS: {response.content[:200]}...")
            else:
                print("❌ No response")
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_fixes())