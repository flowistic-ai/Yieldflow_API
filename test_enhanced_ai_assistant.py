#!/usr/bin/env python3
"""
FAST TEST for Enhanced AI Assistant - All Example Queries
Tests the optimized AI assistant with quick responses
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List

class FastAITester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_key = "yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # All example queries from the frontend
        self.example_queries = [
            # Stock Screening
            "Find dividend stocks with yield above 4%",
            "Show me technology stocks under $100", 
            "Search for defensive stocks in healthcare sector",
            
            # Portfolio Optimization (Quick ones)
            "Optimize a portfolio with AAPL, MSFT, JNJ",
            
            # Stock Analysis (Quick ones)
            "Analyze AAPL dividend quality",
            "How good is JNJ for dividend investing?",
            
            # Advanced Queries
            "Find conservative stocks for retirement",
            "What's the best dividend ETF alternative?"
        ]

    async def test_single_query(self, query: str) -> Dict:
        """Test a single query with timing"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/query/ask",
                    headers=self.headers,
                    json={
                        "query": query,
                        "user_context": {"session_id": "fast_test"}
                    },
                    timeout=aiohttp.ClientTimeout(total=30)  # 30 second timeout
                ) as response:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "query": query,
                            "success": True,
                            "duration": duration,
                            "response_success": result.get("success", False),
                            "explanation_length": len(result.get("explanation", "")),
                            "has_data": bool(result.get("data")),
                            "confidence": result.get("confidence", 0)
                        }
                    else:
                        return {
                            "query": query,
                            "success": False,
                            "duration": duration,
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            return {
                "query": query,
                "success": False, 
                "duration": duration,
                "error": str(e)
            }

    async def run_all_tests(self):
        """Run all example queries and report results"""
        print("🚀 TESTING OPTIMIZED AI ASSISTANT")
        print("=" * 60)
        print(f"Testing {len(self.example_queries)} example queries...")
        print()
        
        results = []
        total_start = time.time()
        
        # Test all queries
        for i, query in enumerate(self.example_queries, 1):
            print(f"🔍 Test {i}/{len(self.example_queries)}: {query[:50]}...")
            
            result = await self.test_single_query(query)
            results.append(result)
            
            if result["success"] and result.get("response_success"):
                print(f"   ✅ SUCCESS in {result['duration']:.1f}s")
            else:
                print(f"   ❌ FAILED in {result['duration']:.1f}s - {result.get('error', 'Unknown error')}")
            print()
        
        total_time = time.time() - total_start
        
        # Generate summary
        successful_tests = [r for r in results if r["success"] and r.get("response_success")]
        failed_tests = [r for r in results if not (r["success"] and r.get("response_success"))]
        
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(results)}")
        print(f"✅ Successful: {len(successful_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"🕐 Total Time: {total_time:.1f}s")
        if successful_tests:
            avg_time = sum(r['duration'] for r in successful_tests) / len(successful_tests)
            print(f"⚡ Average Response Time: {avg_time:.1f}s")
        print()
        
        if successful_tests:
            print("✅ WORKING QUERIES:")
            for result in successful_tests:
                print(f"   • {result['query'][:50]}... ({result['duration']:.1f}s)")
        
        if failed_tests:
            print()
            print("❌ FAILED QUERIES:")
            for result in failed_tests:
                print(f"   • {result['query'][:50]}... - {result.get('error', 'Unknown')}")
        
        return len(successful_tests) == len(results)

async def main():
    tester = FastAITester()
    
    # Wait for server to be ready
    print("⏳ Waiting for server to start...")
    await asyncio.sleep(5)
    
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! AI Assistant is working optimally.")
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 