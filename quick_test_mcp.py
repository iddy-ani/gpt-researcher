#!/usr/bin/env python3
"""
Quick test for GPT Researcher MCP Server using synchronous approach
"""

import json
import subprocess
import sys
import time

def test_mcp_server_quick():
    """Quick test of the MCP server"""
    print("🧪 Quick test of GPT Researcher MCP Server...")
    
    try:
        # Start the server process with correct venv python
        python_exe = "C:/Users/ianimash/source/repos/venvs/gpt-researcher/Scripts/python.exe"
        print("🚀 Starting server...")
        proc = subprocess.Popen(
            [python_exe, "gpt_researcher_mcp.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Send initialize request
        init_msg = {
            "jsonrpc": "2.0",
            "method": "initialize", 
            "id": 1,
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        print("📨 Sending initialize...")
        proc.stdin.write(json.dumps(init_msg) + "\n")
        proc.stdin.flush()
        
        # Try to read response with timeout
        try:
            response = proc.stdout.readline()
            if response:
                print(f"✅ Got response: {response.strip()}")
                
                # Send initialized notification (required by MCP protocol)
                print("📨 Sending initialized notification...")
                initialized_msg = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                proc.stdin.write(json.dumps(initialized_msg) + "\n")
                proc.stdin.flush()
                
            else:
                print("❌ No response received")
        except Exception as e:
            print(f"❌ Error reading response: {e}")
        
        # Send a quick tool call test
        print("📨 Testing quick tool call...")
        tool_msg = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 2,
            "params": {
                "name": "check-status",
                "arguments": {}
            }
        }
        
        proc.stdin.write(json.dumps(tool_msg) + "\n")
        proc.stdin.flush()
        
        # Try to read tool response
        try:
            tool_response = proc.stdout.readline()
            if tool_response:
                print(f"✅ Tool response: {tool_response.strip()}")
            else:
                print("❌ No tool response")
        except Exception as e:
            print(f"❌ Error reading tool response: {e}")
        
        # Check stderr (non-blocking)
        print("📝 Checking server logs...")
        proc.poll()  # Update return code
        
        # Clean up
        print("🛑 Terminating server...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            print("⚠️ Force killing server...")
            proc.kill()
            proc.wait()
        
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_mcp_server_quick()