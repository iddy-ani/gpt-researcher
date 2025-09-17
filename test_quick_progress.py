#!/usr/bin/env python3
"""
Quick test to check progress notifications in Python script mode
"""

import asyncio
import json
import subprocess
import time
import sys

def create_json_rpc_message(method: str, params: dict, id: int = None) -> str:
    """Create a JSON-RPC message"""
    message = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params
    }
    if id is not None:
        message["id"] = id
    return json.dumps(message) + '\n'

async def quick_progress_test():
    """Quick test of progress notifications"""
    print("🚀 Starting Quick Progress Test...")
    
    # Start the Python MCP server
    process = await asyncio.create_subprocess_exec(
        "C:/Users/ianimash/source/repos/venvs/gpt-researcher/Scripts/python.exe",
        "gpt_researcher_mcp_streaming.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Initialize protocol
        init_request = create_json_rpc_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {"progress": True},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }, 1)
        
        process.stdin.write(init_request.encode('utf-8'))
        await process.stdin.drain()
        
        # Read initialize response
        response_line = await process.stdout.readline()
        if response_line:
            print("✅ Initialize response received")
        
        # Send initialized notification
        initialized_notif = create_json_rpc_message("notifications/initialized", {})
        process.stdin.write(initialized_notif.encode('utf-8'))
        await process.stdin.drain()
        
        # Call quick research
        quick_research_request = create_json_rpc_message("tools/call", {
            "name": "quick-research",
            "arguments": {
                "query": "AI trends 2025"
            }
        }, 3)
        
        print("📨 Starting quick research...")
        process.stdin.write(quick_research_request.encode('utf-8'))
        await process.stdin.drain()
        
        # Monitor for progress notifications and final result
        progress_count = 0
        start_time = time.time()
        
        while time.time() - start_time < 30.0:  # 30 second timeout
            try:
                line = await asyncio.wait_for(process.stdout.readline(), timeout=2.0)
                if not line:
                    break
                    
                try:
                    response = json.loads(line.decode('utf-8').strip())
                    
                    # Check for progress notification
                    if response.get('method') == 'notifications/progress':
                        progress_count += 1
                        params = response.get('params', {})
                        message = params.get('message', 'No message')
                        progress = params.get('progress', 0)
                        print(f"   📊 Progress #{progress_count}: {message} ({progress})")
                    
                    # Check for final result
                    elif 'result' in response and response.get('id') == 3:
                        print("✅ Research completed!")
                        break
                        
                    # Check for errors
                    elif 'error' in response:
                        print(f"❌ Error: {response.get('error', {}).get('message', 'Unknown')}")
                        break
                        
                except json.JSONDecodeError:
                    continue
                    
            except asyncio.TimeoutError:
                continue
        
        print(f"\n📊 Total progress notifications received: {progress_count}")
        
        # Check stderr for any debug output
        try:
            stderr_output = await asyncio.wait_for(process.stderr.read(), timeout=1.0)
            if stderr_output:
                print(f"\n🔍 Debug output from stderr:")
                print(stderr_output.decode('utf-8'))
        except asyncio.TimeoutError:
            pass
        
    finally:
        # Clean shutdown
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

if __name__ == "__main__":
    asyncio.run(quick_progress_test())