# Neo4j Enhancement Proposal for SportsBrain

## Current State vs. Design Gap Analysis

### What We Have:
- **Player nodes**: 572 (basic properties only: id, name, position, is_active, stats)
- **Team nodes**: 30
- **Injury nodes**: 182 with HAD_INJURY relationships
- **Trade nodes**: 15 (minimal properties)
- **Relationships**: PLAYS_FOR, HAD_INJURY, SIMILAR_TO (13), IMPACTED_BY (3)

### What's Missing (Critical for Demo Scenarios):
- Player properties: age, ADP, keeper_round_value, projections, breakout_score, usage_rate
- Strategy nodes and relationships (for punt build demos)
- TEAMMATE_OF relationships (for trade impact analysis)
- PLAYED_AGAINST relationships (for matchup analysis)

## 🚀 Phase 1 Enhancements (<4 Days)

### 1. **Enrich Player Nodes** (Day 1)
Pull from PostgreSQL and add critical properties:
```cypher
// Update all Player nodes with fantasy-relevant data
MATCH (p:Player {name: $name})
SET p.age = $age,
    p.adp_rank = $adp_rank,
    p.adp_round = $adp_round,
    p.keeper_round = $keeper_round,
    p.projected_ppg = $projected_ppg,
    p.projected_rpg = $projected_rpg,
    p.projected_apg = $projected_apg,
    p.breakout_candidate = $breakout_candidate,
    p.sleeper_score = $sleeper_score,
    p.consistency_rating = $consistency_rating,
    p.usage_rate = $usage_rate,
    p.player_type = $player_type  // 'rookie', 'sophomore', 'veteran'
```

### 2. **Create TEAMMATE_OF Relationships** (Day 1)
Essential for trade impact analysis:
```cypher
// Create bidirectional teammate relationships
MATCH (p1:Player {team: $team})
MATCH (p2:Player {team: $team})
WHERE p1.id < p2.id
MERGE (p1)-[:TEAMMATE_OF {
    season: '2024-25',
    synergy_score: $synergy_score  // Calculate based on positions/styles
}]-(p2)
```

### 3. **Add Strategy Nodes** (Day 2)
Critical for punt strategy demos:
```cypher
// Create punt strategy nodes
CREATE (s:Strategy {
    id: 'punt_ft_2024',
    type: 'punt_ft',
    title: 'Punt FT% Build Guide',
    description: 'Target high FG%, REB, BLK while ignoring FT%',
    category_gains: {fg_pct: '+15%', reb: '+20%', blk: '+25%'},
    target_stats: ['FG%', 'REB', 'BLK', 'PTS'],
    avoid_stats: ['FT%']
})

// Link strategies to ideal players
MATCH (s:Strategy {type: 'punt_ft'})
MATCH (p:Player)
WHERE p.name IN ['Giannis Antetokounmpo', 'Rudy Gobert', 'Clint Capela']
CREATE (s)-[:FEATURES_PLAYER {
    round: p.adp_round,
    reason: 'Elite FG% and REB with poor FT%',
    fit_score: 0.95
}]->(p)
```

### 4. **Enhanced Trade Relationships** (Day 2)
Improve trade impact analysis:
```cypher
// Create detailed trade impacts
MATCH (t:Trade {headline: 'Porzingis to Celtics'})
MATCH (tatum:Player {name: 'Jayson Tatum'})
MATCH (porzingis:Player {name: 'Kristaps Porzingis'})
CREATE (t)-[:IMPACTS {
    player_role: 'primary_scorer',
    usage_change: '+2.5%',
    shot_attempts_change: '+2.3',
    spacing_improvement: 'elite',
    fantasy_impact: '+3.2 fantasy PPG'
}]->(tatum)
```

