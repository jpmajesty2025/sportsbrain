# Neo4j Population Plan for SportsBrain
## Multi-Hop Query Opportunities

## Current State
- ✅ 572 Player nodes with basic properties
- ✅ ~30 Team nodes
- ✅ PLAYS_FOR relationships (572)
- **Total**: ~600 nodes, ~572 relationships

## Goal: Rich Graph for Multi-Hop Queries
Target: 2000+ nodes, 5000+ relationships to enable interesting traversals

## Enhanced Demo Scenarios with Multi-Hop Variants

### 1. Original: "Should I keep Ja Morant in round 3?"
**Multi-Hop Variant**: "Should I keep Ja Morant considering his teammates' injury history?"
```cypher
MATCH (ja:Player {name: "Ja Morant"})-[:PLAYS_FOR]->(team:Team)
MATCH (team)<-[:PLAYS_FOR]-(teammate:Player)
MATCH (teammate)-[:HAD_INJURY]->(injury:Injury)
WHERE injury.date > date('2024-01-01')
RETURN ja.keeper_value, count(injury) as teammate_injuries, 
       avg(injury.games_missed) as avg_games_missed
```

### 2. Original: "How does Porzingis trade affect Tatum?"
**Multi-Hop Variant**: "How do trades affecting star players impact their teammates' fantasy value in similar situations?"
```cypher
MATCH (trade:Trade)-[:IMPACTS {impact: 'negative'}]->(star:Player {role: 'primary_option'})
MATCH (star)-[:TEAMMATE_OF]->(teammate:Player)
MATCH (similar:Player)-[:SIMILAR_TO]->(star)
MATCH (similar)-[:TEAMMATE_OF]->(similar_teammate:Player)
MATCH (past_trade:Trade)-[:IMPACTS]->(similar_teammate)
RETURN star.name, teammate.name, similar_teammate.name, 
       past_trade.impact_score, teammate.fantasy_projection
```

### 3. Original: "Find me sleepers like last year's Sengun"
**Multi-Hop Variant**: "Find sleepers on teams that lost a star player via trade"
```cypher
MATCH (trade:Trade {season: '2024-25'})-[:TRADED_AWAY]->(star:Player)
MATCH (star)-[:LEFT_TEAM]->(team:Team)
MATCH (team)<-[:PLAYS_FOR]-(sleeper:Player)
WHERE sleeper.usage_projection > sleeper.last_season_usage + 5
MATCH (sengun:Player {name: 'Alperen Sengun'})-[:SIMILAR_TO]->(sleeper)
RETURN sleeper.name, sleeper.usage_projection, trade.date
ORDER BY sleeper.breakout_score DESC
```

### 4. Original: "Best punt FT% build around Giannis"
**Multi-Hop Variant**: "Find punt FT% pairs who have played together successfully"
```cypher
MATCH (giannis:Player {name: 'Giannis'})-[:FITS_STRATEGY]->(strategy:Strategy {type: 'punt_ft'})
MATCH (strategy)<-[:FITS_STRATEGY]-(partner:Player)
MATCH (partner)-[:PLAYED_WITH {games: g}]->(former_teammate:Player)
WHERE g > 30 AND former_teammate.ft_pct < 0.70
MATCH (former_teammate)-[:HAD_PERFORMANCE]->(perf:Performance)
WHERE perf.fantasy_points > 40
RETURN partner.name, former_teammate.name, avg(perf.fantasy_points) as avg_fantasy
ORDER BY avg_fantasy DESC
```

### 5. New: "Which team's schedule is best for fantasy playoffs?"
```cypher
MATCH (team:Team)-[:PLAYS_AGAINST]->(matchup:Matchup)-[:AGAINST]->(opponent:Team)
WHERE matchup.date >= date('2025-03-15') AND matchup.date <= date('2025-04-15')
MATCH (opponent)-[:ALLOWS_STATS]->(defensive:DefensiveRating)
RETURN team.name, count(matchup) as playoff_games, 
       avg(defensive.points_allowed) as avg_points_allowed,
       sum(CASE WHEN defensive.rank > 20 THEN 1 ELSE 0 END) as easy_matchups
ORDER BY easy_matchups DESC
```

