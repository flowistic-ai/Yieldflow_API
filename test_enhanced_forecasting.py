#!/usr/bin/env python3
"""
Test Enhanced Dividend Forecasting Service
Tests the integration of news sentiment with quantitative finance models
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_dividend_forecaster import EnhancedDividendForecaster
from app.services.dividend_service import DividendService
from datetime import date, timedelta, datetime
import json

async def test_enhanced_forecasting():
    """Test the enhanced dividend forecasting with news analysis"""
    
    print("🚀 Testing Enhanced Dividend Forecasting Service")
    print("=" * 60)
    
    # Initialize services
    enhanced_forecaster = EnhancedDividendForecaster()
    dividend_service = DividendService()
    
    # Test tickers
    test_tickers = ['AAPL', 'MSFT', 'JNJ', 'GOOGL']
    
    for ticker in test_tickers:
        print(f"\n📊 Testing Enhanced Forecast for {ticker}")
        print("-" * 40)
        
        try:
            # Get historical dividends and financials
            end_date = date.today()
            start_date = end_date - timedelta(days=365 * 5)  # 5 years
            
            dividends = await dividend_service._get_yfinance_dividends(ticker, start_date, end_date)
            financials = await dividend_service._fetch_comprehensive_financials(ticker)
            market_data = await dividend_service._fetch_market_data(ticker)
            
            print(f"✅ Fetched {len(dividends)} dividend records")
            print(f"✅ Obtained financial data: EPS={financials.get('eps', 'N/A')}")
            print(f"✅ Market data: Sector={market_data.get('sector', 'Unknown')}")
            
            # Generate enhanced forecast
            enhanced_result = await enhanced_forecaster.generate_enhanced_forecast(
                ticker=ticker,
                dividends=dividends,
                financials=financials,
                market_data=market_data,
                years=3
            )
            
            # Display results
            print(f"\n📈 Enhanced Forecast Results:")
            print(f"Methodology: {enhanced_result['methodology']}")
            
            # Financial Model
            model = enhanced_result['financial_model']
            print(f"\n🏦 Financial Model:")
            print(f"  Base Growth Rate: {model['base_growth_rate']:.2%}")
            print(f"  News Sentiment Adjustment: {model['news_sentiment_adjustment']:+.2%}")
            print(f"  Sector Momentum: {model['sector_momentum']:+.2%}")
            print(f"  Beta: {model['beta']:.2f}")
            print(f"  Geopolitical Risk: {model['geopolitical_risk']:.1%}")
            print(f"  Model Confidence: {model['confidence_score']:.1%}")
            
            # News Analysis
            news = enhanced_result['news_analysis']
            print(f"\n📰 News Analysis:")
            print(f"  Sentiment Score: {news['sentiment_score']:+.2f}")
            print(f"  News Volume: {news['news_volume']} articles")
            print(f"  Key Themes: {', '.join(news.get('dividend_themes', ['None'])[:3])}")
            print(f"  Key Insights: {len(news.get('key_insights', []))} insights")
            
            # Projections
            print(f"\n📅 3-Year Projections:")
            for i, proj in enumerate(enhanced_result['projections']):
                print(f"  Year {proj['year']}: ${proj['projected_dividend']:.4f}")
                print(f"    Growth Rate: {proj['enhanced_growth_rate']:.2%}")
                print(f"    News Impact: {proj.get('news_adjustment', 0):+.2%}")
                print(f"    Confidence: {proj['confidence_interval']['confidence_level']:.0%}")
                print(f"    Range: ${proj['confidence_interval']['lower_95']:.4f} - ${proj['confidence_interval']['upper_95']:.4f}")
                print()
            
            # Investment Analysis (truncated)
            analysis = enhanced_result['investment_analysis']
            if analysis:
                print(f"📝 Investment Analysis Summary:")
                print(f"  {analysis[:200]}..." if len(analysis) > 200 else f"  {analysis}")
            
            print(f"\n✅ Enhanced forecasting completed successfully for {ticker}")
            
        except Exception as e:
            print(f"❌ Error testing {ticker}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Enhanced Forecasting Test Complete!")
    print("=" * 60)

async def test_integration_with_dividend_service():
    """Test the integration with the main dividend service"""
    
    print("\n🔧 Testing Integration with Dividend Service")
    print("=" * 50)
    
    dividend_service = DividendService()
    
    test_ticker = 'AAPL'
    print(f"Testing integrated forecast for {test_ticker}")
    
    try:
        # Test the updated _generate_professional_forecast method
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * 5)
        
        dividends = await dividend_service._get_yfinance_dividends(test_ticker, start_date, end_date)
        financials = await dividend_service._fetch_comprehensive_financials(test_ticker)
        economic_context = await dividend_service._fetch_economic_context()
        
        # Test integrated forecast
        forecast = await dividend_service._generate_professional_forecast(
            'AAPL',
            dividends, financials, economic_context, 3
        )
        
        print(f"✅ Integrated forecast generated successfully")
        print(f"Forecast items: {len(forecast)}")
        
        if forecast:
            first_projection = forecast[0]
            print(f"\nFirst projection:")
            print(f"  Year: {first_projection.get('year', 'N/A')}")
            print(f"  Projected Dividend: ${first_projection.get('projected_dividend', 0):.4f}")
            print(f"  Growth Rate: {first_projection.get('growth_rate', 0):.2f}%")
            print(f"  Methodology: {first_projection.get('methodology', 'Unknown')}")
            
            if 'news_adjustment' in first_projection:
                print(f"  News Adjustment: {first_projection['news_adjustment']:+.2f}%")
                print(f"  ✅ Enhanced forecasting is active!")
            else:
                print(f"  ⚠️  Using traditional forecasting (fallback)")
                
            if 'investment_analysis' in first_projection:
                print(f"  📝 Investment analysis included")
                
        # Test full comprehensive analysis
        print(f"\n🔍 Testing Full Comprehensive Analysis...")
        full_analysis = await dividend_service.get_comprehensive_dividend_analysis(
            test_ticker, include_forecast=True
        )
        
        if 'forecast' in full_analysis and full_analysis['forecast']:
            forecast_data = full_analysis['forecast']
            print(f"✅ Full analysis includes enhanced forecast")
            print(f"Forecast methodology: {forecast_data.get('methodology', 'Unknown')}")
        else:
            print(f"⚠️  Full analysis missing forecast data")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_news_analysis_standalone():
    """Test news analysis functionality standalone"""
    
    print("\n📰 Testing News Analysis Functionality")
    print("=" * 45)
    
    forecaster = EnhancedDividendForecaster()
    
    test_tickers = ['AAPL', 'JNJ']
    
    for ticker in test_tickers:
        print(f"\nTesting news analysis for {ticker}")
        try:
            news_analysis = await forecaster._analyze_ticker_news_for_dividends(ticker)
            
            print(f"  Sentiment Score: {news_analysis['sentiment_score']:+.2f}")
            print(f"  Confidence: {news_analysis['confidence']:.2f}")
            print(f"  News Volume: {news_analysis['news_volume']}")
            print(f"  Geopolitical Risk: {news_analysis['geopolitical_risk']:.2f}")
            print(f"  Dividend Themes: {news_analysis['dividend_themes'][:3]}")
            print(f"  Key Insights: {len(news_analysis['key_insights'])}")
            print(f"  Risk Factors: {len(news_analysis['risk_factors'])}")
            
        except Exception as e:
            print(f"  ❌ News analysis failed: {e}")

def save_test_results(results):
    """Save test results to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"enhanced_forecasting_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"📄 Test results saved to {filename}")

async def main():
    """Main test function"""
    print("🎯 Enhanced Dividend Forecasting Test Suite")
    print("=" * 60)
    print("Testing news-enhanced dividend forecasting with quantitative finance models")
    print("Features: CAPM, Gordon Growth Model, News Sentiment, Geopolitical Risk")
    print("=" * 60)
    
    # Run all tests
    await test_enhanced_forecasting()
    await test_integration_with_dividend_service()
    await test_news_analysis_standalone()
    
    print("\n🎉 All tests completed!")
    print("The enhanced forecasting service combines:")
    print("  ✅ Traditional dividend analysis (CAGR, payout ratios)")
    print("  ✅ Quantitative finance models (CAPM, Gordon Growth)")
    print("  ✅ Real-time news sentiment analysis")
    print("  ✅ Geopolitical risk assessment")
    print("  ✅ Monte Carlo-style confidence intervals")
    print("  ✅ Investment thesis generation")

if __name__ == "__main__":
    asyncio.run(main()) 