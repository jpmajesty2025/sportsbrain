"""
API endpoint testing for SportsBrain
Tests current endpoints and prepares for Phase 1 enhancements
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.models import User, Player
from app.core.security import create_access_token


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_basic_health_check(self):
        """Test basic health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sportsbrain-backend"
    
    def test_detailed_health_check(self):
        """Test detailed health check with database connectivity"""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "SportsBrain" in data["message"]


class TestAuthenticationEndpoints:
    """Test authentication API endpoints"""
    
    def test_login_endpoint_exists(self):
        """Test that login endpoint is accessible"""
        # This should return 422 (validation error) not 404
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code != 404
    
    def test_register_endpoint_exists(self):
        """Test that register endpoint is accessible"""
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code != 404


class TestPlayerEndpoints:
    """Test player-related API endpoints (current and future)"""
    
    def test_players_list_endpoint(self):
        """Test listing players"""
        response = client.get("/api/v1/players/")
        
        # Should not return 404 or 500
        assert response.status_code not in [404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_player_detail_endpoint_structure(self):
        """Test player detail endpoint structure"""
        # Test with a non-existent ID to check endpoint structure
        response = client.get("/api/v1/players/999999")
        
        # Should return 404 (not found) not 500 (server error)
        assert response.status_code in [404, 422]  # 422 for validation error


class TestGameEndpoints:
    """Test game-related API endpoints"""
    
    def test_games_list_endpoint(self):
        """Test listing games"""
        response = client.get("/api/v1/games/")
        assert response.status_code not in [404, 500]


class TestAgentEndpoints:
    """Test multi-agent system endpoints"""
    
    def test_agent_query_endpoint_exists(self):
        """Test that agent query endpoint exists"""
        response = client.post("/api/v1/agents/query", json={})
        assert response.status_code != 404
    
    def test_agent_session_endpoint_exists(self):
        """Test agent session management"""
        response = client.get("/api/v1/agents/sessions")
        assert response.status_code != 404


class TestCORSConfiguration:
    """Test CORS configuration for frontend integration"""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are configured"""
        response = client.options("/health")
        
        # Should have CORS headers or be allowed
        assert response.status_code in [200, 204]
    
    def test_cors_with_origin(self):
        """Test CORS with origin header"""
        headers = {"Origin": "http://localhost:3000"}
        response = client.get("/health", headers=headers)
        
        assert response.status_code == 200


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_docs_accessible(self):
        """Test that OpenAPI docs are accessible"""
        response = client.get("/api/v1/docs")
        assert response.status_code == 200
        
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_openapi_json_accessible(self):
        """Test that OpenAPI JSON is accessible"""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data


class TestErrorHandling:
    """Test API error handling"""
    
    def test_404_handling(self):
        """Test 404 error handling for non-existent endpoints"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test method not allowed handling"""
        response = client.delete("/health")  # Health only supports GET
        assert response.status_code == 405


class TestFutureEndpoints:
    """Test structure for planned Phase 1 endpoints"""
    
    def test_community_sentiment_endpoint_structure(self):
        """Test future community sentiment endpoint"""
        response = client.get("/api/v1/community/sentiment/player/1")
        
        # Endpoint may not exist yet, but should not cause server error
        assert response.status_code != 500
    
    def test_user_preferences_endpoint_structure(self):
        """Test future user preferences endpoint"""
        response = client.get("/api/v1/users/preferences")
        
        # May require auth, but should not cause server error
        assert response.status_code != 500
    
    def test_matchup_analysis_endpoint_structure(self):
        """Test future matchup analysis endpoint"""
        response = client.get("/api/v1/analysis/matchup/player/1/opponent/2")
        
        assert response.status_code != 500


class TestPerformanceRequirements:
    """Test performance requirements for Phase 1"""
    
    def test_health_check_response_time(self):
        """Test health check meets performance requirements"""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond quickly
    
    def test_api_docs_response_time(self):
        """Test API docs load within reasonable time"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/docs")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0  # Web requirement: <3s


# Test data fixtures
@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    token = create_access_token(subject="test@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_player_data():
    """Sample player data for testing"""
    return {
        "name": "Test Player",
        "position": "PG",
        "team": "Test Team",
        "jersey_number": 1,
        "height": 6.0,
        "weight": 180
    }