## Node Types to Add

### 1. Trade Nodes (~50 nodes)
```cypher
(:Trade {
  id: "trade_2024_001",
  date: "2024-07-15",
  headline: "Porzingis to Celtics",
  season: "2024-25",
  type: "offseason",  // deadline, buyout
  impact_level: "major"  // minor, medium, major
})
```

### 2. Strategy Nodes (~200 nodes)
```cypher
(:Strategy {
  id: "punt_ft_2024",
  type: "punt_ft",
  title: "Elite Punt FT% Build",
  difficulty: "intermediate",
  season: "2024-25",
  success_rate: 0.78
})
```

### 3. Injury Nodes (~300 nodes)
```cypher
(:Injury {
  id: "injury_2024_ja_001",
  player_id: "ja_morant",
  date: "2024-12-15",
  type: "knee",
  severity: "moderate",
  games_missed: 12,
  fantasy_impact: -25.5
})
```

### 4. Performance Nodes (~500 nodes)
```cypher
(:Performance {
  id: "perf_tatum_2024_12_25",
  player_id: "tatum",
  date: "2024-12-25",
  opponent: "LAL",
  pts: 35, reb: 8, ast: 6,
  fantasy_points: 52.5,
  exceeded_projection: true
})
```

### 5. Matchup Nodes (~400 nodes)
```cypher
(:Matchup {
  id: "matchup_BOS_LAL_2024_12_25",
  date: "2024-12-25",
  home_team: "BOS",
  away_team: "LAL",
  pace: 102.3,
  total_points: 235
})
```

### 6. Fantasy Context Nodes (~100 nodes)
```cypher
(:FantasyWeek {
  week_num: 15,
  start_date: "2025-01-20",
  end_date: "2025-01-26",
  is_playoff_week: false,
  games_per_team: {"BOS": 4, "LAL": 3, ...}
})
```

## Relationship Types to Add

### 1. Trade Relationships (~200)
```cypher
(trade:Trade)-[:TRADED_AWAY]->(player:Player)
(trade:Trade)-[:TRADED_TO {team: "BOS"}]->(player:Player)
(trade:Trade)-[:IMPACTS {usage_change: -2.1, fantasy_change: -0.05}]->(affected:Player)
```

### 2. Strategy Relationships (~1000)
```cypher
(player:Player)-[:FITS_STRATEGY {score: 0.92}]->(strategy:Strategy)
(strategy:Strategy)-[:PAIRS_WELL {synergy: 0.88}]->(combo:PlayerCombo)
(strategy:Strategy)-[:TARGETS_ROUND {round: 1}]->(player:Player)
```

### 3. Similarity Relationships (~2000)
```cypher
// Each player gets 3-5 similar players
(player1:Player)-[:SIMILAR_TO {score: 0.89, basis: "stats+age+role"}]->(player2:Player)
```

### 4. Performance Relationships (~500)
```cypher
(player:Player)-[:HAD_PERFORMANCE]->(perf:Performance)
(perf:Performance)-[:AGAINST_TEAM]->(team:Team)
(perf:Performance)-[:IN_MATCHUP]->(matchup:Matchup)
```

### 5. Teammate Relationships (~300)
```cypher
(player1:Player)-[:TEAMMATE_OF {season: "2024-25", synergy: 0.82}]->(player2:Player)
(player1:Player)-[:PLAYED_WITH {games: 45, seasons: ["2023-24"]}]->(player2:Player)
```

### 6. Injury Relationships (~300)
```cypher
(player:Player)-[:HAD_INJURY]->(injury:Injury)
(injury:Injury)-[:AFFECTED_GAMES]->(matchup:Matchup)
```

