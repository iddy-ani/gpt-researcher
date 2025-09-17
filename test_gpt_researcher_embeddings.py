#!/usr/bin/env python3
"""
Test GPT Researcher embeddings configuration
"""
import sys
import os

# Add the gpt_researcher directory to the path
sys.path.append('.')

from gpt_researcher.memory.embeddings import Memory

def test_gpt_researcher_embeddings():
    """Test GPT Researcher embeddings with hardcoded Azure configuration"""
    print("=== GPT Researcher Embeddings Test ===")
    
    try:
        # Initialize Memory with Azure OpenAI
        memory = Memory(
            embedding_provider="azure_openai",
            model="text-embedding-3-large"
        )
        
        print("✅ Memory initialized successfully")
        
        # Test embedding generation
        test_text = "This is a test document for GPT Researcher embeddings."
        
        print(f"🧪 Testing embedding generation for: '{test_text}'")
        
        # Get embeddings
        embeddings_result = memory._embeddings.embed_documents([test_text])
        
        if embeddings_result and len(embeddings_result) > 0:
            embedding_size = len(embeddings_result[0])
            print(f"✅ Embedding generated successfully!")
            print(f"📊 Embedding size: {embedding_size}")
            print(f"🎯 First few values: {embeddings_result[0][:5]}")
            return True
        else:
            print("❌ No embeddings returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gpt_researcher_embeddings()
    
    if success:
        print(f"\n🎉 GPT Researcher embeddings are working correctly!")
    else:
        print(f"\n🔧 GPT Researcher embeddings configuration needs fixing.")