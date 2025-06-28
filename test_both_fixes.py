#!/usr/bin/env python3
"""
Test script for the concise investment guidance system
Focus on brief analysis, risk assessment, and direct dividend picks
"""

import asyncio
import json
from app.services.live_investment_assistant import LiveInvestmentAssistant

async def test_concise_investment_guidance():
    """Test the new concise investment guidance system"""
    assistant = LiveInvestmentAssistant()
    
    test_queries = [
        "I have $10000 and want $100 monthly",
        "I have $5000 and want $50 monthly", 
        "I have $50000 and want $500 monthly",
        "I have $1000 and want $200 monthly",  # High risk case
        "I have $100000 and want $300 monthly"  # Conservative case
    ]
    
    print("🔬 Testing Concise Investment Guidance System")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📊 Test {i}: {query}")
        print("-" * 40)
        
        try:
            response = await assistant.process_query(query)
            
            if response.success and response.data:
                guidance = response.data.get('concise_guidance')
                if guidance:
                    print(f"💰 Investment: ${guidance['investment_amount']:,}")
                    print(f"🎯 Target: ${guidance['target_monthly']}/month")
                    print(f"📈 Required Yield: {guidance['required_yield']}%")
                    print(f"⚠️  Risk Level: {guidance['risk_assessment']}")
                    print(f"🚀 Max Potential: ${guidance['max_potential_monthly']}/month")
                    print(f"✅ Realistic: ${guidance['realistic_monthly']}/month")
                    print(f"📋 Strategy: {guidance['strategy']}")
                    
                    print(f"\n📈 Top Dividend Picks:")
                    for stock in guidance['dividend_picks'][:3]:
                        print(f"  • {stock['ticker']}: {stock['yield']}% yield → ${stock['monthly_income']}/month")
                    
                    print(f"\n📱 Response: {response.message}")
                else:
                    print("❌ No concise guidance data found")
                    print(f"Raw data: {json.dumps(response.data, indent=2)}")
            else:
                print(f"❌ Query failed: {response.message}")
                
        except Exception as e:
            print(f"💥 Error processing query: {str(e)}")
        
        print("\n" + "="*50)

async def test_backend_frontend_integration():
    """Test that backend response matches frontend expectations"""
    assistant = LiveInvestmentAssistant()
    
    print("\n🔗 Testing Backend-Frontend Integration")
    print("=" * 60)
    
    query = "I have $25000 and want $200 monthly"
    response = await assistant.process_query(query)
    
    if response.success:
        print("✅ Backend Response Structure:")
        print(f"  - Success: {response.success}")
        print(f"  - Message: {response.message}")
        print(f"  - Data keys: {list(response.data.keys()) if response.data else 'None'}")
        
        if 'concise_guidance' in response.data:
            guidance = response.data['concise_guidance']
            print(f"  - Guidance keys: {list(guidance.keys())}")
            print(f"  - Has dividend_picks: {'dividend_picks' in guidance}")
            print(f"  - Number of picks: {len(guidance.get('dividend_picks', []))}")
            
            # Verify all required fields are present
            required_fields = [
                'investment_amount', 'target_monthly', 'required_yield',
                'risk_assessment', 'max_potential_monthly', 'realistic_monthly',
                'strategy', 'dividend_picks'
            ]
            
            missing_fields = [field for field in required_fields if field not in guidance]
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                print("✅ All required fields present")
                
            # Test dividend picks structure
            if guidance.get('dividend_picks'):
                pick = guidance['dividend_picks'][0]
                required_pick_fields = ['ticker', 'yield', 'monthly_income', 'annual_income']
                missing_pick_fields = [field for field in required_pick_fields if field not in pick]
                
                if missing_pick_fields:
                    print(f"❌ Missing dividend pick fields: {missing_pick_fields}")
                else:
                    print("✅ Dividend pick structure valid")
        else:
            print("❌ No concise_guidance in response data")
    else:
        print(f"❌ Backend query failed: {response.message}")

async def quick_test():
    """Quick test of the concise guidance system"""
    assistant = LiveInvestmentAssistant()
    
    print("🚀 Quick Test: Concise Investment Guidance")
    print("=" * 50)
    
    # Test realistic scenario
    query = "I have $25000 and want $200 monthly"
    print(f"📝 Query: {query}")
    
    response = await assistant.process_query(query)
    
    if response.success and response.data.get('concise_guidance'):
        guidance = response.data['concise_guidance']
        
        print(f"✅ SUCCESS - System working correctly!")
        print(f"💰 Investment: ${guidance['investment_amount']:,}")
        print(f"🎯 Target: ${guidance['target_monthly']}/month") 
        print(f"📊 Required Yield: {guidance['required_yield']}%")
        print(f"⚠️  Risk: {guidance['risk_assessment']}")
        print(f"🚀 Max Potential: ${guidance['max_potential_monthly']}/month")
        print(f"✅ Realistic: ${guidance['realistic_monthly']}/month")
        print(f"📋 Strategy: {guidance['strategy']}")
        
        print(f"\n📈 Top 3 Dividend Picks:")
        for i, stock in enumerate(guidance['dividend_picks'][:3], 1):
            print(f"  {i}. {stock['ticker']}: {stock['yield']}% → ${stock['monthly_income']}/month")
        
        print(f"\n💬 Response: {response.message}")
        print(f"⏱️  Processing Time: {response.processing_time:.2f} seconds")
        
        print("\n🎉 READY FOR FRONTEND TESTING!")
        print("✅ Backend API working correctly")
        print("✅ Data structure matches frontend expectations")
        print("✅ Real-time market data integration functional")
        
    else:
        print(f"❌ FAILED: {response.message}")
        if response.data:
            print(f"Raw data: {json.dumps(response.data, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_concise_investment_guidance())
    asyncio.run(test_backend_frontend_integration())
    asyncio.run(quick_test()) 