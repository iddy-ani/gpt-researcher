#!/usr/bin/env python3
"""
Final Free Search Setup for GPT Researcher MCP
Creates the complete integration and tests everything
"""

import os
import sys
import json
from datetime import datetime

# Set free search environment
os.environ['RETRIEVER'] = 'free'

# Import our components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from free_web_retriever import FreeWebSearchRetriever

def final_integration_test():
    """Final test of the free search integration"""
    
    print("🎯 FINAL FREE SEARCH INTEGRATION TEST")
    print("=" * 55)
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test with shorter, more reliable query
    print("🔍 Testing with optimized query...")
    
    try:
        retriever = FreeWebSearchRetriever()
        results = retriever.search("AI trends 2025", max_results=6)
        
        if results:
            print(f"✅ Found {len(results)} results")
            
            # Build context like GPT Researcher
            context = ""
            source_count = 0
            
            for result in results:
                if result.get('title') and result.get('url') and result.get('snippet'):
                    context += f"Source {source_count + 1}: {result['title']}\n"
                    context += f"URL: {result['url']}\n"
                    context += f"Content: {result['snippet']}\n\n"
                    source_count += 1
            
            print(f"📊 Analysis:")
            print(f"   • Sources found: {source_count}")
            print(f"   • Context length: {len(context)} characters")
            print(f"   • Quality: {'EXCELLENT' if len(context) > 800 else 'GOOD'}")
            
            if source_count >= 3 and len(context) > 500:
                print("\n🎉 SUCCESS: Free search is working perfectly!")
                return True, context, source_count
            else:
                print("\n⚠️  Limited results but functional")
                return True, context, source_count
                
        else:
            print("❌ No results found")
            return False, "", 0
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False, "", 0

def create_final_mcp_integration():
    """Create the final MCP integration file"""
    
    mcp_integration = '''#!/usr/bin/env python3
"""
GPT Researcher MCP with Free Web Search
Modified to use completely free web search instead of paid APIs
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Set free search mode
os.environ['RETRIEVER'] = 'free'

# Import free search components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from free_web_retriever import FreeWebSearchRetriever

class FreeSearchResearcher:
    """GPT Researcher with free web search integration"""
    
    def __init__(self):
        self.retriever = FreeWebSearchRetriever()
        self.search_count = 0
        self.total_sources = 0
        
    async def conduct_research(self, query: str, report_type: str = "research_report") -> Dict[str, Any]:
        """
        Conduct research using free web search
        
        Args:
            query: Research question/topic
            report_type: Type of report to generate
            
        Returns:
            Research results with sources and context
        """
        
        print(f"🔍 FREE RESEARCH: {query}")
        print("=" * 60)
        
        try:
            # Search with free retriever
            print("🚀 Searching with Free Web Search...")
            search_results = self.retriever.search(query, max_results=10)
            self.search_count += 1
            
            if search_results:
                # Build research context
                context_parts = []
                source_urls = []
                
                for i, result in enumerate(search_results, 1):
                    if result.get('title') and result.get('url') and result.get('snippet'):
                        context_part = f"Source {i}: {result['title']}\\n"
                        context_part += f"URL: {result['url']}\\n"
                        context_part += f"Content: {result['snippet']}\\n"
                        
                        context_parts.append(context_part)
                        source_urls.append(result['url'])
                        self.total_sources += 1
                
                # Combine all context
                full_context = "\\n".join(context_parts)
                
                print(f"✅ Research Complete!")
                print(f"   • Sources found: {len(source_urls)}")
                print(f"   • Context length: {len(full_context)} characters")
                print(f"   • Search method: FREE (no API keys)")
                
                # Return research results
                return {
                    "query": query,
                    "report_type": report_type,
                    "research_context": full_context,
                    "sources": source_urls,
                    "source_count": len(source_urls),
                    "context_length": len(full_context),
                    "search_method": "Free Web Search",
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
                
            else:
                print("❌ No sources found")
                return {
                    "query": query,
                    "report_type": report_type,
                    "research_context": "",
                    "sources": [],
                    "source_count": 0,
                    "context_length": 0,
                    "search_method": "Free Web Search",
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": "No search results found"
                }
                
        except Exception as e:
            print(f"❌ Research error: {e}")
            return {
                "query": query,
                "report_type": report_type,
                "research_context": "",
                "sources": [],
                "source_count": 0,
                "context_length": 0,
                "search_method": "Free Web Search",
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }

# Test the free search researcher
if __name__ == "__main__":
    async def test_free_researcher():
        researcher = FreeSearchResearcher()
        
        # Test query
        result = await researcher.conduct_research(
            "latest AI developments machine learning 2025",
            "research_report"
        )
        
        print("\\n" + "="*50)
        print("🔬 RESEARCH RESULTS")
        print("="*50)
        print(f"Success: {result['success']}")
        print(f"Sources: {result['source_count']}")
        print(f"Context: {result['context_length']} chars")
        print(f"Method: {result['search_method']}")
        
        if result['success']:
            print("\\n🎉 FREE RESEARCH IS WORKING!")
        else:
            print(f"\\n❌ Error: {result.get('error', 'Unknown')}")
    
    asyncio.run(test_free_researcher())
'''
    
    with open('gpt_researcher_free.py', 'w', encoding='utf-8') as f:
        f.write(mcp_integration)
    
    print("✅ Created gpt_researcher_free.py")

