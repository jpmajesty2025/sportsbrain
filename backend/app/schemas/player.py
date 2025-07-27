from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PlayerBase(BaseModel):
    name: str
    position: Optional[str] = None
    team: Optional[str] = None
    jersey_number: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    birth_date: Optional[datetime] = None
    nationality: Optional[str] = None

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    team: Optional[str] = None
    jersey_number: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    birth_date: Optional[datetime] = None
    nationality: Optional[str] = None
    is_active: Optional[bool] = None

class Player(PlayerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class GameStatsBase(BaseModel):
    points: int = 0
    assists: int = 0
    rebounds: int = 0
    steals: int = 0
    blocks: int = 0
    turnovers: int = 0
    field_goals_made: int = 0
    field_goals_attempted: int = 0
    three_pointers_made: int = 0
    three_pointers_attempted: int = 0
    free_throws_made: int = 0
    free_throws_attempted: int = 0
    minutes_played: float = 0.0
    plus_minus: int = 0

class GameStatsCreate(GameStatsBase):
    player_id: int
    game_id: int

class GameStats(GameStatsBase):
    id: int
    player_id: int
    game_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True