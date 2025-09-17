#!/usr/bin/env python3
"""
Simple Executable Test - Just test basic MCP functionality without research
"""

import asyncio
import json
import subprocess
import sys
import time
import os
from datetime import datetime

def create_json_rpc_message(method: str, params: dict = None, id: int = 1) -> str:
    """Create a JSON-RPC 2.0 message"""
    message = {
        "jsonrpc": "2.0",
        "method": method,
        "id": id
    }
    if params:
        message["params"] = params
    
    return json.dumps(message) + "\n"

def create_notification(method: str, params: dict = None) -> str:
    """Create a JSON-RPC notification (no id)"""
    message = {
        "jsonrpc": "2.0", 
        "method": method
    }
    if params:
        message["params"] = params
    
    return json.dumps(message) + "\n"

async def simple_exe_test():
    """Simple test of executable basic functionality"""
    print("🔧 SIMPLE EXECUTABLE TEST: Basic MCP Protocol")
    print("=" * 50)
    print(f"🕐 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify API key first
    api_key = os.getenv('EGPT_API_KEY')
    if api_key:
        print(f"✅ EGPT_API_KEY is set: {api_key[:10]}...")
    else:
        print("❌ EGPT_API_KEY is not set!")
    
    # Path to the executable
    exe_path = "dist/gpt-researcher-mcp-streaming.exe"
    
    # Check if executable exists
    if not os.path.exists(exe_path):
        print(f"❌ Executable not found at: {exe_path}")
        return False
    
    print(f"📦 Testing executable: {exe_path}")
    
    try:
        print("\n🚀 Starting executable...")
        
        # Create environment with all current variables
        env = os.environ.copy()
        
        process = await asyncio.create_subprocess_exec(
            exe_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd(),
            env=env
        )
        
        print("✅ Executable started")
        
        # Initialize Protocol
        print("\n📋 Testing MCP initialization...")
        init_request = create_json_rpc_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "simple-test", "version": "1.0.0"}
        })
        
        process.stdin.write(init_request.encode('utf-8'))
        await process.stdin.drain()
        
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        if response_line:
            try:
                response = json.loads(response_line.decode('utf-8', errors='replace'))
                server_info = response.get('result', {}).get('serverInfo', {})
                print(f"✅ Init successful: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
            except json.JSONDecodeError:
                print("❌ Invalid init response")
                return False
        
        # Send initialized notification
        initialized_notif = create_notification("notifications/initialized")
        process.stdin.write(initialized_notif.encode('utf-8'))
        await process.stdin.drain()
        
        # Test tools/list
        print("\n🔧 Testing tools list...")
        tools_request = create_json_rpc_message("tools/list", {}, 2)
        
        process.stdin.write(tools_request.encode('utf-8'))
        await process.stdin.drain()
        
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        if response_line:
            try:
                response = json.loads(response_line.decode('utf-8', errors='replace'))
                if 'result' in response:
                    tools = response['result'].get('tools', [])
                    print(f"✅ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"   - {tool.get('name', 'Unknown')}")
                else:
                    print(f"❌ Tools list failed: {response.get('error', {})}")
                    return False
            except json.JSONDecodeError:
                print("❌ Invalid tools response")
                return False
        
        # Test simple status check
        print("\n📊 Testing status check...")
        status_request = create_json_rpc_message("tools/call", {
            "name": "check-status",
            "arguments": {}
        }, 3)
        
        process.stdin.write(status_request.encode('utf-8'))
        await process.stdin.drain()
        
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=15.0)
        if response_line:
            try:
                response = json.loads(response_line.decode('utf-8', errors='replace'))
                if 'result' in response:
                    content = response['result'].get('content', [])
                    if content and content[0].get('type') == 'text':
                        status_text = content[0]['text']
                        print("✅ Status check successful")
                        print("📄 Status info:")
                        lines = status_text.split('\\n')[:5]  # First 5 lines
                        for line in lines:
                            if line.strip():
                                print(f"   {line.strip()}")
                    else:
                        print("❌ Invalid status response format")
                        return False
                else:
                    print(f"❌ Status check failed: {response.get('error', {})}")
                    return False
            except json.JSONDecodeError:
                print("❌ Invalid status response")
                return False
        
        print("\n🎉 SIMPLE EXECUTABLE TEST PASSED!")
        print("✅ MCP protocol working")
        print("✅ Tools available")
        print("✅ Status check functional")
        print("📝 Executable basic functionality confirmed")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        return False
    
    finally:
        if 'process' in locals():
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
                print("✅ Cleanup complete")
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()

async def main():
    success = await simple_exe_test()
    
    if success:
        print("\\n🎯 SIMPLE TEST RESULT: PASSED! 🎉")
        print("🔧 Executable MCP protocol functionality confirmed")
        print("💡 Research functionality may need debugging")
        return 0
    else:
        print("\\n💥 SIMPLE TEST RESULT: FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))