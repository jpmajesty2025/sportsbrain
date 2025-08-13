# Data Population Plan for SportsBrain

## Overview
This document outlines what data we need, where to get it, and how to populate the remaining Milvus collections and Neo4j relationships to support all demo scenarios.

## Current State
- ✅ **Milvus sportsbrain_players**: 572 entities (complete)
- ❌ **Milvus sportsbrain_strategies**: 0 entities (empty)
- ❌ **Milvus sportsbrain_trades**: 0 entities (empty)
- ⚠️ **Neo4j**: Basic Player→Team relationships only

## Demo Scenarios & Data Requirements

### 1. "Should I keep Ja Morant in round 3?" ✅ WORKING
**Current Data**: Player ADP, keeper values in Milvus metadata
**Status**: Fully functional

### 2. "How does Porzingis trade affect Tatum?" ❌ NOT WORKING
**Needs**:
- Trade data in `sportsbrain_trades` collection
- Trade impact analysis (usage rate changes, etc.)
- Neo4j IMPACTS relationships
- TEAMMATE_OF relationships in Neo4j

### 3. "Find me sleepers like last year's Sengun" ⚠️ PARTIAL
**Current**: Vector similarity works
**Needs**:
- Historical stats in player metadata
- Breakout scores
- SIMILAR_TO relationships in Neo4j
- Year-over-year improvement metrics

### 4. "Best punt FT% build around Giannis" ❌ NOT WORKING
**Needs**:
- Strategy documents in `sportsbrain_strategies`
- Build examples with player combinations
- Synergy scores between players
- Strategy→Player relationships in Neo4j

### 5. "Which sophomores will break out?" ❌ NOT WORKING
**Needs**:
- Player experience data (draft year, years in league)
- Breakout scores/predictions
- Historical progression data

## Data Collection Plan

### 1. sportsbrain_strategies Collection

#### Data Needed
- Draft strategy guides (punt builds, balanced builds)
- Strategy type, difficulty level
- Key player recommendations by round
- Category targets and punts
- Build synergies

#### Sources (Free)
1. **Reddit r/fantasybball**
   - Strategy guides from top posts
   - Punt build discussions
   - API: Reddit API (free tier: 60 requests/minute)
   
2. **HashtagBasketball Free Articles**
   - Punt guides
   - Strategy articles
   - Web scraping needed

3. **BasketballMonster Free Content**
   - Category punt analysis
   - Build guides

#### Sources (Paid)
1. **The Athletic Fantasy Basketball** ($7.99/month)
   - Premium strategy content
   - Expert analysis

2. **Locked On Fantasy Basketball** (Patreon $5/month)
   - Strategy podcasts transcripts

#### Mock Data Approach (For Demo)
Create 20-30 strategy documents covering:
- 5 punt builds (FT%, FG%, AST, PTS, etc.)
- 3 balanced builds
- Position-specific strategies
- Keeper league strategies

### 2. sportsbrain_trades Collection

#### Data Needed
- Trade announcements
- Impact analysis
- Community reactions/sentiment
- Fantasy implications

#### Sources (Free)
1. **Reddit r/nba and r/fantasybball**
   - Trade threads
   - Impact discussions
   - API: Same Reddit API

2. **ESPN Trade Machine**
   - Trade scenarios
   - Web scraping

3. **Twitter/X API** (Free tier: 1,500 tweets/month)
   - Woj/Shams tweets
   - Trade reactions

#### Sources (Paid)
1. **The Athletic** (Same subscription)
   - Trade analysis articles

#### Mock Data Approach (For Demo)
Use existing trades_2024.json and expand:
- Add 10-15 major trades from 2023-24
- Include Reddit discussions
- Add sentiment scores
- Fantasy impact analysis

### 3. Neo4j Enhancements

#### Data Needed
- Player similarity scores
- Trade relationships
- Teammate synergies
- Historical matchup data

