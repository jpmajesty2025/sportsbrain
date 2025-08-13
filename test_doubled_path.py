#!/usr/bin/env python3
"""Test the doubled path to confirm it works"""

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

# Test with the doubled path
print("\nTesting with doubled path: /api/v1/api/v1/secure/query")
response = requests.post(
    f"{base_url}/api/v1/api/v1/secure/query",
    json={
        "agent_name": "IntelligenceAgent",
        "query": "Find sleepers like Sengun"
    },
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30
)

print(f"Response status: {response.status_code}")
if response.status_code == 200:
    print("SUCCESS! The doubled path works.")
    result = response.json()
    print(f"Response preview: {json.dumps(result, indent=2)[:500]}...")
else:
    print(f"Error: {response.text}")