#!/usr/bin/env python3
"""
Test script to find working models on Intel's API endpoint
"""
import asyncio
import os
from gpt_researcher.utils.llm import create_chat_completion
from gpt_researcher.config.config import Config

async def test_model(model_name, cfg):
    """Test a specific model"""
    try:
        response = await create_chat_completion(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            temperature=0.1,
            llm_provider=cfg.smart_llm_provider,
        )
        print(f"✅ {model_name}: Working - {response[:50]}...")
        return True
    except Exception as e:
        error_msg = str(e)
        if "DeploymentNotFound" in error_msg:
            print(f"❌ {model_name}: Model not found/deployed")
        elif "InvalidRequestError" in error_msg:
            print(f"⚠️ {model_name}: Invalid request - {error_msg[:100]}...")
        else:
            print(f"❌ {model_name}: Error - {error_msg[:100]}...")
        return False

async def find_working_models():
    """Test common OpenAI model names to find what works"""
    print("Testing Intel API endpoint with SSL verification disabled...")
    print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")
    
    cfg = Config()
    
    # Common OpenAI model names to test
    models_to_test = [
        "gpt-4",
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gpt-35-turbo",  # Azure style naming
        "text-davinci-003",
        "gpt-4-0613",
        "gpt-4-32k",
        cfg.smart_llm_model,  # Test the configured model
    ]
    
    print(f"\nTesting {len(models_to_test)} different models...\n")
    
    working_models = []
    for model in models_to_test:
        if model:  # Skip None values
            is_working = await test_model(model, cfg)
            if is_working:
                working_models.append(model)
    
    print(f"\n=== Results ===")
    if working_models:
        print(f"✅ Working models: {', '.join(working_models)}")
        print(f"\nTo use a working model, update your configuration:")
        print(f"export SMART_LLM_MODEL={working_models[0]}")
        print(f"export FAST_LLM_MODEL={working_models[0]}")
    else:
        print("❌ No working models found. Check Intel API configuration.")
    
    return working_models

if __name__ == "__main__":
    asyncio.run(find_working_models())