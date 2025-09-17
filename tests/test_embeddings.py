#!/usr/bin/env python3
"""
Test script to verify embeddings configuration
"""
import os
import asyncio
from gpt_researcher.memory.embeddings import Memory

async def test_embeddings():
    """Test embeddings configuration"""
    print("=== Testing Embeddings Configuration ===")
    
    # Test current configuration
    embedding_config = 'text-embedding-3-large'
    print(f"Current EMBEDDING config: {embedding_config}")
    
    provider, model = embedding_config.split(':', 1)
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    
    try:
        # Initialize memory with current config
        memory = Memory(embedding_provider=provider, model=model)
        print(f"✅ Memory initialized successfully")
        
        # Test embedding a simple text
        test_text = "This is a test document about cakes and baking."
        print(f"🧪 Testing embedding: '{test_text}'")
        
        # Get embeddings
        embeddings = memory._embeddings.embed_documents([test_text])
        
        if embeddings and len(embeddings) > 0:
            embedding_size = len(embeddings[0])
            print(f"✅ Embedding successful! Vector size: {embedding_size}")
            print(f"🎉 Embeddings are working correctly!")
            return True
        else:
            print("❌ No embeddings returned")
            return False
            
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def test_azure_embeddings():
    """Test Azure OpenAI embeddings if configured"""
    print("\n=== Testing Azure OpenAI Embeddings ===")
    
    azure_endpoint = 'https://appi-gpt4.openai.azure.com/'
    azure_key = 'b448d4e96f3a416786f75bffa9108fcc'
    azure_version = '2024-02-15-preview'
    
    if not all([azure_endpoint, azure_key, azure_version]):
        print("⚠️ Azure OpenAI not configured. Skipping Azure test.")
        print("To use Azure OpenAI embeddings, set:")
        print("  export EMBEDDING=azure_openai:text-embedding-3-large")
        print("  export AZURE_OPENAI_ENDPOINT=https://appi-gpt4.openai.azure.com/")
        print("  export AZURE_OPENAI_API_KEY=your_key")
        print("  export AZURE_OPENAI_API_VERSION=2024-02-15-preview")
        return False
    
    print(f"Azure Endpoint: {azure_endpoint}")
    print(f"Azure API Version: {azure_version}")
    print(f"Azure API Key: {'Set' if azure_key else 'Not set'}")
    
    try:
        # Test Azure OpenAI embeddings
        memory = Memory(embedding_provider="azure_openai", model="text-embedding-3-large")
        test_text = "This is a test for Azure OpenAI embeddings."
        
        embeddings = memory._embeddings.embed_documents([test_text])
        
        if embeddings and len(embeddings) > 0:
            embedding_size = len(embeddings[0])
            print(f"✅ Azure embeddings successful! Vector size: {embedding_size}")
            return True
        else:
            print("❌ No Azure embeddings returned")
            return False
            
    except Exception as e:
        print(f"❌ Azure embedding test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        # Test current configuration
        current_success = await test_embeddings()
        
        # Test Azure configuration if available
        azure_success = await test_azure_embeddings()
        
        print(f"\n=== Results ===")
        print(f"Current embeddings: {'✅ Working' if current_success else '❌ Failed'}")
        print(f"Azure embeddings: {'✅ Working' if azure_success else '⚠️ Not configured or failed'}")
        
        if current_success:
            print("\n🎉 Embeddings are working! GPT Researcher should work without SSL errors.")
        elif azure_success:
            print("\n💡 Consider switching to Azure OpenAI embeddings for better reliability.")
        else:
            print("\n🔧 Embeddings need configuration. Please check your settings.")
    
    asyncio.run(main())