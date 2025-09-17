#!/usr/bin/env python3
"""
Direct test of our custom retriever to see import and search behavior
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

def test_custom_retriever():
    print("🔍 Testing CustomRetriever directly...")
    
    try:
        from gpt_researcher.retrievers.custom.custom import CustomRetriever
        print("✅ CustomRetriever imported successfully")
        
        retriever = CustomRetriever("artificial intelligence 2025 trends")
        print(f"✅ CustomRetriever initialized, available: {retriever.available}")
        
        print("🔎 Performing search...")
        results = retriever.search(max_results=3)
        
        print(f"📊 Search results: {len(results) if results else 0} items")
        if results:
            for i, result in enumerate(results[:2]):
                print(f"  {i+1}. URL: {result.get('href', 'N/A')}")
                print(f"     Content: {result.get('body', 'N/A')[:100]}...")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_custom_retriever()