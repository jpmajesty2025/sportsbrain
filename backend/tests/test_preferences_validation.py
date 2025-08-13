"""Test to diagnose preferences validation error"""
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User, UserPreferences
from app.core.security import get_password_hash


def test_preferences_validation_debug(client: TestClient, db_session: Session):
    """Debug test to see exact validation error"""
    
    # Create a test user
    user = User(
        email="validate@example.com",
        username="validateuser",
        full_name="Validate User",
        hashed_password=get_password_hash("validatepassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "validateuser", "password": "validatepassword"}
    )
    
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get preferences - this should create defaults
    response = client.get("/api/v1/users/preferences", headers=headers)
    
    print(f"\n=== GET PREFERENCES RESPONSE ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        error_body = response.json()
        print(f"Error Response: {json.dumps(error_body, indent=2)}")
        
        # If it's a validation error, show details
        if "detail" in error_body and isinstance(error_body["detail"], list):
            for err in error_body["detail"]:
                print(f"\nValidation Error:")
                print(f"  Location: {err.get('loc', [])}")
                print(f"  Message: {err.get('msg', '')}")
                print(f"  Type: {err.get('type', '')}")
                if "input" in err:
                    print(f"  Input: {err['input']}")
    else:
        print(f"Success: {json.dumps(response.json(), indent=2)}")
    
    # Check what's in the database
    db_prefs = db_session.query(UserPreferences).filter(
        UserPreferences.user_id == user.id
    ).first()
    
    if db_prefs:
        print(f"\n=== DATABASE PREFERENCES ===")
        for column in UserPreferences.__table__.columns:
            if column.name not in ['created_at', 'updated_at']:
                value = getattr(db_prefs, column.name)
                print(f"  {column.name}: {value} (type: {type(value).__name__})")
    else:
        print("\n=== NO PREFERENCES IN DATABASE ===")
    
    assert response.status_code == 200, "Preferences endpoint should return 200"