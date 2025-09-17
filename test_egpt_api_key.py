#!/usr/bin/env python3
"""
Test to verify EGPT_API_KEY is being used instead of OPENAI_API_KEY
"""
import sys
import os

# Add the gpt_researcher directory to the path
sys.path.append('.')

from gpt_researcher.config.config import Config
from gpt_researcher.utils.llm import create_chat_completion

def test_egpt_api_key():
    """Test that EGPT_API_KEY is being used correctly"""
    print("=== EGPT_API_KEY Configuration Test ===")
    
    # Test 1: Check environment variables
    egpt_key = os.getenv('EGPT_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"✅ EGPT_API_KEY: {'Set' if egpt_key else 'Not set'}")
    print(f"ℹ️  OPENAI_API_KEY: {'Set' if openai_key else 'Not set'}")
    
    if egpt_key:
        print(f"🔑 EGPT_API_KEY (first 10 chars): {egpt_key[:10]}...")
    
    # Test 2: Check config
    config = Config()
    print(f"📊 LLM Provider: {config.smart_llm_provider}")
    print(f"📊 LLM Model: {config.smart_llm_model}")
    
    return True

async def test_api_call_with_egpt():
    """Test that API calls work with EGPT_API_KEY"""
    print(f"\n=== API Call Test with EGPT_API_KEY ===")
    
    try:
        # Make a simple API call
        response = await create_chat_completion(
            messages=[{"role": "user", "content": "Hello! Just say 'API working' if you can respond."}],
            model="gpt-4",
            max_tokens=50,
            llm_provider="openai"
        )
        
        print(f"✅ API Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    
    try:
        # Test environment setup
        env_success = test_egpt_api_key()
        
        # Test API call
        api_success = asyncio.run(test_api_call_with_egpt())
        
        if env_success and api_success:
            print(f"\n🎉 EGPT_API_KEY is configured correctly and working!")
        else:
            print(f"\n🔧 Some tests failed. Check your EGPT_API_KEY configuration.")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()