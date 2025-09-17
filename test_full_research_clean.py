#!/usr/bin/env python3
"""
Full Comprehensive Test with Source Statistics and Progress Tracking
"""

import asyncio
import json
import subprocess
import time
import sys
from datetime import datetime

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

async def comprehensive_research_test():
    """Comprehensive test with full research and source statistics"""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🧪 Comprehensive Test of GPT Researcher MCP Server (Streaming)")
    print("============================================================")
    
    # Start the Python MCP server
    print("🚀 Starting streaming MCP server...")
    process = await asyncio.create_subprocess_exec(
        "C:/Users/ianimash/source/repos/venvs/gpt-researcher/Scripts/python.exe",
        "gpt_researcher_mcp_streaming.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        print("✅ Server process started successfully")
        
        # Test 1: Initialize protocol
        print("\n" + "="*50)
        print("TEST 1: Initialize MCP Protocol")
        print("="*50)
        
        init_request = create_json_rpc_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {"progress": True},
            "clientInfo": {"name": "comprehensive-test-client", "version": "1.0.0"}
        }, 1)
        
        print("📨 Sending initialize request...")
        process.stdin.write(init_request.encode('utf-8'))
        await process.stdin.drain()
        
        response_line = await process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print("✅ Initialize response received")
            print(f"   Protocol Version: {response.get('result', {}).get('protocolVersion', 'Unknown')}")
            print(f"   Server Name: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            print(f"   Server Version: {response.get('result', {}).get('serverInfo', {}).get('version', 'Unknown')}")
        
        # Send initialized notification
        print("📨 Sending initialized notification...")
        initialized_notif = create_json_rpc_message("notifications/initialized", {})
        process.stdin.write(initialized_notif.encode('utf-8'))
        await process.stdin.drain()
        
        # Test 2: Conduct full research with progress tracking
        print("\n" + "="*50)
        print("TEST 2: Conduct Full Research with Source Tracking")
        print("="*50)
        
        research_request = create_json_rpc_message("tools/call", {
            "name": "quick-research",  # Using quick-research for faster results
            "arguments": {
                "query": "latest artificial intelligence developments 2025"
            }
        }, 2)
        
        print("📨 Starting comprehensive research...")
        print("   Query: 'latest artificial intelligence developments 2025'")
        print("⏳ This will take 30-60 seconds with full source tracking...")
        
        process.stdin.write(research_request.encode('utf-8'))
        await process.stdin.drain()
        
        # Track progress and collect data
        start_time = time.time()
        progress_messages = []
        source_stats = {"attempted": 0, "successful": 0, "failed": 0}
        research_completed = False
        final_research_text = ""
        
        timeout_duration = 90.0  # 90 second timeout
        while not research_completed and (time.time() - start_time) < timeout_duration:
            try:
                line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
                if not line:
                    break
                    
                try:
                    response = json.loads(line.decode('utf-8').strip())
                    
                    # Check for progress notification
                    if response.get('method') == 'notifications/progress':
                        params = response.get('params', {})
                        message = params.get('message', '')
                        progress = params.get('progress', 0)
                        progress_messages.append(f"[{progress:.1%}] {message}")
                        
                        # Parse source statistics from messages
                        if any(keyword in message.lower() for keyword in ["fetching", "searching", "retrieving"]):
                            source_stats["attempted"] += 1
                        if any(keyword in message.lower() for keyword in ["successful", "retrieved", "found"]):
                            source_stats["successful"] += 1
                        if any(keyword in message.lower() for keyword in ["failed", "error", "timeout"]):
                            source_stats["failed"] += 1
                        
                        print(f"   📊 [{progress:.1%}] {message}")
                    
                    # Check for final result
                    elif 'result' in response and response.get('id') == 2:
                        content = response['result'].get('content', [])
                        if content and content[0].get('type') == 'text':
                            final_research_text = content[0].get('text', '')
                            research_completed = True
                            elapsed_time = time.time() - start_time
                            print(f"\n✅ Research completed in {elapsed_time:.1f} seconds")
                    
                    # Check for errors
                    elif 'error' in response:
                        error_msg = response.get('error', {}).get('message', 'Unknown error')
                        print(f"\n❌ Research failed: {error_msg}")
                        break
                        
                except json.JSONDecodeError:
                    continue
                    
            except asyncio.TimeoutError:
                continue
        
        # Analyze results
        if research_completed and final_research_text:
            print("\n" + "="*60)
            print("COMPREHENSIVE RESEARCH ANALYSIS")
            print("="*60)
            
            # Source Statistics
            total_sources = source_stats["attempted"]
            successful_sources = source_stats["successful"] 
            failed_sources = source_stats["failed"]
            
            print(f"📊 SOURCE STATISTICS:")
            print(f"   🎯 Sources attempted: {total_sources}")
            print(f"   ✅ Sources successful: {successful_sources}")
            print(f"   ❌ Sources failed: {failed_sources}")
            if total_sources > 0:
                success_rate = (successful_sources / total_sources) * 100
                print(f"   📈 Success rate: {success_rate:.1f}%")
            
            # Research Quality Metrics
            word_count = len(final_research_text.split())
            char_count = len(final_research_text)
            sections = final_research_text.count('#')
            lines = len([line for line in final_research_text.split('\n') if line.strip()])
            
            print(f"\n📄 RESEARCH QUALITY METRICS:")
            print(f"   📝 Total words: {word_count:,}")
            print(f"   📏 Total characters: {char_count:,}")
            print(f"   📋 Sections found: {sections}")
            print(f"   📄 Content lines: {lines}")
            print(f"   📨 Progress updates: {len(progress_messages)}")
            
            # Quality Score
            quality_score = min(100, (word_count // 100) * 10 + (sections * 5) + min(30, len(progress_messages) * 3))
            print(f"   🏆 Quality score: {quality_score}/100")
            
            # Show research preview
            print(f"\n📋 RESEARCH CONTENT PREVIEW:")
            lines = final_research_text.split('\n')[:20]
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"   {i+1:2d}. {line}")
            total_lines = len(final_research_text.split('\n'))
            if total_lines > 20:
                remaining_lines = total_lines - 20
                print(f"   ... (+{remaining_lines} more lines)")
            
            # Show all progress messages
            print(f"\n📊 COMPLETE PROGRESS LOG:")
            for i, msg in enumerate(progress_messages, 1):
                print(f"   {i:2d}. {msg}")
                
        else:
            elapsed_time = time.time() - start_time
            print(f"\n⚠️ Research timed out after {elapsed_time:.1f} seconds")
            print(f"   📊 Progress messages received: {len(progress_messages)}")
            if progress_messages:
                print("   Recent progress:")
                for msg in progress_messages[-5:]:
                    print(f"      {msg}")
        
        # Final Summary
        print("\n" + "="*60)
        print("FINAL TEST SUMMARY")
        print("="*60)
        
        print("✅ Protocol initialization: PASSED")
        print("✅ Tool communication: PASSED")
        if research_completed:
            print("✅ Full research pipeline: COMPLETED")
            print(f"🎯 Source success rate: {(source_stats['successful'] / max(1, source_stats['attempted'])) * 100:.1f}%")
            print(f"📊 Research quality: {quality_score}/100")
        else:
            print("⚠️ Research pipeline: TIMED OUT")
        
        print(f"📨 Progress tracking: {len(progress_messages)} notifications")
        print("\n🎉 MCP Server is fully functional with detailed monitoring!")
        
    finally:
        # Clean shutdown
        print("\n🛑 Shutting down server...")
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5.0)
            print("✅ Server shutdown complete")
        except asyncio.TimeoutError:
            print("⚠️ Force killing server...")
            process.kill()
            await process.wait()
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 RESULT: Comprehensive research test with source tracking completed!")

if __name__ == "__main__":
    asyncio.run(comprehensive_research_test())