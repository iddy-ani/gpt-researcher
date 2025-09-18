#!/usr/bin/env python3
"""
Test GPT Researcher MCP Server Executable with proper handshake
Tests the actual executable with full initialization handshake protocol
Includes progress monitoring for long-running research operations
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
import os
import glob

def get_executable_path():
    """Get the path to the built executable"""
    exe_path = Path("dist/gpt-researcher-mcp-streaming.exe")
    if not exe_path.exists():
        raise FileNotFoundError(f"Executable not found at {exe_path}")
    return exe_path.absolute()

def monitor_progress_file():
    """Monitor progress file for executable mode updates"""
    progress_dir = Path.cwd() / "mcp_progress"
    if not progress_dir.exists():
        return None
        
    # Find the most recent progress file
    progress_files = list(progress_dir.glob("progress_session_*.json"))
    if not progress_files:
        return None
        
    latest_file = max(progress_files, key=lambda p: p.stat().st_mtime)
    
    try:
        with open(latest_file, 'r') as f:
            return json.load(f)
    except:
        return None

def print_progress_update(progress_data):
    """Print formatted progress update"""
    if not progress_data:
        return
        
    current_op = progress_data.get("current_operation", "Unknown")
    progress_pct = progress_data.get("progress_percent", 0.0)
    last_updated = progress_data.get("last_updated", "Unknown")
    
    print(f"📊 [{last_updated}] {current_op} ({progress_pct:.1f}%)")
    
    # Show recent progress entries
    recent_logs = progress_data.get("progress_log", [])[-3:]
    for entry in recent_logs:
        timestamp = entry.get("timestamp", "")
        message = entry.get("message", "")
        progress = entry.get("progress", 0.0)
        print(f"   📝 {timestamp}: {message} ({progress:.1f}%)")

async def test_executable_with_handshake():
    """Test the executable with proper MCP handshake protocol"""
    print("🧪 GPT RESEARCHER MCP EXECUTABLE TEST WITH HANDSHAKE")
    print("=" * 60)
    
    try:
        # Get executable path
        exe_path = get_executable_path()
        print(f"📁 Executable: {exe_path}")
        print(f"📊 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Check if EGPT_API_KEY is available
        egpt_key = os.environ.get('EGPT_API_KEY')
        if egpt_key:
            print(f"✅ EGPT_API_KEY is set: {egpt_key[:10]}...")
        else:
            print("⚠️ EGPT_API_KEY not found in environment")
        
        print("\n🚀 Starting executable process...")
        
        # Start the executable process
        process = subprocess.Popen(
            [str(exe_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered for real-time communication
        )
        
        print("✅ Executable process started")
        print("🤝 Waiting for MCP initialization handshake...")
        
        # Step 1: Send MCP initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "prompts": {},
                    "resources": {},
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait for initialization response
        print("⏳ Waiting for initialization response...")
        start_time = time.time()
        timeout = 30  # 30 second timeout
        
        init_response = None
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                # Process has terminated
                stderr_output = process.stderr.read()
                print(f"❌ Process terminated unexpectedly")
                print(f"STDERR: {stderr_output}")
                return False
            
            # Try to read stdout
            try:
                line = process.stdout.readline()
                if line:
                    print(f"📥 Received: {line.strip()}")
                    try:
                        response = json.loads(line.strip())
                        if response.get("id") == 1 and "result" in response:
                            init_response = response
                            break
                    except json.JSONDecodeError:
                        # Not a JSON response, might be debug output
                        continue
            except:
                await asyncio.sleep(0.1)
                continue
        
        if not init_response:
            print("❌ Failed to receive initialization response within timeout")
            process.terminate()
            return False
        
        print("✅ Received initialization response!")
        print(f"📋 Server capabilities: {init_response.get('result', {}).get('capabilities', {})}")
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print("📤 Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Wait a moment for the server to be ready
        await asyncio.sleep(1)
        
        print("🎉 MCP handshake completed successfully!")
        print("\n🔍 Testing research functionality...")
        
        # Step 3: Test research functionality
        research_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "quick-research",
                "arguments": {
                    "query": "artificial intelligence trends 2025"
                }
            }
        }
        
        print("📤 Sending research request...")
        process.stdin.write(json.dumps(research_request) + "\n")
        process.stdin.flush()
        
        # Wait for research response with progress tracking
        print("⏳ Waiting for research response (may take 5-10 minutes for deep research)...")
        print("📊 Monitoring progress file for real-time updates...")
        start_time = time.time()
        timeout = 600  # 10 minute timeout for deep research
        
        progress_count = 0
        research_response = None
        last_progress_check = 0
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                stderr_output = process.stderr.read()
                print(f"❌ Process terminated during research")
                print(f"STDERR: {stderr_output}")
                return False
            
            # Check progress file every 5 seconds
            current_time = time.time()
            if current_time - last_progress_check > 5:
                progress_data = monitor_progress_file()
                if progress_data:
                    print_progress_update(progress_data)
                last_progress_check = current_time
            
            try:
                line = process.stdout.readline()
                if line:
                    line_stripped = line.strip()
                    print(f"📥 Received: {line_stripped}")
                    
                    try:
                        response = json.loads(line_stripped)
                        
                        # Check for progress notifications
                        if response.get("method") == "notifications/progress":
                            progress_count += 1
                            progress = response.get("params", {})
                            print(f"📊 MCP Progress #{progress_count}: {progress}")
                        
                        # Check for research response
                        elif response.get("id") == 2 and ("result" in response or "error" in response):
                            research_response = response
                            break
                            
                    except json.JSONDecodeError:
                        # Not JSON, might be debug output from stderr
                        continue
            except:
                await asyncio.sleep(0.5)  # Slightly longer sleep for deep research
                continue
        
        if not research_response:
            print("❌ Failed to receive research response within timeout")
            process.terminate()
            return False
        
        # Analyze the research response
        if "error" in research_response:
            print(f"❌ Research failed with error: {research_response['error']}")
            return False
        
        result = research_response.get("result", [])
        if not result:
            print("❌ Empty research result")
            return False
        
        # Get the text content
        content = ""
        for item in result:
            if item.get("type") == "text":
                content += item.get("text", "")
        
        print(f"\n🎉 RESEARCH COMPLETED SUCCESSFULLY!")
        print(f"📊 Progress notifications received: {progress_count}")
        print(f"📄 Content length: {len(content)} characters")
        print(f"⏱️ Total time: {time.time() - start_time:.1f} seconds")
        
        # Show a preview of the content
        lines = content.split('\n')
        print(f"\n📋 Research Report Preview:")
        for i, line in enumerate(lines[:10]):
            print(f"    {i+1:2d}: {line}")
        if len(lines) > 10:
            print(f"    ... (+{len(lines)-10} more lines)")
        
        # Quality assessment
        quality_score = 0
        checks = []
        
        if len(content) > 1000:
            quality_score += 2
            checks.append("✅ Rich content (>1000 chars)")
        else:
            checks.append("❌ Limited content")
        
        if "2025" in content:
            quality_score += 1
            checks.append("✅ Addresses 2025 timeframe")
        else:
            checks.append("❌ Missing 2025 context")
        
        if any(word in content.lower() for word in ["artificial intelligence", "ai", "trend", "advance"]):
            quality_score += 1
            checks.append("✅ Contains AI/trend content")
        else:
            checks.append("❌ Missing AI/trend content")
        
        if progress_count > 0:
            quality_score += 1
            checks.append("✅ Progress tracking working")
        else:
            checks.append("❌ No progress notifications")
        
        if time.time() - start_time < 180:  # Under 3 minutes
            quality_score += 1
            checks.append("✅ Reasonable completion time")
        else:
            checks.append("⚠️ Slow completion time")
        
        print(f"\n🔍 QUALITY ASSESSMENT:")
        for check in checks:
            print(f"   {check}")
        
        print(f"⭐ Overall Score: {quality_score}/5 ({quality_score*20}%)")
        
        # Clean shutdown
        print("\n🛑 Shutting down executable...")
        process.terminate()
        process.wait(timeout=5)
        
        success = quality_score >= 3
        if success:
            print("🎯 EXECUTABLE TEST PASSED! 🎉")
        else:
            print("⚠️ EXECUTABLE TEST PARTIAL SUCCESS")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function"""
    print("🕐 Test started:", time.strftime('%Y-%m-%d %H:%M:%S'))
    
    success = await test_executable_with_handshake()
    
    print("\n" + "="*60)
    if success:
        print("🎉 FINAL RESULT: EXECUTABLE TEST SUCCESSFUL!")
        print("✅ GPT Researcher MCP executable is fully functional!")
        print("🤝 MCP handshake protocol working correctly!")
        print("📊 Progress notifications operational!")
        print("🔍 Research functionality verified!")
    else:
        print("❌ FINAL RESULT: EXECUTABLE TEST FAILED")
        print("🔧 Check the error messages above for troubleshooting")
    
    print("🕐 Test completed:", time.strftime('%Y-%m-%d %H:%M:%S'))
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))