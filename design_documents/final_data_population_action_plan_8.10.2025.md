# Final Data Population Action Plan
## Ready for Implementation

## Target Metrics
- **Milvus Embeddings**: 1,200+ total (currently 572)
- **Neo4j Nodes**: 2,000+ total
- **Neo4j Relationships**: 5,000+ total
- **Timeline**: 3-4 days of implementation

## Phase 1: Data Collection & Generation (Day 1)

### 1.1 Real Data Collection (via NBA API)

#### Script: `fetch_real_nba_data.py`
```python
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.static import players, teams

def fetch_performance_data():
    """Get 500 real game performances"""
    # Get top 50 fantasy players from 2024-25
    top_players = get_top_fantasy_players(50)
    
    performances = []
    for player in top_players:
        # Get player's top 10 games from 2024-25 season
        gamelog = playergamelog.PlayerGameLog(
            player_id=player['id'],
            season='2024-25'
        )
        games = gamelog.get_data_frames()[0]
        
        # Sort by fantasy points (custom calculation)
        games['fantasy_pts'] = calculate_fantasy_points(games)
        top_games = games.nlargest(10, 'fantasy_pts')
        
        performances.extend(top_games.to_dict('records'))
    
    return performances  # 500 performance records

def fetch_matchup_data():
    """Get 400 real matchups from 2024-25"""
    matchups = []
    
    # Get all teams
    all_teams = teams.get_teams()
    
    for team in all_teams[:20]:  # Top 20 teams
        gamelog = teamgamelog.TeamGameLog(
            team_id=team['id'],
            season='2024-25'
        )
        games = gamelog.get_data_frames()[0]
        
        # Get 20 games per team
        matchups.extend(games.head(20).to_dict('records'))
    
    return matchups  # 400 matchup records
```

### 1.2 Mock Data Generation

#### Script: `generate_mock_trades.py`
```python
def generate_trade_documents():
    """Generate 250 trade-related documents"""
    
    # Base trades (plausible 2024-25 scenarios)
    base_trades = [
        {
            "date": "2024-07-15",
            "headline": "Pascal Siakam Traded to Pacers",
            "teams": ["TOR", "IND"],
            "players": ["Pascal Siakam", "Bruce Brown", "Jordan Nwora"],
            "type": "offseason"
        },
        {
            "date": "2024-12-15",
            "headline": "Zach LaVine to Lakers",
            "teams": ["CHI", "LAL"],
            "players": ["Zach LaVine", "Rui Hachimura", "picks"],
            "type": "contender_move"
        },
        # ... 15 total base trades
    ]
    
    documents = []
    for trade in base_trades:
        # Generate 15-20 documents per trade
        documents.extend([
            create_initial_report(trade),
            create_woj_tweet(trade),
            create_reddit_thread(trade),
            create_impact_analysis(trade, "player1"),
            create_impact_analysis(trade, "player2"),
            create_fantasy_implications(trade),
            create_team_perspective(trade, "team1"),
            create_team_perspective(trade, "team2"),
            create_winners_losers(trade),
            create_fan_reaction(trade),
            create_expert_analysis(trade),
            create_one_week_later(trade),
            create_dynasty_impact(trade),
            create_betting_impact(trade),
            create_coach_comments(trade)
        ])
    
    return documents  # ~250 documents
```

#### Script: `generate_strategy_documents.py`
```python
def generate_strategy_documents():
    """Generate 200 strategy documents"""
    
    strategies = []
    
    # Punt builds (6 types × 25 variations = 150)
    punt_types = ["FT%", "FG%", "AST", "PTS", "3PM", "REB"]
    for punt_type in punt_types:
        for i in range(25):
            strategies.append(create_punt_strategy(punt_type, variation=i))
    
    # Balanced builds (20)
    for i in range(20):
        strategies.append(create_balanced_strategy(variation=i))
    
    # Position-heavy builds (20)
    positions = ["guard_heavy", "big_heavy", "wing_heavy", "balanced"]
    for pos in positions:
        for i in range(5):
            strategies.append(create_position_strategy(pos, variation=i))
    
    # Keeper/Dynasty strategies (10)
    for i in range(10):
        strategies.append(create_keeper_strategy(variation=i))
    
    return strategies  # 200 documents
```

#### Script: `generate_mock_injuries.py`
```python
def generate_injury_history():
    """Generate 300 injury records"""
    
    injuries = []
    injury_prone = ["Anthony Davis", "Kawhi Leonard", "Kyrie Irving", 
                   "Zion Williamson", "Joel Embiid", "Karl-Anthony Towns"]
    
    # High-injury players get more records
    for player in injury_prone:
        for i in range(5):  # 5 injuries each
            injuries.append(create_injury_record(player, severity="varies"))
    
    # Regular players get 1-2 injuries
    regular_players = get_all_players()[:135]
    for player in regular_players:
        for i in range(2):
            injuries.append(create_injury_record(player, severity="minor"))
    
    return injuries  # 300 records
```

