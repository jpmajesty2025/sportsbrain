"""Debug test for preferences endpoint"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_auth_login_works(client: TestClient, test_user):
    """Test that we can login and get a token"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    print(f"Login response status: {response.status_code}")
    print(f"Login response body: {response.json()}")
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]


def test_preferences_endpoint_with_token(client: TestClient, test_user):
    """Test preferences endpoint with explicit token"""
    # First login
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Now try to get preferences
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/preferences", headers=headers)
    
    print(f"Preferences response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Preferences response body: {response.json()}")
    
    assert response.status_code == 200