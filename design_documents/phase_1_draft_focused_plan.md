# SportsBrain Phase 1: Off-Season Draft Prep Focus

## Executive Summary
SportsBrain pivots to solve the **immediate need** of fantasy basketball players in August: **winning their upcoming drafts**. This positions us perfectly for the bootcamp demo while setting up for full-season features post-launch.

## Timeline Context
- **Now (August)**: Peak draft preparation season
- **Bootcamp Demo (Mid-August)**: Show draft prep value
- **September**: Most fantasy drafts occur
- **October**: Season starts, transition to in-game features

## Phase 1 MVP: Draft Intelligence System

### Core Value Proposition
**"Your AI-powered draft assistant that analyzes off-season moves, projects player values, and helps you dominate your fantasy draft"**

### Three Specialized Agents

#### 1. DraftPrep Agent
**Purpose**: Optimize draft strategy based on league settings
```python
Capabilities:
- Mock draft simulations with AI opponents
- Optimal pick recommendations by round
- Punting strategy analysis (e.g., punt FT%, punt assists)
- Keeper league value calculations
- ADP (Average Draft Position) vs projected value analysis

Example Queries:
- "Who should I target in round 3 if I'm punting assists?"
- "Is Wembanyama worth a keeper spot over Haliburton?"
- "Show me the best value picks after round 8"
```

#### 2. TradeImpact Agent  
**Purpose**: Analyze how off-season moves affect player fantasy value
```python
Capabilities:
- Usage rate projections after trades
- Team pace and style changes
- Coaching system impact
- Depth chart analysis
- Historical similar situations

Example Queries:
- "How does Chris Paul joining the Warriors affect Curry's assists?"
- "Will Scoot Henderson's arrival hurt Lillard's usage?"
- "Which Suns player benefits most from the new Big 3?"
```

#### 3. ProjectionAnalyst Agent
**Purpose**: Project next season's fantasy performance
```python
Capabilities:
- Statistical projections based on age curves
- Injury recovery timelines
- Breakout candidate identification
- Decline risk assessment
- Sophomore leap predictions

Example Queries:
- "Project Paolo Banchero's second-year stats"
- "Which players over 32 are decline risks?"
- "Find me this year's Lauri Markkanen breakout"
```

## Data Architecture

### Vector RAG (Milvus) - 1500+ Embeddings
```
Player Statistics (600 embeddings):
- 2023-24 season stats (450 players)
- 2022-23 season stats for trends
- Per-game, per-36, advanced stats

Draft Intelligence (400 embeddings):
- Mock draft results
- ADP trends over time
- Expert rankings aggregated
- Punting strategy guides

Trade Analysis (300 embeddings):
- All 2024 off-season trades
- Historical trade impacts
- Team system changes
- Coaching philosophy shifts

Injury & Projection Data (200 embeddings):
- Injury history and recovery
- Age-based projection models
- Breakout indicators
- Team situation reports
```

### Graph RAG (Neo4j) - Relationships
```cypher
// Player Networks
(Player)-[:PLAYS_FOR]->(Team)
(Player)-[:TRADED_FROM]->(OldTeam)
(Player)-[:SIMILAR_STATS_TO]->(Player)
(Player)-[:SHARED_COURT_WITH]->(Player)

// Team Dynamics  
(Team)-[:COACHED_BY]->(Coach)
(Team)-[:PLAYS_STYLE]->(Style)
(Trade)-[:AFFECTED_PLAYER]->(Player)
(Trade)-[:BETWEEN_TEAMS]->(Team)

// Fantasy Relationships
(Player)-[:DRAFT_COMP_TO]->(HistoricalPlayer)
(Player)-[:KEEPER_VALUE]->(FantasyTier)
```

### Real-Time Data Sources

1. **Reddit r/fantasybball API**
   - Daily discussion threads
   - Trade reaction threads
   - Mock draft results
   - Injury news
   - Data Quality: Sentiment analysis, spam filtering

2. **NBA Stats API** 
   - Last season's complete stats
   - Summer League stats
   - Official transactions
   - Data Quality: Null checks, outlier detection

3. **ESPN/Yahoo Fantasy APIs** (if available)
   - ADP data
   - Expert rankings
   - Mock draft trends

## Implementation Priorities (10 Days)

### Days 1-3: Data Foundation
- [ ] Load 2023-24 season stats into Milvus
- [ ] Create player embeddings (stats, playing style, situation)
- [ ] Build Neo4j graph with player/team relationships
- [ ] Set up Reddit API integration

### Days 4-6: Agent Development
- [ ] Implement DraftPrep Agent with LangChain
- [ ] Build TradeImpact Agent with trade analysis
- [ ] Create ProjectionAnalyst with statistical models
- [ ] Integrate agents with RAG databases

### Days 7-8: UI & Integration
- [ ] Build chat interface for draft questions
- [ ] Create draft board visualization
- [ ] Implement mock draft simulator
- [ ] Add re-ranking based on user preferences

### Days 9-10: Polish & Deploy
- [ ] Run 5+ integration test queries
- [ ] Implement rate limiting & abuse protection
- [ ] Create demo scenarios
- [ ] Final deployment and documentation

## Demo Scenarios for Bootcamp

### Scenario 1: "The Keeper Dilemma"
**User**: "I can keep 2 of: Giannis (1st round), Sabonis (5th round), or Maxey (12th round)"
**SportsBrain**: 
- Analyzes keeper value vs draft cost
- Projects next season performance
- Recommends optimal keepers based on value

### Scenario 2: "Post-Trade Analysis"
**User**: "How does the Lillard trade affect the Bucks' fantasy landscape?"
**SportsBrain**:
- Shows usage rate changes for Giannis, Middleton
- Analyzes pace increase potential
- Identifies beneficiaries and losers

### Scenario 3: "Late Round Gems"
**User**: "Find me potential breakout players after round 10"
**SportsBrain**:
- Identifies players in improved situations
- Shows historical breakout patterns
- Ranks by upside potential

### Scenario 4: "Punting Strategy"
**User**: "I want to punt FT% and build around Giannis"
**SportsBrain**:
- Suggests compatible players (Gobert, Simmons)
- Shows optimal draft flow
- Calculates category projections

## Post-Bootcamp Roadmap

### Phase 2 (Season Start - October)
- Add live game tracking
- Waiver wire recommendations
- Injury news integration
- Trade analyzer

### Phase 3 (Mid-Season)
- Playoff schedule optimization
- Dynasty league features
- DFS (daily fantasy) integration
- Advanced analytics dashboard

### Phase 4 (Future)
- Multi-sport expansion
- League integration APIs
- Mobile app
- Premium features

## Success Metrics
- ✅ 1500+ embeddings in vector DB
- ✅ Graph relationships for all players/teams
- ✅ 3 functioning agents with distinct capabilities
- ✅ Real-time Reddit integration
- ✅ 5+ tested query scenarios
- ✅ Live deployment with abuse protection
- ✅ Clear value for August draft prep
- ✅ Compelling demo for Zach