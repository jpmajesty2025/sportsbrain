#!/usr/bin/env python3
"""Test to find the actual working path"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

base_url = "https://sportsbrain-backend-production.up.railway.app"

# Login
username = os.getenv("SPORTSBRAIN_USERNAME")
password = os.getenv("SPORTSBRAIN_PASSWORD")

print("Logging in...")
login_response = requests.post(
    f"{base_url}/api/v1/auth/login",
    data={"username": username, "password": password},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"Got token: {token[:30]}...")

# Test different paths
paths_to_test = [
    "/secure/query",
    "/api/v1/secure/query", 
    "/api/v1/api/v1/secure/query",
    "/api/secure/query",
]

for path in paths_to_test:
    print(f"\nTesting path: {path}")
    response = requests.post(
        f"{base_url}{path}",
        json={
            "message": "Find sleepers like Sengun",
            "agent_type": "intelligence"
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        timeout=5
    )
    
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  SUCCESS! This path works: {path}")
        result = response.json()
        if "content" in result:
            print(f"  Response preview: {result['content'][:100]}...")
        break
    elif response.status_code == 422:
        print(f"  422 - Validation error: {response.text[:100]}")
    elif response.status_code == 404:
        print(f"  404 - Not found")