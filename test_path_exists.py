#!/usr/bin/env python3
"""Just test if paths exist (not 404)"""

import requests
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
    data={"username": username, "password": password}
)

token = login_response.json()["access_token"]
print(f"Got token\n")

# Test paths - just check if they exist
paths = [
    "/api/v1/api/v1/secure/query",
    "/api/v1/secure/query", 
    "/secure/query",
]

for path in paths:
    print(f"Testing {path}...")
    try:
        response = requests.post(
            f"{base_url}{path}",
            json={"message": "test", "agent_type": "intelligence"},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=2  # Short timeout - we just want to see if it's 404 or not
        )
        print(f"  Status: {response.status_code}")
        if response.status_code != 404:
            print(f"  ✓ PATH EXISTS at {path}")
    except requests.exceptions.Timeout:
        print(f"  Timeout - but path likely exists (agent processing)")
    except Exception as e:
        print(f"  Error: {e}")