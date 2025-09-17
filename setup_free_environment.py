#!/usr/bin/env python3
"""
Environment Setup for Free Search
Sets up environment variables for free search
"""

import os

def setup_free_search_environment():
    """Setup environment for free search"""
    
    print("🔧 Setting up Free Search Environment")
    print("=" * 50)
    
    # Set retriever to custom
    os.environ['RETRIEVER'] = 'free'
    
    # Disable other retrievers that might interfere
    if 'BING_API_KEY' in os.environ:
        print("📝 Note: BING_API_KEY is set but will be ignored")
    
    if 'TAVILY_API_KEY' in os.environ:
        print("📝 Note: TAVILY_API_KEY is set but will be ignored")
    
    print("✅ Environment configured for FREE search")
    print("✅ RETRIEVER=free")
    print("✅ No API keys required!")
    
    return True

if __name__ == "__main__":
    setup_free_search_environment()
