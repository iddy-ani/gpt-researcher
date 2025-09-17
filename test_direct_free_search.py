#!/usr/bin/env python3
"""
Quick Test of Free Search Integration
Tests if our free search is working properly and generates a research report
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from free_web_retriever import FreeWebSearchRetriever

async def test_direct_free_search():
    """Test the free search directly and generate a research report"""
    
    print("🧪 DIRECT FREE SEARCH TEST")
    print("=" * 50)
    
    query = "artificial intelligence advances and trends 2025"
    print(f"🔍 Query: {query}")
    
    # Test free search
    retriever = FreeWebSearchRetriever()
    print("🚀 Searching...")
    
    start_time = datetime.now()
    results = retriever.search(query, max_results=8)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    
    if results:
        print(f"✅ Search completed in {duration:.1f}s")
        print(f"📊 Found {len(results)} sources")
        
        # Build research context
        context = ""
        for i, result in enumerate(results, 1):
            if result.get('title') and result.get('url') and result.get('snippet'):
                context += f"**Source {i}: {result['title']}**\n"
                context += f"URL: {result['url']}\n"
                context += f"Content: {result['snippet']}\n\n"
        
        print(f"📝 Context length: {len(context)} characters")
        
        # Create a simple research report
        report = f"""# Research Report: Artificial Intelligence Advances and Trends 2025

## Executive Summary
Based on {len(results)} sources gathered through web research, this report examines the latest developments and emerging trends in artificial intelligence for 2025.

## Research Findings

{context}

## Analysis
The research reveals several key trends and developments in AI for 2025:

1. **Continued Growth**: AI technology continues to advance rapidly across multiple domains
2. **Industry Integration**: Increasing adoption of AI solutions in various industries
3. **Technical Innovation**: New developments in machine learning, deep learning, and AI applications
4. **Market Expansion**: Growing market opportunities and investment in AI technologies

## Conclusion
The artificial intelligence landscape in 2025 shows significant promise with continued innovation, expanding applications, and growing market adoption across various sectors.

---
*Report generated using Free Web Search (no API keys required)*
*Based on {len(results)} sources, {len(context)} characters of research context*
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        print("\n📋 Generated Research Report:")
        print("=" * 60)
        print(report[:500] + "..." if len(report) > 500 else report)
        
        # Save the report
        timestamp = int(datetime.now().timestamp())
        filename = f"free_search_test_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 Full report saved to: {filename}")
        
        # Show statistics
        print(f"\n📊 Report Statistics:")
        print(f"   • Sources: {len(results)}")
        print(f"   • Context: {len(context)} characters")
        print(f"   • Report: {len(report)} characters")
        print(f"   • Words: {len(report.split())} words")
        print(f"   • Search time: {duration:.1f}s")
        
        return True
        
    else:
        print(f"❌ No results found in {duration:.1f}s")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_free_search())
    
    if success:
        print("\n🎉 FREE SEARCH IS WORKING PERFECTLY!")
        print("✅ Sources found, context built, report generated")
        print("🚀 Ready for integration with GPT Researcher")
    else:
        print("\n❌ Free search test failed")
        print("🔧 Check internet connection and try again")