"""
User preferences API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.models.models import User, UserPreferences
from app.api.endpoints.auth import get_current_user

router = APIRouter()

class UserPreferencesUpdate(BaseModel):
    theme_mode: Optional[str] = None
    sidebar_collapsed: Optional[bool] = None
    preferred_agent: Optional[str] = None
    agent_response_style: Optional[str] = None
    league_type: Optional[str] = None
    team_size: Optional[int] = None
    favorite_team: Optional[str] = None
    email_notifications: Optional[bool] = None
    injury_alerts: Optional[bool] = None
    trade_alerts: Optional[bool] = None
    default_stat_view: Optional[str] = None
    show_advanced_stats: Optional[bool] = None

class UserPreferencesResponse(BaseModel):
    theme_mode: str
    sidebar_collapsed: bool
    preferred_agent: str
    agent_response_style: str
    league_type: str
    team_size: int
    favorite_team: Optional[str]
    email_notifications: bool
    injury_alerts: bool
    trade_alerts: bool
    default_stat_view: str
    show_advanced_stats: bool

    class Config:
        from_attributes = True

@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's preferences"""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not preferences:
        # Create default preferences for user
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return preferences

@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's preferences"""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not preferences:
        # Create new preferences with the update
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
    
    # Update only provided fields
    update_data = preferences_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)
    
    db.commit()
    db.refresh(preferences)
    
    return preferences

@router.patch("/preferences/theme", response_model=dict)
async def toggle_theme_mode(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle between light and dark theme"""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not preferences:
        preferences = UserPreferences(
            user_id=current_user.id,
            theme_mode="dark"  # If no preferences, first toggle goes to dark
        )
        db.add(preferences)
    else:
        # Toggle the theme
        preferences.theme_mode = "dark" if preferences.theme_mode == "light" else "light"
    
    db.commit()
    db.refresh(preferences)
    
    return {"theme_mode": preferences.theme_mode}

@router.post("/preferences/reset", response_model=UserPreferencesResponse)
async def reset_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset user preferences to defaults"""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if preferences:
        # Reset to defaults
        preferences.theme_mode = "light"
        preferences.sidebar_collapsed = False
        preferences.preferred_agent = "intelligence"
        preferences.agent_response_style = "detailed"
        preferences.league_type = "h2h_9cat"
        preferences.team_size = 12
        preferences.favorite_team = None
        preferences.email_notifications = True
        preferences.injury_alerts = True
        preferences.trade_alerts = True
        preferences.default_stat_view = "season"
        preferences.show_advanced_stats = False
    else:
        # Create new with defaults
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
    
    db.commit()
    db.refresh(preferences)
    
    return preferences