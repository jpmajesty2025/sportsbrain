from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import Player, GameStats
from app.schemas.player import Player as PlayerSchema, PlayerCreate, PlayerUpdate, GameStats as GameStatsSchema
from app.api.endpoints.auth import get_current_user
from app.models.models import User

router = APIRouter()

@router.get("/", response_model=List[PlayerSchema])
async def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = db.query(Player).offset(skip).limit(limit).all()
    return players

@router.post("/", response_model=PlayerSchema)
async def create_player(
    player: PlayerCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_player = Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@router.get("/{player_id}", response_model=PlayerSchema)
async def read_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.put("/{player_id}", response_model=PlayerSchema)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    update_data = player_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)
    
    db.commit()
    db.refresh(player)
    return player

@router.get("/{player_id}/stats", response_model=List[GameStatsSchema])
async def read_player_stats(player_id: int, db: Session = Depends(get_db)):
    stats = db.query(GameStats).filter(GameStats.player_id == player_id).all()
    return stats

@router.delete("/{player_id}")
async def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    player.is_active = False
    db.commit()
    return {"message": "Player deactivated successfully"}