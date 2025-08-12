"""Tests for user preferences endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.models import User, UserPreferences


def test_get_preferences_creates_default(
    client: TestClient,
    db_session: Session,
    auth_headers: dict
):
    """Test that getting preferences creates defaults if none exist"""
    response = client.get("/api/v1/users/preferences", headers=auth_headers)
    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["theme_mode"] == "light"  # Default theme
    assert data["preferred_agent"] == "intelligence"  # Default agent
    assert data["league_type"] == "h2h_9cat"  # Default league type


def test_update_theme_preference(
    client: TestClient,
    db_session: Session,
    auth_headers: dict
):
    """Test updating theme preference"""
    # Update theme to dark
    response = client.put(
        "/api/v1/users/preferences",
        json={"theme_mode": "dark"},
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["theme_mode"] == "dark"
    
    # Verify it persisted
    response = client.get("/api/v1/users/preferences", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["theme_mode"] == "dark"


def test_toggle_theme(
    client: TestClient,
    db_session: Session,
    auth_headers: dict
):
    """Test theme toggle endpoint"""
    # Get initial theme
    response = client.get("/api/v1/users/preferences", headers=auth_headers)
    initial_theme = response.json()["theme_mode"]
    
    # Toggle theme
    response = client.patch("/api/v1/users/preferences/theme", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    expected_theme = "dark" if initial_theme == "light" else "light"
    assert data["theme_mode"] == expected_theme


def test_reset_preferences(
    client: TestClient,
    db_session: Session,
    auth_headers: dict
):
    """Test resetting preferences to defaults"""
    # First change some preferences
    client.put(
        "/api/v1/users/preferences",
        json={
            "theme_mode": "dark",
            "preferred_agent": "draft_prep",
            "team_size": 10
        },
        headers=auth_headers
    )
    
    # Reset preferences
    response = client.post("/api/v1/users/preferences/reset", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["theme_mode"] == "light"  # Back to default
    assert data["preferred_agent"] == "intelligence"  # Back to default
    assert data["team_size"] == 12  # Back to default


def test_preferences_require_auth(client: TestClient):
    """Test that preferences endpoints require authentication"""
    # All endpoints should return 401 without auth
    response = client.get("/api/v1/users/preferences")
    assert response.status_code == 401
    
    response = client.put("/api/v1/users/preferences", json={"theme_mode": "dark"})
    assert response.status_code == 401
    
    response = client.patch("/api/v1/users/preferences/theme")
    assert response.status_code == 401
    
    response = client.post("/api/v1/users/preferences/reset")
    assert response.status_code == 401