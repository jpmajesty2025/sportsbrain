"""
Comprehensive local test script for all benchmark questions
Tests each agent and captures both tool outputs and agent responses
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced
from app.agents.draft_prep_agent_tools import DraftPrepAgent
from app.agents.trade_impact_agent_tools import TradeImpactAgent

# Monkey-patch to capture tool outputs
original_tool_calls = {}
tool_outputs = []

def capture_tool_output(tool_name: str, original_func):
    """Decorator to capture tool outputs before agent processing"""
    def wrapper(*args, **kwargs):
        result = original_func(*args, **kwargs)
        tool_outputs.append({
            "tool": tool_name,
            "input": str(args) if args else str(kwargs),
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        return result
    return wrapper

# Benchmark questions from benchmark_agent_questions_v1.md
BENCHMARK_QUESTIONS = {
    "Intelligence": [
        # Questions that should work through agent
        "Find sleeper candidates",
        "What are Scoot Henderson's stats?",
        "Compare Scottie Barnes and Paolo Banchero",
        
        # Questions that require bypass
        "Is Gary Trent Jr. worth drafting?",
        "Is Paolo Banchero a breakout candidate?",
        
        # Position-filtered questions (testing the fix)
        "Who are the most undervalued shooting guards for fantasy?",
        "Which centers are sleepers?",
        "Find me high-upside guards going late in drafts",
    ],
    
    "DraftPrep": [
        # Questions that bypass to tools
        "Should I keep Ja Morant in round 3?",
        "Build a punt FT% team",
        "What's LaMelo Ball's ADP?",
        
        # Complex queries that might use agent
        "Build me a complete draft strategy for pick 12",
        "What's the best strategy if I keep both Giannis and Embiid?",
        
        # Other bypass patterns
        "Best sleepers in rounds 8-10",
        "Is LaMelo Ball worth keeping in the 4th round?",
    ],
    
    "TradeImpact": [
        # Questions that work through agent
        "How does the Porzingis trade affect Tatum?",
        "Which players benefit from recent trades?",
        "What's the usage rate change for Brunson after the OG trade?",
        
        # Questions that might fail or timeout
        "How would a hypothetical Donovan Mitchell to Miami trade affect Bam Adebayo?",
        "If the Lakers trade for Trae Young, what happens to Austin Reaves?",
    ]
}

async def test_agent(agent_name: str, agent_instance, questions: List[str]) -> List[Dict]:
    """Test an agent with a list of questions"""
    results = []
    
    for question in questions:
        print(f"\n{'='*80}")
        print(f"Testing {agent_name}: {question}")
        print('='*80)
        
        # Clear tool outputs for this question
        global tool_outputs
        tool_outputs = []
        
        try:
            # Run the agent
            start_time = datetime.now()
            response = await agent_instance.process_message(question)
            end_time = datetime.now()
            
            result = {
                "agent": agent_name,
                "question": question,
                "agent_response": response.content if hasattr(response, 'content') else str(response),
                "response_time": (end_time - start_time).total_seconds(),
                "tool_outputs": tool_outputs.copy(),
                "metadata": response.metadata if hasattr(response, 'metadata') else None,
                "tools_used": response.tools_used if hasattr(response, 'tools_used') else None,
                "confidence": response.confidence if hasattr(response, 'confidence') else None,
                "status": "success"
            }
            
            print(f"[OK] Response received in {result['response_time']:.2f}s")
            
        except asyncio.TimeoutError:
            result = {
                "agent": agent_name,
                "question": question,
                "agent_response": "TIMEOUT",
                "response_time": 30.0,
                "tool_outputs": tool_outputs.copy(),
                "status": "timeout"
            }
            print("[FAIL] Timeout after 30 seconds")
            
        except Exception as e:
            result = {
                "agent": agent_name,
                "question": question,
                "agent_response": f"ERROR: {str(e)}",
                "response_time": 0,
                "tool_outputs": tool_outputs.copy(),
                "status": "error",
                "error": str(e)
            }
            print(f"[FAIL] Error: {str(e)}")
        
        results.append(result)
        
        # Small delay between questions
        await asyncio.sleep(1)
    
    return results

async def main():
    """Run all benchmark tests and generate report"""
    print("="*80)
    print("SPORTSBRAIN AGENT BENCHMARK TEST - LOCAL")
    print(f"Started at: {datetime.now().isoformat()}")
    print("="*80)
    
    all_results = []
    
    # Initialize agents
    print("\nInitializing agents...")
    
    try:
        intelligence_agent = IntelligenceAgentEnhanced()
        
        # Patch Intelligence Agent tools to capture outputs
        for tool in intelligence_agent.tools:
            tool_name = tool.name
            if hasattr(tool, 'func'):
                original_func = tool.func
                tool.func = capture_tool_output(f"Intelligence.{tool_name}", original_func)
        
        print("[OK] Intelligence Agent initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize Intelligence Agent: {e}")
        intelligence_agent = None
    
    try:
        draft_prep_agent = DraftPrepAgent()
        
        # Patch DraftPrep Agent tools
        for tool in draft_prep_agent.tools:
            tool_name = tool.name
            if hasattr(tool, 'func'):
                original_func = tool.func
                tool.func = capture_tool_output(f"DraftPrep.{tool_name}", original_func)
        
        print("[OK] DraftPrep Agent initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize DraftPrep Agent: {e}")
        draft_prep_agent = None
    
    try:
        trade_impact_agent = TradeImpactAgent()
        
        # Patch TradeImpact Agent tools
        for tool in trade_impact_agent.tools:
            tool_name = tool.name
            if hasattr(tool, 'func'):
                original_func = tool.func
                tool.func = capture_tool_output(f"TradeImpact.{tool_name}", original_func)
        
        print("[OK] TradeImpact Agent initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize TradeImpact Agent: {e}")
        trade_impact_agent = None
    
    # Test each agent
    if intelligence_agent:
        print("\n" + "="*80)
        print("TESTING INTELLIGENCE AGENT")
        print("="*80)
        results = await test_agent("Intelligence", intelligence_agent, BENCHMARK_QUESTIONS["Intelligence"])
        all_results.extend(results)
    
    if draft_prep_agent:
        print("\n" + "="*80)
        print("TESTING DRAFTPREP AGENT")
        print("="*80)
        results = await test_agent("DraftPrep", draft_prep_agent, BENCHMARK_QUESTIONS["DraftPrep"])
        all_results.extend(results)
    
    if trade_impact_agent:
        print("\n" + "="*80)
        print("TESTING TRADEIMPACT AGENT")
        print("="*80)
        results = await test_agent("TradeImpact", trade_impact_agent, BENCHMARK_QUESTIONS["TradeImpact"])
        all_results.extend(results)
    
    # Generate report
    generate_report(all_results)
    
    print("\n" + "="*80)
    print(f"Test completed at: {datetime.now().isoformat()}")
    print(f"Total tests run: {len(all_results)}")
    print(f"Successful: {sum(1 for r in all_results if r['status'] == 'success')}")
    print(f"Failed: {sum(1 for r in all_results if r['status'] != 'success')}")
    print("="*80)

def generate_report(results: List[Dict]):
    """Generate a detailed markdown report"""
    
    report = f"""# SportsBrain Agent Benchmark Test Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Tests: {len(results)}
