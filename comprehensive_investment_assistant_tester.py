"""
Comprehensive Investment Assistant Testing Agent

This agent will thoroughly test the AI investment assistant to identify:
1. Mathematical accuracy issues
2. Parameter parsing problems
3. Data consistency errors
4. Logic flaws in filtering
5. Edge cases and boundary conditions
"""

import asyncio
import json
import requests
import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import pandas as pd

@dataclass
class TestCase:
    """Structure for test cases"""
    name: str
    query: str
    expected_behavior: str
    validation_rules: List[str]

@dataclass
class TestResult:
    """Structure for test results"""
    test_name: str
    query: str
    success: bool
    response_data: Dict[str, Any]
    issues_found: List[str]
    processing_time: float
    accuracy_score: float

class InvestmentAssistantTester:
    """Comprehensive testing agent for the investment assistant"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        
        # Known accurate data for validation
        self.known_stocks = {
            'AAPL': {'yield': 0.52, 'price_range': (180, 220), 'sector': 'Technology'},
            'MSFT': {'yield': 0.68, 'price_range': (450, 520), 'sector': 'Technology'},
            'JNJ': {'yield': 3.44, 'price_range': (140, 170), 'sector': 'Healthcare'},
            'KO': {'yield': 2.89, 'price_range': (60, 75), 'sector': 'Consumer Defensive'},
            'PEP': {'yield': 4.41, 'price_range': (120, 140), 'sector': 'Consumer Defensive'},
            'VZ': {'yield': 6.40, 'price_range': (35, 50), 'sector': 'Communication Services'},
            'T': {'yield': 3.94, 'price_range': (25, 35), 'sector': 'Communication Services'},
            'O': {'yield': 5.23, 'price_range': (55, 70), 'sector': 'Real Estate'},
        }
        
        # Define comprehensive test cases
        self.test_cases = [
            # Basic filtering tests
            TestCase(
                "Yield Above 3% Test",
                "find dividend stocks with yield above 3%",
                "Should return only stocks with dividend yield > 3.0%",
                ["all_yields_above_3", "no_yields_below_3", "reasonable_count"]
            ),
            TestCase(
                "Yield Below 2% Test", 
                "show me stocks with dividend yield less than 2%",
                "Should return only stocks with dividend yield < 2.0%",
                ["all_yields_below_2", "no_yields_above_2", "includes_aapl_msft"]
            ),
            TestCase(
                "Yield Range Test",
                "find stocks with dividend yield between 2% and 4%",
                "Should return stocks with 2.0% <= yield <= 4.0%",
                ["yields_in_range", "no_yields_outside_range"]
            ),
            TestCase(
                "Exact Yield Boundary Test",
                "find stocks with yield above 3.44%",
                "Should return stocks > 3.44%, JNJ should be excluded",
                ["yields_above_boundary", "jnj_excluded"]
            ),
            
            # Price filtering tests
            TestCase(
                "Price Under $50 Test",
                "show stocks under $50",
                "Should return stocks with price < 50",
                ["all_prices_below_50", "includes_vz_t"]
            ),
            TestCase(
                "Price Above $200 Test",
                "find stocks priced above $200",
                "Should return expensive stocks only",
                ["all_prices_above_200", "includes_aapl_msft"]
            ),
            
            # Sector filtering tests
            TestCase(
                "Technology Sector Test",
                "show me tech stocks",
                "Should return only technology sector stocks",
                ["only_tech_sector", "includes_aapl_msft"]
            ),
            TestCase(
                "Healthcare Sector Test",
                "find healthcare stocks with good dividends",
                "Should return healthcare stocks",
                ["only_healthcare", "includes_jnj"]
            ),
            
            # Complex combined filtering
            TestCase(
                "Complex Filter Test 1",
                "find tech stocks under $300 with yield above 0.5%",
                "Technology + price < 300 + yield > 0.5%",
                ["tech_only", "prices_under_300", "yields_above_0_5"]
            ),
            TestCase(
                "Complex Filter Test 2",
                "show utility stocks with yield above 3% under $100",
                "Utilities + yield > 3% + price < 100",
                ["utilities_only", "yields_above_3", "prices_under_100"]
            ),
            
            # Stock analysis tests
            TestCase(
                "Single Stock Analysis",
                "analyze AAPL",
                "Should return detailed analysis for Apple",
                ["single_stock_aapl", "correct_aapl_data"]
            ),
            TestCase(
                "Multi Stock Analysis",
                "analyze AAPL MSFT JNJ KO",
                "Should analyze 4 specific stocks",
                ["four_stocks_analyzed", "correct_stock_data"]
            ),
            
            # Edge cases and error handling
            TestCase(
                "Invalid Ticker Test",
                "analyze INVALID FAKE AAPL",
                "Should handle invalid tickers gracefully",
                ["handles_invalid_tickers", "includes_valid_aapl"]
            ),
            TestCase(
                "No Results Test",
                "find stocks with yield above 20%",
                "Should handle no results gracefully",
                ["no_results_found", "appropriate_message"]
            ),
            
            # Mathematical precision tests
            TestCase(
                "Decimal Precision Test",
                "find stocks with yield above 3.44%",
                "Should handle decimal precision correctly",
                ["decimal_precision", "boundary_handling"]
            ),
            TestCase(
                "Percentage Parsing Test",
                "show stocks with yield of at least 5.0 percent",
                "Should parse percentage formats correctly",
                ["percentage_parsing", "correct_threshold"]
            ),
        ]
    
    async def run_single_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case"""
        print(f"\n🧪 Running: {test_case.name}")
        print(f"Query: '{test_case.query}'")
        
        start_time = time.time()
        issues_found = []
        accuracy_score = 0.0
        
        try:
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/v1/query/ask",
                headers=self.headers,
                json={"query": test_case.query},
                timeout=10
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                issues_found.append(f"HTTP {response.status_code}: {response.text}")
                return TestResult(test_case.name, test_case.query, False, {}, issues_found, processing_time, 0.0)
            
            data = response.json()
            
            # Validate response structure
            if not data.get('success', False):
                issues_found.append(f"API returned success=False: {data.get('explanation', 'No explanation')}")
                return TestResult(test_case.name, test_case.query, False, data, issues_found, processing_time, 0.0)
            
            # Run validation rules
            validation_results = await self._validate_response(test_case, data)
            issues_found.extend(validation_results['issues'])
            accuracy_score = validation_results['score']
            
            success = len(issues_found) == 0
            
            # Print immediate results
            if success:
                print(f"✅ PASSED - Accuracy: {accuracy_score:.1%} ({processing_time:.3f}s)")
            else:
                print(f"❌ FAILED - Issues found:")
                for issue in issues_found:
                    print(f"   • {issue}")
            
            return TestResult(test_case.name, test_case.query, success, data, issues_found, processing_time, accuracy_score)
            
        except Exception as e:
            processing_time = time.time() - start_time
            issues_found.append(f"Exception: {str(e)}")
            print(f"💥 ERROR: {str(e)}")
            return TestResult(test_case.name, test_case.query, False, {}, issues_found, processing_time, 0.0)
    
    async def _validate_response(self, test_case: TestCase, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response against test rules"""
        issues = []
        score = 1.0
        
        response_data = data.get('data', {})
        
        # Check if it's a screening result or analysis result
        if 'screening_results' in response_data:
            results = response_data['screening_results']
            issues.extend(await self._validate_screening_results(test_case, results))
        elif 'analysis_results' in response_data:
            results = response_data['analysis_results']
            issues.extend(await self._validate_analysis_results(test_case, results))
        else:
            issues.append("Response missing expected data structure")
        
        # Apply validation rules
        for rule in test_case.validation_rules:
            rule_issues = await self._apply_validation_rule(rule, test_case, data)
            issues.extend(rule_issues)
        
        # Calculate score based on issues
        if issues:
            score = max(0.0, 1.0 - (len(issues) * 0.2))
        
        return {'issues': issues, 'score': score}
    
    async def _validate_screening_results(self, test_case: TestCase, results: List[Dict]) -> List[str]:
        """Validate screening results"""
        issues = []
        
        if not results:
            return ["No screening results returned"]
        
        for stock in results:
            # Validate required fields
            required_fields = ['ticker', 'company_name', 'current_price', 'dividend_yield', 'sector']
            for field in required_fields:
                if field not in stock:
                    issues.append(f"Missing field '{field}' in stock {stock.get('ticker', 'unknown')}")
                elif stock[field] is None:
                    issues.append(f"Null value for '{field}' in stock {stock.get('ticker', 'unknown')}")
            
            # Validate data types and ranges
            ticker = stock.get('ticker', '')
            price = stock.get('current_price', 0)
            yield_val = stock.get('dividend_yield', 0)
            
            if price <= 0:
                issues.append(f"{ticker}: Invalid price {price}")
            if yield_val < 0 or yield_val > 20:
                issues.append(f"{ticker}: Suspicious dividend yield {yield_val}%")
            
            # Cross-reference with known data
            if ticker in self.known_stocks:
                known = self.known_stocks[ticker]
                if abs(yield_val - known['yield']) > 0.1:
                    issues.append(f"{ticker}: Yield mismatch - got {yield_val}%, expected ~{known['yield']}%")
                if not (known['price_range'][0] <= price <= known['price_range'][1]):
                    issues.append(f"{ticker}: Price {price} outside expected range {known['price_range']}")
                if stock.get('sector') != known['sector']:
                    issues.append(f"{ticker}: Sector mismatch - got '{stock.get('sector')}', expected '{known['sector']}'")
        
        return issues
    
    async def _validate_analysis_results(self, test_case: TestCase, results: List[Dict]) -> List[str]:
        """Validate analysis results"""
        issues = []
        
        if not results:
            return ["No analysis results returned"]
        
        for stock in results:
            ticker = stock.get('ticker', '')
            
            # Validate against known data
            if ticker in self.known_stocks:
                known = self.known_stocks[ticker]
                yield_val = stock.get('dividend_yield', 0)
                
                if abs(yield_val - known['yield']) > 0.1:
                    issues.append(f"{ticker}: Analysis yield mismatch - got {yield_val}%, expected ~{known['yield']}%")
        
        return issues
    
    async def _apply_validation_rule(self, rule: str, test_case: TestCase, data: Dict[str, Any]) -> List[str]:
        """Apply specific validation rules"""
        issues = []
        response_data = data.get('data', {})
        
        if rule == "all_yields_above_3":
            results = response_data.get('screening_results', [])
            for stock in results:
                if stock.get('dividend_yield', 0) <= 3.0:
                    issues.append(f"Stock {stock.get('ticker')} has yield {stock.get('dividend_yield')}% <= 3%")
        
        elif rule == "all_yields_below_2":
            results = response_data.get('screening_results', [])
            for stock in results:
                if stock.get('dividend_yield', 0) >= 2.0:
                    issues.append(f"Stock {stock.get('ticker')} has yield {stock.get('dividend_yield')}% >= 2%")
        
        elif rule == "includes_aapl_msft":
            results = response_data.get('screening_results', []) + response_data.get('analysis_results', [])
            tickers = [s.get('ticker') for s in results]
            if 'AAPL' not in tickers:
                issues.append("Expected AAPL in results but not found")
            if 'MSFT' not in tickers:
                issues.append("Expected MSFT in results but not found")
        
        elif rule == "only_tech_sector":
            results = response_data.get('screening_results', [])
            for stock in results:
                if stock.get('sector') != 'Technology':
                    issues.append(f"Non-tech stock found: {stock.get('ticker')} ({stock.get('sector')})")
        
        elif rule == "jnj_excluded":
            results = response_data.get('screening_results', [])
            tickers = [s.get('ticker') for s in results]
            if 'JNJ' in tickers:
                issues.append("JNJ should be excluded from results but was found")
        
        elif rule == "reasonable_count":
            results = response_data.get('screening_results', [])
            if len(results) < 5 or len(results) > 50:
                issues.append(f"Unreasonable result count: {len(results)} (expected 5-50)")
        
        # Add more validation rules as needed...
        
        return issues
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all test cases and generate comprehensive report"""
        print("🚀 Starting Comprehensive Investment Assistant Testing")
        print("=" * 60)
        
        results = []
        for test_case in self.test_cases:
            result = await self.run_single_test(test_case)
            results.append(result)
            
            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.1)
        
        # Generate summary report
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        avg_accuracy = sum(r.accuracy_score for r in results) / total_tests if results else 0
        avg_time = sum(r.processing_time for r in results) / total_tests if results else 0
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🎯 Success Rate: {passed_tests/total_tests:.1%}")
        print(f"📈 Average Accuracy: {avg_accuracy:.1%}")
        print(f"⚡ Average Response Time: {avg_time:.3f}s")
        
        # Detailed failure analysis
        if failed_tests > 0:
            print("\n🔍 FAILURE ANALYSIS:")
            for result in results:
                if not result.success:
                    print(f"\n❌ {result.test_name}")
                    print(f"   Query: {result.query}")
                    for issue in result.issues_found:
                        print(f"   • {issue}")
        
        # Performance analysis
        slow_tests = [r for r in results if r.processing_time > 0.1]
        if slow_tests:
            print(f"\n⚠️  SLOW RESPONSES (>{0.1}s):")
            for result in slow_tests:
                print(f"   • {result.test_name}: {result.processing_time:.3f}s")
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': passed_tests/total_tests,
            'average_accuracy': avg_accuracy,
            'average_time': avg_time,
            'results': results
        }