### 5. **Add Synthetic Historical Performance** (Day 3)
Create PLAYED_AGAINST relationships with synthetic but realistic data:
```cypher
// Add key matchup performances for demo scenarios
CREATE (tatum:Player {name: 'Jayson Tatum'})-[:PLAYED_AGAINST {
    date: '2024-03-15',
    opponent: 'LAL',
    pts: 35, reb: 9, ast: 6,
    fg_pct: 0.520, three_pm: 5,
    fantasy_points: 52.5,
    matchup_rating: 'elite'
}]->(lakers:Team {abbreviation: 'LAL'})
```

### 6. **Player Similarity Enhancement** (Day 3)
Expand SIMILAR_TO relationships for better comparisons:
```cypher
// Create similarity relationships based on play style and stats
MATCH (sengun:Player {name: 'Alperen Sengun'})
MATCH (jokic:Player {name: 'Nikola Jokic'})
CREATE (sengun)-[:SIMILAR_TO {
    similarity_score: 0.82,
    based_on: ['passing_center', 'high_ast', 'post_playmaking'],
    fantasy_correlation: 0.75,
    development_path: 'year_3_breakout'
}]->(jokic)
```

## 📊 Data Population Strategy

### From PostgreSQL:
- All fantasy_data fields → Player node properties
- Team relationships → TEAMMATE_OF relationships
- Game stats → PLAYED_AGAINST relationships (aggregated)

### Synthetic Data Generation:
```python
# backend/scripts/populate_neo4j_enhancements.py

synthetic_data = {
    'player_ages': {
        'Paolo Banchero': 21,
        'Jayson Tatum': 26,
        'Giannis Antetokounmpo': 29,
        'Alperen Sengun': 22,
        # ... calculate from draft years
    },
    'usage_rates': {
        'Jayson Tatum': 31.2,
        'Paolo Banchero': 28.5,
        'Giannis Antetokounmpo': 33.1,
        # ... based on team context
    },
    'synergy_scores': {
        ('Jayson Tatum', 'Jaylen Brown'): 0.88,
        ('Paolo Banchero', 'Franz Wagner'): 0.85,
        # ... based on playing styles
    },
    'similarity_mappings': {
        'Alperen Sengun': ['Nikola Jokic', 'Domantas Sabonis'],
        'Paolo Banchero': ['Jayson Tatum', 'Jimmy Butler'],
        'Scottie Barnes': ['Giannis Antetokounmpo', 'Ben Simmons'],
        # ... based on play style
    }
}
```

## 🎯 Impact on Demo Scenarios

### Scenario 1: "Should I keep Ja Morant in round 3?"
**Enhanced with**: keeper_round property, ADP comparison
```cypher
MATCH (p:Player {name: 'Ja Morant'})
RETURN p.keeper_round, p.adp_round, 
       p.adp_round - 3 as value_differential
```

### Scenario 2: "How does Porzingis trade affect Tatum?"
**Enhanced with**: IMPACTS relationship with detailed metrics
```cypher
MATCH (t:Trade)-[i:IMPACTS]->(tatum:Player {name: 'Jayson Tatum'})
MATCH (tatum)-[:TEAMMATE_OF]-(porzingis:Player {name: 'Kristaps Porzingis'})
RETURN i.usage_change, i.spacing_improvement, i.fantasy_impact
```

### Scenario 3: "Find sleepers like Sengun"
**Enhanced with**: SIMILAR_TO relationships with development paths
```cypher
MATCH (sengun:Player {name: 'Alperen Sengun'})-[s:SIMILAR_TO]-(similar:Player)
WHERE similar.sleeper_score > 0.7
RETURN similar, s.development_path, s.fantasy_correlation
```

### Scenario 4: "Best punt FT% build around Giannis"
**Enhanced with**: Strategy nodes and FEATURES_PLAYER relationships
```cypher
MATCH (s:Strategy {type: 'punt_ft'})-[f:FEATURES_PLAYER]->(p:Player)
MATCH (giannis:Player {name: 'Giannis Antetokounmpo'})
WHERE p.name <> giannis.name
RETURN p.name, p.adp_round, f.reason, f.fit_score
ORDER BY p.adp_round
```

