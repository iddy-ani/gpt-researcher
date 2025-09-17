"""
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
