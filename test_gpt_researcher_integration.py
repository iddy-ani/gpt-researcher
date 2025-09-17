#!/usr/bin/env python3
"""
Test if GPT Researcher accepts our custom retriever results
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

def test_gpt_researcher_integration():
    print("🔍 Testing GPT Researcher with our custom retriever...")
    
    try:
        # Set environment to use custom retriever
        os.environ['RETRIEVER'] = 'custom'
        os.environ['EGPT_API_KEY'] = 'pak_CG2pyExb0R9eVSbQefJbcuH7nBr8T2KZp1'
        
        from gpt_researcher import GPTResearcher
        print("✅ GPTResearcher imported")
        
        # Create a researcher instance
        researcher = GPTResearcher(
            query="AI trends 2025",
            report_type="quick_research"
        )
        print("✅ GPTResearcher initialized")
        
        # Check what retriever it's using
        print(f"📋 Configured retriever: {researcher.cfg.retriever}")
        
        # Try to get sources
        print("🔎 Testing source retrieval...")
        sources = researcher.retrieve_sources()
        print(f"📊 Sources retrieved: {len(sources) if sources else 0}")
        
        if sources:
            for i, source in enumerate(sources[:2]):
                print(f"  {i+1}. URL: {source.get('url', 'N/A')}")
                print(f"     Raw content length: {len(source.get('raw_content', ''))}")
        else:
            print("❌ No sources retrieved by GPT Researcher")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gpt_researcher_integration()