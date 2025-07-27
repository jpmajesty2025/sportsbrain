from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class GameBase(BaseModel):
    date: datetime
    home_team: str
    away_team: str
    venue: Optional[str] = None
    season: Optional[str] = None
    week: Optional[int] = None
    game_type: Optional[str] = "regular"

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    date: Optional[datetime] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: Optional[str] = None
    venue: Optional[str] = None
    season: Optional[str] = None
    week: Optional[int] = None
    game_type: Optional[str] = None
    weather_conditions: Optional[Dict[str, Any]] = None

class Game(GameBase):
    id: int
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    weather_conditions: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    name: str
    city: Optional[str] = None
    abbreviation: Optional[str] = None
    conference: Optional[str] = None
    division: Optional[str] = None
    founded_year: Optional[int] = None
    colors: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True