# Agent Behavior Documentation: Bypass vs True Agent Handling

## Overview
Due to LangChain ReAct agent limitations, some queries require direct routing (bypass) while others work through the agent's reasoning system. This document details which queries fall into each category for all three agents.

---

## Intelligence Agent

### ✅ TRUE AGENT HANDLING (Agent reasons and selects tools)

1. **"Find sleeper candidates"**
   - Agent matches to `find_sleepers` tool
   - Returns list of high sleeper score players
   - Note: Output gets summarized by ReAct agent

2. **"What are Scoot Henderson's stats?"**
   - Agent matches to `analyze_player_stats` tool
   - Returns player statistics and projections
   - Works well for specific stat lookups

3. **"Compare Scottie Barnes and Paolo Banchero"**
   - Agent matches to `compare_players` tool
   - Provides head-to-head comparison
   - Good for player vs player analysis

4. **"Who are the most consistent centers?"**
   - Agent matches to `analyze_consistency` tool
   - Returns consistency ratings and risk factors
   - Works for position-based queries

5. **"Project Luka Doncic's performance"**
   - Agent matches to `project_performance` tool
   - Provides 2024-25 projections
   - Handles performance predictions well

### ❌ REQUIRES BYPASS (Direct routing to avoid timeout)

1. **"Is Gary Trent Jr. worth drafting?"**
   - Bypassed via: `if "worth drafting" in message_lower`
   - Routes directly to: `_evaluate_player_draft_value()`
   - Reason: Agent fails to match "worth drafting" to any tool

2. **"Is Paolo Banchero a breakout candidate?"**
   - Bypassed via: `if "breakout candidate" in message_lower`
   - Routes directly to: `_identify_breakout_candidates_enhanced()`
   - Reason: Agent can't handle yes/no breakout questions

3. **"Should I draft Alperen Sengun?"**
   - Bypassed via: `if "should i draft" in message_lower`
   - Routes directly to: `_evaluate_player_draft_value()`
   - Reason: Similar to "worth drafting" pattern

---

## DraftPrep Agent (BETA - 95% Bypass)

### ✅ TRUE AGENT HANDLING (Limited - only complex multi-tool queries)

1. **"Build me a complete draft strategy for pick 12"**
   - Agent might chain multiple tools
   - Combines position scarcity, ADP analysis, strategy building
   - Complex enough to benefit from agent reasoning

2. **"What's the best strategy if I keep both Giannis and Embiid?"**
   - Requires multiple tool calls
   - Agent can reason about punt builds and keeper interactions
   - Multi-faceted analysis

3. **"Compare keeper value of 5 different players"**
   - Agent iterates through players
   - Aggregates and compares results
   - Benefits from agent's ability to chain operations

### ❌ REQUIRES BYPASS (Most queries - direct routing for reliability)

1. **"Should I keep Ja Morant in round 3?"**
   - Bypassed via: `if "keep" in message_lower or "keeper" in message_lower`
   - Routes directly to: `_calculate_keeper_value()`
   - Reason: Common query, faster with direct routing

2. **"Build a punt FT% team"**
   - Bypassed via: `if "punt" in message_lower`
   - Routes directly to: `_build_punt_strategy()`
   - Reason: Straightforward strategy query

3. **"What's LaMelo Ball's ADP?"**
   - Bypassed via: `if "adp" in message_lower or "value" in message_lower`
   - Routes directly to: `_analyze_adp_value()`
   - Reason: Simple lookup query

4. **"Best sleepers in rounds 8-10"**
   - Bypassed via: `if "sleeper" in message_lower or "round" in message_lower`
   - Routes directly to: `_find_draft_sleepers()`
   - Reason: Direct tool call more reliable

5. **"Mock draft from position 6"**
   - Bypassed via: `if "mock" in message_lower or "draft" in message_lower`
   - Routes directly to: `_mock_draft_assistant()`
   - Reason: Specific tool needed

---

## TradeImpact Agent

### ✅ TRUE AGENT HANDLING (Most queries work through agent)

1. **"How does the Porzingis trade affect Tatum?"**
   - Agent selects `analyze_trade_impact` tool
   - Successfully analyzes specific trade scenarios
   - Works well with named trades

2. **"Which players benefit from recent trades?"**
   - Agent might chain `search_trade_documents` and `analyze_trade_impact`
   - Can reason about multiple trades
   - Good for broad trade analysis

3. **"What's the usage rate change for Brunson after the OG trade?"**
   - Agent selects `calculate_usage_impact` tool
   - Handles specific metric queries
   - Works for detailed statistical impacts

4. **"Find trades similar to the Lillard deal"**
   - Agent uses `search_trade_documents` with Milvus
   - Vector similarity search works through agent
   - Good for pattern matching

### ❌ REQUIRES BYPASS (None currently implemented)

The TradeImpact Agent doesn't use direct routing bypasses. Instead, it has:
- Timeout handling (30 seconds)
- Error recovery for iteration limits
- Fallback to PostgreSQL if Milvus fails

However, these queries might still fail:

1. **"Is the Mitchell trade good for fantasy?"**
   - Vague query without specific player focus
   - Agent might iterate without finding right tool

2. **"Trade analysis"**
   - Too generic, no specific trade mentioned
   - Agent struggles without context

3. **"Who won the trade?"**
   - Without specifying which trade
   - Agent can't determine context

---

## Summary Statistics

### Intelligence Agent
- **True Agent Handling**: ~60% of queries
- **Bypass Required**: ~40% of queries (mainly yes/no questions)
- **Bypass Patterns**: 2 (worth drafting, breakout candidate)

### DraftPrep Agent (BETA)
- **True Agent Handling**: ~5% of queries (complex multi-tool only)
- **Bypass Required**: ~95% of queries
- **Bypass Patterns**: 5 (keeper, punt, ADP, sleepers, mock)
- **Note**: Labeled as BETA to set user expectations

### TradeImpact Agent
- **True Agent Handling**: ~90% of queries
- **Bypass Required**: 0% (uses error handling instead)
- **Timeout Protection**: 30-second limit with helpful error messages

---

## Recommendations for Project Documentation

1. **Be Transparent**: Document that DraftPrep is in BETA with direct routing for reliability
2. **Set Expectations**: Explain that Intelligence Agent summarizes detailed outputs (LangChain limitation)
3. **Highlight Success**: TradeImpact Agent is fully agentic and working well
4. **Future Enhancement**: Note that LangGraph migration would resolve these issues

---

## Testing Checklist

### Intelligence Agent Tests
✅ Test "Find sleeper candidates" - Should work via agent
✅ Test "Is Gary Trent Jr. worth drafting?" - Should work via bypass
✅ Test "What's Scoot Henderson's sleeper score?" - Should work via agent
✅ Test "Is Paolo Banchero a breakout candidate?" - Should work via bypass

### DraftPrep Agent Tests
✅ Test "Should I keep Ja Morant in round 3?" - Works via bypass
✅ Test "Build a punt assists team" - Works via bypass
✅ Test complex multi-part query - Should attempt agent reasoning

### TradeImpact Agent Tests
✅ Test "How does Porzingis trade affect Tatum?" - Should work via agent
✅ Test "Which players benefit from trades?" - Should work via agent
✅ Test vague query - Should timeout gracefully with helpful message