#!/usr/bin/env python3
"""
Test script to check retriever configuration
"""
import os
import asyncio

async def test_retriever_config():
    """Test the current retriever configuration"""
    print("=== Retriever Configuration Test ===")
    
    retriever = os.getenv('RETRIEVER', 'tavily')  # Default to tavily
    print(f"Current RETRIEVER: {retriever}")
    
    if retriever == 'bing':
        bing_api_key = os.getenv('BING_API_KEY')
        if bing_api_key:
            print(f"✅ BING_API_KEY: Set (Key: {bing_api_key[:10]}...)")
            print("🎉 Bing retriever should work!")
        else:
            print("❌ BING_API_KEY: Not set")
            print("⚠️  You need to set BING_API_KEY environment variable")
            print("   Or change RETRIEVER to 'duckduckgo' (no API key needed)")
    
    elif retriever == 'tavily':
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            print(f"✅ TAVILY_API_KEY: Set (Key: {tavily_api_key[:10]}...)")
            print("🎉 Tavily retriever should work!")
        else:
            print("❌ TAVILY_API_KEY: Not set")
            print("⚠️  You need to set TAVILY_API_KEY environment variable")
    
    elif retriever == 'duckduckgo':
        print("✅ DuckDuckGo retriever selected - no API key needed!")
        print("🎉 DuckDuckGo retriever should work!")
    
    else:
        print(f"ℹ️  Retriever '{retriever}' selected")
        print("   Make sure you have the required API keys for this retriever")
    
    print(f"\n=== Other Environment Variables ===")
    openai_base_url = os.getenv('OPENAI_BASE_URL')
    print(f"OPENAI_BASE_URL: {openai_base_url}")
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key:
        print(f"OPENAI_API_KEY: Set (Key: {openai_api_key[:10]}...)")
    else:
        print("OPENAI_API_KEY: Not set")

if __name__ == "__main__":
    asyncio.run(test_retriever_config())