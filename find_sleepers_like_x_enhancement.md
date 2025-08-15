## Detailed Plan for "Find Sleepers Like X" Enhancement

### Current State Analysis:

**What We Have:**
1. **Existing Tool**: `_find_sleeper_candidates_enhanced` - Returns generic sleepers based on `sleeper_score > 0.6`
2. **Comparison Tool**: `_compare_players_enhanced` - Compares two specific players
3. **Data Available**:
   - PostgreSQL: `playing_style` field (e.g., "Shooter" for Poole)
   - Milvus: 572 player embeddings for vector similarity
   - Game stats: 3PT attempts, usage rate, scoring patterns

**What's Missing:**
- No tool that finds sleepers SIMILAR to a reference player
- No linkage between player style and sleeper identification

### Proposed Solution:

#### **Option 1: Create New Tool** (Recommended)
Create `_find_similar_sleepers` tool specifically for this use case:

```python
def _find_similar_sleepers(self, reference_player: str) -> str:
    """Find sleeper candidates similar to a reference player"""
```

#### **Option 2: Enhance Existing Tool**
Modify `_find_sleeper_candidates_enhanced` to accept optional player reference:

```python
def _find_sleeper_candidates_enhanced(self, criteria: str = "", similar_to: str = None) -> str:
```

### Data Requirements & Availability:

| Data Needed | Current Status | Source | Action Required |
|------------|----------------|---------|-----------------|
| Player embeddings | ✅ Available | Milvus (572 players) | Use for similarity |
| Playing style | ✅ Available | PostgreSQL | Filter by style |
| Statistical profile | ✅ Available | game_stats table | Calculate averages |
| Sleeper scores | ✅ Available | fantasy_data table | Filter candidates |
| 3PT patterns | ✅ Available | game_stats | For shooters like Poole |
| Usage rates | ✅ Available | game_stats | For role similarity |
| **Play type percentages** | ❌ Missing | Need to generate | Synthetic data needed |
| **Shot distribution** | ⚠️ Partial | game_stats has attempts | Need percentages |

### Implementation Strategy:

#### **Step 1: Create Player Profile Characterization**
```python
def _characterize_player(self, player_name: str) -> dict:
    """Create a player profile for similarity matching"""
    
    # Get from PostgreSQL
    player_data = db.execute("""
        SELECT 
            p.playing_style,
            p.position,
            AVG(gs.three_pointers_attempted) as avg_3pa,
            AVG(gs.three_pointers_made) / NULLIF(AVG(gs.three_pointers_attempted), 0) as 3p_pct,
            AVG(gs.usage_rate) as avg_usage,
            AVG(gs.points) as avg_points,
            AVG(gs.assists) as avg_assists,
            fd.sleeper_score
        FROM players p
        JOIN game_stats gs ON p.id = gs.player_id
        JOIN fantasy_data fd ON p.id = fd.player_id
        WHERE p.name = :name
        GROUP BY p.id, p.playing_style, p.position, fd.sleeper_score
    """)
    
    return {
        'style': player_data.playing_style,
        'is_shooter': avg_3pa > 6,  # 6+ attempts = shooter
        'is_playmaker': avg_assists > 5,
        'usage_tier': 'high' if avg_usage > 28 else 'medium' if avg_usage > 22 else 'low',
        'scoring_load': avg_points
    }
```

#### **Step 2: Use Milvus for Vector Similarity**
```python
def _find_similar_via_embeddings(self, player_name: str, min_sleeper_score: float = 0.6):
    """Find similar players using Milvus embeddings"""
    
    # Get player's embedding
    player_vec = collection.query(
        expr=f'player_name == "{player_name}"',
        output_fields=['vector']
    )[0]['vector']
    
    # Search for similar players who are also sleepers
    similar = collection.search(
        data=[player_vec],
        anns_field="vector",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=20,
        output_fields=['player_name', 'position']
    )
    
    # Filter by sleeper criteria in PostgreSQL
    sleeper_candidates = []
    for match in similar:
        if match.distance < 0.5:  # Similarity threshold
            # Check if they're a sleeper in PostgreSQL
            is_sleeper = check_sleeper_score(match.player_name)
            if is_sleeper:
                sleeper_candidates.append(match)
    
    return sleeper_candidates
```

#### **Step 3: Synthetic Data Generation for Missing Attributes**
Since we're missing some play style details, we can generate them based on stats:

```python
# backend/scripts/generate_player_styles.py

player_style_mapping = {
    'Jordan Poole': {
        'archetype': 'volume_scorer',
        'shot_distribution': {'3PT': 45, 'midrange': 20, 'paint': 35},
        'creation_type': 'off_ball',
        'defensive_impact': 'low'
    },
    'Alperen Sengun': {
        'archetype': 'point_center',
        'shot_distribution': {'3PT': 5, 'midrange': 30, 'paint': 65},
        'creation_type': 'playmaker',
        'defensive_impact': 'medium'
    },
    # Generate for all 150 fantasy-relevant players
}

# Store in new PostgreSQL table or as JSON in fantasy_data
```

### Quick Implementation Path (<4 days):

#### **Day 1: Create New Tool**
```python
# Add to intelligence_agent_enhanced.py

Tool(
    name="find_similar_sleepers",
    description="Find sleeper candidates similar to a specific player",
    func=self._find_similar_sleepers
)

def _find_similar_sleepers(self, player_reference: str) -> str:
    """Find sleepers with similar play style to reference player"""
    
    # 1. Get reference player profile
    ref_profile = self._characterize_player(player_reference)
    
    # 2. Use Milvus for initial similarity
    similar_players = self._find_similar_via_embeddings(player_reference)
    
    # 3. Filter by sleeper criteria and style match
    sleepers = []
    for player in similar_players:
        if player.sleeper_score > 0.6:
            sleepers.append({
                'name': player.name,
                'similarity': player.similarity_score,
                'why_similar': self._explain_similarity(ref_profile, player)
            })
    
    # 4. Format response with reasoning
    return self._format_similar_sleepers_response(player_reference, sleepers)
```

#### **Day 2: Add Statistical Similarity Logic**
- Compare 3PT attempts, usage rates, scoring patterns
- Weight similarity by fantasy relevance
- Add position flexibility matching

#### **Day 3: Test & Refine**
- Test with known examples (Poole, Sengun, etc.)
- Adjust similarity thresholds
- Add edge case handling

### Expected Output:
```
Query: "Find sleepers like Jordan Poole"

Jordan Poole Profile:
• Volume scorer (17.4 PPG) with 3PT focus (7.8 attempts/game)
• Off-ball shooter with streaky upside
• ADP dropped from 65 to 95 after Washington trade

Similar Sleepers:

1. Gary Trent Jr. (SG, TOR) - 92% similarity
   • Similar: High-volume 3PT shooter (7.4 attempts)
   • Similar: Off-ball scorer role
   • Sleeper angle: ADP 140 despite starter minutes
   
2. Malik Beasley (SG, MIL) - 87% similarity
   • Similar: 3PT specialist (8.2 attempts)
   • Similar: Streaky scorer profile
   • Sleeper angle: ADP 125, role increase potential
```

This approach leverages our existing data (Milvus embeddings + PostgreSQL stats) while creating a new specialized tool for similarity-based sleeper finding.