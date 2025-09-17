"""
Free Web Search Retriever for GPT Researcher
No API keys required - uses web scraping and public search instances
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from typing import List, Dict
import logging

class FreeWebSearchRetriever:
    """Free web search retriever that doesn't require API keys"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 2  # seconds between requests
        
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search the web using free methods
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, snippet
        """
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_request_time < self.min_delay:
            time.sleep(self.min_delay - (current_time - self.last_request_time))
        
        self.last_request_time = time.time()
        
        # Try different search methods
        methods = [
            self._search_duckduckgo,
            self._search_bing,
            self._search_startpage,
        ]
        
        for method in methods:
            try:
                results = method(query, max_results)
                if results:
                    logging.info(f"Free search successful with {method.__name__}")
                    return results
            except Exception as e:
                logging.warning(f"Search method {method.__name__} failed: {e}")
                continue
        
        return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """Search using DuckDuckGo HTML"""
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        for result_div in soup.find_all('div', class_='result')[:max_results]:
            title_link = result_div.find('a', class_='result__a')
            snippet_div = result_div.find('a', class_='result__snippet')
            
            if title_link:
                title = title_link.text.strip()
                url = title_link.get('href', '')
                snippet = snippet_div.text.strip() if snippet_div else ''
                
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
        
        return results
    
    def _search_bing(self, query: str, max_results: int) -> List[Dict]:
        """Search using Bing HTML"""
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        for result_li in soup.find_all('li', class_='b_algo')[:max_results]:
            title_h2 = result_li.find('h2')
            url_a = title_h2.find('a') if title_h2 else None
            snippet_p = result_li.find('p')
            
            if url_a:
                title = title_h2.text.strip()
                url = url_a.get('href', '')
                snippet = snippet_p.text.strip() if snippet_p else ''
                
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
        
        return results
    
    def _search_startpage(self, query: str, max_results: int) -> List[Dict]:
        """Search using StartPage"""
        url = f"https://www.startpage.com/sp/search?query={urllib.parse.quote(query)}"
        
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        for result_div in soup.find_all('div', class_='w-gl__result')[:max_results]:
            title_a = result_div.find('a', class_='w-gl__result-title')
            snippet_p = result_div.find('p', class_='w-gl__description')
            
            if title_a:
                title = title_a.text.strip()
                url = title_a.get('href', '')
                snippet = snippet_p.text.strip() if snippet_p else ''
                
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
        
        return results

# For GPT Researcher integration
def search_web(query: str, max_results: int = 10) -> List[Dict]:
    """
    Free web search function for GPT Researcher
    """
    retriever = FreeWebSearchRetriever()
    return retriever.search(query, max_results)

if __name__ == "__main__":
    # Test the free search
    retriever = FreeWebSearchRetriever()
    results = retriever.search("artificial intelligence latest developments", 5)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   {result['snippet'][:100]}...")
        print()
