# Data Sourcing Reality Check

## Trade Data (2024-25 Season)

### NBA API Limitations
- **nba_api does NOT have trade/transaction endpoints**
- Only provides player stats, team rosters, game data
- Cannot get trade information directly

### Alternative Sources for Real Trades

#### Option 1: Web Scraping (Most Realistic)
**ESPN Trade Tracker**
- URL: `https://www.espn.com/nba/trades`
- Has all 2024-25 trades in structured format
- Would need BeautifulSoup/Selenium
- Risk: Site structure changes

**Basketball Reference**
- URL: `https://www.basketball-reference.com/leagues/NBA_2025_transactions.html`
- Very structured HTML
- More stable than ESPN

#### Option 2: Manual Collection + Mock Expansion
**Realistic Approach for 7-day timeline:**
1. Manually collect 10-15 major trades from 2024-25
2. Expand each into multiple documents (as planned)
3. Total: 150-200 trade documents

**Known Major 2024-25 Trades to Include:**
- (Note: Since we're in August 2025, the season is ongoing)
- We can create realistic trades based on 2023-24 patterns
- Focus on trades that would impact fantasy basketball

#### Option 3: Sports Data APIs (Paid)
- **SportsDataIO**: $200+/month - has trade data
- **Sportradar**: Enterprise pricing
- **The Stats Perform**: Enterprise pricing
- Not realistic for project timeline

### Recommended Approach: Hybrid Mock Data

```python
# Create realistic trade scenarios based on patterns
trades_2024_25 = [
    {
        "date": "2024-07-01",
        "headline": "Damian Lillard Trade Saga Continues",
        "players": ["Damian Lillard", "Tyler Herro", "Duncan Robinson"],
        "teams": ["POR", "MIA"],
        "type": "offseason",
        "fantasy_impact": "major"
    },
    {
        "date": "2024-12-15",  # First day trades allowed
        "headline": "Contender Bolsters Roster", 
        "players": ["Zach LaVine", "Draft Picks"],
        "teams": ["CHI", "LAL"],
        "type": "deadline_prep",
        "fantasy_impact": "moderate"
    },
    # ... create 10-15 plausible trades
]
```

## Other Data Types

### 1. Injury Data

#### NBA API Capability
```python
from nba_api.stats.endpoints import playerinjuries
# This MAY exist but returns limited current data only
```

#### Reality: Mock Required
- Historical injury data not available via free APIs
- Current injuries only show active status
- **Plan**: Generate realistic injury patterns

```python
injury_patterns = {
    "high_risk_players": ["Kawhi Leonard", "Anthony Davis", "Kyrie Irving"],
    "common_injuries": ["knee", "ankle", "back", "hamstring"],
    "typical_games_missed": {
        "minor": range(1, 5),
        "moderate": range(5, 15),
        "major": range(15, 40)
    }
}
```

### 2. Performance Data

#### NBA API Capability
```python
from nba_api.stats.endpoints import playergamelog
# This EXISTS and works well!
```

**We CAN get real performance data:**
- Game-by-game stats for any player
- Box scores for specific games
- Can pull 10-20 games per star player

```python
def get_player_performances(player_id, season="2024-25"):
    gamelog = playergamelog.PlayerGameLog(
        player_id=player_id,
        season=season
    )
    return gamelog.get_data_frames()[0]
```

### 3. Matchup Data

#### NBA API Capability
```python
from nba_api.stats.endpoints import leaguegamelog, teamgamelog
# These EXIST for historical games
```

**We CAN get real matchup data:**
- Historical game results
- Team vs team records
- Score, pace, etc.

### 4. Strategy Data
**100% Mock Required**
- No API provides fantasy strategy content
- Must be generated from templates

## Recommended Data Mix

### Real Data (API/Scraping)
1. **Performance nodes**: 500 real game performances
   - Use nba_api playergamelog
   - Top 50 players × 10 games each
   
2. **Matchup nodes**: 400 real matchups
   - Use nba_api teamgamelog
   - Focus on nationally televised games

### Mock Data (Generated)
1. **Trade documents**: 200-300
   - Start with 10-15 plausible trades
   - Expand each into multiple angles
   
2. **Strategy documents**: 200
   - Template-based generation
   - Consistent structure
   
3. **Injury nodes**: 300
   - Realistic patterns based on player history
   - Common injury types and durations

4. **News/Updates**: 150 (if needed)
   - Generated from templates
   - Player updates, team news

## Implementation Priority

### Day 1: Real Data Collection
```python
# Get real performance data
performances = []
top_players = get_top_50_fantasy_players()
for player in top_players:
    games = get_player_performances(player['id'])
    performances.extend(games.head(10))  # Top 10 games

# Get real matchup data  
matchups = get_team_matchups(season="2024-25")
```

### Day 2: Mock Data Generation
```python
# Generate trades
trades = generate_trade_scenarios(count=15)
trade_documents = expand_trades_to_documents(trades)

# Generate strategies
strategies = generate_from_templates(count=200)

# Generate injuries
injuries = generate_injury_history(players, patterns)
```

### Day 3: Load Everything
- Load to Milvus collections
- Create Neo4j nodes/relationships
- Verify counts meet requirements

## Scripts Needed

1. **fetch_real_performances.py**
   - Uses nba_api
   - Gets actual game data
   
2. **generate_mock_trades.py**
   - Creates plausible trade scenarios
   - Expands to multiple documents
   
3. **generate_strategies.py**
   - Template-based generation
   - Multiple strategy types
   
4. **create_neo4j_graph.py**
   - Combines real and mock data
   - Creates all relationships

## Risk Mitigation
- Don't over-promise on "real" trade data
- Focus on making mock data realistic and useful
- Leverage nba_api where it actually works (performances, matchups)
- Use templates to ensure consistency