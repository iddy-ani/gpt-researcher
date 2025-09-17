#!/usr/bin/env python3
"""
Full end-to-end test of GPT Researcher with Intel API and Azure embeddings
"""
import asyncio
import sys
import os

# Add the gpt_researcher directory to the path
sys.path.append('.')

from gpt_researcher import GPTResearcher

async def main():
    """Run a complete research task using Intel API and Azure embeddings"""
    print("=== Full GPT Researcher End-to-End Test ===")
    print("🔧 Using Intel's internal API for LLM")
    print("🔧 Using Azure OpenAI for embeddings")
    print("🔧 Using DuckDuckGo for search")
    
    query = "What are the main benefits of renewable energy?"
    report_type = "research_report"
    
    print(f"\n📝 Research Query: {query}")
    print(f"📊 Report Type: {report_type}")
    
    try:
        # Initialize researcher
        researcher = GPTResearcher(query=query, report_type=report_type)
        
        print(f"\n🚀 Starting research...")
        
        # Conduct research
        research_result = await researcher.conduct_research()
        
        print(f"\n📋 Research completed!")
        print(f"📊 Sources found: {len(research_result) if research_result else 0}")
        
        # Generate report
        report = await researcher.write_report()
        
        print(f"\n📝 Report generated!")
        print(f"📊 Report length: {len(report)} characters")
        print(f"\n--- Report Preview (first 500 chars) ---")
        print(report[:500] + "..." if len(report) > 500 else report)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during research: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print(f"\n🎉 GPT Researcher is working correctly with Intel API and Azure embeddings!")
    else:
        print(f"\n🔧 GPT Researcher needs additional configuration.")