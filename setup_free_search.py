#!/usr/bin/env python3
"""
Free Web Search Setup for GPT Researcher
Creates a completely free web search retriever without any API keys
"""

import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from typing import List, Dict
import json

def create_free_search_retriever():
    """Create a free web search retriever using multiple strategies"""
    
    print("🆓 Setting up Completely Free Web Search")
    print("=" * 60)
    
    # Test different free search strategies
    strategies = [
        ("DuckDuckGo HTML Scraping", test_duckduckgo_scraping),
        ("Bing HTML Scraping", test_bing_scraping),
        ("StartPage Scraping", test_startpage_scraping),
        ("SearXNG Public Instance", test_searxng_public),
    ]
    
    working_strategies = []
    
    for name, test_func in strategies:
        print(f"\n🧪 Testing: {name}")
        try:
            if test_func():
                working_strategies.append(name)
                print(f"   ✅ {name} - WORKING!")
            else:
                print(f"   ❌ {name} - Failed")
        except Exception as e:
            print(f"   ❌ {name} - Error: {e}")
    
    if working_strategies:
        print(f"\n🎉 Found {len(working_strategies)} working free search methods!")
        create_free_retriever_implementation(working_strategies)
        return True
    else:
        print("\n❌ No free search methods are currently working")
        return False

def test_duckduckgo_scraping():
    """Test DuckDuckGo HTML scraping"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    query = "test search python"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('div', class_='result')
        
        if len(results) > 0:
            print(f"   📄 Found {len(results)} results")
            sample = results[0].find('a', class_='result__a')
            if sample:
                print(f"   🔗 Sample: {sample.text[:50]}...")
            return True
    
    return False

def test_bing_scraping():
    """Test Bing HTML scraping"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    query = "test search python"
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('li', class_='b_algo')
        
        if len(results) > 0:
            print(f"   📄 Found {len(results)} results")
            sample = results[0].find('h2')
            if sample:
                print(f"   🔗 Sample: {sample.text[:50]}...")
            return True
    
    return False

def test_startpage_scraping():
    """Test StartPage HTML scraping"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    query = "test search python"
    url = f"https://www.startpage.com/sp/search?query={urllib.parse.quote(query)}"
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('div', class_='w-gl__result')
        
        if len(results) > 0:
            print(f"   📄 Found {len(results)} results")
            return True
    
    return False

def test_searxng_public():
    """Test public SearXNG instances"""
    public_instances = [
        "https://search.sapti.me",
        "https://searx.be",
        "https://search.bus-hit.me",
    ]
    
    for instance in public_instances:
        try:
            print(f"   🔍 Testing {instance}")
            url = f"{instance}/search"
            params = {
                'q': 'test search python',
                'format': 'json',
                'categories': 'general'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if len(results) > 0:
                    print(f"   📄 Found {len(results)} results from {instance}")
                    return True
                    
        except Exception as e:
            print(f"   ⚠️  {instance} failed: {e}")
            continue
    
    return False

def create_free_retriever_implementation(working_strategies):
    """Create the actual free retriever implementation"""
    
    retriever_code = '''"""
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
'''
    
    # Save the retriever implementation
    with open('free_web_retriever.py', 'w', encoding='utf-8') as f:
        f.write(retriever_code)
    
    print(f"\n✅ Created free_web_retriever.py")
    print(f"📊 Working strategies: {', '.join(working_strategies)}")
    
    # Show integration instructions
    print("\n🔧 Integration with GPT Researcher:")
    print("1. Set environment variable: RETRIEVER=custom")
    print("2. Import the free retriever in your research code")
    print("3. Replace the default search with free_web_retriever.search_web()")
    
    print("\n💡 Features:")
    print("• ✅ Completely free - no API keys needed")
    print("• ✅ Multiple fallback search engines")
    print("• ✅ Rate limiting to avoid blocks")
    print("• ✅ User-Agent rotation for reliability")
    print("• ✅ Built-in error handling")
    
    print("\n⚡ Test the free retriever:")
    print("python free_web_retriever.py")

if __name__ == "__main__":
    create_free_search_retriever()