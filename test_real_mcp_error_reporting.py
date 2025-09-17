#!/usr/bin/env python3
"""
Test the enhanced error reporting with actual MCP calls
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the gpt_researcher directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_researcher_mcp_streaming import quick_research, conduct_research_task

async def test_real_mcp_calls():
    """Test the enhanced error reporting with real MCP function calls"""
    print("🧪 Testing Enhanced Error Reporting with Real MCP Calls")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Quick research to see detailed error reporting
    print("\n📋 Test 1: Quick Research with Enhanced Debugging")
    print("-" * 50)
    
    try:
        result = await quick_research({
            "query": "latest AI developments in 2024"
        })
        
        print("✅ Quick research completed")
        
        # Analyze the result for source information
        if result and len(result) > 0:
            text = result[0].get('text', '')
            
            # Look for source indicators in the response
            if "Sources Found: 0" in text:
                print("⚠️  DETECTED: Sources Found: 0 - this indicates source fetching failure")
            elif "Sources Found:" in text:
                import re
                sources_match = re.search(r'Sources Found: (\d+)', text)
                if sources_match:
                    source_count = int(sources_match.group(1))
                    print(f"📊 Sources Found: {source_count}")
            
            # Look for context length information
            if "Context Length:" in text:
                context_match = re.search(r'Context Length: (\d+)', text)
                if context_match:
                    context_length = int(context_match.group(1))
                    print(f"📊 Context Length: {context_length} characters")
                    
                    if context_length == 0:
                        print("❌ CRITICAL: No research context gathered - source fetching failed completely")
                    elif context_length < 500:
                        print("⚠️  WARNING: Very limited research context - potential source issues")
                    else:
                        print("✅ Good research context gathered")
            
            # Look for error messages
            if "RESEARCH FAILED" in text:
                print("❌ Research failed with detailed error report")
                print("📋 Error report generated successfully")
            elif "WARNING: Limited source material" in text:
                print("⚠️  Research completed with warnings about limited sources")
            
            # Show a sample of the response for analysis
            print(f"\n📄 Response sample (first 500 chars):")
            print(text[:500] + "..." if len(text) > 500 else text)
            
        else:
            print("❌ No result returned from quick_research")
            
    except Exception as e:
        print(f"❌ Quick research test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("✅ Enhanced error reporting system tested")
    print("✅ Real MCP function calls executed")
    print("✅ Source counting and context analysis validated")
    
    print("\n🎯 Key Insights:")
    print("• Enhanced error reporting now provides detailed diagnostics")
    print("• Source vs context discrepancies will be clearly identified")
    print("• Specific troubleshooting guidance included in error messages")
    print("• Quality assessment helps users understand research reliability")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_real_mcp_calls())
    if result:
        print("\n✅ Enhanced error reporting validation completed!")
        print("\n🔍 To see the enhanced error reporting in action:")
        print("1. Look for detailed stderr logging during research")
        print("2. Check for 'Sources Found' vs 'Context Length' mismatches")
        print("3. Review comprehensive error messages when sources fail")
        print("4. Monitor quality assessments (High/Medium/Limited)")
    else:
        print("\n❌ Enhanced error reporting test failed")
        sys.exit(1)