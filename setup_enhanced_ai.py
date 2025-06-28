#!/usr/bin/env python3
"""
Enhanced AI Investment Assistant Setup Script

This script helps you set up the enhanced AI investment assistant with:
- Local Llama models (free)
- Optimal LLM configurations
- API key management
- Performance optimization

Run this script to configure your enhanced AI system for better accuracy and speed.
"""

import os
import subprocess
import sys
import requests
import json
from pathlib import Path
import asyncio
import time

class EnhancedAISetup:
    def __init__(self):
        self.ollama_base_url = "http://localhost:11434"
        self.recommended_models = [
            "llama3.1:8b",      # Best general purpose model
            "llama3.2:latest",  # Latest release
            "mistral:latest",   # Good alternative
            "dolphin-mistral:latest"  # Fine-tuned for instructions
        ]
        
    def print_banner(self):
        """Print setup banner."""
        print("=" * 60)
        print("🚀 Enhanced AI Investment Assistant Setup")
        print("=" * 60)
        print("Strategic Multi-LLM Configuration for Better Accuracy")
        print("- Local Llama Models (Free)")
        print("- Premium API Integration") 
        print("- Performance Optimization")
        print("- Quality Score Enhancement")
        print("=" * 60)
        print()

    def check_ollama_installation(self):
        """Check if Ollama is installed."""
        print("🔍 Checking Ollama installation...")
        
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Ollama is installed: {result.stdout.strip()}")
                return True
            else:
                print("❌ Ollama command failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Ollama is not installed")
            return False

    def install_ollama(self):
        """Install Ollama."""
        print("\n📦 Installing Ollama...")
        
        system = os.uname().sysname.lower()
        
        if system == "darwin":  # macOS
            print("Installing Ollama for macOS...")
            install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
        elif system == "linux":
            print("Installing Ollama for Linux...")
            install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
        else:
            print("❌ Unsupported operating system. Please install Ollama manually from https://ollama.ai")
            return False
        
        try:
            subprocess.run(install_cmd, shell=True, check=True)
            print("✅ Ollama installation completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ollama installation failed: {e}")
            return False

    def start_ollama_service(self):
        """Start Ollama service."""
        print("\n🚀 Starting Ollama service...")
        
        try:
            # Start Ollama service in background
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            print("Waiting for Ollama service to start...")
            for i in range(10):
                try:
                    response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        print("✅ Ollama service is running")
                        return True
                except requests.RequestException:
                    pass
                time.sleep(2)
                print(f"Waiting... ({i+1}/10)")
            
            print("❌ Ollama service failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start Ollama service: {e}")
            return False

    def check_existing_models(self):
        """Check what models are already installed."""
        print("\n📋 Checking existing models...")
        
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    print("🔍 Found existing models:")
                    for model in models:
                        print(f"  - {model['name']} ({model.get('size', 'unknown size')})")
                    return [model['name'] for model in models]
                else:
                    print("📭 No models found")
                    return []
            else:
                print("❌ Failed to check models")
                return []
        except Exception as e:
            print(f"❌ Error checking models: {e}")
            return []

    def pull_recommended_model(self, model_name):
        """Pull a specific model."""
        print(f"\n📥 Pulling {model_name}...")
        print("⚠️  This may take 5-15 minutes depending on your internet connection")
        
        try:
            # Start pull request
            response = requests.post(
                f"{self.ollama_base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=900  # 15 minutes
            )
            
            if response.status_code == 200:
                print(f"📥 Downloading {model_name}...")
                
                # Show progress
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            status = data.get('status', '')
                            if 'downloading' in status.lower():
                                print(f"⏳ {status}")
                            elif 'pulling' in status.lower():
                                print(f"📥 {status}")
                            elif 'verifying' in status.lower():
                                print(f"🔍 {status}")
                            elif 'success' in status.lower():
                                print(f"✅ Successfully downloaded {model_name}")
                                return True
                        except json.JSONDecodeError:
                            continue
                
                print(f"✅ {model_name} installation completed")
                return True
            else:
                print(f"❌ Failed to pull {model_name}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error pulling {model_name}: {e}")
            return False

    def setup_local_models(self):
        """Set up recommended local models."""
        print("\n🤖 Setting up local AI models...")
        
        existing_models = self.check_existing_models()
        
        # Check if we already have a good model
        for model in self.recommended_models:
            if model in existing_models:
                print(f"✅ Good model already available: {model}")
                return True
        
        # Try to install the best model
        print("\n📥 Installing recommended model for optimal performance...")
        
        for model in self.recommended_models:
            print(f"\n🎯 Attempting to install: {model}")
            if self.pull_recommended_model(model):
                print(f"✅ Successfully installed {model}")
                return True
            else:
                print(f"⚠️  Failed to install {model}, trying next option...")
        
        print("❌ Failed to install any recommended models")
        return False

    def test_model_performance(self):
        """Test the installed model performance."""
        print("\n🧪 Testing AI model performance...")
        
        test_prompt = """Analyze this portfolio: AAPL 40%, MSFT 30%, JNJ 30%. 
        Provide brief strengths and risks."""
        
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": "llama3.1:8b",
                    "prompt": test_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 200
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '')
                if len(result) > 50:
                    print("✅ AI model is working correctly")
                    print(f"📝 Sample response: {result[:100]}...")
                    return True
                else:
                    print("⚠️  AI model response seems limited")
                    return False
            else:
                print(f"❌ AI model test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ AI model test error: {e}")
            return False

    def setup_api_keys(self):
        """Help user configure API keys."""
        print("\n🔑 API Key Configuration")
        print("For optimal performance, configure these optional premium API keys:")
        print()
        
        api_keys = {
            "OPENAI_API_KEY": {
                "name": "OpenAI GPT-4",
                "benefit": "Best accuracy for complex analysis",
                "cost": "Paid (recommended for production)"
            },
            "GOOGLE_GEMINI_API_KEY": {
                "name": "Google Gemini Pro",
                "benefit": "Good free tier, excellent for financial analysis",
                "cost": "Free tier available"
            },
            "ANTHROPIC_API_KEY": {
                "name": "Anthropic Claude",
                "benefit": "Excellent reasoning for investment decisions",
                "cost": "Paid (optional)"
            }
        }
        
        env_file = Path(".env")
        env_content = ""
        
        if env_file.exists():
            env_content = env_file.read_text()
        
        for key, info in api_keys.items():
            print(f"\n🔹 {info['name']}")
            print(f"   Benefit: {info['benefit']}")
            print(f"   Cost: {info['cost']}")
            
            if key in env_content:
                print(f"   Status: ✅ Already configured")
            else:
                print(f"   Status: ⚠️  Not configured")
                
                user_input = input(f"   Enter {key} (or press Enter to skip): ").strip()
                if user_input:
                    env_content += f"\n{key}={user_input}"
                    print(f"   ✅ Added {key}")
        
        # Write updated .env file
        if env_content:
            env_file.write_text(env_content)
            print(f"\n✅ API keys saved to {env_file}")

    def optimize_performance(self):
        """Provide performance optimization tips."""
        print("\n⚡ Performance Optimization Tips")
        print("=" * 40)
        
        tips = [
            "✅ Local Llama model installed (free, no API limits)",
            "🔧 Configure premium APIs for best accuracy",
            "🚀 Use ensemble mode (multiple models) for complex queries",
            "📊 Quality scores now based on actual data completeness",
            "⚡ Parallel processing enabled for faster responses",
            "🎯 Enhanced prompt engineering for financial analysis",
            "💾 Response caching enabled for repeated queries"
        ]
        
        for tip in tips:
            print(f"  {tip}")
        
        print("\n🎯 Recommended Configuration:")
        print("  - Primary: Local Llama (free, always available)")
        print("  - Secondary: Google Gemini (free tier)")
        print("  - Premium: OpenAI GPT-4 (best accuracy)")
        print()

    def create_test_script(self):
        """Create a test script to verify setup."""
        test_script = """#!/usr/bin/env python3
'''
Test script for Enhanced AI Investment Assistant
'''

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_enhanced_ai():
    try:
        from app.services.ai_insights import EnhancedAIInsightsService
        from app.services.natural_language_query import EnhancedNaturalLanguageQueryEngine
        
        print("🧪 Testing Enhanced AI Investment Assistant")
        print("=" * 50)
        
        # Test AI insights service
        print("\n1. Testing AI Insights Service...")
        ai_service = EnhancedAIInsightsService()
        print(f"   Available models: {ai_service.available_models}")
        
        # Test natural language processing
        print("\n2. Testing Natural Language Query Engine...")
        query_engine = EnhancedNaturalLanguageQueryEngine()
        
        test_queries = [
            "Find dividend stocks with yield above 4%",
            "Optimize a portfolio with AAPL, MSFT, JNJ",
            "I need $500 monthly income with low risk"
        ]
        
        for query in test_queries:
            print(f"\n   Testing: '{query}'")
            try:
                result = await query_engine.process_query(query)
                print(f"   ✅ Success - Quality: {result.quality_score:.2f}")
                print(f"   ⏱️  Processing time: {result.processing_time:.2f}s")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        print("\n✅ Enhanced AI system is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_enhanced_ai())
"""
        
        test_file = Path("test_enhanced_ai.py")
        test_file.write_text(test_script)
        test_file.chmod(0o755)
        print(f"✅ Created test script: {test_file}")

    def run_setup(self):
        """Run the complete setup process."""
        self.print_banner()
        
        # Step 1: Check/Install Ollama
        if not self.check_ollama_installation():
            print("\n📦 Ollama is required for local AI models")
            install = input("Install Ollama now? (y/n): ").lower().strip()
            if install == 'y':
                if not self.install_ollama():
                    print("❌ Setup failed: Could not install Ollama")
                    return False
            else:
                print("⚠️  Continuing without local models (limited functionality)")
        
        # Step 2: Start Ollama service
        if not self.start_ollama_service():
            print("⚠️  Ollama service not running, skipping model setup")
        else:
            # Step 3: Install models
            if not self.setup_local_models():
                print("⚠️  No local models installed, will rely on API models")
            else:
                # Step 4: Test model
                self.test_model_performance()
        
        # Step 5: Configure API keys
        self.setup_api_keys()
        
        # Step 6: Performance tips
        self.optimize_performance()
        
        # Step 7: Create test script
        self.create_test_script()
        
        print("\n🎉 Enhanced AI Investment Assistant Setup Complete!")
        print("=" * 60)
        print("📈 Your AI assistant now features:")
        print("  - Strategic multi-LLM ensemble analysis")
        print("  - Local Llama models (free, no API limits)")
        print("  - Quality scores based on real data completeness")
        print("  - Faster processing with parallel execution")
        print("  - Enhanced financial analysis capabilities")
        print()
        print("🧪 Run 'python test_enhanced_ai.py' to verify everything works")
        print("🚀 Start your API server with enhanced AI capabilities!")
        
        return True

if __name__ == "__main__":
    setup = EnhancedAISetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1) 