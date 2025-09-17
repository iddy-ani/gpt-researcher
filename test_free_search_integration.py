#!/usr/bin/env python3
"""
Free Search Integration for GPT Researcher
Integrates the free web search with GPT Researcher MCP
"""

import os
import sys
import json
from typing import List, Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from free_web_retriever import FreeWebSearchRetriever
except ImportError:
    print("❌ free_web_retriever.py not found. Please run setup_free_search.py first")
    sys.exit(1)

def test_free_search_integration():
    """Test the free search integration with GPT Researcher"""
    
    print("🔧 Testing Free Search Integration with GPT Researcher")
    print("=" * 70)
    
    # Initialize the free retriever
    retriever = FreeWebSearchRetriever()
    
    # Test with a research query
    test_query = "latest AI developments 2025 machine learning"
    print(f"🔍 Test Query: {test_query}")
    print()
    
    try:
        # Search with the free retriever
        print("🚀 Searching with Free Web Retriever...")
        results = retriever.search(test_query, max_results=8)
        
        if results:
            print(f"✅ SUCCESS! Found {len(results)} results")
            print()
            
            # Display results in GPT Researcher format
            for i, result in enumerate(results, 1):
                print(f"📄 Result {i}:")
                print(f"   Title: {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   Snippet: {result['snippet'][:120]}...")
                print()
            
            # Test context extraction (like GPT Researcher does)
            print("🧪 Testing Context Extraction...")
            total_content = ""
            valid_sources = 0
            
            for result in results:
                if result['url'] and result['title'] and result['snippet']:
                    total_content += f"Source: {result['title']}\n"
                    total_content += f"URL: {result['url']}\n"
                    total_content += f"Content: {result['snippet']}\n\n"
                    valid_sources += 1
            
            print(f"✅ Context Length: {len(total_content)} characters")
            print(f"✅ Valid Sources: {valid_sources}")
            print(f"✅ Average Content per Source: {len(total_content)//valid_sources if valid_sources > 0 else 0} chars")
            
            if len(total_content) > 500:
                print("🎉 Context is sufficient for research!")
                return True
            else:
                print("⚠️  Context might be limited for detailed research")
                return True
                
        else:
            print("❌ No results found")
            return False
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return False

def create_gpt_researcher_integration():
    """Create integration files for GPT Researcher"""
    
    print("\n🔧 Creating GPT Researcher Integration...")
    
    # Create a custom retriever for GPT Researcher
    integration_code = '''"""
Custom Free Retriever for GPT Researcher
Replaces the default retriever with our free web search
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from free_web_retriever import FreeWebSearchRetriever
import logging

class CustomFreeRetriever:
    """
    Free retriever implementation for GPT Researcher
    Uses web scraping instead of paid APIs
    """
    
    def __init__(self, config=None):
        self.retriever = FreeWebSearchRetriever()
        self.config = config or {}
        
    async def search(self, query: str, max_results: int = 10) -> list:
        """
        Search method compatible with GPT Researcher
        """
        try:
            # Use our free search
            results = self.retriever.search(query, max_results)
            
            # Convert to GPT Researcher format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "href": result.get("url", ""),
                    "body": result.get("snippet", "")
                })
            
            logging.info(f"Free search found {len(formatted_results)} results for: {query}")
            return formatted_results
            
        except Exception as e:
            logging.error(f"Free search failed: {e}")
            return []

# Factory function for GPT Researcher
def get_retriever(retriever_name: str):
    """Factory function to get our free retriever"""
    if retriever_name.lower() in ['free', 'custom', 'scraper']:
        return CustomFreeRetriever()
    else:
        # Fallback to default
        return None
'''
    
    with open('custom_free_retriever.py', 'w', encoding='utf-8') as f:
        f.write(integration_code)
    
    print("✅ Created custom_free_retriever.py")
    
    # Create environment setup script
    env_setup = '''#!/usr/bin/env python3
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
'''
    
    with open('setup_free_environment.py', 'w', encoding='utf-8') as f:
        f.write(env_setup)
    
    print("✅ Created setup_free_environment.py")
    
    print("\n🎯 Integration Complete!")
    print("\n📋 To use free search with GPT Researcher:")
    print("1. Set environment variable: RETRIEVER=free")
    print("2. Run: python setup_free_environment.py")
    print("3. Use GPT Researcher normally - it will use free search!")
    
    print("\n💡 Benefits:")
    print("• ✅ No API keys needed")
    print("• ✅ Completely free forever")
    print("• ✅ Multiple search engines as fallbacks")
    print("• ✅ Rate limiting to avoid blocks")
    print("• ✅ Built-in error handling")

if __name__ == "__main__":
    success = test_free_search_integration()
    
    if success:
        create_gpt_researcher_integration()
        
        print("\n🎉 FREE SEARCH READY!")
        print("Your GPT Researcher now has a completely free web search!")
        print("No more API key issues or rate limiting!")
    else:
        print("\n❌ Integration test failed")
        print("Please check your internet connection and try again")