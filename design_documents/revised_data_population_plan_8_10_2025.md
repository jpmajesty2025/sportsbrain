# Revised Data Population Plan for SportsBrain
## Meeting the 1000+ Embeddings Requirement

## Current State
- ✅ **Milvus sportsbrain_players**: 572 embeddings
- ❌ **Milvus sportsbrain_strategies**: 0 embeddings
- ❌ **Milvus sportsbrain_trades**: 0 embeddings
- **TOTAL**: 572 embeddings
- **NEEDED**: 428+ more embeddings to reach 1000

## Embedding Distribution Strategy

### Option A: Balanced Approach (Recommended)
- **sportsbrain_strategies**: 150-200 embeddings
- **sportsbrain_trades**: 250-300 embeddings
- **Total**: 972-1072 embeddings

### Option B: Add Fourth Collection
- **sportsbrain_strategies**: 100 embeddings
- **sportsbrain_trades**: 150 embeddings
- **sportsbrain_injuries**: 100 embeddings (NEW)
- **sportsbrain_matchups**: 100 embeddings (NEW)
- **Total**: 1022 embeddings

### Option C: Content-Heavy Approach
- **sportsbrain_strategies**: 200 embeddings
- **sportsbrain_trades**: 300 embeddings
- **sportsbrain_reddit_discussions**: 150 embeddings (NEW)
- **Total**: 1222 embeddings

## Recommended: Enhanced Option A (Balanced + Extra)

### 1. sportsbrain_strategies: 200 Documents
**Categories:**
- 30 Punt build strategies (6 categories × 5 variations each)
  - Punt FT% (5 docs)
  - Punt FG% (5 docs)
  - Punt AST (5 docs)
  - Punt PTS (5 docs)
  - Punt 3PM (5 docs)
  - Punt REB/BLK (5 docs)
- 20 Balanced build strategies
- 20 Position-specific strategies (PG-heavy, big-man, etc.)
- 30 Keeper league strategies
- 30 Dynasty league strategies
- 20 DFS strategies
- 20 Auction draft strategies
- 30 Weekly matchup strategies

**Data Generation Approach:**
```python
strategy_templates = {
    "punt_ft": {
        "base_text": "This punt FT% build focuses on players like {player1} and {player2}...",
        "variations": [
            {"player1": "Giannis", "player2": "Gobert", "focus": "elite blocks"},
            {"player1": "Giannis", "player2": "Simmons", "focus": "assists"},
            {"player1": "Zion", "player2": "Claxton", "focus": "FG%"},
            # etc.
        ]
    }
}
```

### 2. sportsbrain_trades: 300 Documents
**Categories:**
- 50 Actual 2023-24 trades with analysis
- 50 Trade rumors and speculation
- 50 Historical trades (2022-23 season)
- 50 Trade proposals from Reddit
- 50 Dynasty trade value discussions
- 50 Buy-low/Sell-high recommendations

**Sources to Expand:**
- Use trades_2024.json as base (3-4 trades → 50)
- Generate variations with different analysis angles
- Add community reactions/discussions
- Include pre-trade and post-trade analysis

**Example Expansion:**
```python
# From 1 Porzingis trade, generate:
1. "Breaking: Porzingis to Celtics - Initial Analysis"
2. "How Porzingis Trade Affects Tatum's Fantasy Value"
3. "Winners and Losers: Porzingis Trade Edition"
4. "Reddit Reacts: Porzingis Trade Megathread"
5. "One Month Later: Porzingis Trade Impact Review"
# = 5 documents from 1 trade
```

### 3. Optional: sportsbrain_news (150 Documents)
**If we still need more embeddings:**
- 50 Injury reports
- 50 Player news/updates
- 50 Team news
- This would bring total to 1222 embeddings

## Data Structure Examples

### Enhanced Strategy Document
```python
{
    "strategy_id": "punt_ft_giannis_gobert_2024",
    "title": "Elite Punt FT% - Giannis + Gobert Core",
    "strategy_type": "punt_ft",
    "text": """
        This punt FT% build leverages Giannis Antetokounmpo's elite production 
        across all categories except free throws. By pairing him with Rudy Gobert 
        in rounds 2-3, you create an unstoppable force in FG%, rebounds, blocks, 
        and defensive stats. 
        
        Round 1: Target Giannis Antetokounmpo
        Round 2-3: Rudy Gobert or Ben Simmons
        Round 4-6: Jarrett Allen, Nic Claxton, Kevon Looney
        Round 7-10: Derrick White, Bruce Brown, Ayo Dosunmu
        
        This build dominates 8 of 9 categories while completely punting FT%.
        Expected category wins: FG%, REB, AST, STL, BLK, TO, PTS (competitive)
        """,
    "metadata": {
        "difficulty": "intermediate",
        "season": "2024-25",
        "categories": {
            "strong": ["FG%", "REB", "BLK", "STL", "TO"],
            "competitive": ["PTS", "AST"],
            "punt": ["FT%", "3PM"]
        },
        "key_players": {
            "core": ["Giannis Antetokounmpo", "Rudy Gobert"],
            "targets": ["Ben Simmons", "Jarrett Allen", "Nic Claxton"],
            "late_rounds": ["Kevon Looney", "Isaiah Stewart", "Jalen Duren"]
        },
        "synergy_matrix": {
            "Giannis+Gobert": 0.94,
            "Giannis+Simmons": 0.89,
            "Gobert+Allen": 0.85
        },
        "source": "expert_analysis",
        "author": "FantasyGuru2024",
        "rating": 4.8,
        "views": 15234
    }
}
```

