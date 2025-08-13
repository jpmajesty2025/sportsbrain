#!/usr/bin/env python3
"""Test enhanced Intelligence Agent"""

import requests
import os
from dotenv import load_dotenv
import json

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
print(f"Logged in successfully\n")

# Test queries to showcase enhanced reasoning
test_queries = [
    "Which sophomores will break out?",
    "Analyze Paolo Banchero in detail",
    "Find sleepers like Sengun"
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)
    
    response = requests.post(
        f"{base_url}/api/v1/secure/query",
        json={
            "message": query,
            "agent_type": "intelligence"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result.get('content', 'No content')
        
        # Clean up for display
        content = content.encode('ascii', 'ignore').decode('ascii')
        
        print(f"\nResponse from Enhanced Intelligence Agent:")
        print("-" * 40)
        print(content[:1500])  # Show first 1500 chars
        if len(content) > 1500:
            print("\n[... response truncated ...]")
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:500])