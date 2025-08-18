"""
Production Monitoring Script for Reranking Verification
Checks if reranking is active and working correctly in production
"""

import asyncio
import time
import json
import sys
from typing import Dict, List, Tuple
from datetime import datetime
import requests
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

class RerankingMonitor:
    def __init__(self, base_url: str = "https://sportsbrain-backend-production.up.railway.app"):
        """Initialize the monitoring tool
        
        Args:
            base_url: The base URL of the API (defaults to production)
        """
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.test_queries = {
            "trade_impact": [
                "How does the Porzingis trade affect Tatum's fantasy value?",
                "What's the impact of Lillard going to Milwaukee on Giannis?",
                "Analyze the fantasy impact of the OG Anunoby trade to the Knicks"
            ],
            "intelligence": [
                "Find me sleepers like last year's Sengun",
                "Analyze Paolo Banchero's performance and potential",
                "Compare Scottie Barnes vs Paolo Banchero for fantasy"
            ]
        }
        
    def print_header(self):
        """Print a nice header for the monitoring output"""
        print("\n" + "="*70)
        print(f"{Fore.CYAN}SPORTSBRAIN RERANKING MONITOR{Style.RESET_ALL}")
        print(f"Target: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    def check_health(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health/detailed", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"{Fore.GREEN}[OK] API Health Check Passed{Style.RESET_ALL}")
                
                # Check specific services
                services = health_data.get('services', {})
                for service, status in services.items():
                    if status.get('status') == 'healthy':
                        print(f"  • {service}: {Fore.GREEN}Healthy{Style.RESET_ALL}")
                    else:
                        print(f"  • {service}: {Fore.YELLOW}Warning - {status.get('error', 'Unknown')}{Style.RESET_ALL}")
                
                return True
            else:
                print(f"{Fore.RED}[FAILED] API Health Check Failed (Status: {response.status_code}){Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Cannot reach API: {e}{Style.RESET_ALL}")
            return False
    
    def analyze_response(self, response_text: str, agent_type: str, response_time: float) -> Dict:
        """Analyze a response for reranking indicators
        
        Returns dict with analysis results
        """
        indicators = {
            "response_time": response_time,
            "has_enhanced_label": False,
            "has_relevance_scores": False,
            "has_rank_changes": False,
            "has_ai_enhanced": False,
            "has_reranking_header": False,
            "likely_reranked": False,
            "quality_indicators": []
        }
        
        # Check for specific reranking indicators
        if "Enhanced with Reranking" in response_text:
            indicators["has_reranking_header"] = True
            indicators["quality_indicators"].append("Explicit reranking header found")
        
        if "AI-Enhanced" in response_text or "AI-enhanced" in response_text:
            indicators["has_ai_enhanced"] = True
            indicators["quality_indicators"].append("AI-Enhanced section present")
        
        if "Relevance Score:" in response_text:
            indicators["has_relevance_scores"] = True
            indicators["quality_indicators"].append("Relevance scores displayed")
        
        if "moved up" in response_text or "moved down" in response_text:
            indicators["has_rank_changes"] = True
            indicators["quality_indicators"].append("Rank change indicators present")
        
        # Check response time as indicator
        if response_time > 8.0:
            indicators["quality_indicators"].append(f"Long response time ({response_time:.1f}s) suggests reranking")
        elif response_time < 3.0:
            indicators["quality_indicators"].append(f"Fast response ({response_time:.1f}s) - might be cached or no reranking")
        
        # Check for quality content indicators
        if agent_type == "trade_impact":
            if "usage rate" in response_text.lower() or "fantasy impact" in response_text.lower():
                indicators["quality_indicators"].append("Contains specific trade impact analysis")
        elif agent_type == "intelligence":
            if "shot distribution" in response_text.lower() or "similarity" in response_text.lower():
                indicators["quality_indicators"].append("Contains enhanced player analysis")
        
        # Determine if likely reranked
        reranking_signals = sum([
            indicators["has_enhanced_label"],
            indicators["has_relevance_scores"],
            indicators["has_rank_changes"],
            indicators["has_ai_enhanced"],
            indicators["has_reranking_header"],
            response_time > 8.0
        ])
        
        indicators["likely_reranked"] = reranking_signals >= 2
        indicators["confidence_score"] = min(100, reranking_signals * 20)
        
        return indicators
    
    async def test_agent(self, agent_type: str, query: str) -> Tuple[bool, Dict]:
        """Test a specific agent with a query
        
        Returns (success, analysis_results)
        """
        print(f"\n{Fore.BLUE}Testing {agent_type.upper()} Agent:{Style.RESET_ALL}")
        print(f"Query: '{query[:60]}...'")
        
        try:
            start_time = time.time()
            
            # Make the request
            payload = {
                "message": query,
                "agent_type": agent_type
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/secure/query",
                json=payload,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("content", data.get("response", ""))
                
                # Analyze the response
                analysis = self.analyze_response(response_text, agent_type, response_time)
                
                # Print results
                print(f"  • Response Time: {response_time:.1f}s")
                print(f"  • Response Length: {len(response_text)} characters")
                
                if analysis["likely_reranked"]:
                    print(f"  • {Fore.GREEN}[OK] LIKELY RERANKED (Confidence: {analysis['confidence_score']}%){Style.RESET_ALL}")
                else:
                    print(f"  • {Fore.YELLOW}[?] RERANKING UNCERTAIN (Confidence: {analysis['confidence_score']}%){Style.RESET_ALL}")
                
                if analysis["quality_indicators"]:
                    print("  • Quality Indicators:")
                    for indicator in analysis["quality_indicators"]:
                        print(f"    - {indicator}")
                
                # Show a snippet of the response
                snippet = response_text[:200].replace('\n', ' ')
                print(f"  • Response Preview: {snippet}...")
                
                return True, analysis
                
            else:
                print(f"  • {Fore.RED}[ERROR] Request failed with status {response.status_code}{Style.RESET_ALL}")
                return False, {}
                
        except requests.Timeout:
            print(f"  • {Fore.RED}[TIMEOUT] Request timed out after 30 seconds{Style.RESET_ALL}")
            return False, {"error": "timeout"}
            
        except Exception as e:
            print(f"  • {Fore.RED}[ERROR] Error: {e}{Style.RESET_ALL}")
            return False, {"error": str(e)}
    
    async def run_monitoring(self):
        """Run the complete monitoring suite"""
        self.print_header()
        
        # Step 1: Check API health
        print(f"{Fore.CYAN}Step 1: Checking API Health{Style.RESET_ALL}")
        if not self.check_health():
            print(f"\n{Fore.RED}Cannot proceed - API is not healthy{Style.RESET_ALL}")
            return
        
        # Step 2: Test Trade Impact Agent
        print(f"\n{Fore.CYAN}Step 2: Testing Trade Impact Agent with Reranking{Style.RESET_ALL}")
        trade_results = []
        for query in self.test_queries["trade_impact"]:
            success, analysis = await self.test_agent("trade_impact", query)
            trade_results.append({"query": query, "success": success, "analysis": analysis})
            await asyncio.sleep(2)  # Don't overwhelm the API
        
        # Step 3: Test Intelligence Agent
        print(f"\n{Fore.CYAN}Step 3: Testing Intelligence Agent with Reranking{Style.RESET_ALL}")
        intel_results = []
        for query in self.test_queries["intelligence"]:
            success, analysis = await self.test_agent("intelligence", query)
            intel_results.append({"query": query, "success": success, "analysis": analysis})
            await asyncio.sleep(2)
        
        # Step 4: Generate Summary Report
        print(f"\n{Fore.CYAN}Step 4: Summary Report{Style.RESET_ALL}")
        print("="*70)
        
        # Trade Impact Summary
        trade_reranked = sum(1 for r in trade_results if r["analysis"].get("likely_reranked", False))
        trade_total = len(trade_results)
        
        print(f"\n{Fore.BLUE}Trade Impact Agent:{Style.RESET_ALL}")
        print(f"  • Queries Tested: {trade_total}")
        print(f"  • Likely Reranked: {trade_reranked}/{trade_total}")
        
        avg_time = sum(r["analysis"].get("response_time", 0) for r in trade_results) / trade_total if trade_total > 0 else 0
        print(f"  • Average Response Time: {avg_time:.1f}s")
        
        if trade_reranked == trade_total:
            print(f"  • Status: {Fore.GREEN}[OK] RERANKING ACTIVE{Style.RESET_ALL}")
        elif trade_reranked > 0:
            print(f"  • Status: {Fore.YELLOW}[WARNING] PARTIAL RERANKING{Style.RESET_ALL}")
        else:
            print(f"  • Status: {Fore.RED}[FAILED] RERANKING NOT DETECTED{Style.RESET_ALL}")
        
        # Intelligence Summary
        intel_reranked = sum(1 for r in intel_results if r["analysis"].get("likely_reranked", False))
        intel_total = len(intel_results)
        
        print(f"\n{Fore.BLUE}Intelligence Agent:{Style.RESET_ALL}")
        print(f"  • Queries Tested: {intel_total}")
        print(f"  • Likely Reranked: {intel_reranked}/{intel_total}")
        
        avg_time = sum(r["analysis"].get("response_time", 0) for r in intel_results) / intel_total if intel_total > 0 else 0
        print(f"  • Average Response Time: {avg_time:.1f}s")
        
        if intel_reranked == intel_total:
            print(f"  • Status: {Fore.GREEN}[OK] RERANKING ACTIVE{Style.RESET_ALL}")
        elif intel_reranked > 0:
            print(f"  • Status: {Fore.YELLOW}[WARNING] PARTIAL RERANKING{Style.RESET_ALL}")
        else:
            print(f"  • Status: {Fore.RED}[FAILED] RERANKING NOT DETECTED{Style.RESET_ALL}")
        
        # Overall Assessment
        print(f"\n{Fore.CYAN}Overall Assessment:{Style.RESET_ALL}")
        total_reranked = trade_reranked + intel_reranked
        total_queries = trade_total + intel_total
        percentage = (total_reranked / total_queries * 100) if total_queries > 0 else 0
        
        if percentage >= 80:
            print(f"  {Fore.GREEN}[SUCCESS] RERANKING IS WORKING WELL ({percentage:.0f}% queries show reranking){Style.RESET_ALL}")
        elif percentage >= 50:
            print(f"  {Fore.YELLOW}[WARNING] RERANKING IS PARTIALLY WORKING ({percentage:.0f}% queries show reranking){Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}[FAILED] RERANKING ISSUES DETECTED ({percentage:.0f}% queries show reranking){Style.RESET_ALL}")
        
        # Save results to file
        self.save_results(trade_results, intel_results)
        
        print("\n" + "="*70)
        print(f"Monitoring complete. Results saved to reranking_monitor_results.json")
        print("="*70 + "\n")
    
    def save_results(self, trade_results: List, intel_results: List):
        """Save monitoring results to a JSON file"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "api_url": self.base_url,
            "trade_impact_results": trade_results,
            "intelligence_results": intel_results,
            "summary": {
                "trade_impact": {
                    "total_queries": len(trade_results),
                    "likely_reranked": sum(1 for r in trade_results if r["analysis"].get("likely_reranked", False)),
                    "avg_response_time": sum(r["analysis"].get("response_time", 0) for r in trade_results) / len(trade_results) if trade_results else 0
                },
                "intelligence": {
                    "total_queries": len(intel_results),
                    "likely_reranked": sum(1 for r in intel_results if r["analysis"].get("likely_reranked", False)),
                    "avg_response_time": sum(r["analysis"].get("response_time", 0) for r in intel_results) / len(intel_results) if intel_results else 0
                }
            }
        }
        
        with open("reranking_monitor_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor SportsBrain Reranking in Production")
    parser.add_argument(
        "--url",
        default="https://sportsbrain-backend-production.up.railway.app",
        help="API base URL (defaults to production)"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local development server (http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    if args.local:
        url = "http://localhost:8000"
    else:
        url = args.url
    
    monitor = RerankingMonitor(url)
    await monitor.run_monitoring()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Monitoring interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)