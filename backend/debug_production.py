"""
Debug script to check what's happening in production
"""

import requests
import json

def check_production():
    base_url = "https://sportsbrain-backend-production.up.railway.app"
    
    # 1. Check health
    print("1. Checking API Health...")
    health = requests.get(f"{base_url}/health/detailed")
    if health.status_code == 200:
        data = health.json()
        print(f"   Health: {data['status']}")
        print(f"   Services: {json.dumps(data['checks'], indent=2)}")
    else:
        print(f"   Failed: {health.status_code}")
    
    print("\n2. Checking API Docs...")
    # Try to get OpenAPI schema
    docs = requests.get(f"{base_url}/openapi.json")
    if docs.status_code == 200:
        schema = docs.json()
        # Look for agent endpoints
        paths = schema.get("paths", {})
        agent_endpoints = [p for p in paths if "agent" in p.lower() or "secure" in p.lower()]
        print(f"   Found {len(agent_endpoints)} agent-related endpoints:")
        for ep in agent_endpoints[:5]:
            print(f"     - {ep}")
    else:
        print(f"   Docs not accessible: {docs.status_code}")
    
    print("\n3. Response Time Check...")
    # The responses you got suggest agents ARE working, just not with reranking
    print("   Based on your responses:")
    print("   - Intelligence Agent: Responding but no reranking indicators")
    print("   - TradeImpact Agent: Responding but no reranking indicators")
    print("   - Likely issue: Reranking not active or being summarized")
    
    print("\n4. Recommendations:")
    print("   a) Check Railway logs for:")
    print("      - 'Reranker initialized successfully'")
    print("      - 'Milvus search found X documents'")
    print("      - 'Applying reranking to X documents'")
    print("      - Any errors loading BGE model")
    print("   b) Verify environment variables:")
    print("      - OPENAI_API_KEY is set")
    print("      - MILVUS_HOST and MILVUS_TOKEN are correct")
    print("   c) Check if Milvus collections are accessible from Railway")

if __name__ == "__main__":
    check_production()