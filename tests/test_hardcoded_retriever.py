#!/usr/bin/env python3
"""
Test script to verify hardcoded retriever configuration
"""
import sys
import os

# Add the gpt_researcher directory to the path
sys.path.append('.')

from gpt_researcher.config.config import Config

def test_hardcoded_retriever():
    """Test that retriever is hardcoded to DuckDuckGo regardless of environment variables"""
    print("=== Hardcoded Retriever Configuration Test ===")
    
    # Test 1: No environment variable set
    if 'RETRIEVER' in os.environ:
        del os.environ['RETRIEVER']
    
    config = Config()
    print(f"✅ Test 1 - No env var: RETRIEVER = {config.retrievers}")
    assert 'duckduckgo' in config.retrievers, f"Expected 'duckduckgo' in retrievers, got {config.retrievers}"
    
    # Test 2: Environment variable set to different value (should be ignored)
    os.environ['RETRIEVER'] = 'tavily'
    config2 = Config()
    print(f"✅ Test 2 - Env var set to 'tavily': RETRIEVER = {config2.retrievers}")
    assert 'duckduckgo' in config2.retrievers, f"Expected 'duckduckgo' (env var should be ignored), got {config2.retrievers}"
    
    # Test 3: Environment variable set to another value (should be ignored)
    os.environ['RETRIEVER'] = 'bing'
    config3 = Config()
    print(f"✅ Test 3 - Env var set to 'bing': RETRIEVER = {config3.retrievers}")
    assert 'duckduckgo' in config3.retrievers, f"Expected 'duckduckgo' (env var should be ignored), got {config3.retrievers}"
    
    # Clean up
    if 'RETRIEVER' in os.environ:
        del os.environ['RETRIEVER']
    
    print(f"\n🎉 All tests passed! Retriever is hardcoded to DuckDuckGo and ignores environment variables.")
    return True

if __name__ == "__main__":
    try:
        success = test_hardcoded_retriever()
        if success:
            print(f"\n✅ Retriever configuration is successfully hardcoded!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()