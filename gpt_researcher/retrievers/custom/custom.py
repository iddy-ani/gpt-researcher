from typing import Any, Dict, List, Optional
import requests
import os
import sys


class CustomRetriever:
    """
    Free Web Search Retriever - No API keys required
    Uses web scraping for completely free search
    """

    def __init__(self, query: str, query_domains=None):
        self.query = query
        self.query_domains = query_domains
        
        # Try to import our free search
        try:
            # Add multiple potential directories to path to find free_web_retriever
            import_paths = [
                os.getcwd(),
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),  # Project root
                os.path.expanduser("~/source/repos/gpt-researcher"),  # Windows user path
                "c:/Users/ianimash/source/repos/gpt-researcher"  # Full absolute path
            ]
            
            for path in import_paths:
                if path and os.path.exists(path) and path not in sys.path:
                    sys.path.insert(0, path)
                    print(f"📂 Added to path: {path}", file=sys.stderr)
            
            from free_web_retriever import FreeWebSearchRetriever
            self.free_retriever = FreeWebSearchRetriever()
            self.available = True
            print("✅ Free web search retriever loaded successfully", file=sys.stderr)
        except ImportError as e:
            self.available = False
            print(f"⚠️ Free web search not available: {e}", file=sys.stderr)
            print(f"📍 Current working directory: {os.getcwd()}", file=sys.stderr)
            print(f"📍 Python path: {sys.path[:3]}...", file=sys.stderr)
            # Fallback to original custom retriever behavior
            self.endpoint = os.getenv('RETRIEVER_ENDPOINT')
            if not self.endpoint:
                raise ValueError("RETRIEVER_ENDPOINT environment variable not set and free search not available")
            self.params = self._populate_params()

    def _populate_params(self) -> Dict[str, Any]:
        """
        Populates parameters from environment variables prefixed with 'RETRIEVER_ARG_'
        """
        return {
            key[len('RETRIEVER_ARG_'):].lower(): value
            for key, value in os.environ.items()
            if key.startswith('RETRIEVER_ARG_')
        }

    def search(self, max_results: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Performs the search using free web search if available, otherwise falls back to custom endpoint.

        :param max_results: Maximum number of results to return
        :return: JSON response in the format expected by GPT Researcher:
            [
              {
                "url": "http://example.com/page1",
                "raw_content": "Content of page 1"
              },
              {
                "url": "http://example.com/page2", 
                "raw_content": "Content of page 2"
              }
            ]
        """
        
        if self.available:
            # Use our free web search
            try:
                print(f"🆓 FREE SEARCH: {self.query}", file=sys.stderr)
                results = self.free_retriever.search(self.query, max_results=max_results)
                
                if results:
                    print(f"✅ Free search found {len(results)} results", file=sys.stderr)
                    
                    # Convert to GPT Researcher format
                    formatted_results = []
                    for result in results:
                        if result.get('title') and result.get('url') and result.get('snippet'):
                            formatted_entry = {
                                "href": result['url'],  # Use 'href' instead of 'url'
                                "body": f"{result['title']}\n\n{result['snippet']}"  # Use 'body' instead of 'raw_content'
                            }
                            formatted_results.append(formatted_entry)
                            print(f"📝 Formatted result: href={formatted_entry['href'][:50]}..., body_len={len(formatted_entry['body'])}", file=sys.stderr)
                    
                    print(f"🎯 Returning {len(formatted_results)} formatted results to GPT Researcher", file=sys.stderr)
                    return formatted_results
                else:
                    print("❌ Free search returned no results", file=sys.stderr)
                    return []
                    
            except Exception as e:
                print(f"❌ Free search error: {e}", file=sys.stderr)
                return []
        
        else:
            # Fallback to original custom retriever
            try:
                response = requests.get(self.endpoint, params={**self.params, 'query': self.query})
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"Failed to retrieve search results: {e}")
                return None