- Successful: {sum(1 for r in results if r['status'] == 'success')}
- Timeouts: {sum(1 for r in results if r['status'] == 'timeout')}
- Errors: {sum(1 for r in results if r['status'] == 'error')}

## Detailed Results

"""
    
    # Group by agent
    for agent_name in ["Intelligence", "DraftPrep", "TradeImpact"]:
        agent_results = [r for r in results if r['agent'] == agent_name]
        if not agent_results:
            continue
            
        report += f"### {agent_name} Agent\n\n"
        
        for idx, result in enumerate(agent_results, 1):
            report += f"#### Test {idx}: {result['question']}\n\n"
            report += f"**Status**: {result['status']}\n"
            report += f"**Response Time**: {result['response_time']:.2f}s\n"
            
            if result.get('metadata'):
                if result['metadata'].get('direct_routing'):
                    report += f"**Routing**: BYPASS (direct to tool)\n"
                else:
                    report += f"**Routing**: Through agent\n"
            
            if result.get('tools_used'):
                report += f"**Tools Used**: {', '.join(result['tools_used'])}\n"
            
            report += f"\n**Agent Response** (length: {len(result['agent_response'])} chars):\n"
            report += "```\n"
            report += result['agent_response'][:500]  # First 500 chars
            if len(result['agent_response']) > 500:
                report += "\n... [truncated]"
            report += "\n```\n"
            
            # Show tool outputs if any
            if result.get('tool_outputs'):
                report += f"\n**Raw Tool Outputs** ({len(result['tool_outputs'])} calls):\n"
                for tool_call in result['tool_outputs'][:2]:  # Show first 2 tool calls
                    report += f"\n*Tool*: {tool_call['tool']}\n"
                    report += f"*Output Length*: {len(str(tool_call['output']))} chars\n"
                    report += "```\n"
                    output_str = str(tool_call['output'])[:500]
                    report += output_str
                    if len(str(tool_call['output'])) > 500:
                        report += "\n... [truncated]"
                    report += "\n```\n"
            
            # Analysis
            if result.get('tool_outputs') and result['status'] == 'success':
                tool_output_len = sum(len(str(t['output'])) for t in result['tool_outputs'])
                agent_response_len = len(result['agent_response'])
                compression_ratio = agent_response_len / tool_output_len if tool_output_len > 0 else 0
                
                report += f"\n**Analysis**:\n"
                report += f"- Tool output total: {tool_output_len} chars\n"
                report += f"- Agent response: {agent_response_len} chars\n"
                report += f"- Compression ratio: {compression_ratio:.2%}\n"
                
                if compression_ratio < 0.5:
                    report += "- [WARN] Significant summarization detected\n"
            
            report += "\n---\n\n"
    
    # Save report
    report_path = f"C:\\Projects\\sportsbrain\\benchmark_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[FILE] Report saved to: {report_path}")
    
    # Also save raw JSON data
    json_path = report_path.replace('.md', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"[DATA] Raw data saved to: {json_path}")

if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault("DATABASE_URL", "postgresql://postgres:password@localhost/sportsbrain")
    
    # Run the async main function
    asyncio.run(main())