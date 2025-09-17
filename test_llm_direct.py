#!/usr/bin/env python3
"""
Debug LLM configuration and API calls
"""
import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.getcwd())

async def test_llm_direct():
    print("🔍 Testing LLM configuration directly...")
    
    try:
        # Get the actual EGPT_API_KEY from environment
        egpt_api_key = os.environ.get('EGPT_API_KEY')
        if not egpt_api_key:
            print("❌ EGPT_API_KEY not found in environment variables")
            return
            
        # Set up environment like the MCP server would
        os.environ['OPENAI_BASE_URL'] = 'https://expertgpt.apps1-ir-int.icloud.intel.com/v1'
        os.environ['OPENAI_API_KEY'] = egpt_api_key
        
        print(f"🌐 OPENAI_BASE_URL: {os.environ.get('OPENAI_BASE_URL')}")
        print(f"🔑 OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
        print(f"🔑 EGPT_API_KEY: {'Set' if egpt_api_key else 'Not set'}")
        print(f"🔑 API Key preview: {egpt_api_key[:10]}..." if egpt_api_key else "🔑 No API key")
        
        from gpt_researcher import GPTResearcher
        from gpt_researcher.utils.llm import create_chat_completion
        
        # Create researcher
        researcher = GPTResearcher(query="AI trends", report_type="quick_research")
        
        # Debug configuration
        print(f"📋 Smart LLM: {researcher.cfg.smart_llm}")
        print(f"📋 Smart LLM Provider: {researcher.cfg.smart_llm_provider}")
        print(f"📋 Smart LLM Model: {researcher.cfg.smart_llm_model}")
        
        # Test direct LLM call
        print("\n🧪 Testing direct LLM call...")
        test_prompt = "Please respond with exactly: 'LLM is working correctly'"
        
        try:
            response = await create_chat_completion(
                messages=[{"role": "user", "content": test_prompt}],
                llm_provider=researcher.cfg.smart_llm_provider,
                model=researcher.cfg.smart_llm_model,
                temperature=0.1,
                max_tokens=50
            )
            
            print(f"✅ LLM Response: {response}")
            
        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Try to get more details
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_direct())