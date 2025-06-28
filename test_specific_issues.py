#!/usr/bin/env python3
"""
Focused test for specific AI assistant issues reported by user
"""

import asyncio
import sys
sys.path.append('.')

from app.services.natural_language_query import NaturalLanguageQueryEngine

async def test_specific_issues():
    """Test the specific issues reported by the user."""
    print("🔍 Testing Specific AI Assistant Issues")
    print("=" * 50)
    
    query_engine = NaturalLanguageQueryEngine()
    
    # Test 1: Dividend yield accuracy
    print("\n📊 Test 1: Dividend Yield Accuracy")
    print("-" * 30)
    
    query = "Find dividend stocks with yield above 4%"
    response = await query_engine.process_query(query)
    
    if response.success:
        results = response.data.get('screening_results', [])
        print(f"Found {len(results)} stocks")
        
        if results:
            for i, stock in enumerate(results[:3], 1):
                yield_val = stock['dividend_yield']
                price = stock.get('current_price', 0)
                print(f"{i}. {stock['ticker']}: Yield={yield_val:.2f}%, Price=${price:.2f}")
                
                # Check for unrealistic yields
                if yield_val > 20:
                    print(f"   ⚠️  WARNING: Unrealistic yield of {yield_val:.2f}%")
                elif yield_val == 0:
                    print(f"   ⚠️  WARNING: Zero yield reported")
                elif price == 0:
                    print(f"   ⚠️  WARNING: Zero price reported")
                else:
                    print(f"   ✅ Data looks reasonable")
        else:
            print("❌ No results found")
    else:
        print(f"❌ Query failed: {response.explanation}")
    
    # Test 2: Income recommendations accuracy  
    print("\n💰 Test 2: Income Recommendations Accuracy")
    print("-" * 30)
    
    query = "I need $500 monthly income with low risk"
    response = await query_engine.process_query(query)
    
    if response.success:
        income_recs = response.data.get('income_recommendations', [])
        target_income = response.data.get('target_income', 0)
        
        print(f"Target Income: ${target_income:,.0f} annually")
        print(f"Recommendations: {len(income_recs)}")
        
        if income_recs:
            print("\nTop 3 recommendations:")
            for i, stock in enumerate(income_recs[:3], 1):
                yield_val = stock['dividend_yield']
                investment = stock.get('required_investment', 0)
                quality = stock.get('quality_score', 0)
                
                print(f"{i}. {stock['ticker']} ({stock['company_name']})")
                print(f"   Yield: {yield_val:.2f}%")
                print(f"   Investment needed: ${investment:,.0f}")
                print(f"   Quality score: {quality:.1f}")
                
                # Validate calculations
                if yield_val > 0 and investment > 0:
                    calculated_income = investment * (yield_val / 100)
                    print(f"   Calculated income: ${calculated_income:,.0f}")
                    
                    if abs(calculated_income - target_income) < 100:
                        print(f"   ✅ Math checks out")
                    else:
                        print(f"   ⚠️  Math doesn't match target")
                
                # Check for data quality issues
                if yield_val > 25:
                    print(f"   ❌ Unrealistic yield: {yield_val:.2f}%")
                elif yield_val == 0:
                    print(f"   ❌ Zero yield")
                elif investment == 0:
                    print(f"   ❌ Zero investment calculation")
                else:
                    print(f"   ✅ Data quality OK")
        else:
            print("❌ No income recommendations generated")
        
        # Check for AI insights
        if "💡 AI Insights:" in response.explanation:
            print("\n✅ AI enhancement is working")
        else:
            print("\n⚠️  AI enhancement may not be working")
    else:
        print(f"❌ Income recommendations failed: {response.explanation}")
    
    # Test 3: Check specific stock data (Apple)
    print("\n🍎 Test 3: Apple Inc. Data Accuracy")
    print("-" * 30)
    
    query = "Tell me about Apple Inc. dividend"
    response = await query_engine.process_query(query)
    
    if response.success:
        print("✅ Apple analysis successful")
        print(f"Response: {response.explanation[:200]}...")
        
        # Check if response contains realistic data
        if "20%" in response.explanation and "dividend yield" in response.explanation.lower():
            print("❌ Found unrealistic 20% dividend yield mention")
        else:
            print("✅ No obvious data errors in response")
    else:
        print(f"❌ Apple analysis failed: {response.explanation}")

if __name__ == "__main__":
    asyncio.run(test_specific_issues()) 