async def main():
    """Run the comprehensive testing"""
    tester = InvestmentAssistantTester()
    
    print("🔍 Testing AI Investment Assistant for Accuracy Issues...")
    print("This will test multiple scenarios to identify problems.\n")
    
    report = await tester.run_comprehensive_tests()
    
    # Save detailed report
    with open('investment_assistant_test_report.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'summary': {
                'total_tests': report['total_tests'],
                'passed': report['passed'],
                'failed': report['failed'],
                'success_rate': report['success_rate'],
                'average_accuracy': report['average_accuracy'],
                'average_time': report['average_time']
            },
            'detailed_results': [
                {
                    'test_name': r.test_name,
                    'query': r.query,
                    'success': r.success,
                    'issues': r.issues_found,
                    'accuracy_score': r.accuracy_score,
                    'processing_time': r.processing_time,
                    'response_data': r.response_data
                }
                for r in report['results']
            ]
        }, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: investment_assistant_test_report.json")
    
    if report['failed'] > 0:
        print(f"\n🚨 CRITICAL ISSUES FOUND: {report['failed']} tests failed")
        print("Review the detailed failure analysis above to identify specific problems.")
    else:
        print(f"\n🎉 ALL TESTS PASSED! System appears to be working correctly.")

if __name__ == "__main__":
    asyncio.run(main()) 