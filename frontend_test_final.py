#!/usr/bin/env python3
"""
Final Frontend-Backend Integration Test Script
Tests the improvements made to N/A handling and data accuracy
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any
from datetime import datetime

# Test configuration
BASE_URL = 'http://localhost:8000/api/v1'
API_KEY = 'yk_eXZGE3PhU1E39cg5lEdTRSFl6BRKBX3w6Gk8GK0fD_g'
HEADERS = {
    'X-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

# Focus on critical tickers for data quality
CRITICAL_TEST_TICKERS = {
    'dividend_payers': ['AAPL', 'MSFT', 'JNJ', 'PG', 'KO'],
    'high_yield': ['T', 'VZ', 'XOM'],
    'new_payers': ['META', 'NVDA'],
    'no_dividend': ['TSLA', 'BRK.B'],
    'edge_cases': ['INVALID', '']
}

class DataQualityTester:
    def __init__(self):
        self.session = None
        self.issues = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_ticker(self, ticker: str) -> Dict[str, Any]:
        """Test a single ticker for data quality issues"""
        print(f"🔍 Testing {ticker}...")
        
        results = {
            'ticker': ticker,
            'endpoints': {},
            'na_count': 0,
            'null_count': 0,
            'empty_count': 0,
            'status': 'PASS'
        }
        
        # Test key endpoints
        endpoints = [
            f'dividends/{ticker}/current',
            f'dividends/{ticker}/analysis',
            f'dividends/{ticker}/charts/growth'
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{BASE_URL}/{endpoint}"
                async with self.session.get(url, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        quality_metrics = self.analyze_data_quality(data)
                        results['endpoints'][endpoint.split('/')[-1]] = {
                            'status': 'SUCCESS',
                            'quality': quality_metrics
                        }
                        results['na_count'] += quality_metrics['na_count']
                        results['null_count'] += quality_metrics['null_count']
                        results['empty_count'] += quality_metrics['empty_count']
                    else:
                        results['endpoints'][endpoint.split('/')[-1]] = {
                            'status': f'ERROR_{response.status}',
                            'quality': {'na_count': 0, 'null_count': 0, 'empty_count': 0}
                        }
                        if response.status not in [404]:  # 404 is expected for non-dividend stocks
                            results['status'] = 'FAIL'
                            
            except Exception as e:
                results['endpoints'][endpoint.split('/')[-1]] = {
                    'status': f'EXCEPTION: {str(e)}',
                    'quality': {'na_count': 0, 'null_count': 0, 'empty_count': 0}
                }
                results['status'] = 'FAIL'
        
        # Overall assessment
        total_issues = results['na_count'] + results['null_count'] + results['empty_count']
        if total_issues > 5:  # More than 5 data quality issues
            results['status'] = 'WARNING'
        
        return results

    def analyze_data_quality(self, data: Any, path: str = "") -> Dict[str, int]:
        """Analyze data for quality issues"""
        metrics = {'na_count': 0, 'null_count': 0, 'empty_count': 0}
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if value == 'N/A':
                    metrics['na_count'] += 1
                    self.issues.append(f"N/A at {current_path}")
                elif value is None:
                    metrics['null_count'] += 1
                    self.issues.append(f"null at {current_path}")
                elif value == '':
                    metrics['empty_count'] += 1
                    self.issues.append(f"empty string at {current_path}")
                elif isinstance(value, (dict, list)):
                    sub_metrics = self.analyze_data_quality(value, current_path)
                    for k, v in sub_metrics.items():
                        metrics[k] += v
                        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                sub_metrics = self.analyze_data_quality(item, current_path)
                for k, v in sub_metrics.items():
                    metrics[k] += v
                    
        return metrics

    async def run_tests(self):
        """Run comprehensive data quality tests"""
        print("🚀 FINAL DATA QUALITY ASSESSMENT")
        print("=" * 60)
        
        all_results = {}
        total_na = 0
        total_null = 0
        total_empty = 0
        
        for category, tickers in CRITICAL_TEST_TICKERS.items():
            print(f"\n📊 Testing {category.upper()} category...")
            category_results = []
            
            for ticker in tickers:
                result = await self.test_ticker(ticker)
                category_results.append(result)
                
                total_na += result['na_count']
                total_null += result['null_count'] 
                total_empty += result['empty_count']
                
                # Print immediate feedback
                status_emoji = "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'WARNING' else "❌"
                issues = result['na_count'] + result['null_count'] + result['empty_count']
                print(f"  {status_emoji} {ticker}: {result['status']} ({issues} data issues)")
                
            all_results[category] = category_results
        
        # Generate final report
        print(f"\n📈 FINAL ASSESSMENT SUMMARY")
        print("=" * 60)
        print(f"Total N/A values found: {total_na}")
        print(f"Total null values found: {total_null}")
        print(f"Total empty values found: {total_empty}")
        print(f"Total data quality issues: {total_na + total_null + total_empty}")
        
        # Quality grade
        total_issues = total_na + total_null + total_empty
        if total_issues == 0:
            grade = "A+ (Perfect)"
            print("🎉 EXCELLENT: No data quality issues found!")
        elif total_issues < 10:
            grade = "A (Excellent)"
            print("✅ VERY GOOD: Minimal data quality issues")
        elif total_issues < 25:
            grade = "B (Good)"
            print("⚠️ GOOD: Some improvements needed")
        elif total_issues < 50:
            grade = "C (Needs Work)"
            print("🔧 NEEDS WORK: Multiple data quality issues")
        else:
            grade = "F (Poor)"
            print("❌ POOR: Major data quality problems")
            
        print(f"Overall Grade: {grade}")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 30)
        if total_na > 0:
            print(f"• Replace {total_na} 'N/A' values with meaningful defaults")
        if total_null > 0:
            print(f"• Handle {total_null} null values properly")
        if total_empty > 0:
            print(f"• Replace {total_empty} empty strings with defaults")
            
        if total_issues == 0:
            print("• System is performing excellently!")
            print("• Ready for production use")
        
        return all_results

async def main():
    """Main test execution"""
    async with DataQualityTester() as tester:
        results = await tester.run_tests()
        
        # Save detailed results
        with open('final_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: final_test_results.json")
        print(f"🔍 Total issues logged: {len(tester.issues)}")
        
        return results

if __name__ == "__main__":
    asyncio.run(main()) 