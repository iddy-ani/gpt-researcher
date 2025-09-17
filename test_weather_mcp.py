#!/usr/bin/env python3
"""
Test the weather MCP server to understand the working protocol
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_weather_mcp():
    """Test the weather MCP server to understand the protocol"""
    print("🌤️ Testing Weather MCP Server Protocol")
    print("=" * 50)
    
    try:
        # Start the weather MCP server
        process = subprocess.Popen(
            [sys.executable, 'weather-info-completed.py'],
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
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📡 Sending initialize request...")
        request_str = json.dumps(init_request) + '\n'
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize response: {json.dumps(response, indent=2)}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("\n📡 Sending initialized notification...")
        notification_str = json.dumps(initialized_notification) + '\n'
        process.stdin.write(notification_str)
        process.stdin.flush()
        
        # Test list tools
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("\n🔧 Sending tools/list request...")
        request_str = json.dumps(list_tools_request) + '\n'
        process.stdin.write(request_str)
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Tools list response: {json.dumps(response, indent=2)}")
        
        # Test tool call
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "convert-temperature",
                "arguments": {
                    "temperature": 25,
                    "from_unit": "celsius", 
                    "to_unit": "fahrenheit"
                }
            }
        }
        
        print("\n🛠️ Sending tool call request...")
        request_str = json.dumps(tool_call_request) + '\n'
        process.stdin.write(request_str)
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Tool call response: {json.dumps(response, indent=2)}")
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("\n🎉 Weather MCP test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.kill()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_weather_mcp())
    sys.exit(0 if success else 1)