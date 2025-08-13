#!/usr/bin/env python3
"""Test with correct field names and doubled path"""

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

# Test with correct field names and doubled path
print("\nTesting with correct format:")
print("  Path: /api/v1/api/v1/secure/query")
print("  Fields: message (not query), agent_type (not agent_name)")

response = requests.post(
    f"{base_url}/api/v1/api/v1/secure/query",
    json={
        "message": "Find sleepers like Sengun",
        "agent_type": "intelligence"
    },
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30
)

print(f"\nResponse status: {response.status_code}")
if response.status_code == 200:
    print("SUCCESS! The agent responded.")
    result = response.json()
    print(f"\nFull response structure:")
    print(json.dumps(result, indent=2))
    
    if "content" in result:
        print(f"\nAgent response content:\n{result['content']}")
else:
    print(f"Error: {response.text}")