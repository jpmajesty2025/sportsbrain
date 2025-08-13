#!/usr/bin/env python3
"""Test script to verify secure agent endpoint routing"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_secure_agent_endpoint():
    """Test the secure agent query endpoint"""
    
    # Configuration
    base_url = "https://sportsbrain-backend-production.up.railway.app"
    
    # First, we need to login to get a token
    print("Step 1: Testing login endpoint...")
    login_url = f"{base_url}/api/v1/auth/login"
    
    # Get credentials from environment
    username = os.getenv("SPORTSBRAIN_USERNAME")
    password = os.getenv("SPORTSBRAIN_PASSWORD")
    
    if not username or not password:
        print("ERROR: SPORTSBRAIN_USERNAME and SPORTSBRAIN_PASSWORD must be set in .env file")
        print("Please add these to your .env file:")
        print("  SPORTSBRAIN_USERNAME=your_username")
        print("  SPORTSBRAIN_PASSWORD=your_password")
        return
    
    print(f"Using username: {username}")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        # Test login (form data)
        login_response = requests.post(
            login_url,
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            print("\nTrying without authentication...")
            token = None
        else:
            token = login_response.json().get("access_token")
            print(f"Login successful, got token: {token[:20]}..." if token else "No token received")
    except Exception as e:
        print(f"Login error: {e}")
        token = None
    
    # Test the secure agent endpoint
    print("\nStep 2: Testing secure agent query endpoint...")
    query_url = f"{base_url}/api/v1/secure/query"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "agent_name": "IntelligenceAgent",
        "query": "Find sleepers like Sengun"
    }
    
    print(f"POST {query_url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            query_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("Success! Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print("\nParsed error:")
                print(json.dumps(error_data, indent=2))
            except:
                pass
                
    except requests.exceptions.Timeout:
        print("Request timed out after 30 seconds")
    except Exception as e:
        print(f"Request error: {e}")
    
    # Also test what endpoints are available
    print("\n" + "="*50)
    print("Step 3: Checking available endpoints...")
    
    # Try to get the OpenAPI schema
    openapi_url = f"{base_url}/api/v1/openapi.json"
    print(f"GET {openapi_url}")
    
    try:
        response = requests.get(openapi_url, timeout=10)
        if response.status_code == 200:
            openapi_data = response.json()
            print("\nAvailable paths:")
            paths = openapi_data.get("paths", {})
            
            # Look for secure-related endpoints
            secure_paths = [path for path in paths.keys() if "secure" in path.lower()]
            if secure_paths:
                print("Secure endpoints found:")
                for path in secure_paths:
                    methods = list(paths[path].keys())
                    print(f"  {path}: {methods}")
            else:
                print("No secure endpoints found in OpenAPI spec")
                
            # Show all paths if no secure paths found
            if not secure_paths and len(paths) < 50:
                print("\nAll available paths:")
                for path in sorted(paths.keys()):
                    methods = list(paths[path].keys())
                    print(f"  {path}: {methods}")
        else:
            print(f"Could not fetch OpenAPI spec: {response.status_code}")
    except Exception as e:
        print(f"Error fetching OpenAPI spec: {e}")

if __name__ == "__main__":
    test_secure_agent_endpoint()