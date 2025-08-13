# Neo4j Schema Design for SportsBrain

## Current State
- Player nodes with basic properties
- Team nodes
- PLAYS_FOR relationships

## Required Schema for Demo Queries

### Nodes

#### Player
```cypher
(:Player {
  id: "player_123",
  name: "Jayson Tatum",
  position: "SF",
  team: "BOS",
  age: 26,
  years_in_league: 7,
  player_type: "veteran",  // rookie, sophomore, veteran
  draft_year: 2017,
  draft_position: 3,
  
  // Current stats
  ppg: 27.5,
  rpg: 8.1,
  apg: 4.8,
  
  // Fantasy relevant
  adp: 8.5,
  keeper_round_value: 1,
  fantasy_ranking: 7,
  
  // For consistency/breakout analysis
  consistency_score: 85.2,
  breakout_score: 0.15,
  usage_rate: 31.2
})
```

#### Team
```cypher
(:Team {
  abbreviation: "BOS",
  name: "Boston Celtics",
  conference: "Eastern",
  division: "Atlantic",
  defensive_rating: 110.5,
  pace: 98.3
})
```

#### Trade
```cypher
(:Trade {
  id: "trade_2024_001",
  date: "2024-07-15",
  headline: "Porzingis to Celtics",
  type: "offseason"
})
```

#### Strategy
```cypher
(:Strategy {
  id: "punt_ft_2024",
  type: "punt_ft",
  title: "Punt FT% Build Guide",
  difficulty: "intermediate"
})
```

### Relationships

#### Player Relationships
```cypher
// Current team
(player:Player)-[:PLAYS_FOR {season: "2023-24", role: "primary"}]->(team:Team)

// Historical performance
(player:Player)-[:PLAYED_AGAINST {
  date: "2024-03-15",
  pts: 35,
  reb: 9,
  ast: 6,
  performance_score: 52.5
}]->(opponent:Team)

// Similarity (for "players like X" queries)
(player1:Player)-[:SIMILAR_TO {
  score: 0.92,
  based_on: ["stats", "style", "age"]
}]->(player2:Player)

// Trade impacts
(trade:Trade)-[:INVOLVES]->(player:Player)
(trade:Trade)-[:IMPACTS {
  usage_change: -3.5,
  fantasy_value_change: 0.05
}]->(player:Player)

// Teammate relationships (for chemistry/usage)
(player1:Player)-[:TEAMMATE_OF {
  season: "2023-24",
  synergy_score: 0.85
}]->(player2:Player)
```

#### Strategy Relationships
```cypher
// Strategy to key players
(strategy:Strategy)-[:FEATURES_PLAYER {
  round: 1,
  reason: "Elite everywhere except FT%"
}]->(player:Player)

// Strategy synergies
(strategy:Strategy)-[:SYNERGY_WITH {
  score: 0.92
}]->(player_combo:PlayerCombo)
```

## Queries This Enables

### 1. Keeper Decision
```cypher
MATCH (p:Player {name: "Ja Morant"})
RETURN p.keeper_round_value, p.adp, p.injury_history
```

### 2. Trade Impact
```cypher
MATCH (trade:Trade)-[:IMPACTS]->(tatum:Player {name: "Jayson Tatum"})
WHERE trade.headline CONTAINS "Porzingis"
MATCH (porzingis:Player {name: "Kristaps Porzingis"})-[:TEAMMATE_OF]->(tatum)
RETURN trade, tatum.usage_rate, porzingis.usage_rate
```

### 3. Find Similar Players
```cypher
MATCH (sengun:Player {name: "Alperen Sengun"})
MATCH (sengun)-[:SIMILAR_TO]->(similar:Player)
WHERE similar.breakout_score > 0.7
RETURN similar ORDER BY similar.breakout_score DESC
```

### 4. Punt Strategy Build
```cypher
MATCH (s:Strategy {type: "punt_ft"})
MATCH (s)-[:FEATURES_PLAYER]->(p:Player)
MATCH (giannis:Player {name: "Giannis"})
MATCH (p)-[:SYNERGY_WITH]->(giannis)
RETURN p ORDER BY p.round
```

### 5. Sophomore Breakouts
```cypher
MATCH (p:Player {player_type: "sophomore"})
WHERE p.breakout_score > 0.7
RETURN p ORDER BY p.breakout_score DESC
```

## Implementation Priority

1. **High Priority** (Needed for basic demos)
   - Add experience fields to Player nodes
   - Create SIMILAR_TO relationships
   - Add Trade nodes and IMPACTS relationships

2. **Medium Priority** (Enhanced demos)
   - PLAYED_AGAINST with performance data
   - TEAMMATE_OF relationships
   - Strategy nodes and relationships

3. **Low Priority** (Nice to have)
   - Historical team relationships
   - Coach relationships
   - Injury timeline nodes