"""
Enhanced Milvus collection schemas for SportsBrain
Additions to support all demo queries
"""
from pymilvus import CollectionSchema, FieldSchema, DataType
from typing import Dict, Any


# Enhanced metadata examples showing new fields
ENHANCED_METADATA_EXAMPLES = {
    "player": {
        # Existing fields
        "team": "LAL",
        "season": "2023-24",
        "stats": {
            "ppg": 25.3,
            "rpg": 7.1,
            "apg": 5.2,
            "fg_pct": 0.513,
            "ft_pct": 0.742
        },
        "advanced_stats": {
            "per": 24.8,
            "ts_pct": 0.614,
            "usage": 29.3
        },
        "fantasy": {
            "adp": 15.5,
            "ranking": 12,
            "categories": ["PTS", "REB", "AST"],
            # NEW: Keeper value support
            "keeper_round_value": 2,  # What round they're worth keeping
            "keeper_cost_next_year": 3  # What round it costs to keep them
        },
        "age": 28,
        "height": "6-8",
        "injury_status": "healthy",
        
        # NEW FIELDS for demo queries:
        "experience": {
            "draft_year": 2018,
            "years_in_league": 6,
            "player_type": "veteran",  # rookie, sophomore, veteran
            "draft_position": 7
        },
        
        # Historical progression (for sleeper/breakout analysis)
        "historical_stats": {
            "2022-23": {"ppg": 22.1, "rpg": 6.8, "apg": 4.9},
            "2021-22": {"ppg": 18.5, "rpg": 6.2, "apg": 4.1},
            "improvement_rate": 0.15,  # Year-over-year improvement
            "breakout_score": 0.78  # ML-derived breakout probability
        },
        
        # Injury tracking
        "injury_history": [
            {"date": "2024-01-15", "type": "knee", "games_missed": 8}
        ],
        
        # Additional context
        "team_context": {
            "role": "primary_option",  # or secondary, role_player
            "new_teammates": ["Porzingis"],  # For trade impact
            "usage_projection": 28.5
        }
    },
    
    "strategy": {
        # Existing fields remain the same
        "positions_focus": ["PG", "SG"],
        "difficulty": "intermediate",
        "categories": {
            "target": ["PTS", "3PM", "AST", "STL"],
            "punt": ["FG%", "REB", "BLK"]
        },
        "key_players": ["Curry", "Lillard", "Young"],
        "author": "fantasyguru123",
        "upvotes": 245,
        "draft_round_targets": {
            "1-2": ["Elite PG"],
            "3-5": ["3PT specialists"],
            "6-9": ["AST/STL guards"],
            "10+": ["High volume shooters"]
        },
        
        # NEW: Better support for punt builds
        "build_examples": [
            {
                "round": 1,
                "player": "Giannis",
                "reason": "Elite in all cats except FT%"
            },
            {
                "round": 2,
                "player": "Gobert",
                "reason": "Doubles down on punt FT%, elite blocks"
            }
        ],
        "synergy_scores": {
            "Giannis+Gobert": 0.92,
            "Giannis+Simmons": 0.88
        }
    },
    
    "trade": {
        # Existing fields remain the same
        "players_mentioned": ["Lillard", "Holiday", "Ayton"],
        "teams_involved": ["MIL", "POR", "PHX"],
        "sentiment": 0.85,
        "impact_analysis": {
            "Lillard": {"usage": "+5%", "assists": "-2.0"},
            "Giannis": {"usage": "-3%", "assists": "+1.5"}
        },
        "reddit_metrics": {
            "score": 1523,
            "comments": 89,
            "awards": 3
        },
        "author_flair": "Bucks Fan",
        "url": "https://reddit.com/r/fantasybball/...",
        
        # NEW: Better trade impact modeling
        "trade_date": "2024-07-15",
        "trade_type": "offseason",  # or deadline, buyout
        "fantasy_impact_scores": {
            "Lillard": -0.15,  # Negative means decrease in fantasy value
            "Giannis": 0.05,
            "Holiday": 0.20
        }
    }
}