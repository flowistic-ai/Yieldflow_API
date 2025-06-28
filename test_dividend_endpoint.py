#!/usr/bin/env python3
"""
Test script for the new dividend endpoint
"""
import asyncio
import aiohttp
import json
from datetime import date, timedelta

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "test-key"  # Replace with your actual API key

async def test_dividend_endpoints():
    """Test all dividend endpoints"""
    
    headers = {"X-API-Key": API_KEY}
    
    # Test companies with known dividend history
    test_tickers = ["AAPL", "MSFT", "KO", "JNJ", "PG"]
    
    async with aiohttp.ClientSession() as session:
        
        print("🔍 Testing Dividend Endpoints")
        print("=" * 50)
        
        # Test 1: Economic Indicators
        print("\n1. Testing Economic Indicators Endpoint...")
        try:
            url = f"{BASE_URL}/dividends/economic-indicators"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Economic indicators retrieved successfully")
                    print(f"   Available indicators: {list(data.get('economic_indicators', {}).keys())}")
                else:
                    print(f"❌ Failed with status {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 2: Current Dividend Info
        print("\n2. Testing Current Dividend Info...")
        for ticker in test_tickers[:2]:  # Test first 2 tickers
            try:
                url = f"{BASE_URL}/dividends/{ticker}/current"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        current_info = data.get('current_dividend_info', {})
                        print(f"✅ {ticker}: Current yield: {current_info.get('current_yield', 'N/A')}, "
                              f"Last dividend: ${current_info.get('last_dividend_amount', 'N/A')}")
                    else:
                        print(f"❌ {ticker}: Failed with status {response.status}")
            except Exception as e:
                print(f"❌ {ticker}: Error: {e}")
        
        # Test 3: Dividend History
        print("\n3. Testing Dividend History...")
        ticker = "AAPL"
        try:
            url = f"{BASE_URL}/dividends/{ticker}/history"
            params = {
                "limit": 10,
                "start_date": (date.today() - timedelta(days=365*2)).isoformat()
            }
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    summary = data.get('summary', {})
                    print(f"✅ {ticker}: Found {summary.get('total_payments', 0)} dividend payments")
                    print(f"   Total amount: ${summary.get('total_amount', 0):.2f}")
                    print(f"   Years covered: {summary.get('years_covered', 0)}")
                else:
                    print(f"❌ {ticker}: Failed with status {response.status}")
        except Exception as e:
            print(f"❌ {ticker}: Error: {e}")
        
        # Test 4: Comprehensive Analysis
        print("\n4. Testing Comprehensive Dividend Analysis...")
        ticker = "MSFT"
        try:
            url = f"{BASE_URL}/dividends/{ticker}/analysis"
            params = {
                "include_forecast": "true",
                "start_date": (date.today() - timedelta(days=365*3)).isoformat()
            }
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    analysis = data.get('analysis', {})
                    print(f"✅ {ticker}: Analysis completed successfully")
                    print(f"   Current yield: {analysis.get('current_dividend_yield', 'N/A')}%")
                    print(f"   Consecutive increases: {analysis.get('years_of_consecutive_increases', 'N/A')} years")
                    print(f"   Dividend aristocrat: {analysis.get('is_dividend_aristocrat', 'N/A')}")
                    print(f"   Economic indicators: {len(data.get('economic_indicators', {}))}")
                    print(f"   Has forecast: {bool(data.get('forecast'))}")
                else:
                    print(f"❌ {ticker}: Failed with status {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ {ticker}: Error: {e}")
        
        # Test 5: Dividend Forecast
        print("\n5. Testing Dividend Forecast...")
        ticker = "JNJ"
        try:
            url = f"{BASE_URL}/dividends/{ticker}/forecast"
            params = {"years": 3}
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    forecasts = data.get('forecasts', [])
                    print(f"✅ {ticker}: Generated {len(forecasts)} forecasts")
                    for forecast in forecasts:
                        print(f"   {forecast.get('forecast_date')}: ${forecast.get('estimated_amount', 0):.4f} "
                              f"(confidence: {forecast.get('confidence_level', 0):.2f})")
                else:
                    print(f"❌ {ticker}: Failed with status {response.status}")
        except Exception as e:
            print(f"❌ {ticker}: Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Dividend endpoint testing completed!")

if __name__ == "__main__":
    asyncio.run(test_dividend_endpoints()) 