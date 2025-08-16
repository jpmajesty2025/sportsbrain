# ADP Analysis Recommendations for DraftPrep Agent

## Current State
We have:
- **Data**: 150 players with ADP ranks (1-150) and rounds (1-13)
- **Tools**: `analyze_adp_value` and `get_adp_rankings`
- **Capability**: Basic ADP value analysis

## Working ADP Queries (Current)
1. "Who are the best ADP value picks?" - Returns top value players
2. "Show current ADP rankings" - Returns top ranked players
3. "Which players are undervalued?" - Returns value picks

## Limitations
1. Can't find overvalued/reaches (tool always shows undervalued)
2. Can't look up specific player ADPs properly
3. Can't compare ADP to projections meaningfully
4. Mock draft is tangential to ADP analysis

## Recommended Canned Prompts for ADP Analysis
Based on what actually works:

### Option 1: Simple Value Query
**Prompt**: "Who are the best value picks in rounds 3-5?"
**Why it works**: Directly asks for value analysis which the tool handles

### Option 2: ADP Rankings Query  
**Prompt**: "Show me the current top 20 ADP rankings"
**Why it works**: Direct request for rankings data we have

### Option 3: Undervalued Players
**Prompt**: "Which mid-round players offer the best value?"
**Why it works**: Combines ADP position with value analysis

## Quick Enhancements Needed (if time permits)

### 1. Fix Player Lookup (5 min fix)
```python
def _get_adp_rankings(self, query: str = "") -> str:
    # Parse for specific player names better
    if "trae young" in query.lower():
        # Query for Trae Young specifically
```

### 2. Add Overvalued Detection (10 min)
```python
def _find_overvalued_players(self, criteria: str = "") -> str:
    # Query for players with low value_ratio
    # (high ADP rank but low projections)
```

### 3. Better Value Calculation
Currently using: `(projected_fantasy_ppg * 82 / adp_rank)`
Better would be: Compare to average at that ADP position

## Recommended Agent Card Update
Current: "Keeper decisions, ADP analysis, and punt strategies"
Better: "Keeper decisions, draft value analysis, and punt strategies"
OR
Keep as is but add: "mock drafts" since we have that tool

## Best Immediate Action
Use this canned prompt: **"Who are the best value picks in the middle rounds?"**

This works with current tools and provides meaningful ADP analysis without requiring changes.