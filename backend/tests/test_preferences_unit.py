"""Unit tests for preferences endpoints (no database required)"""
import pytest
from app.api.endpoints.preferences import create_default_preferences


def test_create_default_preferences():
    """Test that create_default_preferences sets all required fields"""
    prefs = create_default_preferences(user_id=1)
    
    # Check all required fields are present and not None
    assert prefs.user_id == 1
    assert prefs.theme_mode == "light"
    assert prefs.sidebar_collapsed == False
    assert prefs.preferred_agent == "intelligence"
    assert prefs.agent_response_style == "detailed"
    assert prefs.league_type == "h2h_9cat"
    assert prefs.team_size == 12
    assert prefs.favorite_team is None  # This one is allowed to be None
    assert prefs.email_notifications == True
    assert prefs.injury_alerts == True
    assert prefs.trade_alerts == True
    assert prefs.default_stat_view == "season"
    assert prefs.show_advanced_stats == False
    
    # Verify that all non-nullable fields have values
    non_nullable_fields = [
        'theme_mode', 'sidebar_collapsed', 'preferred_agent',
        'agent_response_style', 'league_type', 'team_size',
        'email_notifications', 'injury_alerts', 'trade_alerts',
        'default_stat_view', 'show_advanced_stats'
    ]
    
    for field in non_nullable_fields:
        value = getattr(prefs, field)
        assert value is not None, f"Field {field} should not be None"


def test_preferences_response_model():
    """Test that UserPreferencesResponse model validates correctly"""
    from app.api.endpoints.preferences import UserPreferencesResponse
    
    # Test with valid data
    valid_data = {
        "theme_mode": "light",
        "sidebar_collapsed": False,
        "preferred_agent": "intelligence",
        "agent_response_style": "detailed",
        "league_type": "h2h_9cat",
        "team_size": 12,
        "favorite_team": None,
        "email_notifications": True,
        "injury_alerts": True,
        "trade_alerts": True,
        "default_stat_view": "season",
        "show_advanced_stats": False
    }
    
    response = UserPreferencesResponse(**valid_data)
    assert response.theme_mode == "light"
    
    # Test that missing required fields raise error
    invalid_data = {
        "theme_mode": "light",
        # Missing other required fields
    }
    
    with pytest.raises(Exception):  # Pydantic ValidationError
        UserPreferencesResponse(**invalid_data)