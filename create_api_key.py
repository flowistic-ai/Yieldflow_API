#!/usr/bin/env python3
"""
Simple API Key Generator for Yieldflow API
Creates test API keys for development and testing
"""

import secrets
import hashlib
import uuid
from datetime import datetime, timedelta
import json

def generate_api_key():
    """Generate a secure API key"""
    return f"yk_{secrets.token_urlsafe(32)}"

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_test_user_and_key(plan: str = "pro"):
    """Create a test user and API key"""
    
    # Generate API key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    key_id = str(uuid.uuid4())
    
    # Create user data
    user_data = {
        "id": 1,
        "email": "test@yieldflow.ai", 
        "full_name": "Test User",
        "company": "Yieldflow Testing",
        "plan": plan,
        "is_verified": True,
        "is_superuser": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Create API key data
    api_key_data = {
        "key_id": key_id,
        "key": api_key,
        "key_hash": key_hash,
        "name": f"{plan.title()} Test Key",
        "user_id": 1,
        "is_active": True,
        "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "allowed_ips": None,
        "scopes": None
    }
    
    return user_data, api_key_data, api_key

def main():
    """Main function to create API keys for different plans"""
    
    print("🔑 Yieldflow API Key Generator")
    print("=" * 50)
    
    plans = ["free", "basic", "pro", "enterprise"]
    
    print("\nAvailable plans:")
    for i, plan in enumerate(plans, 1):
        print(f"{i}. {plan.title()}")
    
    try:
        choice = input("\nSelect plan (1-4) or press Enter for Pro: ").strip()
        if not choice:
            selected_plan = "pro"
        else:
            selected_plan = plans[int(choice) - 1]
    except (ValueError, IndexError):
        selected_plan = "pro"
    
    print(f"\n🎯 Creating {selected_plan.title()} API key...")
    
    user_data, api_key_data, api_key = create_test_user_and_key(selected_plan)
    
    print("\n✅ API Key Generated Successfully!")
    print("=" * 50)
    print(f"🔑 API Key: {api_key}")
    print(f"📋 Plan: {selected_plan.title()}")
    print(f"👤 User: {user_data['email']}")
    print(f"🏢 Company: {user_data['company']}")
    print(f"⏰ Expires: {api_key_data['expires_at'][:10]}")
    
    # Rate limits
    rate_limits = {
        "free": "1K requests/day, 10/min",
        "basic": "10K requests/day, 60/min", 
        "pro": "50K requests/day, 300/min",
        "enterprise": "200K requests/day, 1000/min"
    }
    
    print(f"📊 Rate Limits: {rate_limits[selected_plan]}")
    
    # Features
    features = {
        "free": ["Basic company info", "Basic financial data"],
        "basic": ["Company info", "Financial data", "Financial ratios", "Trend analysis"],
        "pro": ["All Basic features", "Advanced analytics", "Peer comparison", "Forecasting"],
        "enterprise": ["All Pro features", "Bulk data", "Real-time data", "API webhooks"]
    }
    
    print(f"🎁 Features: {', '.join(features[selected_plan])}")
    
    print("\n📝 Usage Instructions:")
    print("=" * 50)
    print("1. Copy the API key above")
    print("2. Use it in your requests:")
    print(f'   curl -H "Authorization: Bearer {api_key}" \\')
    print('        "http://localhost:8000/financial/company/AAPL"')
    
    print("\n🧪 Or test with our test endpoints (no auth needed):")
    print('   curl "http://localhost:8000/financial/test/company/AAPL"')
    
    # Save to file for easy access
    save_data = {
        "api_key": api_key,
        "plan": selected_plan,
        "user_data": user_data,
        "api_key_data": api_key_data,
        "created_at": datetime.utcnow().isoformat()
    }
    
    with open(f"api_key_{selected_plan}.json", "w") as f:
        json.dump(save_data, f, indent=2)
    
    print(f"\n💾 API key details saved to: api_key_{selected_plan}.json")
    print("\n🚀 Your API is ready to use!")

if __name__ == "__main__":
    main() 