#!/usr/bin/env python3
"""
Test script to verify Grounding with Bing Search API key
"""
import os
import requests
import json

def test_bing_api():
    """Test the Bing API key"""
    print("=== Testing Grounding with Bing Search API ===")
    
    api_key = os.getenv('BING_API_KEY')
    if not api_key:
        print("❌ BING_API_KEY environment variable not set")
        print("Please run: export BING_API_KEY=your_api_key")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test the standard Bing Web Search API endpoint
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Content-Type': 'application/json'
    }
    params = {
        "responseFilter": "Webpages",
        "q": "test query",
        "count": 3,
        "setLang": "en-US",
        "textDecorations": False,
        "textFormat": "HTML",
        "safeSearch": "Strict"
    }
    
    try:
        print(f"🔍 Testing API endpoint: {url}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'webPages' in data and 'value' in data['webPages']:
                results_count = len(data['webPages']['value'])
                print(f"✅ Success! Got {results_count} search results")
                print(f"🎉 Your Grounding with Bing Search API key is working!")
                
                # Show first result
                if results_count > 0:
                    first_result = data['webPages']['value'][0]
                    print(f"📝 First result: {first_result.get('name', 'No title')}")
                    print(f"🔗 URL: {first_result.get('url', 'No URL')}")
                return True
            else:
                print("⚠️ Unexpected response format")
                print(f"Response: {response.text[:200]}...")
                return False
        
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - API key is invalid or expired")
            print("Please check your API key in the Azure portal")
            return False
            
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API key doesn't have proper permissions")
            print("Check your Azure subscription and API permissions")
            return False
            
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_bing_api()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Your API key is working!")
        print("2. Make sure RETRIEVER=bing is set in your environment")
        print("3. Restart your GPT Researcher application")
        print("4. Test with a research query")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Verify your API key in Azure portal")
        print("2. Check that the service is 'Bing Search' (not just grounding)")
        print("3. Ensure your subscription is active")
        print("4. Try regenerating the API key if needed")