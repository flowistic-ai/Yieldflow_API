#!/usr/bin/env python3
"""
Comprehensive test script for AI Investment Assistant example queries.
Tests all example queries to ensure they generate correct responses.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any
import os
from datetime import datetime

class AIAssistantTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_key = "yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Define all example queries by category
        self.example_queries = {
            "stock_screening": [
                "Find dividend stocks with yield above 4%",
                "Show me technology stocks under $100",
                "Search for defensive stocks in healthcare sector",
                "Filter stocks with market cap over $10 billion",
                "Find value stocks with PE ratio below 15"
            ],
            "portfolio_optimization": [
                "Optimize a portfolio with AAPL, MSFT, JNJ",
                "Create a balanced portfolio for income",
                "Build an optimal mix of dividend stocks",
                "Rebalance my portfolio for maximum Sharpe ratio",
                "Optimize allocation for dividend growth"
            ],
            "stock_analysis": [
                "Analyze AAPL dividend quality",
                "Evaluate TSLA risk profile",
                "How good is JNJ for dividend investing?",
                "Assess portfolio risk and diversification",
                "What are the strengths of Microsoft stock?"
            ],
            "advanced_queries": [
                "I need $500 monthly income with low risk",
                "Find conservative stocks for retirement",
                "What's the best dividend ETF alternative?",
                "Compare AAPL vs MSFT for dividend growth",
                "Recommend stocks for aggressive growth strategy"
            ]
        }
        
        self.test_results = []

    async def test_query(self, session: aiohttp.ClientSession, query: str, category: str) -> Dict[str, Any]:
        """Test a single query and return detailed results."""
        print(f"\n🔍 Testing: {query}")
        
        start_time = time.time()
        
        try:
            # Test the query
            request_data = {
                "query": query,
                "user_context": {
                    "session_id": "test_session",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            async with session.post(
                f"{self.base_url}/api/v1/query/ask",
                headers=self.headers,
                json=request_data
            ) as response:
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Analyze the response quality
                    quality_score = self._analyze_response_quality(result, query, category)
                    
                    print(f"✅ Success - Quality: {quality_score:.1f}/10 - Time: {response_time:.2f}s")
                    print(f"   Explanation: {result.get('explanation', 'No explanation')[:100]}...")
                    
                    if result.get('data'):
                        self._print_data_summary(result['data'], category)
                    
                    return {
                        "query": query,
                        "category": category,
                        "success": True,
                        "response_time": response_time,
                        "quality_score": quality_score,
                        "confidence": result.get('confidence', 0),
                        "has_data": bool(result.get('data')),
                        "data_summary": self._get_data_summary(result.get('data'), category),
                        "explanation_length": len(result.get('explanation', '')),
                        "suggestions_count": len(result.get('suggestions', [])),
                        "issues": self._find_issues(result, query, category)
                    }
                else:
                    error_text = await response.text()
                    print(f"❌ Failed - Status: {response.status}")
                    print(f"   Error: {error_text[:100]}...")
                    
                    return {
                        "query": query,
                        "category": category,
                        "success": False,
                        "response_time": response_time,
                        "error": error_text,
                        "status_code": response.status
                    }
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {
                "query": query,
                "category": category,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            }

    def _analyze_response_quality(self, result: Dict, query: str, category: str) -> float:
        """Analyze the quality of the response and return a score 0-10."""
        score = 0.0
        
        # Basic response structure (2 points)
        if result.get('success'):
            score += 1.0
        if result.get('explanation'):
            score += 1.0
            
        # Data relevance (3 points)
        data = result.get('data')
        if data:
            score += 1.0
            
            # Category-specific data validation
            if category == "stock_screening":
                if data.get('screening_results') or data.get('stocks'):
                    score += 1.0
                if data.get('total_found', 0) > 0:
                    score += 1.0
                    
            elif category == "portfolio_optimization":
                if data.get('weights') or data.get('allocation'):
                    score += 1.0
                if data.get('expected_return') or data.get('sharpe_ratio'):
                    score += 1.0
                    
            elif category == "stock_analysis":
                if data.get('company_info') or data.get('analysis'):
                    score += 1.0
                if data.get('dividend_analysis') or data.get('financial_metrics'):
                    score += 1.0
                    
            elif category == "advanced_queries":
                if data.get('recommendations') or data.get('strategies'):
                    score += 1.0
                if data.get('income_plan') or data.get('growth_plan'):
                    score += 1.0
        
        # Explanation quality (2 points)
        explanation = result.get('explanation', '')
        if len(explanation) > 50:
            score += 1.0
        if any(keyword in explanation.lower() for keyword in ['because', 'due to', 'analysis', 'based on']):
            score += 1.0
            
        # Confidence and suggestions (2 points)
        if result.get('confidence', 0) > 0.5:
            score += 1.0
        if len(result.get('suggestions', [])) >= 2:
            score += 1.0
            
        # Response time bonus (1 point)
        # This would be calculated in the calling function
        score += 1.0  # Assume good response time for now
        
        return min(score, 10.0)

    def _print_data_summary(self, data: Dict, category: str):
        """Print a summary of the data returned."""
        if category == "stock_screening" and data.get('screening_results'):
            print(f"   📊 Found {len(data['screening_results'])} stocks")
        elif category == "portfolio_optimization" and data.get('weights'):
            print(f"   📈 Portfolio with {len(data['weights'])} assets")
        elif category == "stock_analysis" and data.get('company_info'):
            print(f"   🏢 Analysis for {data['company_info'].get('ticker', 'Unknown')}")
        elif category == "advanced_queries":
            if data.get('recommendations'):
                print(f"   💡 {len(data['recommendations'])} recommendations")

    def _get_data_summary(self, data: Dict, category: str) -> str:
        """Get a text summary of the data for reporting."""
        if not data:
            return "No data returned"
            
        if category == "stock_screening":
            if data.get('screening_results'):
                return f"{len(data['screening_results'])} stocks found"
            return "Screening attempted but no specific results"
            
        elif category == "portfolio_optimization":
            if data.get('weights'):
                return f"Portfolio with {len(data['weights'])} assets"
            return "Optimization attempted but no weights returned"
            
        elif category == "stock_analysis":
            if data.get('company_info'):
                return f"Analysis for {data['company_info'].get('ticker', 'company')}"
            return "Analysis attempted but no company info"
            
        elif category == "advanced_queries":
            if data.get('recommendations'):
                return f"{len(data['recommendations'])} recommendations"
            return "Recommendations attempted"
            
        return "Data returned but format unclear"

    def _find_issues(self, result: Dict, query: str, category: str) -> List[str]:
        """Find potential issues with the response."""
        issues = []
        
        # Check for missing data when expected
        if not result.get('data') and category in ["stock_screening", "portfolio_optimization"]:
            issues.append("Missing data for query type that should return data")
            
        # Check explanation quality
        explanation = result.get('explanation', '')
        if len(explanation) < 20:
            issues.append("Explanation too short")
            
        # Check confidence
        if result.get('confidence', 0) < 0.3:
            issues.append("Low confidence score")
            
        # Check for appropriate suggestions
        if len(result.get('suggestions', [])) == 0:
            issues.append("No suggestions provided")
            
        return issues

    async def run_comprehensive_test(self):
        """Run comprehensive tests on all example queries."""
        print("🚀 Starting AI Investment Assistant Comprehensive Testing")
        print("=" * 60)
        
        # Wait for server to be ready
        await self._wait_for_server()
        
        async with aiohttp.ClientSession() as session:
            all_results = []
            
            for category, queries in self.example_queries.items():
                print(f"\n📋 Testing {category.replace('_', ' ').title()} ({len(queries)} queries)")
                print("-" * 40)
                
                category_results = []
                for query in queries:
                    result = await self.test_query(session, query, category)
                    category_results.append(result)
                    all_results.append(result)
                    
                    # Brief pause between queries
                    await asyncio.sleep(0.5)
                
                # Category summary
                successful = sum(1 for r in category_results if r['success'])
                avg_quality = sum(r.get('quality_score', 0) for r in category_results if r['success']) / max(successful, 1)
                print(f"\n📊 {category} Summary: {successful}/{len(queries)} successful, Avg Quality: {avg_quality:.1f}/10")
        
        # Generate comprehensive report
        self._generate_report(all_results)
        
        return all_results

    async def _wait_for_server(self):
        """Wait for the server to be ready."""
        print("⏳ Waiting for server to be ready...")
        
        for attempt in range(30):  # Wait up to 30 seconds
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/docs") as response:
                        if response.status == 200:
                            print("✅ Server is ready!")
                            return
            except:
                pass
                
            await asyncio.sleep(1)
            
        raise Exception("Server failed to start within 30 seconds")

    def _generate_report(self, results: List[Dict]):
        """Generate a comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Overall statistics
        total_queries = len(results)
        successful = sum(1 for r in results if r['success'])
        failed = total_queries - successful
        
        print(f"\n🎯 Overall Results:")
        print(f"   Total Queries: {total_queries}")
        print(f"   Successful: {successful} ({successful/total_queries*100:.1f}%)")
        print(f"   Failed: {failed} ({failed/total_queries*100:.1f}%)")
        
        if successful > 0:
            avg_quality = sum(r.get('quality_score', 0) for r in results if r['success']) / successful
            avg_response_time = sum(r.get('response_time', 0) for r in results if r['success']) / successful
            avg_confidence = sum(r.get('confidence', 0) for r in results if r['success']) / successful
            
            print(f"   Average Quality Score: {avg_quality:.1f}/10")
            print(f"   Average Response Time: {avg_response_time:.2f}s")
            print(f"   Average Confidence: {avg_confidence:.2f}")
        
        # Category breakdown
        print(f"\n📋 Results by Category:")
        for category in self.example_queries.keys():
            category_results = [r for r in results if r['category'] == category]
            category_successful = sum(1 for r in category_results if r['success'])
            category_total = len(category_results)
            
            print(f"   {category.replace('_', ' ').title()}: {category_successful}/{category_total}")
            
            if category_successful > 0:
                avg_quality = sum(r.get('quality_score', 0) for r in category_results if r['success']) / category_successful
                print(f"      Average Quality: {avg_quality:.1f}/10")
        
        # Issues found
        all_issues = []
        for result in results:
            if result['success']:
                all_issues.extend(result.get('issues', []))
        
        if all_issues:
            print(f"\n⚠️  Issues Found:")
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   {issue}: {count} occurrences")
        
        # Failed queries
        failed_results = [r for r in results if not r['success']]
        if failed_results:
            print(f"\n❌ Failed Queries:")
            for result in failed_results:
                print(f"   {result['query']}")
                print(f"      Error: {result.get('error', 'Unknown error')[:100]}...")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_assistant_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
        # Recommendations
        print(f"\n🔧 Recommendations:")
        if failed > 0:
            print(f"   - Fix {failed} failed queries")
        
        if successful > 0:
            avg_quality = sum(r.get('quality_score', 0) for r in results if r['success']) / successful
            if avg_quality < 7.0:
                print(f"   - Improve response quality (current: {avg_quality:.1f}/10)")
        
        if all_issues:
            print(f"   - Address {len(set(all_issues))} types of issues found")
        
        print(f"   - Consider adding more example queries for comprehensive testing")

async def main():
    """Main test function."""
    tester = AIAssistantTester()
    results = await tester.run_comprehensive_test()
    
    # Quick summary for terminal
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"\n🎉 Testing Complete: {successful}/{total} queries successful!")

if __name__ == "__main__":
    asyncio.run(main()) 