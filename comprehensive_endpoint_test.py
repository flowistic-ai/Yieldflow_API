#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script
Tests all Yieldflow API endpoints to ensure they work correctly
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "yk_wMUsnDqpdIjHFj2lFB-CxjHdKQte4BkpJBY1rNFA3bw"  # Enterprise key

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

test_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]

def test_endpoint(method, endpoint, description, expected_status=200, params=None, custom_headers=None):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🧪 Testing: {description}")
        print(f"   URL: {method} {url}")
        
        if params:
            print(f"   Params: {params}")
        
        # Use custom headers if provided, otherwise use default
        request_headers = custom_headers if custom_headers else headers
        
        if method == "GET":
            response = requests.get(url, headers=request_headers, params=params)
        else:
            response = requests.request(method, url, headers=request_headers, params=params)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                if isinstance(data, dict):
                    print(f"   Success: {len(data)} fields returned")
                    # Show sample data structure
                    if data:
                        sample_keys = list(data.keys())[:5]
                        print(f"   Sample fields: {sample_keys}")
                else:
                    print(f"   Success: {type(data)} returned")
            else:
                print(f"   Success: Non-JSON response")
            return True, response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
        else:
            print(f"   ❌ FAILED: Expected {expected_status}, got {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   Error: {error_data}")
            else:
                print(f"   Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        return False, None

def main():
    """Run comprehensive endpoint tests"""
    print("🚀 Starting Comprehensive Yieldflow API Test Suite")
    print(f"   Base URL: {BASE_URL}")
    print(f"   API Key: {API_KEY[:20]}...")
    print("=" * 80)
    
    results = []
    
    # 1. Health Check
    success, _ = test_endpoint("GET", "/health", "Health Check")
    results.append(("Health Check", success))
    
    # 2. Root endpoint
    success, _ = test_endpoint("GET", "/", "Root endpoint")
    results.append(("Root endpoint", success))
    
    # Test with primary ticker (AAPL)
    ticker = "AAPL"
    
    # 3. Company Information
    success, data = test_endpoint("GET", f"/financial/company/{ticker}", "Company Information")
    results.append(("Company Info", success))
    
    # 4. Financial Ratios - All categories
    ratio_categories = ["profitability", "liquidity", "leverage", "efficiency", "growth"]
    
    for category in ratio_categories:
        success, _ = test_endpoint("GET", f"/financial/ratios/{ticker}", 
                                 f"Financial Ratios - {category.title()}", 
                                 params={"ratio_category": category})
        results.append((f"Ratios - {category.title()}", success))
    
    # 5. Financial Analysis - All types
    analysis_types = ["comprehensive", "trends", "liquidity", "profitability", "cashflow"]
    
    for analysis_type in analysis_types:
        success, data = test_endpoint("GET", f"/financial/analysis/{ticker}", 
                                    f"Financial Analysis - {analysis_type.title()}", 
                                    params={"analysis_type": analysis_type, "period": "annual"})
        results.append((f"Analysis - {analysis_type.title()}", success))
        
        # Show detailed results for comprehensive analysis
        if success and analysis_type == "comprehensive" and data:
            print(f"   📊 Comprehensive Analysis Results:")
            if 'overall_score' in data:
                print(f"      Overall Score: {data.get('overall_score', 'N/A')}/10")
            if 'summary' in data:
                print(f"      Summary: {data.get('summary', 'N/A')[:100]}...")
    
    # 6. Financial Overview
    success, _ = test_endpoint("GET", f"/financial/overview/{ticker}", "Financial Overview")
    results.append(("Financial Overview", success))
    
    # 7. Test endpoints without authentication (should fail)
    print(f"\n🔒 Testing Authentication (should fail without API key)")
    headers_no_auth = {"Content-Type": "application/json"}
    
    try:
        response = requests.get(f"{BASE_URL}/financial/company/{ticker}", headers=headers_no_auth)
        if response.status_code == 403:
            print(f"   ✅ Authentication working: 403 Forbidden as expected")
            results.append(("Authentication Security", True))
        else:
            print(f"   ❌ Authentication failed: Expected 403, got {response.status_code}")
            results.append(("Authentication Security", False))
    except Exception as e:
        print(f"   ❌ Authentication test exception: {str(e)}")
        results.append(("Authentication Security", False))
    
    # 8. Test with multiple tickers
    print(f"\n🔄 Testing Multiple Tickers")
    for test_ticker in ["MSFT", "GOOGL"]:
        success, _ = test_endpoint("GET", f"/financial/company/{test_ticker}", 
                                 f"Company Info - {test_ticker}")
        results.append((f"Company Info - {test_ticker}", success))
    
    # 9. Test Test Endpoints (no auth required)
    print(f"\n🧪 Testing No-Auth Test Endpoints")
    test_endpoints = [
        f"/financial/test/company/{ticker}",
        f"/financial/test/ratios/{ticker}",
        f"/financial/test/overview/{ticker}"
    ]
    
    for endpoint in test_endpoints:
        success, _ = test_endpoint("GET", endpoint, f"Test Endpoint: {endpoint}", 
                                 custom_headers={"Content-Type": "application/json"})
        results.append((f"Test: {endpoint.split('/')[-1]}", success))
    
    # 10. API Documentation
    success, _ = test_endpoint("GET", "/docs", "API Documentation (Swagger UI)")
    results.append(("API Documentation", success))
    
    success, _ = test_endpoint("GET", "/openapi.json", "OpenAPI Schema")
    results.append(("OpenAPI Schema", success))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} tests ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! API is working perfectly!")
    else:
        print("❌ Some tests failed. Check details above.")
        print("\nFailed tests:")
        for test_name, success in results:
            if not success:
                print(f"   - {test_name}")
    
    print("\n🏁 Test suite completed!")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 