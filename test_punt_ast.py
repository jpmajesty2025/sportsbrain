#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test punt AST build directly"""

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

# Test punt AST build
print("\nTesting punt AST build...")
response = requests.post(
    f"{base_url}/api/v1/secure/query",
    json={
        "message": "Best punt AST build?",
        "agent_type": "draft_prep"
    },
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    timeout=30
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Agent: {result.get('agent', 'unknown')}")
    content = result.get('content', 'no content')
    # Handle unicode issues
    try:
        print(f"Content: {content}")
    except UnicodeEncodeError:
        print(f"Content (encoded): {content.encode('ascii', 'ignore').decode('ascii')}")
    print(f"Metadata: {result.get('metadata', {})}")
else:
    print(f"Error: {response.text}")