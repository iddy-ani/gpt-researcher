#!/usr/bin/env python3
"""
Quick end-to-end test to verify everything works with EGPT_API_KEY
"""
import asyncio
import sys
import os

# Add the gpt_researcher directory to the path
sys.path.append('.')

from gpt_researcher import GPTResearcher

async def test_egpt_end_to_end():
    """Test GPT Researcher end-to-end with EGPT_API_KEY"""
    print("=== End-to-End Test with EGPT_API_KEY ===")
    
    # Check environment
    egpt_key = os.getenv('EGPT_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    
    print(f"🔑 EGPT_API_KEY: {'Set' if egpt_key else 'Not set'}")
    print(f"🌐 Base URL: {base_url}")
    
    if egpt_key:
        print(f"📊 API Key (first 10): {egpt_key[:10]}...")
    
    query = "What are the key advantages of edge computing?"
    
    try:
        researcher = GPTResearcher(query=query, report_type="research_report")
        
        print(f"\n🚀 Starting research: {query}")
        
        # Conduct research
        research_result = await researcher.conduct_research()
        print(f"📋 Research completed! Found {len(research_result)} sources")
        
        # Generate report  
        report = await researcher.write_report()
        print(f"📝 Report generated! Length: {len(report)} characters")
        
        # Show preview
        print(f"\n--- Report Preview ---")
        print(report[:300] + "..." if len(report) > 300 else report)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_egpt_end_to_end())
    
    if success:
        print(f"\n🎉 End-to-end test successful with EGPT_API_KEY!")
    else:
        print(f"\n🔧 End-to-end test failed.")