## Data Generation Plan

### Phase 1: Core Nodes (Day 1)
1. Create Trade nodes from trades data
2. Create Strategy nodes from strategy collection
3. Create Injury nodes (mock data for top 100 players)
4. Total: ~550 new nodes

### Phase 2: Performance & Matchups (Day 2)
1. Generate 5-10 key performances per star player (50 players × 10 = 500)
2. Create matchup nodes for key games
3. Total: ~900 new nodes

### Phase 3: Relationships - High Value (Day 3)
1. SIMILAR_TO relationships (572 players × 3 = ~1700)
2. FITS_STRATEGY relationships (200 strategies × 5 players = 1000)
3. Trade IMPACTS relationships
4. Total: ~3000 new relationships

### Phase 4: Relationships - Supporting (Day 4)
1. TEAMMATE_OF relationships
2. Performance relationships
3. Injury relationships
4. Total: ~1500 new relationships

## Final Graph Stats
- **Nodes**: ~2000-2500
  - 572 Players
  - 30 Teams
  - 50 Trades
  - 200 Strategies
  - 300 Injuries
  - 500 Performances
  - 400 Matchups
  - 100 FantasyWeeks

- **Relationships**: ~6000-7000
  - 572 PLAYS_FOR
  - 1700 SIMILAR_TO
  - 1000 FITS_STRATEGY
  - 500 HAD_PERFORMANCE
  - 300 TEAMMATE_OF
  - 300 HAD_INJURY
  - 200 Trade relationships
  - Plus supporting relationships

## Implementation Scripts

### 1. create_similarity_relationships.py
```python
def create_similarity_relationships():
    """Create SIMILAR_TO relationships based on vector similarity"""
    
    # Get all player embeddings from Milvus
    players = get_all_players_with_embeddings()
    
    for player in players:
        # Find top 3-5 similar players using cosine similarity
        similar = find_similar_players(player, top_k=4)
        
        for sim_player, score in similar:
            create_relationship(
                player, sim_player,
                rel_type="SIMILAR_TO",
                properties={"score": score, "basis": "embeddings"}
            )
```

### 2. create_trade_graph.py
```python
def create_trade_impacts():
    """Create trade nodes and impact relationships"""
    
    trades = load_trades_data()
    
    for trade in trades:
        # Create trade node
        trade_node = create_trade_node(trade)
        
        # Create impact relationships
        for player, impact in trade['impacts'].items():
            create_relationship(
                trade_node, player,
                rel_type="IMPACTS",
                properties=impact
            )
```

### 3. create_performance_history.py
```python
def create_performance_nodes():
    """Create performance nodes for key games"""
    
    # Focus on top 50 fantasy players
    top_players = get_top_fantasy_players(50)
    
    for player in top_players:
        # Create 10 notable performances
        performances = generate_performances(player, count=10)
        
        for perf in performances:
            perf_node = create_performance_node(perf)
            create_relationship(player, perf_node, "HAD_PERFORMANCE")
```

## Query Examples Enabled

### 1. Complex Keeper Decision
"Who should I keep: Player A who has injury-prone teammates or Player B on a team that made major trades?"

### 2. Trade Cascade Analysis
"Show me all players whose fantasy value improved after their team traded away a ball-dominant guard"

### 3. Strategy Optimization
"Find the best punt-assist build using only players who have never been injured more than 10 games"

### 4. Schedule + Matchup Analysis
"Which players have the easiest playoff schedule against teams they've historically dominated?"

### 5. Breakout Prediction
"Find sophomores whose situation improved due to trades and have similar stats to previous breakout players"

## Success Metrics
✅ Support for 5+ hop queries
✅ All demo scenarios have multi-hop variants
✅ Graph traversal < 1 second for 3-hop queries
✅ Rich enough for exploratory analysis
✅ Realistic relationship weights/scores