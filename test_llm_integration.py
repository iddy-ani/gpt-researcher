#!/usr/bin/env python3
"""
Test the GPT Researcher LLM integration to debug report generation issues
"""
import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.getcwd())

async def test_gpt_researcher_llm():
    print("🔍 Testing GPT Researcher LLM integration...")
    
    try:
        # Set environment to use custom retriever
        os.environ['RETRIEVER'] = 'custom'
        os.environ['EGPT_API_KEY'] = 'pak_CG2pyExb0R9eVSbQefJbcuH7nBr8T2KZp1'
        
        from gpt_researcher import GPTResearcher
        print("✅ GPTResearcher imported")
        
        # Create a researcher instance
        researcher = GPTResearcher(
            query="AI trends 2025",
            report_type="quick_research"
        )
        print("✅ GPTResearcher initialized")
        
        # Check configuration
        print(f"📋 Configured retriever: {researcher.cfg.retriever}")
        print(f"📋 LLM provider: {researcher.cfg.smart_llm_provider}")
        print(f"📋 LLM model: {researcher.cfg.smart_llm_model}")
        print(f"📋 Temperature: {researcher.cfg.temperature}")
        
        # Test the research process
        print("🔎 Conducting research...")
        research_result = await researcher.conduct_research()
        
        # Check research context
        if hasattr(researcher, 'get_research_context'):
            context = researcher.get_research_context()
            context_length = len(context)
            print(f"📊 Research context length: {context_length} characters")
            if context_length > 0:
                print(f"📄 Context preview: {context[:200]}...")
            else:
                print("❌ No research context found")
        else:
            print("⚠️ No get_research_context method available")
        
        # Test LLM report generation
        print("📝 Testing report generation...")
        try:
            report = await researcher.write_report()
            if report:
                print(f"✅ Report generated: {len(report)} characters")
                print(f"📄 Report preview: {report[:300]}...")
            else:
                print("❌ Report generation returned None/empty")
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gpt_researcher_llm())