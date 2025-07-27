from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import Game, GameStats, User
from app.schemas.game import Game as GameSchema, GameCreate, GameUpdate
from app.schemas.player import GameStats as GameStatsSchema, GameStatsCreate
from app.api.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[GameSchema])
async def read_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    games = db.query(Game).offset(skip).limit(limit).all()
    return games

@router.post("/", response_model=GameSchema)
async def create_game(
    game: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_game = Game(**game.dict())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

@router.get("/{game_id}", response_model=GameSchema)
async def read_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.put("/{game_id}", response_model=GameSchema)
async def update_game(
    game_id: int,
    game_update: GameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    
    update_data = game_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(game, field, value)
    
    db.commit()
    db.refresh(game)
    return game

@router.get("/{game_id}/stats", response_model=List[GameStatsSchema])
async def read_game_stats(game_id: int, db: Session = Depends(get_db)):
    stats = db.query(GameStats).filter(GameStats.game_id == game_id).all()
    return stats

@router.post("/{game_id}/stats", response_model=GameStatsSchema)
async def create_game_stats(
    game_id: int,
    stats: GameStatsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify game exists
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Set the game_id from URL
    stats.game_id = game_id
    
    db_stats = GameStats(**stats.dict())
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return db_stats