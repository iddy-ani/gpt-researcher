#!/usr/bin/env python3
"""
Simple test for hardcoded Azure OpenAI embeddings
"""
import os
import sys
sys.path.append('.')

def test_hardcoded_azure_embeddings():
    """Test the hardcoded Azure OpenAI configuration"""
    print("=== Testing Hardcoded Azure OpenAI Embeddings ===")
    
    try:
        from gpt_researcher.memory.embeddings import Memory
        
        print("✅ Imports successful")
        
        # Test with the hardcoded configuration
        memory = Memory(embedding_provider="azure_openai", model="text-embedding-3-large")
        print("✅ Memory initialized with Azure OpenAI")
        
        # Test a simple embedding
        test_text = "This is a test document."
        print(f"🧪 Testing embedding: '{test_text}'")
        
        embeddings = memory._embeddings.embed_documents([test_text])
        
        if embeddings and len(embeddings) > 0:
            print(f"✅ Success! Vector size: {len(embeddings[0])}")
            print("🎉 Hardcoded Azure OpenAI embeddings are working!")
            return True
        else:
            print("❌ No embeddings returned")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Check if it's an API key issue
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            print("💡 This might be an API key issue. Make sure OPENAI_API_KEY is set with your Azure key.")
        
        return False

if __name__ == "__main__":
    # Check environment
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OPENAI_API_KEY is set: {api_key[:10]}...")
    else:
        print("❌ OPENAI_API_KEY not set")
    
    # Run test
    success = test_hardcoded_azure_embeddings()
    
    if success:
        print("\n🚀 Ready to restart GPT Researcher with new configuration!")
    else:
        print("\n🔧 Check the configuration and try again.")