### Enhanced Trade Document
```python
{
    "trade_id": "porzingis_celtics_impact_tatum",
    "headline": "Tatum's Usage After Porzingis Trade - Deep Dive",
    "text": """
        The Kristaps Porzingis acquisition significantly impacts Jayson Tatum's 
        fantasy value. With another high-usage scorer joining the Celtics, 
        Tatum's shot attempts decreased from 21.3 to 19.8 per game. However, 
        his efficiency improved with better spacing.
        
        Key impacts:
        - Usage rate: 31.2% → 29.1% (-2.1%)
        - Assists: 4.5 → 5.3 (+0.8)
        - FG%: 46.5% → 48.2% (+1.7%)
        - Fantasy points: 45.2 → 44.8 (-0.4)
        
        Verdict: Slight downgrade for Tatum in volume-based leagues, 
        but improved efficiency in category leagues.
        """,
    "source": "reddit_analysis",
    "date_posted": "2023-07-15",
    "metadata": {
        "primary_players": ["Jayson Tatum", "Kristaps Porzingis"],
        "secondary_players": ["Jaylen Brown", "Marcus Smart"],
        "teams": ["BOS", "WAS", "MEM"],
        "trade_date": "2023-06-22",
        "impact_scores": {
            "Tatum": -0.05,
            "Brown": 0.02,
            "Porzingis": 0.18,
            "Smart": -0.25
        },
        "community_sentiment": {
            "overall": 0.72,
            "celtics_fans": 0.85,
            "neutral": 0.65
        },
        "discussion_metrics": {
            "reddit_comments": 342,
            "upvotes": 2156,
            "awards": 8
        },
        "analysis_type": "player_impact",
        "time_frame": "immediate"
    }
}
```

## Implementation Plan (7 Days)

### Day 1: Generate Strategy Content (200 docs)
- Create strategy generator script
- Use templates with variations
- Generate embeddings
- Load to Milvus

### Day 2: Generate Trade Content (300 docs)
- Expand trades_2024.json
- Create trade impact variations
- Generate Reddit-style discussions
- Load to Milvus

### Day 3: Verify 1000+ Embeddings
- Check all collections
- Add more if needed
- Test vector search quality

### Day 4-5: Neo4j Enhancements
- Add relationships for new content
- Strategy→Player relationships
- Trade→Player impacts

### Day 6: Integration Testing
- Test all 5 demo scenarios
- Verify embedding quality
- Check response times

### Day 7: Final Polish
- Documentation
- Demo preparation

## Scripts Needed

### 1. generate_strategies_bulk.py
```python
def generate_strategy_variations():
    strategies = []
    
    # Punt builds - 6 types × 30-35 variations = 180-210 docs
    punt_types = ["FT%", "FG%", "AST", "PTS", "3PM", "REB"]
    for punt_type in punt_types:
        for variation in range(35):
            strategy = create_punt_strategy(punt_type, variation)
            strategies.append(strategy)
    
    # Other strategies to reach 200
    # ...
    
    return strategies
```

### 2. generate_trades_bulk.py
```python
def expand_trade_coverage():
    trades = []
    base_trades = load_json("trades_2024.json")
    
    for trade in base_trades:
        # Generate 10 different angles per trade
        trades.append(create_initial_analysis(trade))
        trades.append(create_player_impact(trade, "player1"))
        trades.append(create_player_impact(trade, "player2"))
        trades.append(create_reddit_thread(trade))
        trades.append(create_fantasy_implications(trade))
        trades.append(create_dynasty_impact(trade))
        trades.append(create_team_analysis(trade))
        trades.append(create_winners_losers(trade))
        trades.append(create_one_month_review(trade))
        trades.append(create_community_reaction(trade))
    
    return trades  # 10x expansion
```

## Success Metrics
✅ Total embeddings ≥ 1000 (requirement met)
✅ All 5 demo scenarios functional
✅ Realistic, varied content
✅ Good vector search results
✅ < 3 second response times

## Risk Mitigation
- Generate extra content (target 1100-1200 to be safe)
- Use templates to ensure consistency
- Test embedding quality with sample queries
- Have backup content generation ready

## Additional Collection Ideas (If Needed)
1. **sportsbrain_injuries** (100 docs)
   - Injury reports with fantasy impact
   - Recovery timelines
   - Historical injury patterns

2. **sportsbrain_matchups** (100 docs)
   - Team vs team historical performance
   - Defensive matchup analysis
   - Schedule strength analysis

3. **sportsbrain_podcasts** (100 docs)
   - Transcripts from fantasy podcasts
   - Expert opinions
   - Weekly preview content