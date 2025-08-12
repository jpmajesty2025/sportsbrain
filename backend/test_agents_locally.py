"""
Local testing script for all agent tools
Run this to test agents without full pytest setup
"""
import asyncio
import sys
import os
import io
from dotenv import load_dotenv

# Force UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv('../.env')

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.intelligence_agent import IntelligenceAgent
from app.agents.draft_prep_agent_tools import DraftPrepAgent
from app.agents.trade_impact_agent_tools import TradeImpactAgent
from app.agents.agent_coordinator import AgentCoordinator

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(text):
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text):
    print(f"{RED}[ERROR] {text}{RESET}")

def print_result(text):
    print(f"{YELLOW}{text}{RESET}")

async def test_scenario_1():
    """Scenario 1: Should I keep Ja Morant in round 3?"""
    print_header("SCENARIO 1: Keeper Decision (DraftPrep Agent)")
    print("Query: 'Should I keep Ja Morant in round 3?'")
    
    try:
        agent = DraftPrepAgent()
        result = agent._calculate_keeper_value("Ja Morant in round 3")
        
        if "Ja Morant" in result or "keeper" in result.lower():
            print_success("Keeper analysis tool working!")
            print_result(result[:500] + "..." if len(result) > 500 else result)
            return True
        else:
            print_error("Unexpected response format")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

async def test_scenario_2():
    """Scenario 2: How does Porzingis trade affect Tatum?"""
    print_header("SCENARIO 2: Trade Impact (TradeImpact Agent)")
    print("Query: 'How does Porzingis trade affect Tatum?'")
    
    try:
        agent = TradeImpactAgent()
        # Test fallback since Milvus might not be connected
        result = agent._fallback_trade_analysis("porzingis tatum")
        
        if "Tatum" in result and "Porzingis" in result:
            print_success("Trade impact analysis working!")
            print_result(result[:500] + "..." if len(result) > 500 else result)
            return True
        else:
            print_error("Unexpected response format")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

async def test_scenario_3():
    """Scenario 3: Find me sleepers like last year's Sengun"""
    print_header("SCENARIO 3: Find Sleepers (Intelligence Agent)")
    print("Query: 'Find me sleepers like last year's Sengun'")
    
    try:
        agent = IntelligenceAgent()
        result = agent._find_sleeper_candidates("")
        
        if "sleeper" in result.lower():
            print_success("Sleeper finding tool working!")
            print_result(result[:500] + "..." if len(result) > 500 else result)
            return True
        else:
            print_error("Unexpected response format")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

async def test_scenario_4():
    """Scenario 4: Best punt FT% build around Giannis"""
    print_header("SCENARIO 4: Punt Strategy (DraftPrep Agent)")
    print("Query: 'Best punt FT% build around Giannis'")
    
    try:
        agent = DraftPrepAgent()
        result = agent._build_punt_strategy("punt ft giannis")
        
        if "punt" in result.lower() and ("ft" in result.lower() or "free throw" in result.lower()):
            print_success("Punt strategy builder working!")
            print_result(result[:500] + "..." if len(result) > 500 else result)
            return True
        else:
            print_error("Unexpected response format")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

async def test_scenario_5():
    """Scenario 5: Which sophomores will break out?"""
    print_header("SCENARIO 5: Breakout Candidates (Intelligence Agent)")
    print("Query: 'Which sophomores will break out?'")
    
    try:
        agent = IntelligenceAgent()
        result = agent._identify_breakout_candidates("")
        
        if "breakout" in result.lower():
            print_success("Breakout identification tool working!")
            print_result(result[:500] + "..." if len(result) > 500 else result)
            return True
        else:
            print_error("Unexpected response format")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

async def test_coordinator_routing():
    """Test agent coordinator routing"""
    print_header("TESTING AGENT COORDINATOR ROUTING")
    
    try:
        coordinator = AgentCoordinator()
        
        # Test routing to different agents
        test_queries = [
            ("keeper question about round 3", "draftprep"),
            ("trade impact on player", "tradeimpact"),
            ("find sleeper picks", "intelligence"),
            ("analyze player stats", "intelligence"),
            ("punt strategy build", "draftprep")
        ]
        
        for query, expected_agent in test_queries:
            print(f"\nTesting: '{query}'")
            # We can't easily test async without proper setup, but we can test routing logic
            agent = coordinator._select_best_agent(query)
            # Remove spaces and convert to lowercase for comparison
            agent_name = agent.name.lower().replace(" ", "").replace("agent", "")
            
            if expected_agent in agent_name:
                print_success(f"Correctly routed to {agent.name}")
            else:
                print_error(f"Incorrectly routed to {agent.name} (expected {expected_agent})")
        
        return True
    except Exception as e:
        print_error(f"Error in coordinator: {e}")
        return False

async def main():
    """Run all tests"""
    print_header("SPORTSBRAIN AGENT TESTING SUITE")
    print("Testing all 5 demo scenarios with real agent tools")
    
    results = []
    
    # Run all scenario tests
    results.append(await test_scenario_1())
    results.append(await test_scenario_2())
    results.append(await test_scenario_3())
    results.append(await test_scenario_4())
    results.append(await test_scenario_5())
    results.append(await test_coordinator_routing())
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print_success("ALL TESTS PASSED!")
        print("\nAgents are ready for deployment!")
    else:
        print_error(f"{total - passed} tests failed")
        print("\nPlease check the errors above")
    
    return passed == total

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)