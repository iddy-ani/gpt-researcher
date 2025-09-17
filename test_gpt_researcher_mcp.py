#!/usr/bin/env python3
"""
Test script for GPT Researcher MCP Server
Tests the MCP JSON-RPC protocol implementation
"""

import asyncio
import json
import sys
import subprocess
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

async def test_mcp_server():
    """Test the GPT Researcher MCP server"""
    print("🧪 Testing GPT Researcher MCP Server Protocol...")
    
    # Path to the MCP server
    server_path = "python"
    server_args = ["gpt_researcher_mcp.py"]
    
    try:
        # Start the MCP server process
        print("🚀 Starting MCP server process...")
        process = await asyncio.create_subprocess_exec(
            server_path,
            *server_args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd(),
            encoding='utf-8',
            errors='replace'  # Handle encoding errors gracefully
        )
        
        print("✅ MCP server process started")
        
        # Test 1: Initialize
        print("\n📨 Sending initialize request...")
        init_request = create_json_rpc_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        
        process.stdin.write(init_request)
        await process.stdin.drain()
        
        # Read response
        response_line = await process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.decode('utf-8', errors='replace') if isinstance(response_line, bytes) else response_line)
                print(f"✅ Initialize response: {json.dumps(response, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in initialize response: {e}")
                print(f"Raw response: {repr(response_line)}")
        
        # Send initialized notification
        print("\n📨 Sending initialized notification...")
        initialized_notif = create_notification("notifications/initialized")
        process.stdin.write(initialized_notif)
        await process.stdin.drain()
        
        # Test 2: List tools
        print("\n📨 Sending tools/list request...")
        tools_request = create_json_rpc_message("tools/list", {}, 2)
        process.stdin.write(tools_request)
        await process.stdin.drain()
        
        response_line = await process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.decode('utf-8', errors='replace') if isinstance(response_line, bytes) else response_line)
                print(f"✅ Tools list response: {json.dumps(response, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in tools response: {e}")
                print(f"Raw response: {repr(response_line)}")
        
        # Test 3: Call check-status tool
        print("\n📨 Sending tools/call request for check-status...")
        call_request = create_json_rpc_message("tools/call", {
            "name": "check-status",
            "arguments": {}
        }, 3)
        
        process.stdin.write(call_request)
        await process.stdin.drain()
        
        response_line = await process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.decode('utf-8', errors='replace') if isinstance(response_line, bytes) else response_line)
                print(f"✅ Tool call response: {json.dumps(response, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in tool call response: {e}")
                print(f"Raw response: {repr(response_line)}")
        
        # Check for any error output
        print("\n📊 Checking stderr for any issues...")
        try:
            stderr_data = await asyncio.wait_for(process.stderr.read(1024), timeout=1.0)
            if stderr_data:
                print(f"📝 Server stderr: {stderr_data.decode('utf-8', errors='replace')}")
        except asyncio.TimeoutError:
            print("✅ No stderr output (timeout)")
        
        # Clean shutdown
        print("\n🛑 Terminating server...")
        process.terminate()
        await process.wait()
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.terminate()
            await process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())