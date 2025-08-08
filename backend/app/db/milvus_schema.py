"""
Milvus collection schemas for SportsBrain
"""
from pymilvus import CollectionSchema, FieldSchema, DataType
from typing import Dict, Any


def get_player_schema() -> CollectionSchema:
    """Schema for sportsbrain_players collection"""
    fields = [
        # Primary key (mmh3 hash of player data)
        FieldSchema(
            name="primary_key",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=False,
            description="MMH3 hash of player identifier"
        ),
        
        # Dense embedding vector (768 dimensions)
        FieldSchema(
            name="vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=768,
            description="Player profile embedding from sentence-transformers"
        ),
        
        # Text content that was embedded
        FieldSchema(
            name="text",
            dtype=DataType.VARCHAR,
            max_length=65535,
            description="Full text description of player profile and stats"
        ),
        
        # High-frequency filter fields
        FieldSchema(
            name="player_name",
            dtype=DataType.VARCHAR,
            max_length=255,
            description="Player full name for exact matching"
        ),
        
        FieldSchema(
            name="position",
            dtype=DataType.VARCHAR,
            max_length=10,
            description="Primary position (PG, SG, SF, PF, C)"
        ),
        
        # Semi-structured metadata
        FieldSchema(
            name="metadata",
            dtype=DataType.JSON,
            description="Player stats, team, season, rankings, etc."
        ),
        
        # Timestamp
        FieldSchema(
            name="created_at",
            dtype=DataType.INT64,
            description="Unix timestamp of when record was created"
        )
    ]
    
    schema = CollectionSchema(
        fields=fields,
        description="NBA player profiles, stats, and fantasy analysis"
    )
    return schema


def get_strategy_schema() -> CollectionSchema:
    """Schema for sportsbrain_strategies collection"""
    fields = [
        FieldSchema(
            name="primary_key",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=False,
            description="MMH3 hash of strategy content"
        ),
        
        FieldSchema(
            name="vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=768,
            description="Strategy embedding from sentence-transformers"
        ),
        
        FieldSchema(
            name="text",
            dtype=DataType.VARCHAR,
            max_length=65535,
            description="Full strategy description and analysis"
        ),
        
        # Primary filter field
        FieldSchema(
            name="strategy_type",
            dtype=DataType.VARCHAR,
            max_length=50,
            description="Type: punt_ft, punt_ast, balanced, etc."
        ),
        
        FieldSchema(
            name="metadata",
            dtype=DataType.JSON,
            description="Positions, difficulty, categories, author, etc."
        ),
        
        FieldSchema(
            name="created_at",
            dtype=DataType.INT64,
            description="Unix timestamp"
        )
    ]
    
    schema = CollectionSchema(
        fields=fields,
        description="Fantasy basketball draft strategies and guides"
    )
    return schema


def get_trades_schema() -> CollectionSchema:
    """Schema for sportsbrain_trades collection"""
    fields = [
        FieldSchema(
            name="primary_key",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=False,
            description="MMH3 hash of trade content"
        ),
        
        FieldSchema(
            name="vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=768,
            description="Trade analysis embedding"
        ),
        
        FieldSchema(
            name="text",
            dtype=DataType.VARCHAR,
            max_length=65535,
            description="Trade news, analysis, or discussion"
        ),
        
        # High-frequency filters
        FieldSchema(
            name="source",
            dtype=DataType.VARCHAR,
            max_length=50,
            description="Source: reddit, twitter, espn, etc."
        ),
        
        FieldSchema(
            name="date_posted",
            dtype=DataType.INT64,
            description="Unix timestamp of post/article"
        ),
        
        FieldSchema(
            name="metadata",
            dtype=DataType.JSON,
            description="Players, teams, sentiment, engagement metrics"
        ),
        
        FieldSchema(
            name="created_at",
            dtype=DataType.INT64,
            description="Unix timestamp of record creation"
        )
    ]
    
    schema = CollectionSchema(
        fields=fields,
        description="NBA trade news, analysis, and community discussions"
    )
    return schema


# Collection configurations
COLLECTION_CONFIGS = {
    "sportsbrain_players": {
        "schema": get_player_schema,
        "scalar_index_fields": ["position"],  # Only low-cardinality scalar fields
        "vector_config": {
            "metric_type": "IP",  # Inner Product for normalized embeddings
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
    },
    "sportsbrain_strategies": {
        "schema": get_strategy_schema,
        "scalar_index_fields": ["strategy_type"],
        "vector_config": {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 512}
        }
    },
    "sportsbrain_trades": {
        "schema": get_trades_schema,
        "scalar_index_fields": ["source", "date_posted"],
        "vector_config": {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
    }
}


# Example metadata structures for reference
METADATA_EXAMPLES = {
    "player": {
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
            "categories": ["PTS", "REB", "AST"]
        },
        "age": 28,
        "height": "6-8",
        "injury_status": "healthy"
    },
    
    "strategy": {
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
        }
    },
    
    "trade": {
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
        "url": "https://reddit.com/r/fantasybball/..."
    }
}