### Scenario 5: "Which sophomores will break out?"
**Enhanced with**: player_type property and development paths
```cypher
MATCH (p:Player {player_type: 'sophomore'})
WHERE p.breakout_candidate = true
OPTIONAL MATCH (p)-[s:SIMILAR_TO]-(comp:Player)
RETURN p.name, p.projected_ppg, p.breakout_score, 
       collect(comp.name) as similar_breakouts
```

## 🔧 Implementation Priority

### Day 1 (Critical):
1. Enrich Player nodes with PostgreSQL data
2. Create TEAMMATE_OF relationships
3. Test enhanced queries for demos 1-2

### Day 2 (Important):
1. Add Strategy nodes for punt builds
2. Enhance Trade relationships
3. Test demos 3-4

### Day 3 (Polish):
1. Add synthetic performance data
2. Expand SIMILAR_TO relationships
3. Test demo 5 and all integration

### Day 4 (Testing):
1. Full demo scenario testing
2. Performance optimization
3. Documentation

## 📈 Expected Improvements

### Before:
- Simple node lookups with minimal context
- No strategy relationships
- Limited player comparisons

### After:
- Rich property-based queries
- Strategy-driven recommendations
- Player similarity analysis
- Trade impact quantification
- Historical performance context

## 🚀 Quick Implementation Script

```python
# backend/scripts/enhance_neo4j.py
from neo4j import GraphDatabase
import psycopg2
from datetime import datetime

def enrich_player_nodes(neo4j_session, pg_cursor):
    """Pull data from PostgreSQL and enrich Neo4j Player nodes"""
    
    pg_cursor.execute("""
        SELECT p.name, p.birth_date, 
               fd.adp_rank, fd.adp_round, fd.keeper_round,
               fd.projected_ppg, fd.projected_rpg, fd.projected_apg,
               fd.breakout_candidate, fd.sleeper_score
        FROM players p
        JOIN fantasy_data fd ON p.id = fd.player_id
    """)
    
    for row in pg_cursor.fetchall():
        age = calculate_age(row[1]) if row[1] else 25  # Default age
        player_type = determine_player_type(age)
        
        neo4j_session.run("""
            MATCH (p:Player {name: $name})
            SET p.age = $age,
                p.player_type = $player_type,
                p.adp_rank = $adp_rank,
                p.adp_round = $adp_round,
                p.keeper_round = $keeper_round,
                p.projected_ppg = $ppg,
                p.projected_rpg = $rpg,
                p.projected_apg = $apg,
                p.breakout_candidate = $breakout,
                p.sleeper_score = $sleeper
        """, name=row[0], age=age, player_type=player_type, ...)

def create_teammate_relationships(neo4j_session):
    """Create TEAMMATE_OF relationships for all players on same team"""
    
    neo4j_session.run("""
        MATCH (p1:Player)
        MATCH (p2:Player)
        WHERE p1.team = p2.team AND p1.id < p2.id
        MERGE (p1)-[:TEAMMATE_OF {season: '2024-25'}]-(p2)
    """)

def add_strategy_nodes(neo4j_session):
    """Create strategy nodes and link to appropriate players"""
    
    strategies = [
        {
            'type': 'punt_ft',
            'players': ['Giannis Antetokounmpo', 'Rudy Gobert', 'Clint Capela'],
            'gains': {'fg_pct': '+15%', 'reb': '+20%', 'blk': '+25%'}
        },
        {
            'type': 'punt_fg',
            'players': ['Trae Young', 'Damian Lillard', 'James Harden'],
            'gains': {'3pm': '+30%', 'pts': '+20%', 'ast': '+15%'}
        }
    ]
    
    for strategy in strategies:
        # Create strategy node and relationships
        ...

if __name__ == "__main__":
    # Connect to both databases
    # Run enhancement functions
    # Verify with test queries
    pass
```

This enhancement plan focuses on supporting the 5 key demo scenarios with rich, contextual data while being achievable within the 4-day constraint.