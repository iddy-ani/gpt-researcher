#!/usr/bin/env python3
"""
Patient End-to-End Test for GPT Researcher MCP Server (Streaming Version)
This test gives proper time for actual research operations to complete
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

async def patient_research_test():
    """Patient test that allows for long research times"""
    print("🕐 PATIENT RESEARCH TEST: GPT Researcher MCP Server")
    print("=" * 70)
    print(f"🕐 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⏰ This test allows up to 10 minutes for research to complete")
    
    # Verify API key first
    api_key = os.getenv('EGPT_API_KEY')
    if api_key:
        print(f"✅ EGPT_API_KEY is set: {api_key[:10]}...")
    else:
        print("❌ EGPT_API_KEY is not set!")
        return False
    
    python_exe = "C:/Users/ianimash/source/repos/venvs/gpt-researcher/Scripts/python.exe"
    server_script = "gpt_researcher_mcp_streaming.py"
    
    try:
        print("\n🚀 Starting MCP server process...")
        process = await asyncio.create_subprocess_exec(
            python_exe,
            server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        print("✅ Server process started successfully")
        
        # Initialize Protocol
        print("\n📋 Initializing MCP protocol...")
        init_request = create_json_rpc_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "patient-test-client", "version": "1.0.0"}
        })
        
        process.stdin.write(init_request.encode('utf-8'))
        await process.stdin.drain()
        
        response_line = await process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.decode('utf-8', errors='replace'))
                server_info = response.get('result', {}).get('serverInfo', {})
                print(f"✅ Server initialized: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
            except json.JSONDecodeError:
                print("❌ Invalid initialize response")
                return False
        
        # Send initialized notification
        initialized_notif = create_notification("notifications/initialized")
        process.stdin.write(initialized_notif.encode('utf-8'))
        await process.stdin.drain()
        
        # Quick Status Check
        print("\n📊 Quick status check...")
        status_request = create_json_rpc_message("tools/call", {
            "name": "check-status",
            "arguments": {}
        }, 2)
        
        process.stdin.write(status_request.encode('utf-8'))
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            if response_line:
                response = json.loads(response_line.decode('utf-8', errors='replace'))
                if 'result' in response:
                    print("✅ System status: Operational")
                else:
                    print(f"⚠️ Status check issue: {response.get('error', {})}")
        except (asyncio.TimeoutError, json.JSONDecodeError):
            print("⚠️ Status check timeout/error, but continuing...")
        
        # MAIN TEST: Patient Research Operation
        print("\n" + "="*70)
        print("🔬 MAIN TEST: PATIENT RESEARCH OPERATION")
        print("="*70)
        
        research_request = create_json_rpc_message("tools/call", {
            "name": "quick-research",
            "arguments": {
                "query": "recent developments in AI"  # Simple but meaningful query
            }
        }, 3)
        
        print("🔍 Starting research operation...")
        print("   Query: 'recent developments in AI'")
        print("   ⏰ Timeout: 10 minutes (600 seconds)")
        print("   📡 Listening for both progress notifications and final result")
        
        start_time = time.time()
        process.stdin.write(research_request.encode('utf-8'))
        await process.stdin.drain()
        
        print(f"📤 Research request sent at {datetime.now().strftime('%H:%M:%S')}")
        print("🕐 Waiting patiently for research to complete...")
        print("   (Research typically takes 3-8 minutes depending on sources)")
        
        # Patient waiting with periodic status updates
        TIMEOUT_SECONDS = 600  # 10 minutes
        last_update = time.time()
        final_result = None
        
        while time.time() - start_time < TIMEOUT_SECONDS:
            try:
                # Wait for output with shorter intervals for status updates
                response_line = await asyncio.wait_for(process.stdout.readline(), timeout=30.0)
                
                if not response_line:
                    elapsed = time.time() - start_time
                    print(f"📭 No more output after {elapsed:.1f}s")
                    break
                
                raw_line = response_line.decode('utf-8', errors='replace').rstrip()
                if not raw_line:
                    continue
                
                # Show elapsed time every so often
                elapsed = time.time() - start_time
                if time.time() - last_update > 30:  # Update every 30 seconds
                    print(f"⏱️ Still waiting... {elapsed:.0f}s elapsed")
                    last_update = time.time()
                
                try:
                    parsed = json.loads(raw_line)
                    
                    # Check for progress notifications
                    if parsed.get('method') == 'notifications/progress':
                        params = parsed.get('params', {})
                        message = params.get('message', 'Progress update')
                        progress = params.get('progress', 0)
                        print(f"📊 Progress: {message} ({progress:.1%})")
                        continue
                    
                    # Check for final result
                    if 'result' in parsed:
                        print(f"🎯 Received final result after {elapsed:.1f}s!")
                        final_result = parsed['result']
                        break
                    
                    # Check for errors
                    if 'error' in parsed:
                        error_msg = parsed['error'].get('message', 'Unknown error')
                        print(f"❌ Research failed: {error_msg}")
                        return False
                        
                except json.JSONDecodeError:
                    # Might be streaming output or debug info
                    if raw_line.strip():
                        print(f"📝 Server output: {raw_line[:100]}{'...' if len(raw_line) > 100 else ''}")
                
            except asyncio.TimeoutError:
                elapsed = time.time() - start_time
                print(f"⏳ Waiting... {elapsed:.0f}s elapsed (timeout in {TIMEOUT_SECONDS - elapsed:.0f}s)")
                continue
        
        total_elapsed = time.time() - start_time
        
        if final_result:
            print(f"\n🎉 RESEARCH COMPLETED SUCCESSFULLY!")
            print(f"⏱️ Total time: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)")
            
            # Analyze the result
            content = final_result.get('content', [])
            if content and len(content) > 0 and content[0].get('type') == 'text':
                research_text = content[0]['text']
                
                print(f"\n📊 Research Report Analysis:")
                print(f"   📏 Total length: {len(research_text)} characters")
                print(f"   📄 Total lines: {len(research_text.split(chr(10)))}")
                
                # Show first few lines
                lines = research_text.split(chr(10))[:15]
                print(f"\n📋 Research Report Preview:")
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        print(f"   {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
                
                # Save the report
                timestamp = int(time.time())
                output_file = f"research_report_{timestamp}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== GPT RESEARCHER REPORT ===\n")
                    f.write(f"Query: recent developments in AI\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Duration: {total_elapsed:.1f}s\n")
                    f.write(f"\n{research_text}")
                
                print(f"💾 Full report saved to: {output_file}")
                
                # Quality checks
                quality_score = 0
                checks = [
                    (len(research_text) > 1000, "Substantial content (>1000 chars)"),
                    ('AI' in research_text or 'artificial intelligence' in research_text.lower(), "Contains AI content"),
                    ('development' in research_text.lower(), "Addresses developments"),
                    (len(research_text.split(chr(10))) > 20, "Multi-paragraph structure"),
                    ('2024' in research_text or '2025' in research_text, "Recent timeframe")
                ]
                
                print(f"\n🔍 Quality Assessment:")
                for passed, description in checks:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {description}")
                    if passed:
                        quality_score += 1
                
                print(f"\n⭐ Overall Quality Score: {quality_score}/{len(checks)}")
                
                if quality_score >= 4:
                    print("🌟 Excellent research quality!")
                elif quality_score >= 3:
                    print("👍 Good research quality")
                else:
                    print("📝 Basic research completed")
                
                return True
            else:
                print("❌ Invalid result format")
                return False
        else:
            print(f"\n⏰ Research timed out after {total_elapsed:.1f}s")
            print("   This might indicate:")
            print("   - Network connectivity issues")
            print("   - API rate limiting")
            print("   - Complex query requiring more time")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    
    finally:
        print("\n🛑 Cleaning up server process...")
        if 'process' in locals():
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
                print("✅ Server shutdown complete")
            except asyncio.TimeoutError:
                print("⚠️ Force killing server...")
                process.kill()
                await process.wait()

async def main():
    """Main test execution"""
    print("🔬 GPT RESEARCHER MCP SERVER - PATIENT RESEARCH TEST")
    print("⏰ This test allows proper time for research operations to complete")
    print("=" * 70)
    
    success = await patient_research_test()
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n🎯 FINAL RESULT: PATIENT RESEARCH TEST PASSED! 🎉")
        print("✅ GPT Researcher MCP Server successfully completed full research operation!")
        print("🚀 System is ready for production use!")
        return 0
    else:
        print("\n💥 FINAL RESULT: RESEARCH TEST FAILED")
        print("🔧 Check the output above for specific issues")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))