## Phase 2: Milvus Population (Day 2)

### 2.1 Load Strategy Collection
```python
# Script: load_strategies_to_milvus.py
strategies = generate_strategy_documents()  # 200 docs
embeddings = generate_embeddings(strategies)
load_to_milvus("sportsbrain_strategies", strategies, embeddings)
```

### 2.2 Load Trades Collection
```python
# Script: load_trades_to_milvus.py
trades = generate_trade_documents()  # 250 docs
performances = fetch_performance_data()  # 500 real performances

# Combine trades with performance summaries for richer content
combined_docs = trades + create_performance_summaries(performances[:100])
embeddings = generate_embeddings(combined_docs)
load_to_milvus("sportsbrain_trades", combined_docs, embeddings)  # 350 docs
```

### 2.3 Optional: News Collection (if needed for 1000+)
```python
# Script: load_news_to_milvus.py
news = generate_news_updates(100)  # 100 docs
embeddings = generate_embeddings(news)
load_to_milvus("sportsbrain_news", news, embeddings)
```

**Final Milvus Count**: 572 + 200 + 350 + 100 = 1,222 embeddings ✅

## Phase 3: Neo4j Population (Day 3)

### 3.1 Create Additional Nodes
```python
# Script: populate_neo4j_nodes.py

# 1. Trade nodes (50)
create_trade_nodes(base_trades)

# 2. Strategy nodes (200)
create_strategy_nodes(strategies)

# 3. Performance nodes (500) - from real data
create_performance_nodes(performances)

# 4. Matchup nodes (400) - from real data
create_matchup_nodes(matchups)

# 5. Injury nodes (300) - mock
create_injury_nodes(injuries)

# Total new nodes: 1,450
# Total nodes: 572 (players) + 30 (teams) + 1,450 = 2,052 ✅
```

### 3.2 Create Relationships
```python
# Script: create_neo4j_relationships.py

# 1. SIMILAR_TO (1,700)
create_similarity_relationships()  # Use Milvus embeddings

# 2. FITS_STRATEGY (1,000)
create_strategy_fit_relationships()

# 3. HAD_PERFORMANCE (500)
link_performances_to_players()

# 4. IMPACTS (from trades) (200)
create_trade_impact_relationships()

# 5. TEAMMATE_OF (300)
create_teammate_relationships()

# 6. HAD_INJURY (300)
link_injuries_to_players()

# Total new relationships: 4,000
# Total relationships: 572 (PLAYS_FOR) + 4,000 = 4,572 ✅
```

## Phase 4: Testing & Validation (Day 4)

### 4.1 Verify Counts
```python
# Script: verify_data_population.py
print(f"Milvus players: {count_milvus('sportsbrain_players')}")
print(f"Milvus strategies: {count_milvus('sportsbrain_strategies')}")
print(f"Milvus trades: {count_milvus('sportsbrain_trades')}")
print(f"Total embeddings: {count_all_milvus()}")

print(f"Neo4j nodes: {count_neo4j_nodes()}")
print(f"Neo4j relationships: {count_neo4j_relationships()}")
```

### 4.2 Test Demo Scenarios
```python
# Script: test_demo_scenarios.py
test_keeper_decision("Ja Morant", round=3)
test_trade_impact("Porzingis", "Tatum")
test_find_sleepers("Alperen Sengun")
test_punt_strategy("Giannis", "FT%")
test_sophomore_breakouts()
```

## Success Criteria Checklist
- [ ] 1,000+ total embeddings in Milvus
- [ ] All 5 demo scenarios working
- [ ] Multi-hop Neo4j queries functioning
- [ ] Response times < 3 seconds
- [ ] Realistic, coherent generated content

## Implementation Order

### Day 1 (Monday)
1. Write and test `fetch_real_nba_data.py`
2. Write and test `generate_mock_trades.py`
3. Write and test `generate_strategy_documents.py`
4. Write and test `generate_mock_injuries.py`

### Day 2 (Tuesday)
1. Run all data generation scripts
2. Load strategies to Milvus
3. Load trades to Milvus
4. Verify embedding counts

### Day 3 (Wednesday)
1. Create all Neo4j nodes
2. Create all Neo4j relationships
3. Test multi-hop queries

### Day 4 (Thursday)
1. Test all demo scenarios
2. Fix any issues
3. Document final state

## Notes
- SportRadar API saved for future enhancement (post-submission)
- Focus on quality of mock data over trying to scrape
- Real performance/matchup data adds authenticity
- Template-based generation ensures consistency