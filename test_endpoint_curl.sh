#!/bin/bash

# Test secure agent endpoint routing
BASE_URL="https://sportsbrain-backend-production.up.railway.app"

echo "Testing secure agent endpoint routing..."
echo "========================================"

# Test 1: Check if the endpoint exists (should return 401 or 422 without auth, not 404)
echo -e "\n1. Testing POST /api/v1/secure/query (without auth):"
curl -X POST \
  "${BASE_URL}/api/v1/secure/query" \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "IntelligenceAgent", "query": "test"}' \
  -w "\nHTTP Status: %{http_code}\n" \
  -s

# Test 2: Check OpenAPI documentation
echo -e "\n2. Checking OpenAPI spec for secure endpoints:"
curl -s "${BASE_URL}/api/v1/openapi.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
paths = data.get('paths', {})
secure_paths = [p for p in paths if 'secure' in p.lower()]
if secure_paths:
    print('Found secure endpoints:')
    for path in secure_paths:
        print(f'  {path}')
else:
    print('No secure endpoints found')
    print('Looking for query endpoints:')
    query_paths = [p for p in paths if 'query' in p.lower()]
    for path in query_paths:
        print(f'  {path}')
"

# Test 3: Try different possible paths
echo -e "\n3. Testing different possible endpoint paths:"
PATHS=(
    "/api/v1/secure/query"
    "/api/v1/secure-agent-query"
    "/api/v1/agents/secure/query"
    "/secure/query"
)

for path in "${PATHS[@]}"; do
    echo -e "\nTrying ${path}:"
    response=$(curl -X POST \
      "${BASE_URL}${path}" \
      -H "Content-Type: application/json" \
      -d '{"agent_name": "IntelligenceAgent", "query": "test"}' \
      -w "\nHTTP Status: %{http_code}" \
      -s)
    echo "$response" | tail -n 1
done