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
        
        # Database should be healthy in test environment
        assert data["checks"]["database"] == "healthy"
        
        # Redis might not be available in test environment - check it exists
        redis_status = data["checks"]["redis"]
        assert redis_status is not None
    
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
    """Test multi-agent system endpoints (Phase 1: Session Management)"""
    
    def test_agent_sessions_endpoint_exists(self):
        """Test that agent sessions endpoint exists"""
        response = client.get("/api/v1/agents/sessions")
        # Should return 401 (unauthorized) not 404 (not found) since auth is required
        assert response.status_code in [401, 422]  # 422 for validation error
    
    def test_agent_session_creation_endpoint_exists(self):
        """Test agent session creation endpoint exists"""
        response = client.post("/api/v1/agents/sessions", json={})
        # Should return 401 (unauthorized) or 422 (validation error), not 404
        assert response.status_code in [401, 422]


class TestCORSConfiguration:
    """Test CORS configuration for frontend integration"""
    
    def test_cors_with_origin_header(self):
        """Test CORS with origin header"""
        headers = {"Origin": "http://localhost:3000"}
        response = client.get("/health", headers=headers)
        
        assert response.status_code == 200
        # FastAPI CORS middleware should handle this properly
    
    def test_cors_preflight_request(self):
        """Test CORS preflight request handling"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        # Test on a POST endpoint that exists
        response = client.options("/api/v1/agents/sessions", headers=headers)
        
        # Should either handle the preflight or return method not allowed
        # FastAPI CORS middleware handles this automatically
        assert response.status_code in [200, 204, 405]
    
    def test_cors_actual_request(self):
        """Test actual CORS request with origin"""
        headers = {"Origin": "http://localhost:3000"}
        response = client.get("/", headers=headers)
        
        assert response.status_code == 200
        # Response should succeed with CORS headers handled by middleware


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_docs_accessible(self):
        """Test that OpenAPI docs are accessible"""
        response = client.get("/docs")  # FastAPI serves docs at /docs by default
        assert response.status_code == 200
        
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_openapi_json_accessible(self):
        """Test that OpenAPI JSON is accessible"""
        response = client.get("/api/v1/openapi.json")  # This is correctly configured
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
    
    def test_redoc_docs_accessible(self):
        """Test that ReDoc documentation is accessible"""
        response = client.get("/redoc")  # FastAPI also serves ReDoc at /redoc
        assert response.status_code == 200
        
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")


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
    """Test structure for planned future endpoints (Phase 2+)"""
    
    def test_agent_query_endpoint_not_implemented_yet(self):
        """Test that agent query endpoint is not implemented yet in Phase 1"""
        response = client.post("/api/v1/agents/query", json={})
        
        # Should return 404 (not found) since not implemented in Phase 1
        assert response.status_code == 404
    
    def test_community_endpoints_not_implemented_yet(self):
        """Test future community endpoints not implemented"""
        response = client.get("/api/v1/community/sentiment")
        
        # Should return 404 (not found) since community endpoints not implemented in Phase 1
        assert response.status_code == 404
    
    def test_analysis_endpoints_not_implemented_yet(self):
        """Test future analysis endpoints not implemented"""
        response = client.get("/api/v1/analysis/matchup")
        
        # Should return 404 (not found) since analysis endpoints not implemented in Phase 1
        assert response.status_code == 404
    
    def test_user_preferences_subresource_not_implemented_yet(self):
        """Test future user preferences subresource not implemented"""
        response = client.get("/api/v1/users/123/preferences")
        
        # Should return 404 (not found) since preferences subresource not implemented
        assert response.status_code == 404


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
        response = client.get("/docs")  # Correct FastAPI docs URL
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