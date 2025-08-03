#!/usr/bin/env python3
"""
Manual deployment testing script
Run this locally to verify your deployed services are working
"""
import requests
import time
import sys
from typing import Dict, List, Tuple


class DeploymentTester:
    def __init__(self, backend_url: str, frontend_url: str):
        self.backend_url = backend_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/')
        self.results: List[Tuple[str, bool, str]] = []
    
    def test_endpoint(self, name: str, url: str, expected_status: int = 200, timeout: int = 10) -> bool:
        """Test a single endpoint and record results"""
        try:
            print(f"Testing {name}... ", end='', flush=True)
            start_time = time.time()
            
            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            success = response.status_code == expected_status
            
            if success:
                print(f"✅ ({response.status_code}, {response_time:.2f}s)")
                self.results.append((name, True, f"OK - {response_time:.2f}s"))
            else:
                print(f"❌ ({response.status_code})")
                self.results.append((name, False, f"Status {response.status_code}"))
            
            return success
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)}")
            self.results.append((name, False, str(e)))
            return False
    
    def test_json_endpoint(self, name: str, url: str, required_keys: List[str] = None) -> bool:
        """Test JSON endpoint and validate response structure"""
        try:
            print(f"Testing {name}... ", end='', flush=True)
            
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Status {response.status_code}")
                self.results.append((name, False, f"Status {response.status_code}"))
                return False
            
            data = response.json()
            
            if required_keys:
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    print(f"❌ Missing keys: {missing_keys}")
                    self.results.append((name, False, f"Missing keys: {missing_keys}"))
                    return False
            
            print("✅")
            self.results.append((name, True, "OK"))
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.results.append((name, False, str(e)))
            return False
    
    def run_all_tests(self):
        """Run comprehensive deployment tests"""
        print("🚀 SportsBrain Deployment Verification")
        print("=" * 50)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print()
        
        # Backend tests
        print("Backend Service Tests:")
        self.test_json_endpoint("Backend Health", f"{self.backend_url}/health", ["status"])
        self.test_json_endpoint("Backend Detailed Health", f"{self.backend_url}/health/detailed", ["status", "checks"])
        self.test_json_endpoint("Backend Root", f"{self.backend_url}/", ["message"])
        self.test_endpoint("Backend API Docs", f"{self.backend_url}/api/v1/docs")
        
        print()
        
        # Frontend tests
        print("Frontend Service Tests:")
        self.test_endpoint("Frontend Root", f"{self.frontend_url}/")
        
        print()
        
        # Integration tests
        print("Integration Tests:")
        self.test_cors()
        
        print()
        
        # Summary
        self.print_summary()
    
    def test_cors(self):
        """Test CORS configuration"""
        try:
            print("Testing CORS configuration... ", end='', flush=True)
            
            headers = {
                "Origin": self.frontend_url,
                "Access-Control-Request-Method": "GET",
            }
            
            response = requests.options(f"{self.backend_url}/health", headers=headers, timeout=10)
            
            if response.status_code in [200, 204] or "access-control-allow-origin" in response.headers:
                print("✅")
                self.results.append(("CORS Configuration", True, "OK"))
            else:
                print("⚠️  May have CORS issues")
                self.results.append(("CORS Configuration", False, "Potential CORS issues"))
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.results.append(("CORS Configuration", False, str(e)))
    
    def print_summary(self):
        """Print test results summary"""
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        print("Test Results Summary:")
        print("=" * 50)
        
        for name, success, message in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status:8} {name:25} - {message}")
        
        print()
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your deployment is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the results above.")
            return False


def main():
    """Main function to run deployment tests"""
    
    # Default Railway URLs - update these with your actual URLs
    backend_url = input("Enter your backend URL (e.g., https://sportsbrain-backend.railway.app): ").strip()
    frontend_url = input("Enter your frontend URL (e.g., https://sportsbrain-frontend.railway.app): ").strip()
    
    if not backend_url or not frontend_url:
        print("❌ Both URLs are required!")
        sys.exit(1)
    
    tester = DeploymentTester(backend_url, frontend_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()