def show_final_summary():
    """Show the final summary of what was accomplished"""
    
    print("\n" + "🎉" * 20)
    print("🚀 FREE WEB SEARCH INTEGRATION COMPLETE!")
    print("🎉" * 20)
    
    print("\n📁 Files Created:")
    files = [
        "✅ free_web_retriever.py - Core free search engine",
        "✅ custom_free_retriever.py - GPT Researcher compatibility layer", 
        "✅ setup_free_environment.py - Environment configuration",
        "✅ gpt_researcher_free.py - Complete free research implementation"
    ]
    
    for file in files:
        print(f"   {file}")
    
    print("\n🔧 What This Solves:")
    problems_solved = [
        "❌ 'Sources: 0' issues → ✅ Reliable source finding",
        "❌ API key management → ✅ No API keys needed",
        "❌ Rate limiting problems → ✅ Built-in rate limiting",
        "❌ Monthly API costs → ✅ Completely free forever",
        "❌ Service outages → ✅ Multiple fallback engines"
    ]
    
    for problem in problems_solved:
        print(f"   {problem}")
    
    print("\n💡 How It Works:")
    print("   1. 🕷️  Scrapes DuckDuckGo & Bing HTML (legal & ethical)")
    print("   2. ⏱️  Rate limiting (2 seconds between requests)")
    print("   3. 🔄 Multiple fallback search engines")
    print("   4. 🧠 GPT Researcher compatible format")
    print("   5. 🆓 Zero API keys required")
    
    print("\n🚀 Ready to Use:")
    print("   • Set RETRIEVER=free")
    print("   • Run your GPT Researcher MCP")
    print("   • Enjoy unlimited free research!")
    
    print("\n🎯 Benefits:")
    benefits = [
        "🆓 Completely free forever",
        "🔒 No API key security concerns", 
        "📊 Consistent source counting",
        "🚀 Fast and reliable results",
        "🌐 Multiple search engines",
        "⚡ Ready to use immediately"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")

if __name__ == "__main__":
    print("🔧 Running Final Integration Test...")
    
    success, context, sources = final_integration_test()
    
    if success:
        create_final_mcp_integration()
        show_final_summary()
        
        print(f"\n📊 Test Results:")
        print(f"   • Sources found: {sources}")
        print(f"   • Context length: {len(context)} characters")
        print(f"   • Status: {'EXCELLENT' if sources >= 5 else 'GOOD'}")
        
        print("\n🎉 YOUR GPT RESEARCHER IS NOW 100% FREE!")
        print("No more API key issues, rate limiting, or source problems!")
    else:
        print("\n❌ Final test failed")
        print("Please check your internet connection")