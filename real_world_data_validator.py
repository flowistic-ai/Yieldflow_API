"""
Real-World Data Validator

This checks if our pre-cached stock data matches current market reality.
The issue might be that our static data is outdated or inaccurate.
"""

import requests
import yfinance as yf
import time
from typing import Dict, List, Any
import pandas as pd

class RealWorldDataValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_key = "yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        
        # Test a subset of well-known stocks
        self.test_tickers = ['AAPL', 'MSFT', 'JNJ', 'KO', 'PEP', 'VZ', 'T', 'O']
    
    def get_our_data(self, ticker: str) -> Dict[str, Any]:
        """Get data from our investment assistant"""
        response = requests.post(
            f"{self.base_url}/api/v1/query/ask",
            headers=self.headers,
            json={"query": f"analyze {ticker}"}
        )
        
        if response.status_code != 200 or not response.json().get('success'):
            return {}
        
        results = response.json().get('data', {}).get('analysis_results', [])
        if results:
            return results[0]
        return {}
    
    def get_real_market_data(self, ticker: str) -> Dict[str, Any]:
        """Get real market data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="5d")
            
            if hist.empty:
                return {}
            
            current_price = hist['Close'].iloc[-1]
            
            # Get dividend info
            dividends = stock.dividends
            if not dividends.empty:
                # Get annual dividend (sum of last 4 quarters)
                annual_dividend = dividends.tail(4).sum() if len(dividends) >= 4 else dividends.sum()
            else:
                annual_dividend = info.get('dividendRate', 0)
            
            # Calculate dividend yield
            dividend_yield = (annual_dividend / current_price * 100) if current_price > 0 else 0
            
            return {
                'ticker': ticker,
                'current_price': current_price,
                'annual_dividend': annual_dividend,
                'dividend_yield': dividend_yield,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'sector': info.get('sector', 'Unknown')
            }
            
        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")
            return {}
    
    def validate_single_stock(self, ticker: str):
        """Validate a single stock's data"""
        print(f"\n📊 Validating {ticker}")
        print("-" * 30)
        
        # Get our data
        our_data = self.get_our_data(ticker)
        if not our_data:
            print(f"❌ Could not get our data for {ticker}")
            return None
        
        # Get real market data
        print(f"Fetching real market data for {ticker}...")
        real_data = self.get_real_market_data(ticker)
        if not real_data:
            print(f"❌ Could not get real market data for {ticker}")
            return None
        
        # Compare data
        issues = []
        
        # Price comparison (allow 5% tolerance for market movement)
        our_price = our_data.get('current_price', 0)
        real_price = real_data.get('current_price', 0)
        if real_price > 0:
            price_diff_pct = abs(our_price - real_price) / real_price * 100
            if price_diff_pct > 5:
                issues.append(f"Price mismatch: Ours ${our_price:.2f} vs Real ${real_price:.2f} ({price_diff_pct:.1f}% diff)")
        
        # Dividend yield comparison (allow 0.5% tolerance)
        our_yield = our_data.get('dividend_yield', 0)
        real_yield = real_data.get('dividend_yield', 0)
        yield_diff = abs(our_yield - real_yield)
        if yield_diff > 0.5:
            issues.append(f"Yield mismatch: Ours {our_yield:.2f}% vs Real {real_yield:.2f}% ({yield_diff:.2f}% diff)")
        
        # Sector comparison
        our_sector = our_data.get('sector', '')
        real_sector = real_data.get('sector', '')
        if our_sector != real_sector and real_sector != 'Unknown':
            issues.append(f"Sector mismatch: Ours '{our_sector}' vs Real '{real_sector}'")
        
        # Print comparison
        print(f"Price:     Ours ${our_price:.2f}  |  Real ${real_price:.2f}")
        print(f"Dividend:  Ours ${our_data.get('annual_dividend', 0):.2f}  |  Real ${real_data.get('annual_dividend', 0):.2f}")
        print(f"Yield:     Ours {our_yield:.2f}%  |  Real {real_yield:.2f}%")
        print(f"Sector:    Ours {our_sector}  |  Real {real_sector}")
        
        if issues:
            print(f"❌ ISSUES FOUND ({len(issues)}):")
            for issue in issues:
                print(f"  • {issue}")
            return False
        else:
            print("✅ Data looks accurate!")
            return True
    
    def run_comprehensive_validation(self):
        """Validate all test stocks"""
        print("🌍 Real-World Data Validation")
        print("=" * 50)
        print("Comparing our cached data with live market data...")
        
        accurate_stocks = 0
        total_stocks = 0
        all_issues = []
        
        for ticker in self.test_tickers:
            is_accurate = self.validate_single_stock(ticker)
            if is_accurate is not None:
                total_stocks += 1
                if is_accurate:
                    accurate_stocks += 1
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        print("\n" + "=" * 50)
        print(f"📈 VALIDATION SUMMARY")
        print("=" * 50)
        print(f"Stocks Tested: {total_stocks}")
        print(f"✅ Accurate: {accurate_stocks}")
        print(f"❌ Inaccurate: {total_stocks - accurate_stocks}")
        
        if total_stocks > 0:
            accuracy_rate = accurate_stocks / total_stocks * 100
            print(f"🎯 Accuracy Rate: {accuracy_rate:.1f}%")
            
            if accuracy_rate < 80:
                print("\n🚨 CRITICAL: Data accuracy is below 80%!")
                print("Our pre-cached data appears to be outdated or incorrect.")
                print("This explains why users are getting 'incorrect' results.")
            elif accuracy_rate < 95:
                print("\n⚠️  WARNING: Some data inconsistencies found.")
                print("Consider updating the pre-cached data.")
            else:
                print("\n✅ Data accuracy is excellent!")

def main():
    print("🔍 Validating Investment Assistant Data Against Real Market")
    print("=" * 60)
    print("This will check if our pre-cached data matches current market reality.\n")
    
    validator = RealWorldDataValidator()
    validator.run_comprehensive_validation()
    
    print("\n" + "=" * 60)
    print("💡 If accuracy is low, the 'incorrect results' issue is likely")
    print("   due to outdated pre-cached data, not calculation errors.")

if __name__ == "__main__":
    main() 