#!/usr/bin/env python3
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
                        context_part = f"Source {i}: {result['title']}\n"
                        context_part += f"URL: {result['url']}\n"
                        context_part += f"Content: {result['snippet']}\n"
                        
                        context_parts.append(context_part)
                        source_urls.append(result['url'])
                        self.total_sources += 1
                
                # Combine all context
                full_context = "\n".join(context_parts)
                
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
        
        print("\n" + "="*50)
        print("🔬 RESEARCH RESULTS")
        print("="*50)
        print(f"Success: {result['success']}")
        print(f"Sources: {result['source_count']}")
        print(f"Context: {result['context_length']} chars")
        print(f"Method: {result['search_method']}")
        
        if result['success']:
            print("\n🎉 FREE RESEARCH IS WORKING!")
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown')}")
    
    asyncio.run(test_free_researcher())
