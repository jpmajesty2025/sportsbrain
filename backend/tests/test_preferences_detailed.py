"""Detailed debug test for preferences endpoint"""
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User, UserPreferences
from app.core.security import get_password_hash


def test_preferences_with_detailed_error(client: TestClient, db_session: Session):
    """Test preferences endpoint with detailed error reporting"""
    
    # Create a test user
    user = User(
        email="debug@example.com",
        username="debuguser",
        full_name="Debug User",
        hashed_password=get_password_hash("debugpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "debuguser", "password": "debugpassword"}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(f"Login error: {login_response.json()}")
        assert False, "Login failed"
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Now try to get preferences
    response = client.get("/api/v1/users/preferences", headers=headers)
    
    print(f"\n=== RESPONSE DETAILS ===")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code != 200:
        error_detail = response.json()
        print(f"\n=== ERROR DETAILS ===")
        print(json.dumps(error_detail, indent=2))
        
        # Check if it's a validation error
        if "detail" in error_detail:
            if isinstance(error_detail["detail"], list):
                for error in error_detail["detail"]:
                    print(f"\nField: {error.get('loc', 'unknown')}")
                    print(f"Message: {error.get('msg', 'no message')}")
                    print(f"Type: {error.get('type', 'unknown')}")
    else:
        print(f"\n=== SUCCESS RESPONSE ===")
        print(json.dumps(response.json(), indent=2))
    
    # Also check what's actually in the database
    prefs = db_session.query(UserPreferences).filter(
        UserPreferences.user_id == user.id
    ).first()
    
    if prefs:
        print(f"\n=== DATABASE RECORD ===")
        print(f"ID: {prefs.id}")
        print(f"User ID: {prefs.user_id}")
        print(f"Theme Mode: {prefs.theme_mode}")
        print(f"Sidebar Collapsed: {prefs.sidebar_collapsed}")
        print(f"Preferred Agent: {prefs.preferred_agent}")
        print(f"Agent Response Style: {prefs.agent_response_style}")
        print(f"League Type: {prefs.league_type}")
        print(f"Team Size: {prefs.team_size}")
        print(f"Favorite Team: {prefs.favorite_team}")
        print(f"Email Notifications: {prefs.email_notifications}")
        print(f"Injury Alerts: {prefs.injury_alerts}")
        print(f"Trade Alerts: {prefs.trade_alerts}")
        print(f"Default Stat View: {prefs.default_stat_view}")
        print(f"Show Advanced Stats: {prefs.show_advanced_stats}")
    else:
        print("\n=== NO DATABASE RECORD FOUND ===")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"