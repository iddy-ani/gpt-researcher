#!/usr/bin/env python3
"""
Test script to verify that GPT Researcher is using the correct API endpoint
"""
import asyncio
import os
from gpt_researcher.utils.llm import create_chat_completion
from gpt_researcher.config.config import Config

async def test_endpoint():
    """Test that the LLM is using the correct endpoint"""
    print("Testing GPT Researcher with Intel's internal API endpoint...")
    print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'Not set')}")
    print(f"EGPT_API_KEY: {'Set' if os.getenv('EGPT_API_KEY') else 'Not set'}")
    
    # Initialize config
    cfg = Config()
    print(f"Smart LLM Provider: {cfg.smart_llm_provider}")
    print(f"Smart LLM Model: {cfg.smart_llm_model}")
    
    try:
        # Test with the default configured model
        response = await create_chat_completion(
            model=cfg.smart_llm_model,  # Test the default smart model (gpt-5)
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from Intel API!' if you can read this."},
            ],
            temperature=0.1,
            llm_provider=cfg.smart_llm_provider,
        )
        
        print(f"✅ Success! Response: {response}")
        print("🎉 The API endpoint is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This might indicate an issue with the API endpoint or authentication.")

if __name__ == "__main__":
    asyncio.run(test_endpoint())