#### Generation Approach
1. **SIMILAR_TO relationships**
   - Calculate from existing player vectors
   - Use cosine similarity from Milvus embeddings
   - Create relationships for top 5 similar players each

2. **IMPACTS relationships**
   - Use trades_2024.json data
   - Create Trade nodes
   - Link to affected players

3. **TEAMMATE_OF relationships**
   - Use current team rosters
   - Add synergy scores based on position/style

4. **Experience data**
   - Calculate from draft year
   - Classify as rookie/sophomore/veteran

## Implementation Priority (7 Days to Deadline)

### Day 1-2: Mock Data Creation
1. Create 20-30 strategy documents
2. Expand trades data to 15-20 trades
3. Generate embeddings using sentence-transformers
4. Load into Milvus collections

### Day 3-4: Neo4j Enhancements
1. Add experience fields to Player nodes
2. Create SIMILAR_TO relationships
3. Create Trade nodes and IMPACTS relationships
4. Add TEAMMATE_OF relationships

### Day 5-6: Testing & Refinement
1. Test all demo scenarios
2. Refine data as needed
3. Add any missing relationships

### Day 7: Final Testing
1. Complete demo walkthrough
2. Document any limitations

## Data Generation Scripts Needed

1. **generate_strategies.py**
   - Create strategy documents
   - Generate embeddings
   - Load to Milvus

2. **generate_trades.py**
   - Expand trade data
   - Add sentiment/impact analysis
   - Load to Milvus

3. **enhance_neo4j.py**
   - Add player experience data
   - Create similarity relationships
   - Create trade relationships

## Sample Data Structures

### Strategy Document
```python
{
    "title": "Elite Punt FT% Build 2024-25",
    "strategy_type": "punt_ft",
    "text": "This build leverages players like Giannis and Gobert who dominate categories despite poor FT%. Target Giannis round 1, pair with Gobert/Simmons round 2-3...",
    "metadata": {
        "difficulty": "intermediate",
        "categories": {
            "target": ["FG%", "REB", "BLK", "STL", "TO"],
            "punt": ["FT%"]
        },
        "key_players": ["Giannis", "Gobert", "Simmons", "Claxton"],
        "draft_targets": {
            "round_1": ["Giannis"],
            "round_2-3": ["Gobert", "Simmons"],
            "round_4-6": ["Claxton", "Adams", "Zubac"]
        },
        "synergy_scores": {
            "Giannis+Gobert": 0.92,
            "Giannis+Simmons": 0.88
        },
        "author": "FantasyExpert123",
        "source": "reddit",
        "upvotes": 245
    }
}
```

### Trade Document
```python
{
    "headline": "Porzingis Traded to Celtics",
    "text": "The Celtics acquire Kristaps Porzingis from the Wizards in a three-team deal. This impacts Tatum's usage rate and Brown's shot distribution...",
    "source": "reddit",
    "date_posted": "2023-06-22",
    "metadata": {
        "players_mentioned": ["Porzingis", "Tatum", "Brown", "Smart"],
        "teams_involved": ["BOS", "WAS", "MEM"],
        "sentiment": 0.75,
        "impact_analysis": {
            "Tatum": {"usage": -2.1, "assists": 0.8, "fantasy_impact": -0.05},
            "Brown": {"usage": -1.5, "assists": 0.5, "fantasy_impact": 0.0},
            "Porzingis": {"usage": 3.5, "assists": -0.5, "fantasy_impact": 0.15}
        },
        "reddit_metrics": {
            "score": 2834,
            "comments": 156,
            "awards": 5
        }
    }
}
```

## Success Criteria
✅ All 5 demo scenarios work end-to-end
✅ Each collection has sufficient data for realistic demos
✅ Neo4j relationships support complex queries
✅ Response times < 3 seconds for all queries

## Risk Mitigation
- Focus on mock data for demo (faster than API integration)
- Prioritize demo scenarios over comprehensive coverage
- Use existing trades_2024.json as foundation
- Generate strategies programmatically from templates