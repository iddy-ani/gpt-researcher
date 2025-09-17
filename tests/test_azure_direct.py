#!/usr/bin/env python3
"""
Direct test of Azure OpenAI embeddings with hardcoded values
"""
import requests
import json

def test_azure_direct():
    """Test Azure OpenAI directly with hardcoded values"""
    print("=== Direct Azure OpenAI API Test ===")
    
    # Hardcoded values
    azure_endpoint = "https://appi-gpt4.openai.azure.com/"
    api_key = "1ec57c7402ed46ecbae6b09b12cb0e3c"
    api_version = "2024-02-15-preview"
    model = "text-embedding-3-large"
    
    # Construct URL
    url = f"{azure_endpoint}openai/deployments/{model}/embeddings?api-version={api_version}"
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": "This is a test document for Azure OpenAI embeddings.",
        "model": model
    }
    
    print(f"Testing URL: {url}")
    print(f"Model: {model}")
    print(f"API Key: {api_key[:10]}...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                embedding_size = len(data['data'][0]['embedding'])
                print(f"✅ Success! Embedding size: {embedding_size}")
                return True
            else:
                print(f"❌ Unexpected response format: {data}")
                return False
        else:
            print(f"❌ Error response: {response.text}")
            
            # Check for specific errors
            if response.status_code == 404:
                print("💡 Model deployment might not exist. Try these models:")
                print("   - text-embedding-ada-002")
                print("   - text-embedding-3-small") 
                print("   - text-embedding-3-large")
            elif response.status_code == 401:
                print("💡 Check your API key and endpoint in Azure portal")
            
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_different_models():
    """Test different embedding models"""
    models_to_try = [
        "text-embedding-ada-002",
        "text-embedding-3-small",
        "text-embedding-3-large"
    ]
    
    print(f"\n=== Testing Different Models ===")
    
    for model in models_to_try:
        print(f"\n🧪 Testing model: {model}")
        
        azure_endpoint = "https://appi-gpt4.openai.azure.com/"
        api_key = "1ec57c7402ed46ecbae6b09b12cb0e3c"
        api_version = "2024-02-15-preview"
        
        url = f"{azure_endpoint}openai/deployments/{model}/embeddings?api-version={api_version}"
        
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": "Test text",
            "model": model
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {model} works!")
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    embedding_size = len(data['data'][0]['embedding'])
                    print(f"   📊 Embedding size: {embedding_size}")
                return model
            else:
                print(f"   ❌ {model} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {model} error: {e}")
    
    return None

if __name__ == "__main__":
    # Test direct API call
    success = test_azure_direct()
    
    if not success:
        # Try different models
        working_model = test_different_models()
        
        if working_model:
            print(f"\n🎉 Found working model: {working_model}")
            print(f"💡 Update your embeddings.py to use: {working_model}")
        else:
            print(f"\n🔧 No models worked. Check your Azure configuration.")
    else:
        print(f"\n🎉 Azure OpenAI embeddings are working correctly!")