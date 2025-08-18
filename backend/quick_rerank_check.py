"""
Quick Reranking Check - Simplified monitoring for production verification
"""

import requests
import time
import sys
from datetime import datetime

def quick_check(base_url="https://sportsbrain-backend-production.up.railway.app"):
    """Run a quick check to see if reranking is active"""
    
    print("\n" + "="*60)
    print(f"QUICK RERANKING CHECK")
    print(f"Target: {base_url}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("="*60 + "\n")
    
    # Test queries designed to trigger reranking
    test_cases = [
        {
            "agent": "trade_impact",
            "query": "How does Porzingis trade affect Tatum?",
            "expected_indicators": ["Enhanced", "Relevance", "fantasy impact"]
        },
        {
            "agent": "intelligence", 
            "query": "Find sleepers like Sengun",
            "expected_indicators": ["Similar", "Shot", "Sleeper Score"]
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"Testing {test['agent'].upper()}...")
        print(f"  Query: '{test['query']}'")
        
        start = time.time()
        try:
            response = requests.post(
                f"{base_url}/api/v1/secure/query",
                json={
                    "message": test["query"],
                    "agent_type": test["agent"]
                },
                timeout=30
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("content", data.get("response", ""))
                
                # Check for indicators
                found_indicators = []
                for indicator in test["expected_indicators"]:
                    if indicator.lower() in response_text.lower():
                        found_indicators.append(indicator)
                
                # Analyze results
                is_reranked = False
                reasons = []
                
                if elapsed > 8:
                    is_reranked = True
                    reasons.append(f"Long response time ({elapsed:.1f}s)")
                
                if "Enhanced with Reranking" in response_text:
                    is_reranked = True
                    reasons.append("Explicit reranking label")
                
                if "AI-Enhanced" in response_text:
                    is_reranked = True
                    reasons.append("AI-Enhanced content")
                
                if len(found_indicators) >= 2:
                    is_reranked = True
                    reasons.append(f"Found {len(found_indicators)}/{len(test['expected_indicators'])} expected indicators")
                
                # Print results
                if is_reranked:
                    print(f"  [OK] RERANKING DETECTED!")
                    for reason in reasons:
                        print(f"     - {reason}")
                else:
                    print(f"  [?] Reranking uncertain")
                    print(f"     - Response time: {elapsed:.1f}s")
                    print(f"     - Found indicators: {found_indicators}")
                
                # Show snippet
                snippet = response_text[:150].replace('\n', ' ')
                print(f"  Preview: {snippet}...")
                
                results.append({
                    "agent": test["agent"],
                    "reranked": is_reranked,
                    "time": elapsed
                })
                
            else:
                print(f"  [ERROR] Request failed: {response.status_code}")
                results.append({
                    "agent": test["agent"],
                    "reranked": False,
                    "error": response.status_code
                })
                
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            results.append({
                "agent": test["agent"],
                "reranked": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("="*60)
    print("SUMMARY:")
    
    reranked_count = sum(1 for r in results if r.get("reranked", False))
    total_count = len(results)
    
    if reranked_count == total_count:
        print(f"[SUCCESS] RERANKING IS ACTIVE ({reranked_count}/{total_count} agents)")
    elif reranked_count > 0:
        print(f"[WARNING] PARTIAL RERANKING ({reranked_count}/{total_count} agents)")
    else:
        print(f"[FAILED] RERANKING NOT DETECTED (0/{total_count} agents)")
    
    time_results = [r for r in results if "time" in r]
    if time_results:
        avg_time = sum(r.get("time", 0) for r in time_results) / len(time_results)
        print(f"Average response time: {avg_time:.1f}s")
    else:
        print("No successful queries to measure response time")
    
    print("="*60 + "\n")
    
    return reranked_count > 0


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--local":
        url = "http://localhost:8000"
        print("Using local server...")
    else:
        url = "https://sportsbrain-backend-production.up.railway.app"
        print("Using production server...")
    
    success = quick_check(url)
    sys.exit(0 if success else 1)