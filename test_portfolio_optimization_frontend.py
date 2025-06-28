#!/usr/bin/env python3
"""
Test Portfolio Optimization Frontend Integration
Test the portfolio optimization API endpoints with the exact same requests the frontend will make
"""

import requests
import json
import time
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_basic_optimization():
    """Test basic portfolio optimization endpoint"""
    print("🔄 Testing Basic Portfolio Optimization...")
    
    payload = {
        "tickers": ["AAPL", "MSFT", "JNJ"],
        "objective": "balanced",
        "shrinkage_method": "auto"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/portfolio/optimize",
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Basic optimization successful!")
            print(f"   Expected Return: {result['expected_return']*100:.2f}%")
            print(f"   Sharpe Ratio: {result['sharpe_ratio']:.3f}")
            print(f"   Dividend Yield: {result['expected_dividend_yield']*100:.2f}%")
            print(f"   Method: {result['optimization_method']}")
            print(f"   Weights: {result['weights']}")
            return True
        else:
            print(f"❌ Basic optimization failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Basic optimization error: {str(e)}")
        return False

def test_full_optimization():
    """Test full portfolio optimization with all features"""
    print("\n🔄 Testing Full Portfolio Optimization...")
    
    payload = {
        "tickers": ["AAPL", "MSFT", "JNJ", "PG"],
        "objective": "sharpe_ratio",
        "shrinkage_method": "auto",
        "max_weight": 0.4,
        "min_dividend_yield": 0.01
    }
    
    params = {
        "include_efficient_frontier": True,
        "include_comparison": True,
        "include_backtest": False  # Skip backtest for faster testing
    }
    
    try:
        url = f"{API_BASE_URL}/api/v1/portfolio/optimize-full"
        response = requests.post(
            url,
            headers=HEADERS,
            json=payload,
            params=params,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Full optimization successful!")
            
            # Basic results
            opt_result = result['optimization_result']
            print(f"   Expected Return: {opt_result['expected_return']*100:.2f}%")
            print(f"   Sharpe Ratio: {opt_result['sharpe_ratio']:.3f}")
            print(f"   Volatility: {opt_result['volatility']*100:.2f}%")
            
            # Efficient frontier
            if 'efficient_frontier' in result and result['efficient_frontier']:
                frontier = result['efficient_frontier']
                print(f"   Efficient Frontier Points: {len(frontier['frontier_points'])}")
                print(f"   Max Sharpe Portfolio Return: {frontier['max_sharpe_portfolio']['expected_return']*100:.2f}%")
            
            # Comparison
            if 'comparison' in result and result['comparison']:
                comparison = result['comparison']
                epo_sharpe = comparison['epo_portfolio']['sharpe_ratio']
                equal_sharpe = comparison['equal_weight_portfolio']['sharpe_ratio']
                improvement = ((epo_sharpe - equal_sharpe) / equal_sharpe) * 100
                print(f"   Sharpe Ratio Improvement vs Equal Weight: {improvement:.2f}%")
            
            # AI Insights
            if 'insights' in result and result['insights']:
                insights = result['insights']
                print(f"   Quality Score: {insights['quality_score']}/10")
                print(f"   Diversification Score: {insights['diversification_score']}/10")
                print(f"   Summary: {insights['summary'][:100]}...")
            
            return True
        else:
            print(f"❌ Full optimization failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Full optimization error: {str(e)}")
        return False

def test_different_objectives():
    """Test different optimization objectives"""
    print("\n🔄 Testing Different Optimization Objectives...")
    
    objectives = ["sharpe_ratio", "dividend_yield", "dividend_growth", "balanced"]
    
    for objective in objectives:
        print(f"   Testing {objective}...")
        
        payload = {
            "tickers": ["AAPL", "MSFT", "JNJ"],
            "objective": objective,
            "shrinkage_method": "auto"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/portfolio/optimize",
                headers=HEADERS,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"     ✅ {objective}: Return={result['expected_return']*100:.2f}%, "
                      f"Sharpe={result['sharpe_ratio']:.3f}, "
                      f"Yield={result['expected_dividend_yield']*100:.2f}%")
            else:
                print(f"     ❌ {objective} failed: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ {objective} error: {str(e)}")

def test_shrinkage_methods():
    """Test different shrinkage methods"""
    print("\n🔄 Testing Different Shrinkage Methods...")
    
    methods = [
        {"shrinkage_method": "auto"},
        {"shrinkage_method": "fixed"},
        {"shrinkage_method": "custom", "shrinkage_value": 0.5}
    ]
    
    for method in methods:
        method_name = method["shrinkage_method"]
        if "shrinkage_value" in method:
            method_name += f"({method['shrinkage_value']})"
            
        print(f"   Testing {method_name}...")
        
        payload = {
            "tickers": ["AAPL", "MSFT", "JNJ"],
            "objective": "balanced",
            **method
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/portfolio/optimize",
                headers=HEADERS,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"     ✅ {method_name}: Shrinkage Parameter={result['shrinkage_parameter']:.3f}")
            else:
                print(f"     ❌ {method_name} failed: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ {method_name} error: {str(e)}")

def test_error_handling():
    """Test error handling and validation"""
    print("\n🔄 Testing Error Handling...")
    
    test_cases = [
        {
            "name": "Invalid ticker",
            "payload": {"tickers": ["INVALID"], "objective": "balanced"},
            "expected_status": [400, 422]
        },
        {
            "name": "Too few tickers",
            "payload": {"tickers": ["AAPL"], "objective": "balanced"},
            "expected_status": [400, 422]
        },
        {
            "name": "Invalid objective",
            "payload": {"tickers": ["AAPL", "MSFT"], "objective": "invalid"},
            "expected_status": [400, 422]
        }
    ]
    
    for test_case in test_cases:
        print(f"   Testing {test_case['name']}...")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/portfolio/optimize",
                headers=HEADERS,
                json=test_case["payload"],
                timeout=30
            )
            
            if response.status_code in test_case["expected_status"]:
                print(f"     ✅ Correctly rejected with status {response.status_code}")
            else:
                print(f"     ❌ Unexpected status {response.status_code} (expected {test_case['expected_status']})")
                
        except Exception as e:
            print(f"     ❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Testing Portfolio Optimization Frontend Integration")
    print("="*60)
    
    # Test API connectivity
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API connectivity confirmed")
        else:
            print(f"❌ API not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        return
    
    start_time = time.time()
    
    # Run tests
    tests = [
        test_basic_optimization,
        test_full_optimization, 
        test_different_objectives,
        test_shrinkage_methods,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    print(f"🏁 Tests completed in {elapsed:.2f} seconds")
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend integration ready.")
    else:
        print("⚠️  Some tests failed. Check API implementation.")

if __name__ == "__main__":
    main() 