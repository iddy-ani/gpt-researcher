#!/usr/bin/env python3
"""
Test script for GPT Researcher MCP Server
"""

import asyncio
import json
import subprocess
import sys
import os
import signal
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing GPT Researcher MCP Server")
    print("=" * 50)
    
    # Test 1: Check if server starts
    print("📡 Test 1: Server startup...")
    
    try:
        # Start the MCP server
        process = subprocess.Popen(
            [sys.executable, 'gpt_researcher_mcp.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0.0",
                "capabilities": {
                    "roots": {"list": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the request
        request_str = json.dumps(init_request) + '\n'
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # Wait for response
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=10.0
        )
        
        if response_line:
            response = json.loads(response_line.strip())
            if 'result' in response:
                print("✅ Initialize successful")
            else:
                print(f"❌ Initialize failed: {response}")
                
        # Test 2: List tools
        print("\n🔧 Test 2: List tools...")
        
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        request_str = json.dumps(list_tools_request) + '\n'
        process.stdin.write(request_str)
        process.stdin.flush()
        
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=5.0
        )
        
        if response_line:
            response = json.loads(response_line.strip())
            if 'result' in response and 'tools' in response['result']:
                tools = response['result']['tools']
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description']}")
            else:
                print(f"❌ List tools failed: {response}")
        
        # Test 3: Check status
        print("\n📊 Test 3: Check status...")
        
        status_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "check-status",
                "arguments": {}
            }
        }
        
        request_str = json.dumps(status_request) + '\n'
        process.stdin.write(request_str)
        process.stdin.flush()
        
        response_line = await asyncio.wait_for(
            asyncio.create_task(asyncio.to_thread(process.stdout.readline)),
            timeout=5.0
        )
        
        if response_line:
            response = json.loads(response_line.strip())
            if 'result' in response:
                content = response['result']['content']
                if content and len(content) > 0:
                    print("✅ Status check successful")
                    print("📄 Status content preview:")
                    status_text = content[0].get('text', '')[:200]
                    print(f"   {status_text}...")
                else:
                    print("❌ Empty status response")
            else:
                print(f"❌ Status check failed: {response}")
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("\n🎉 MCP Server test completed!")
        return True
        
    except asyncio.TimeoutError:
        print("❌ Test timed out")
        if 'process' in locals():
            process.kill()
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.kill()
        return False

if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)