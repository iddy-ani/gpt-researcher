#!/usr/bin/env python3
"""
Detailed test script to diagnose Intel API endpoint issues
"""
import asyncio
import os
import httpx
from gpt_researcher.utils.llm import create_chat_completion
from gpt_researcher.config.config import Config

async def test_direct_api_call():
    """Test direct API call to Intel endpoint"""
    print("=== Direct API Test ===")
    base_url = os.getenv('OPENAI_BASE_URL')
    api_key = os.getenv('EGPT_API_KEY')
    
    if not base_url or not api_key:
        print("❌ Missing OPENAI_BASE_URL or EGPT_API_KEY")
        return
    
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",  # Try a basic model first
        "messages": [
            {"role": "user", "content": "Hello, can you respond?"}
        ],
        "max_tokens": 50
    }
    
    print(f"Testing URL: {url}")
    print(f"Using API Key: {api_key[:10]}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Text: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ Direct API call successful!")
                return True
            else:
                print(f"❌ API call failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Direct API call failed: {e}")
        return False

async def test_gptr_api_call():
    """Test using GPT Researcher's LLM utilities"""
    print("\n=== GPT Researcher LLM Test ===")
    
    try:
        cfg = Config()
        print(f"Config - Smart LLM Provider: {cfg.smart_llm_provider}")
        print(f"Config - Smart LLM Model: {cfg.smart_llm_model}")
        
        # Try with a simpler model first
        response = await create_chat_completion(
            model="gpt-3.5-turbo",  # Use a basic model
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            temperature=0.1,
            llm_provider=cfg.smart_llm_provider,
        )
        
        print(f"✅ GPT Researcher call successful: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ GPT Researcher call failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Testing Intel API endpoint configuration...\n")
    
    # Test 1: Direct API call
    direct_success = await test_direct_api_call()
    
    # Test 2: GPT Researcher call
    gptr_success = await test_gptr_api_call()
    
    print(f"\n=== Results ===")
    print(f"Direct API call: {'✅ Success' if direct_success else '❌ Failed'}")
    print(f"GPT Researcher call: {'✅ Success' if gptr_success else '❌ Failed'}")
    
    if direct_success and gptr_success:
        print("\n🎉 All tests passed! Intel API endpoint is working correctly.")
    elif direct_success and not gptr_success:
        print("\n⚠️ Direct API works but GPT Researcher integration has issues.")
    else:
        print("\n❌ API endpoint issues detected. Check configuration and connectivity.")

if __name__ == "__main__":
    asyncio.run(main())