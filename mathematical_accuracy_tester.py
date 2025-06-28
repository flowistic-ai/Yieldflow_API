"""
Mathematical Accuracy Tester for Investment Assistant

Focus on validating:
1. Dividend yield calculation accuracy
2. Mathematical consistency between price, dividend, and yield
3. Boundary condition handling
4. Data type and format validation
"""

import requests
import json
from typing import Dict, List, Any

class MathematicalAccuracyTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_key = "yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
    
    def test_dividend_yield_calculation(self):
        """Test if dividend yield = (annual_dividend / current_price) * 100"""
        print("🧮 Testing Dividend Yield Calculation Accuracy")
        print("=" * 50)
        
        # Get some stocks for analysis
        response = requests.post(
            f"{self.base_url}/api/v1/query/ask",
            headers=self.headers,
            json={"query": "analyze AAPL MSFT JNJ PEP VZ O"}
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return
        
        data = response.json()
        stocks = data.get('data', {}).get('analysis_results', [])
        
        calculation_errors = []
        
        for stock in stocks:
            ticker = stock.get('ticker')
            price = stock.get('current_price', 0)
            annual_dividend = stock.get('annual_dividend', 0)
            reported_yield = stock.get('dividend_yield', 0)
            
            # Calculate expected yield
            if price > 0:
                expected_yield = (annual_dividend / price) * 100
                difference = abs(reported_yield - expected_yield)
                
                print(f"\n{ticker}:")
                print(f"  Price: ${price}")
                print(f"  Annual Dividend: ${annual_dividend}")
                print(f"  Reported Yield: {reported_yield}%")
                print(f"  Calculated Yield: {expected_yield:.2f}%")
                print(f"  Difference: {difference:.3f}%")
                
                if difference > 0.05:  # Allow 0.05% tolerance
                    calculation_errors.append({
                        'ticker': ticker,
                        'reported': reported_yield,
                        'calculated': expected_yield,
                        'difference': difference
                    })
                    print(f"  ⚠️  CALCULATION ERROR!")
                else:
                    print(f"  ✅ Calculation OK")
        
        if calculation_errors:
            print(f"\n❌ FOUND {len(calculation_errors)} CALCULATION ERRORS:")
            for error in calculation_errors:
                print(f"  {error['ticker']}: {error['difference']:.3f}% difference")
        else:
            print(f"\n✅ ALL DIVIDEND YIELD CALCULATIONS ARE ACCURATE")
    
    def test_boundary_conditions(self):
        """Test edge cases and boundary conditions"""
        print("\n🎯 Testing Boundary Conditions")
        print("=" * 40)
        
        test_cases = [
            ("yield above 3%", 3.0, "greater_than"),
            ("yield above 3.44%", 3.44, "greater_than"),
            ("yield below 2%", 2.0, "less_than"),
            ("yield below 1%", 1.0, "less_than"),
        ]
        
        for query, threshold, comparison in test_cases:
            print(f"\nTesting: '{query}' (threshold: {threshold}%)")
            
            response = requests.post(
                f"{self.base_url}/api/v1/query/ask",
                headers=self.headers,
                json={"query": f"find stocks with dividend {query}"}
            )
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                continue
            
            data = response.json()
            if not data.get('success'):
                print(f"❌ Query Failed: {data.get('explanation')}")
                continue
            
            stocks = data.get('data', {}).get('screening_results', [])
            boundary_violations = []
            
            for stock in stocks:
                ticker = stock.get('ticker')
                yield_val = stock.get('dividend_yield', 0)
                
                if comparison == "greater_than" and yield_val <= threshold:
                    boundary_violations.append(f"{ticker}: {yield_val}% <= {threshold}%")
                elif comparison == "less_than" and yield_val >= threshold:
                    boundary_violations.append(f"{ticker}: {yield_val}% >= {threshold}%")
            
            if boundary_violations:
                print(f"❌ BOUNDARY VIOLATIONS ({len(boundary_violations)}):")
                for violation in boundary_violations:
                    print(f"  • {violation}")
            else:
                print(f"✅ All {len(stocks)} stocks respect boundary condition")
    
    def test_data_consistency(self):
        """Test for data consistency across different queries"""
        print("\n🔍 Testing Data Consistency")
        print("=" * 35)
        
        # Get the same stock through different queries
        queries = [
            "analyze AAPL",
            "find tech stocks",  # Should include AAPL
            "show stocks with yield below 1%"  # Should include AAPL
        ]
        
        aapl_data = {}
        
        for i, query in enumerate(queries):
            response = requests.post(
                f"{self.base_url}/api/v1/query/ask",
                headers=self.headers,
                json={"query": query}
            )
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            if not data.get('success'):
                continue
            
            # Find AAPL in results
            stocks = (data.get('data', {}).get('analysis_results', []) + 
                     data.get('data', {}).get('screening_results', []))
            
            for stock in stocks:
                if stock.get('ticker') == 'AAPL':
                    aapl_data[f"query_{i}"] = {
                        'price': stock.get('current_price'),
                        'yield': stock.get('dividend_yield'),
                        'annual_dividend': stock.get('annual_dividend'),
                        'sector': stock.get('sector')
                    }
                    break
        
        print("AAPL Data Consistency Check:")
        if len(aapl_data) < 2:
            print("❌ Insufficient data for consistency check")
            return
        
        # Compare all data points
        reference_key = list(aapl_data.keys())[0]
        reference_data = aapl_data[reference_key]
        
        for key, data in aapl_data.items():
            if key == reference_key:
                continue
                
            print(f"\nComparing {reference_key} vs {key}:")
            for field in ['price', 'yield', 'annual_dividend', 'sector']:
                ref_val = reference_data.get(field)
                test_val = data.get(field)
                
                if ref_val != test_val:
                    print(f"  ❌ {field}: {ref_val} vs {test_val}")
                else:
                    print(f"  ✅ {field}: {ref_val}")
    
    def test_suspect_values(self):
        """Test for suspicious or unrealistic values"""
        print("\n🚨 Testing for Suspicious Values")
        print("=" * 40)
        
        # Get a broader set of stocks
        response = requests.post(
            f"{self.base_url}/api/v1/query/ask",
            headers=self.headers,
            json={"query": "find dividend stocks with yield above 0%"}
        )
        
        if response.status_code != 200 or not response.json().get('success'):
            print("❌ Could not get stock data")
            return
        
        stocks = response.json().get('data', {}).get('screening_results', [])
        
        suspicious_values = []
        
        for stock in stocks:
            ticker = stock.get('ticker')
            price = stock.get('current_price', 0)
            yield_val = stock.get('dividend_yield', 0)
            annual_dividend = stock.get('annual_dividend', 0)
            
            # Check for suspicious values
            if yield_val > 15:
                suspicious_values.append(f"{ticker}: Extremely high yield {yield_val}%")
            if yield_val < 0:
                suspicious_values.append(f"{ticker}: Negative yield {yield_val}%")
            if price <= 0:
                suspicious_values.append(f"{ticker}: Invalid price ${price}")
            if annual_dividend < 0:
                suspicious_values.append(f"{ticker}: Negative dividend ${annual_dividend}")
            if price > 0 and annual_dividend > price:
                suspicious_values.append(f"{ticker}: Dividend ${annual_dividend} > Price ${price}")
        
        if suspicious_values:
            print(f"❌ FOUND {len(suspicious_values)} SUSPICIOUS VALUES:")
            for value in suspicious_values:
                print(f"  • {value}")
        else:
            print(f"✅ All {len(stocks)} stocks have realistic values")

def main():
    print("🔬 Mathematical Accuracy Testing for Investment Assistant")
    print("=" * 60)
    
    tester = MathematicalAccuracyTester()
    
    try:
        tester.test_dividend_yield_calculation()
        tester.test_boundary_conditions()
        tester.test_data_consistency()
        tester.test_suspect_values()
        
        print("\n" + "=" * 60)
        print("✅ Mathematical accuracy testing completed!")
        
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")

if __name__ == "__main__":
    main() 