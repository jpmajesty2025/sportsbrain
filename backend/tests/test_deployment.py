"""
Integration tests for deployed services on Railway
These tests verify that all services are running and can communicate
"""
import pytest
import requests
import asyncio
import aiohttp
import os
from typing import Dict, Any


class TestDeployedServices:
    """Test suite for verifying deployed services are working"""
    
    @pytest.fixture
    def base_urls(self) -> Dict[str, str]:
        """Get service URLs from environment or use Railway defaults"""
        return {
            "backend": os.getenv("BACKEND_URL", "https://sportsbrain-backend.railway.app"),
            "frontend": os.getenv("FRONTEND_URL", "https://sportsbrain-frontend.railway.app"),
        }
    
    def test_backend_health_check(self, base_urls):
        """Test that backend service is responding"""
        response = requests.get(f"{base_urls['backend']}/health", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sportsbrain-backend"
    
    def test_backend_detailed_health_check(self, base_urls):
        """Test that backend can connect to database and Redis"""
        response = requests.get(f"{base_urls['backend']}/health/detailed", timeout=15)
        assert response.status_code == 200
        
        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]
        
        # All checks should be healthy
        assert data["checks"]["database"] == "healthy"
        assert data["checks"]["redis"] == "healthy"
        assert data["status"] == "healthy"
    
    def test_backend_root_endpoint(self, base_urls):
        """Test backend root endpoint"""
        response = requests.get(f"{base_urls['backend']}/", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "SportsBrain" in data["message"]
    
    def test_frontend_accessibility(self, base_urls):
        """Test that frontend is serving content"""
        response = requests.get(base_urls["frontend"], timeout=10)
        assert response.status_code == 200
        
        # Check for typical React app indicators
        content = response.text
        assert "<!DOCTYPE html>" in content or "<html" in content
    
    def test_cors_configuration(self, base_urls):
        """Test CORS headers are properly configured"""
        headers = {
            "Origin": base_urls["frontend"],
            "Access-Control-Request-Method": "GET",
        }
        
        # Test preflight request
        response = requests.options(f"{base_urls['backend']}/health", headers=headers, timeout=10)
        
        # Should either succeed or return CORS headers
        assert response.status_code in [200, 204] or "access-control-allow-origin" in response.headers
    
    @pytest.mark.asyncio
    async def test_services_performance(self, base_urls):
        """Test that services respond within acceptable time limits"""
        async with aiohttp.ClientSession() as session:
            # Test backend response time
            import time
            start_time = time.time()
            
            async with session.get(f"{base_urls['backend']}/health") as response:
                assert response.status == 200
                response_time = time.time() - start_time
                
                # Should respond within 3 seconds
                assert response_time < 3.0, f"Backend took {response_time:.2f}s to respond"
    
    def test_api_endpoints_exist(self, base_urls):
        """Test that key API endpoints are accessible"""
        endpoints_to_test = [
            "/",
            "/health", 
            "/health/detailed",
            "/api/v1/docs",  # OpenAPI docs should be available
        ]
        
        for endpoint in endpoints_to_test:
            response = requests.get(f"{base_urls['backend']}{endpoint}", timeout=10)
            
            # Should not return 404 or 500 errors
            assert response.status_code not in [404, 500], f"Endpoint {endpoint} returned {response.status_code}"
            assert response.status_code < 500, f"Server error on {endpoint}: {response.status_code}"


class TestServiceIntegration:
    """Test service-to-service communication"""
    
    @pytest.fixture
    def base_urls(self) -> Dict[str, str]:
        return {
            "backend": os.getenv("BACKEND_URL", "https://sportsbrain-backend.railway.app"),
            "frontend": os.getenv("FRONTEND_URL", "https://sportsbrain-frontend.railway.app"),
        }
    
    def test_full_stack_connectivity(self, base_urls):
        """Test that the full stack is connected and working"""
        # 1. Backend is healthy
        backend_response = requests.get(f"{base_urls['backend']}/health/detailed", timeout=15)
        assert backend_response.status_code == 200
        assert backend_response.json()["status"] == "healthy"
        
        # 2. Frontend is serving
        frontend_response = requests.get(base_urls["frontend"], timeout=10)
        assert frontend_response.status_code == 200
        
        # 3. Backend API docs are accessible (confirms FastAPI is working)
        docs_response = requests.get(f"{base_urls['backend']}/api/v1/docs", timeout=10)
        assert docs_response.status_code == 200


if __name__ == "__main__":
    # Allow running tests directly for manual verification
    pytest.main([__file__, "-v"])