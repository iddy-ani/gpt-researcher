#!/usr/bin/env python3
'''
MCP Server: gpt-researcher (Streaming Version)
Description: Provides AI-powered research capabilities with progress streaming

Compatible with Intel MCP Framework
'''

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# FORCE FREE SEARCH - Set environment before any imports
os.environ['RETRIEVER'] = 'custom'  # Use custom retriever with free search

# FIX TIKTOKEN ENCODING ERROR
try:
    import tiktoken
    # Force register the cl100k_base encoding if missing
    try:
        tiktoken.get_encoding('cl100k_base')
        print("✅ tiktoken cl100k_base encoding available", file=sys.stderr)
    except ValueError:
        print("🔧 tiktoken cl100k_base encoding not found, registering manually...", file=sys.stderr)
        # Try to register the encoding manually
        try:
            # Method 1: Try importing tiktoken extensions
            import tiktoken_ext.openai_public
            tiktoken.get_encoding('cl100k_base')  # Should work now
            print("✅ tiktoken cl100k_base encoding registered successfully", file=sys.stderr)
        except Exception as reg_error:
            try:
                # Method 2: Direct registration approach
                from tiktoken import Encoding
                import tiktoken.load
                
                # Try to load the encoding directly
                enc = tiktoken.load.load_tiktoken_bpe("https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken")
                special_tokens = {
                    "<|endoftext|>": 100257,
                    "<|fim_prefix|>": 100258,
                    "<|fim_middle|>": 100259,
                    "<|fim_suffix|>": 100260,
                    "<|startoftext|>": 100261
                }
                
                cl100k_base = Encoding(
                    name="cl100k_base",
                    pat_str=r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""",
                    mergeable_ranks=enc,
                    special_tokens=special_tokens
                )
                
                # Register the encoding
                tiktoken.registry.ENCODINGS["cl100k_base"] = cl100k_base
                tiktoken.get_encoding('cl100k_base')  # Test it
                print("✅ tiktoken cl100k_base encoding manually registered", file=sys.stderr)
                
            except Exception as manual_error:
                print(f"⚠️ Could not register cl100k_base encoding: {manual_error}", file=sys.stderr)
                # Fallback: Patch the encoding function to use gpt2 instead
                original_get_encoding = tiktoken.get_encoding
                def patched_get_encoding(name):
                    if name == 'cl100k_base':
                        print("🔄 Using gpt2 encoding as fallback for cl100k_base", file=sys.stderr)
                        return original_get_encoding('gpt2')
                    return original_get_encoding(name)
                tiktoken.get_encoding = patched_get_encoding
                print("🔄 Patched tiktoken to use gpt2 as fallback", file=sys.stderr)
except ImportError:
    print("⚠️ tiktoken not available, embeddings may not work optimally", file=sys.stderr)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    Prompt,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolRequest,
    ListToolsRequest,
    ListResourcesRequest,
    ReadResourceRequest,
    ListPromptsRequest,
    GetPromptRequest
)

# Add the gpt_researcher directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import GPT Researcher
try:
    from gpt_researcher import GPTResearcher
    from gpt_researcher.config.config import Config
except ImportError as e:
    print(f"Error importing GPT Researcher: {e}", file=sys.stderr)
    sys.exit(1)

# Import our free search components
try:
    from free_web_retriever import FreeWebSearchRetriever
    FREE_SEARCH_AVAILABLE = True
    print("✅ Free web search available", file=sys.stderr)
    print("🔄 Using RETRIEVER=custom (with free search)", file=sys.stderr)
    
    # Set up ExpertGPT configuration for LLM calls
    import os
    os.environ['OPENAI_BASE_URL'] = 'https://expertgpt.apps1-ir-int.icloud.intel.com/v1'
    os.environ['OPENAI_API_KEY'] = os.environ.get('EGPT_API_KEY', '')
    print("✅ ExpertGPT LLM endpoint configured", file=sys.stderr)
    print("� Embeddings enabled for context compression", file=sys.stderr)
    
except ImportError:
    FREE_SEARCH_AVAILABLE = False
    print("⚠️ Free web search not available", file=sys.stderr)

# Initialize the MCP server
server = Server("gpt-researcher")

# Global reference to write stream for notifications
_write_stream = None
_is_executable_mode = False
_progress_file = None
_session_id = None

# Free search integration
def debug_llm_configuration(researcher):
    """Debug LLM configuration to understand what's being used"""
    try:
        print("\n🔍 === LLM CONFIGURATION DEBUG ===", file=sys.stderr)
        print(f"📋 Smart LLM: {researcher.cfg.smart_llm}", file=sys.stderr)
        print(f"📋 Smart LLM Provider: {researcher.cfg.smart_llm_provider}", file=sys.stderr)
        print(f"📋 Smart LLM Model: {researcher.cfg.smart_llm_model}", file=sys.stderr)
        print(f"📋 Fast LLM: {researcher.cfg.fast_llm}", file=sys.stderr)
        print(f"📋 Strategic LLM: {researcher.cfg.strategic_llm}", file=sys.stderr)
        print(f"📋 Temperature: {researcher.cfg.temperature}", file=sys.stderr)
        
        # Check environment variables
        import os
        print(f"🌐 OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}", file=sys.stderr)
        print(f"🌐 EGPT_API_KEY: {'Set' if os.environ.get('EGPT_API_KEY') else 'Not set'}", file=sys.stderr)
        print(f"🌐 OPENAI_BASE_URL: {os.environ.get('OPENAI_BASE_URL', 'Not set')}", file=sys.stderr)
        print(f"🌐 OPENAI_API_BASE: {os.environ.get('OPENAI_API_BASE', 'Not set')}", file=sys.stderr)
        
        # Test LLM initialization
        try:
            from gpt_researcher.utils.llm import get_llm
            llm = get_llm(researcher.cfg.smart_llm_provider, model=researcher.cfg.smart_llm_model)
            print(f"✅ LLM initialized successfully: {type(llm)}", file=sys.stderr)
            
            # Check if it has the right base URL
            if hasattr(llm, 'openai_api_base'):
                print(f"📍 LLM Base URL: {llm.openai_api_base}", file=sys.stderr)
            elif hasattr(llm, 'base_url'):
                print(f"📍 LLM Base URL: {llm.base_url}", file=sys.stderr)
            else:
                print(f"⚠️ No base URL found in LLM configuration", file=sys.stderr)
                
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}", file=sys.stderr)
            
        print("🔍 === END LLM DEBUG ===\n", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ LLM debug failed: {e}", file=sys.stderr)

def use_free_search_if_available(researcher):
    """Configure researcher to use our custom retriever with free search"""
    if FREE_SEARCH_AVAILABLE:
        try:
            # Force the researcher to use our custom retriever
            print(f"🔄 Configuring researcher for custom retriever (free search)", file=sys.stderr)
            
            # Override the researcher's configuration to use custom retriever
            researcher.cfg.retriever = "custom"
            researcher.cfg.retrievers = ["custom"]
            
            # Debug LLM configuration
            debug_llm_configuration(researcher)
            
            print("✅ Researcher configured to use custom retriever with free search", file=sys.stderr)
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to configure free search: {e}", file=sys.stderr)
            return False
    
    return False

def detect_executable_mode():
    """Detect if we're running as a PyInstaller executable"""
    global _is_executable_mode
    _is_executable_mode = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    return _is_executable_mode

def init_progress_tracking():
    """Initialize progress tracking for executable mode"""
    global _progress_file, _session_id
    if _is_executable_mode:
        try:
            # Create a unique session ID and progress file
            _session_id = f"session_{int(time.time())}"
            temp_dir = Path.cwd() / "mcp_progress"
            temp_dir.mkdir(exist_ok=True)
            _progress_file = temp_dir / f"progress_{_session_id}.json"
            
            # Initialize progress file
            progress_data = {
                "session_id": _session_id,
                "started_at": datetime.now().isoformat(),
                "status": "initialized",
                "mode": "executable",
                "progress_log": [],
                "current_operation": "Starting MCP server...",
                "progress_percent": 0.0
            }
            
            with open(_progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
                
            print(f"📊 Progress tracking initialized: {_progress_file}", file=sys.stderr)
            
        except Exception as e:
            print(f"⚠️ Failed to initialize progress tracking: {e}", file=sys.stderr)
            _progress_file = None

def update_progress_file(message: str, progress: float = None, operation_data: dict = None):
    """Update the progress file for executable mode"""
    global _progress_file, _session_id
    
    if not _progress_file or not _is_executable_mode:
        return
        
    try:
        # Read current progress data
        progress_data = {}
        if _progress_file.exists():
            with open(_progress_file, 'r') as f:
                progress_data = json.load(f)
        
        # Update progress data
        timestamp = datetime.now().isoformat()
        progress_entry = {
            "timestamp": timestamp,
            "message": message,
            "progress": progress if progress is not None else progress_data.get("progress_percent", 0.0)
        }
        
        if operation_data:
            progress_entry.update(operation_data)
        
        # Add to progress log
        if "progress_log" not in progress_data:
            progress_data["progress_log"] = []
        progress_data["progress_log"].append(progress_entry)
        
        # Update current status
        progress_data["last_updated"] = timestamp
        progress_data["current_operation"] = message
        if progress is not None:
            progress_data["progress_percent"] = progress
        
        # Keep only last 50 progress entries to prevent file bloat
        if len(progress_data["progress_log"]) > 50:
            progress_data["progress_log"] = progress_data["progress_log"][-50:]
        
        # Write updated progress data
        with open(_progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
            
        # Also force flush stderr with timestamp for immediate feedback
        print(f"[{timestamp}] {message}", file=sys.stderr, flush=True)
        
    except Exception as e:
        # Silently continue if progress file update fails
        print(f"⚠️ Progress file update failed: {e}", file=sys.stderr, flush=True)

def send_progress_notification_mcp(message: str, progress: float = None):
    """Send proper MCP progress notification (for Python script mode)"""
    global _write_stream
    try:
        if _write_stream:
            notification = {
                "jsonrpc": "2.0",
                "method": "notifications/progress",
                "params": {
                    "message": message,
                    "progress": progress if progress is not None else 0.0
                }
            }
            # Write the notification synchronously to stdout
            print(json.dumps(notification), flush=True)
    except Exception as e:
        # Fallback to stderr if MCP notification fails
        print(f"Progress (fallback): {message}", file=sys.stderr)

def send_progress_notification_stderr(message: str, progress: float = None):
    """Send progress notification to stderr (for executable mode)"""
    try:
        if progress is not None:
            print(f"Progress: {message} ({progress:.1%})", file=sys.stderr)
        else:
            print(f"Progress: {message}", file=sys.stderr)
    except Exception as e:
        # Silently continue if even stderr fails
        pass

def send_progress_notification(message: str, progress: float = None, operation_data: dict = None):
    """Send a progress notification using the appropriate method"""
    if _is_executable_mode:
        # For executable mode: stderr + file-based tracking
        send_progress_notification_stderr(message, progress)
        update_progress_file(message, progress, operation_data)
    else:
        # For Python script mode: MCP notifications
        send_progress_notification_mcp(message, progress)

# Report types supported by GPT Researcher
SUPPORTED_REPORT_TYPES = [
    "research_report",
    "custom_report", 
    "subtopic_report",
    "outline_report",
]

async def conduct_research_task(arguments: dict) -> list[dict]:
    '''
    Conduct comprehensive research with progress updates and detailed error reporting
    '''
    query = arguments.get('query', '').strip()
    report_type = arguments.get('report_type', 'research_report')
    
    if not query:
        return [{
            "type": "text",
            "text": "Error: Query is required. Please provide a research topic or question."
        }]
    
    if report_type not in SUPPORTED_REPORT_TYPES:
        report_type = "research_report"
    
    try:
        send_progress_notification(f"🔍 Starting research on: {query}", 0.1)
        
        # Initialize GPT Researcher
        researcher = GPTResearcher(query=query, report_type=report_type)
        
        # Debug initial configuration
        print(f"\n🔍 === INITIAL RESEARCHER CONFIG ===", file=sys.stderr)
        update_progress_file("Debug: Initial researcher configuration", 0.12)
        print(f"📋 Report type: {report_type}", file=sys.stderr)
        print(f"📋 Retriever: {researcher.cfg.retriever}", file=sys.stderr)
        print(f"📋 LLM Provider: {researcher.cfg.smart_llm_provider}", file=sys.stderr)
        print(f"📋 LLM Model: {researcher.cfg.smart_llm_model}", file=sys.stderr)
        print(f"🔍 === END INITIAL CONFIG ===\n", file=sys.stderr)
        
        # Try to use free search if available
        free_search_enabled = use_free_search_if_available(researcher)
        if free_search_enabled:
            send_progress_notification("🆓 Using FREE web search (no API keys needed)", 0.15)
        else:
            send_progress_notification("📡 Using default search retrievers", 0.15)
        
        # Log configuration details for debugging
        config = researcher.cfg
        print(f"🔧 Research configuration:", file=sys.stderr)
        update_progress_file("Logging research configuration", 0.18)
        print(f"   Retrievers: {[r.__name__ for r in researcher.retrievers]}", file=sys.stderr)
        print(f"   Max iterations: {config.max_iterations}", file=sys.stderr)
        print(f"   Max search results per query: {config.max_search_results_per_query}", file=sys.stderr)
        print(f"   Report type: {report_type}", file=sys.stderr)
        print(f"   LLM Provider: {config.smart_llm_provider}", file=sys.stderr)
        
        send_progress_notification("⚙️ Configuring research parameters...", 0.2)
        
        # Conduct research with progress updates
        send_progress_notification("🌐 Conducting web research...", 0.3)
        
        # Add progress tracking hooks
        print(f"🕐 Research started at: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
        update_progress_file("Web research phase started", 0.35)
        
        # Add periodic progress tracking during research
        import asyncio
        
        async def track_research_progress():
            """Track research progress periodically"""
            for i in range(20):  # Check 20 times over ~5 minutes
                await asyncio.sleep(15)  # 15 second intervals
                progress = 0.35 + (i * 0.0125)  # Increment from 35% to 60%
                update_progress_file(f"Web search in progress... (step {i+1}/20)", progress)
                print(f"🔄 Research progress check {i+1}/20 at {datetime.now().isoformat()}", file=sys.stderr, flush=True)
                
                # Add hang detection warnings
                if i >= 12:  # After 3 minutes
                    update_progress_file(f"WARNING: Research taking longer than expected (step {i+1}/20)", progress, {
                        "warning": "extended_duration",
                        "duration_seconds": (i+1) * 15
                    })
        
        # Start background progress tracking
        progress_task = asyncio.create_task(track_research_progress())
        
        try:
            # Use asyncio.wait_for with an 8-minute timeout for comprehensive research
            research_result = await asyncio.wait_for(
                researcher.conduct_research(), 
                timeout=480  # 8 minutes timeout
            )
            progress_task.cancel()  # Stop progress tracking
            try:
                await progress_task
            except asyncio.CancelledError:
                pass
        except asyncio.TimeoutError:
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass
            
            # Log timeout error
            error_msg = "Research timed out after 8 minutes"
            print(f"❌ {error_msg}", file=sys.stderr, flush=True)
            update_progress_file(f"TIMEOUT: {error_msg}", 0.0, {
                "error_type": "TimeoutError",
                "timeout_duration": 480,
                "last_progress": "Web research operations"
            })
            
            return [{
                "type": "text",
                "text": f"Error: {error_msg}\n\nThe web research operations took too long to complete. This may be due to network issues, rate limiting, or API problems. Please try again in a few minutes."
            }]
        except Exception as e:
            progress_task.cancel()  # Stop progress tracking on error
            try:
                await progress_task
            except asyncio.CancelledError:
                pass
            raise e
        
        print(f"🕐 Research completed at: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
        update_progress_file("Web research phase completed", 0.6)
        
        # Log research results for debugging
        context_length = len(researcher.get_research_context()) if hasattr(researcher, 'get_research_context') else 0
        sources_found = len(research_result) if research_result else 0
        urls_visited = len(researcher.visited_urls) if hasattr(researcher, 'visited_urls') else 0
        
        print(f"📊 Research completed:", file=sys.stderr)
        update_progress_file("Research phase completed - analyzing results", 0.65, {
            "sources_found": sources_found,
            "context_length": context_length,
            "urls_visited": urls_visited
        })
        print(f"   Sources found: {sources_found}", file=sys.stderr)
        print(f"   Context length: {context_length}", file=sys.stderr)
        print(f"   URLs visited: {urls_visited}", file=sys.stderr)
        
        # Check if we actually got any sources/context
        if context_length == 0:
            # No sources found - provide detailed error report
            error_details = []
            error_details.append("🚫 **RESEARCH FAILED: No sources could be retrieved**")
            error_details.append("")
            error_details.append("**Critical Issue:**")
            error_details.append("The research process was unable to gather any usable sources.")
            error_details.append("This means any generated report would be based only on the LLM's")
            error_details.append("training data, which may be outdated and not reflect current information.")
            error_details.append("")
            error_details.append("**Potential root causes:**")
            error_details.append("• **Network connectivity:** Internet connection issues")
            error_details.append("• **API rate limits:** Search providers (DuckDuckGo, Tavily, Bing) are limiting requests")
            error_details.append("• **Missing API keys:** TAVILY_API_KEY or other required keys not configured")
            error_details.append("• **Content filtering:** All found sources filtered out as irrelevant")
            error_details.append("• **Query issues:** Search terms too broad, narrow, or containing restricted content")
            error_details.append("• **Geographic blocks:** Some content may be geo-restricted")
            error_details.append("• **Firewall/proxy:** Corporate or network firewall blocking web requests")
            error_details.append("")
            
            # Retriever configuration analysis
            if researcher.retrievers:
                retriever_names = [r.__name__ for r in researcher.retrievers]
                error_details.append(f"**Configured retrievers:** {', '.join(retriever_names)}")
            else:
                error_details.append("**CRITICAL ERROR:** No retrievers configured!")
            
            error_details.append("")
            error_details.append("**Research attempt details:**")
            error_details.append(f"• Query: '{query}'")
            error_details.append(f"• Report type: {report_type}")
            error_details.append(f"• Max iterations: {config.max_iterations}")
            error_details.append(f"• Max search results per query: {config.max_search_results_per_query}")
            error_details.append(f"• Research context gathered: {context_length} characters")
            error_details.append(f"• URLs attempted: {urls_visited}")
            
            if hasattr(researcher, 'visited_urls') and researcher.visited_urls:
                error_details.append("• Sample URLs attempted:")
                for url in list(researcher.visited_urls)[:5]:
                    error_details.append(f"  - {url}")
            else:
                error_details.append("• No URLs were visited (possible configuration issue)")
            
            error_details.append("")
            error_details.append("**Troubleshooting recommendations:**")
            error_details.append("1. **Verify connectivity:** Test internet access with web browser")
            error_details.append("2. **Check API keys:** Ensure TAVILY_API_KEY and other keys are properly set")
            error_details.append("3. **Refine query:** Try more specific or different search terms")
            error_details.append("4. **Wait and retry:** If rate-limited, wait 5-10 minutes before retrying")
            error_details.append("5. **Try quick research:** Use quick_research function for lighter testing")
            error_details.append("6. **Check logs:** Look for specific error messages in stderr output")
            
            error_response = "\n".join(error_details)
            
            send_progress_notification("❌ No sources found - research failed", 0.0)
            
            return [{
                "type": "text", 
                "text": error_response
            }]
        elif context_length < 1000:
            # Very limited sources - warn user but proceed
            send_progress_notification(f"⚠️ Limited sources ({context_length} chars) - proceeding...", 0.6)
        else:
            send_progress_notification(f"✅ Found {sources_found} sources, {context_length} chars context", 0.6)
        
        send_progress_notification("📝 Analyzing findings and generating report...", 0.7)
        
        # Add detailed logging for report generation
        print(f"📝 Starting report generation at: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
        update_progress_file("Report generation started", 0.75, {
            "context_chars": context_length,
            "sources_found": sources_found
        })
        
        # Generate report with timeout and error handling
        try:
            print(f"📝 Calling researcher.write_report()...", file=sys.stderr, flush=True)
            report = await asyncio.wait_for(
                researcher.write_report(), 
                timeout=180  # 3 minutes timeout for comprehensive report generation
            )
            print(f"📝 Report generation completed successfully at: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
            
        except asyncio.TimeoutError:
            error_msg = "Report generation timed out after 3 minutes"
            print(f"❌ {error_msg}", file=sys.stderr, flush=True)
            update_progress_file(f"TIMEOUT: {error_msg}", 0.0, {
                "error_type": "ReportTimeoutError",
                "timeout_duration": 180,
                "context_available": context_length
            })
            
            return [{
                "type": "text",
                "text": f"Error: {error_msg}\n\nThe report generation took too long despite having {context_length} characters of research context. This may be due to LLM API issues or complex content processing."
            }]
            
        except Exception as report_error:
            error_msg = f"Report generation failed: {str(report_error)}"
            print(f"❌ {error_msg}", file=sys.stderr, flush=True)
            import traceback
            report_traceback = traceback.format_exc()
            print(f"Report generation traceback: {report_traceback}", file=sys.stderr, flush=True)
            
            update_progress_file(f"ERROR: {error_msg}", 0.0, {
                "error_type": type(report_error).__name__,
                "error_details": str(report_error),
                "context_available": context_length,
                "traceback_preview": report_traceback[:500]
            })
            
            return [{
                "type": "text",
                "text": f"Error: {error_msg}\n\nResearch was successful (found {context_length} chars of context), but report generation failed. Check logs for details."
            }]
        
        print(f"📝 Report generation completed at: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
        update_progress_file("Report generation completed", 0.95, {
            "report_length": len(report) if report else 0
        })
        
        send_progress_notification("✅ Research completed successfully!", 1.0, {
            "sources_found": sources_found,
            "urls_visited": urls_visited,
            "context_length": context_length,
            "report_type": report_type,
            "query": query
        })
        
        # Format the response with comprehensive metadata
        response_text = f"""# Research Report: {query}

**Report Type:** {report_type}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Sources Found:** {sources_found}
**URLs Visited:** {urls_visited}
**Context Length:** {context_length} characters
**Research Quality:** {'High' if context_length > 3000 else 'Medium' if context_length > 1000 else 'Limited'}

---

{report}

---

*Report generated by ExpertGPT Researcher*
*Research conducted with {sources_found} sources and {context_length} characters of context*
"""
        
        # Debug: Log that we're about to return the response
        print(f"🎯 About to return response with {len(response_text)} characters", file=sys.stderr, flush=True)
        update_progress_file("Preparing to return final response", 1.0, {
            "response_length": len(response_text),
            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
        })
        
        final_response = [{
            "type": "text",
            "text": response_text
        }]
        
        # Debug: Log the response structure
        print(f"🎯 Final response structure: {len(final_response)} items, first item type: {final_response[0]['type']}", file=sys.stderr, flush=True)
        
        return final_response
        
    except Exception as e:
        error_msg = f"Research failed: {str(e)}"
        send_progress_notification(f"❌ {error_msg}", 0.0)
        print(f"❌ {error_msg}", file=sys.stderr)
        import traceback
        print(f"Full traceback: {traceback.format_exc()}", file=sys.stderr)
        return [{
            "type": "text",
            "text": f"Error: {error_msg}\n\nPlease check the logs for detailed error information."
        }]

async def quick_research(arguments: dict) -> list[dict]:
    '''
    Conduct quick research with progress updates and detailed error reporting
    '''
    query = arguments.get('query', '').strip()
    
    if not query:
        return [{
            "type": "text",
            "text": "Error: Query is required. Please provide a research topic or question."
        }]
    
    try:
        send_progress_notification(f"⚡ Starting quick research: {query}", 0.1)
        
        # Initialize GPT Researcher with custom settings for quick research
        researcher = GPTResearcher(query=query, report_type="research_report")
        
        # Try to use free search if available
        free_search_enabled = use_free_search_if_available(researcher)
        if free_search_enabled:
            send_progress_notification("🆓 Using FREE web search (no API keys needed)", 0.2)
        else:
            send_progress_notification("📡 Using default search retrievers", 0.2)
        
        # Override some config for faster results
        config = researcher.cfg
        config.max_iterations = 2  # Fewer iterations
        config.max_search_results_per_query = 3  # Fewer sources per query
        
        # Log configuration details for debugging
        print(f"🔧 Research configuration:", file=sys.stderr)
        update_progress_file("Quick research: logging configuration", 0.35)
        print(f"   Retrievers: {[r.__name__ for r in researcher.retrievers]}", file=sys.stderr)
        print(f"   Max iterations: {config.max_iterations}", file=sys.stderr)
        print(f"   Max search results per query: {config.max_search_results_per_query}", file=sys.stderr)
        print(f"   LLM Provider: {config.smart_llm_provider}", file=sys.stderr)
        
        send_progress_notification("🔎 Gathering initial sources...", 0.4)
        
        # Add detailed logging for research process
        print(f"🔍 Starting research with {len(researcher.retrievers)} retrievers", file=sys.stderr, flush=True)
        update_progress_file("Initializing retrievers", 0.45, {"retrievers": len(researcher.retrievers)})
        
        # Add detailed logging for quick research
        print(f"🔍 Quick research starting with {len(researcher.retrievers)} retrievers", file=sys.stderr, flush=True)
        update_progress_file("Quick research: initializing retrievers", 0.45, {
            "max_iterations": config.max_iterations,
            "max_results_per_query": config.max_search_results_per_query
        })
        
        # Conduct research with detailed error tracking
        print(f"📡 Beginning quick search operations...", file=sys.stderr, flush=True)
        update_progress_file("Quick research: starting search", 0.5)
        
        # Add periodic progress tracking for quick research
        async def track_quick_research_progress():
            """Track quick research progress periodically"""
            for i in range(12):  # Check 12 times over ~3 minutes (extended)
                await asyncio.sleep(15)  # 15 second intervals
                progress = 0.5 + (i * 0.02)  # Increment from 50% to 74%
                update_progress_file(f"Quick search in progress... (step {i+1}/12)", progress)
                print(f"🔄 Quick research progress check {i+1}/12 at {datetime.now().isoformat()}", file=sys.stderr, flush=True)
                
                # Add hang detection - if we've been running too long, log warning
                if i >= 8:  # After 2 minutes
                    update_progress_file(f"WARNING: Research taking longer than expected (step {i+1}/12)", progress, {
                        "warning": "extended_duration",
                        "duration_seconds": (i+1) * 15
                    })
        
        # Start background progress tracking for quick research
        quick_progress_task = asyncio.create_task(track_quick_research_progress())
        
        # Add timeout protection for the research call
        try:
            # Use asyncio.wait_for with a 4-minute timeout for quick research
            research_result = await asyncio.wait_for(
                researcher.conduct_research(), 
                timeout=240  # 4 minutes timeout
            )
            quick_progress_task.cancel()  # Stop progress tracking
            try:
                await quick_progress_task
            except asyncio.CancelledError:
                pass
        except asyncio.TimeoutError:
            quick_progress_task.cancel()
            try:
                await quick_progress_task
            except asyncio.CancelledError:
                pass
            
            # Log timeout error
            error_msg = "Quick research timed out after 4 minutes"
            print(f"❌ {error_msg}", file=sys.stderr, flush=True)
            update_progress_file(f"TIMEOUT: {error_msg}", 0.0, {
                "error_type": "TimeoutError",
                "timeout_duration": 240,
                "last_progress": "Quick search operations"
            })
            
            return [{
                "type": "text",
                "text": f"Error: {error_msg}\n\nThe web search operations took too long to complete. This may be due to network issues, rate limiting, or API problems. Please try again in a few minutes."
            }]
        except Exception as e:
            quick_progress_task.cancel()  # Stop progress tracking on error
            try:
                await quick_progress_task
            except asyncio.CancelledError:
                pass
            raise e
        
        print(f"📡 Quick search operations completed", file=sys.stderr, flush=True)
        update_progress_file("Quick research: search completed", 0.7)
        
        # Log research results for debugging
        print(f"📊 Research completed:", file=sys.stderr)
        update_progress_file("Quick research: analyzing results", 0.75, {
            "sources_found": len(research_result) if research_result else 0,
            "context_length": len(researcher.get_research_context()) if hasattr(researcher, 'get_research_context') else 0,
            "urls_visited": len(researcher.visited_urls) if hasattr(researcher, 'visited_urls') else 0
        })
        print(f"   Sources found: {len(research_result) if research_result else 0}", file=sys.stderr)
        print(f"   Context length: {len(researcher.get_research_context()) if hasattr(researcher, 'get_research_context') else 'Unknown'}", file=sys.stderr)
        print(f"   Visited URLs: {len(researcher.visited_urls) if hasattr(researcher, 'visited_urls') else 'Unknown'}", file=sys.stderr)
        
        # Check if we actually got any sources/context
        context_length = len(researcher.get_research_context()) if hasattr(researcher, 'get_research_context') else 0
        if context_length == 0:
            # No sources found - provide detailed error report
            error_details = []
            error_details.append("� **RESEARCH FAILED: No sources could be retrieved**")
            error_details.append("")
            error_details.append("**Possible causes:**")
            error_details.append("• Network connectivity issues")
            error_details.append("• API rate limits reached (DuckDuckGo, Tavily, etc.)")
            error_details.append("• Search retrievers not properly configured")
            error_details.append("• All search results filtered out as irrelevant")
            error_details.append("• Firewall or proxy blocking web requests")
            error_details.append("")
            
            # Check retriever configuration
            if researcher.retrievers:
                retriever_names = [r.__name__ for r in researcher.retrievers]
                error_details.append(f"**Configured retrievers:** {', '.join(retriever_names)}")
            else:
                error_details.append("**ERROR:** No retrievers configured!")
            
            error_details.append("")
            error_details.append("**Debugging information:**")
            error_details.append(f"• Query: '{query}'")
            error_details.append(f"• Max search results per query: {config.max_search_results_per_query}")
            error_details.append(f"• Max iterations: {config.max_iterations}")
            error_details.append(f"• Research context length: {context_length}")
            
            if hasattr(researcher, 'visited_urls'):
                error_details.append(f"• URLs visited: {len(researcher.visited_urls)}")
                if researcher.visited_urls:
                    error_details.append("• Visited URL samples:")
                    for url in list(researcher.visited_urls)[:3]:
                        error_details.append(f"  - {url}")
            
            error_details.append("")
            error_details.append("**Recommendations:**")
            error_details.append("1. Check internet connectivity")
            error_details.append("2. Verify API keys are set (TAVILY_API_KEY, etc.)")
            error_details.append("3. Try a different, more specific query")
            error_details.append("4. Check if search services are rate-limiting")
            error_details.append("5. Try running the research again in a few minutes")
            
            error_response = "\n".join(error_details)
            
            send_progress_notification("❌ No sources found - research failed", 0.0)
            
            return [{
                "type": "text", 
                "text": error_response
            }]
        
        send_progress_notification("📄 Generating quick report...", 0.8)
        
        # Add detailed logging for report generation
        print(f"📝 Starting report generation at: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
        update_progress_file("Quick research: report generation started", 0.8, {
            "context_chars": context_length,
            "sources_found": len(research_result) if research_result else 0
        })
        
        # Generate report with timeout and error handling
        try:
            print(f"📝 Calling researcher.write_report()...", file=sys.stderr, flush=True)
            
            # Add a small delay to ensure the log is written
            await asyncio.sleep(0.1)
            
            # Try calling the report generation with more defensive handling
            try:
                # First check if the method exists and is callable
                if not hasattr(researcher, 'write_report'):
                    raise AttributeError("researcher object has no write_report method")
                
                if not callable(researcher.write_report):
                    raise AttributeError("researcher.write_report is not callable")
                
                print(f"📝 write_report method confirmed, starting generation...", file=sys.stderr, flush=True)
                
                # Call the report generation with timeout
                report = await asyncio.wait_for(
                    researcher.write_report(), 
                    timeout=120  # 2 minutes timeout for report generation
                )
                
                print(f"📝 Report generation completed successfully at: {datetime.now().isoformat()}", file=sys.stderr, flush=True)
                print(f"📝 Report length: {len(report) if report else 0} characters", file=sys.stderr, flush=True)
                
            except AttributeError as attr_error:
                error_msg = f"Researcher method error: {str(attr_error)}"
                print(f"❌ {error_msg}", file=sys.stderr, flush=True)
                
                # Try alternative report generation if available
                try:
                    print(f"🔄 Attempting alternative report generation...", file=sys.stderr, flush=True)
                    
                    # Check for alternative methods
                    if hasattr(researcher, 'generate_report'):
                        report = await researcher.generate_report()
                    elif hasattr(researcher, 'create_report'):
                        report = await researcher.create_report()
                    else:
                        # Manual report creation from context
                        context = researcher.get_research_context() if hasattr(researcher, 'get_research_context') else ""
                        report = f"# Research Report: {query}\n\n**Generated using fallback method**\n\n{context[:5000]}..."
                        
                    print(f"🔄 Alternative report generation successful", file=sys.stderr, flush=True)
                    
                except Exception as alt_error:
                    report = f"# Research Report: {query}\n\n**Error during report generation**\n\nResearch was successful but report generation failed.\nContext gathered: {context_length} characters from {len(researcher.visited_urls) if hasattr(researcher, 'visited_urls') else 'unknown'} URLs.\n\nError: {str(attr_error)}"
                    
            except Exception as inner_error:
                # Re-raise to be caught by outer exception handler
                raise inner_error
                
        except asyncio.TimeoutError:
            error_msg = "Report generation timed out after 2 minutes"
            print(f"❌ {error_msg}", file=sys.stderr, flush=True)
            update_progress_file(f"TIMEOUT: {error_msg}", 0.0, {
                "error_type": "ReportTimeoutError",
                "timeout_duration": 120,
                "context_available": context_length
            })
            
            return [{
                "type": "text",
                "text": f"Error: {error_msg}\n\nThe report generation took too long despite having {context_length} characters of research context. This may be due to LLM API issues or complex content processing."
            }]
            
        except Exception as report_error:
            error_msg = f"Report generation failed: {str(report_error)}"
            print(f"❌ {error_msg}", file=sys.stderr, flush=True)
            import traceback
            report_traceback = traceback.format_exc()
            print(f"Report generation traceback: {report_traceback}", file=sys.stderr, flush=True)
            
            update_progress_file(f"ERROR: {error_msg}", 0.0, {
                "error_type": type(report_error).__name__,
                "error_details": str(report_error),
                "context_available": context_length,
                "traceback_preview": report_traceback[:500]
            })
            
            # Create a fallback report with the research context
            try:
                context = researcher.get_research_context() if hasattr(researcher, 'get_research_context') else ""
                fallback_report = f"""# Research Report: {query}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** Fallback report due to generation error
**Context Length:** {context_length} characters
**URLs Visited:** {len(researcher.visited_urls) if hasattr(researcher, 'visited_urls') else 'Unknown'}

## Error Information
Report generation failed with error: {str(report_error)}

## Research Context
{context[:3000]}{'...' if len(context) > 3000 else ''}

---
*Fallback report generated after successful research but failed report generation*
"""
                
                return [{
                    "type": "text",
                    "text": fallback_report
                }]
                
            except Exception as fallback_error:
                return [{
                    "type": "text",
                    "text": f"Error: {error_msg}\n\nResearch was successful (found {context_length} chars of context), but report generation failed. Fallback report creation also failed: {str(fallback_error)}"
                }]
        
        send_progress_notification("✅ Quick research completed!", 1.0, {
            "sources_found": len(research_result) if research_result else 0,
            "urls_visited": len(researcher.visited_urls) if hasattr(researcher, 'visited_urls') else 0,
            "context_length": context_length,
            "query": query
        })
        
        # Get source information for detailed reporting
        sources_found = len(research_result) if research_result else 0
        urls_visited = len(researcher.visited_urls) if hasattr(researcher, 'visited_urls') else 0
        
        # Format the response with detailed source information
        response_text = f"""# Quick Research: {query}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Sources Found:** {sources_found}
**URLs Visited:** {urls_visited}
**Context Length:** {context_length} characters

{report}

---

*Quick research by ExpertGPT Researcher*
"""
        
        # Debug: Log that we're about to return the response
        print(f"🎯 About to return quick research response with {len(response_text)} characters", file=sys.stderr, flush=True)
        update_progress_file("Preparing to return quick research response", 1.0, {
            "response_length": len(response_text),
            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
        })
        
        final_response = [{
            "type": "text",
            "text": response_text
        }]
        
        # Debug: Log the response structure
        print(f"🎯 Quick research final response: {len(final_response)} items, first item type: {final_response[0]['type']}", file=sys.stderr, flush=True)
        
        return final_response
        
    except Exception as e:
        error_msg = f"Quick research failed: {str(e)}"
        send_progress_notification(f"❌ {error_msg}", 0.0)
        print(f"❌ {error_msg}", file=sys.stderr, flush=True)
        import traceback
        full_traceback = traceback.format_exc()
        print(f"Full traceback: {full_traceback}", file=sys.stderr, flush=True)
        
        # Log error to progress file
        update_progress_file(f"ERROR: {error_msg}", 0.0, {
            "error_type": type(e).__name__,
            "error_details": str(e),
            "traceback_preview": full_traceback[:500]
        })
        
        return [{
            "type": "text",
            "text": f"Error: {error_msg}\n\nPlease check the logs for detailed error information."
        }]

async def generate_subtopics(arguments: dict) -> list[dict]:
    '''
    Generate subtopics for a research area
    '''
    query = arguments.get('query', '').strip()
    max_subtopics = arguments.get('max_subtopics', 5)
    
    if not query:
        return [{
            "type": "text",
            "text": "Error: Query is required. Please provide a main research topic."
        }]
    
    try:
        send_progress_notification(f"🧠 Generating subtopics for: {query}", 0.3)
        
        # Initialize researcher for subtopic generation
        researcher = GPTResearcher(query=query, report_type="subtopic_report")
        
        send_progress_notification("🔍 Analyzing topic structure...", 0.7)
        
        # Use GPT Researcher's built-in subtopic generation
        from gpt_researcher.utils.llm import construct_subtopics
        
        subtopics_response = await construct_subtopics(
            task=query,
            data="",  # No prior context
            config=researcher.cfg,
            subtopics=max_subtopics,
            prompt_family=None,
        )
        
        send_progress_notification("✅ Subtopics generated successfully!", 1.0)
        
        response_text = f"""# Subtopics for: {query}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Number of Subtopics:** {max_subtopics}

{subtopics_response}

---

*Subtopics generated by ExpertGPT Researcher*
"""
        
        return [{
            "type": "text",
            "text": response_text
        }]
        
    except Exception as e:
        error_msg = f"Subtopic generation failed: {str(e)}"
        send_progress_notification(f"❌ {error_msg}", 0.0)
        print(f"❌ {error_msg}", file=sys.stderr)
        return [{
            "type": "text",
            "text": f"Error: {error_msg}"
        }]

async def check_system_status(arguments: dict) -> list[dict]:
    '''
    Check GPT Researcher system status and configuration
    '''
    try:
        send_progress_notification("🔧 Checking system configuration...", 0.5)
        
        config = Config()
        
        # Basic configuration check
        status_info = {
            "system_status": "✅ Operational",
            "llm_provider": getattr(config, 'smart_llm_provider', 'Unknown'),
            "llm_model": getattr(config, 'smart_llm_model', 'Unknown'),
            "api_base": getattr(config, 'openai_api_base', getattr(config, 'smart_llm_api_base', 'Unknown')),
            "retrievers": getattr(config, 'retrievers', ['Unknown']),
            "max_search_results": getattr(config, 'max_search_results_per_query', 'Unknown'),
            "max_iterations": getattr(config, 'max_iterations', 'Unknown'),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        send_progress_notification("✅ System status check completed!", 1.0)
        
        status_text = f"""# GPT Researcher System Status

**Status:** {status_info['system_status']}
**Timestamp:** {status_info['timestamp']}

## Configuration
- **LLM Provider:** {status_info['llm_provider']}
- **LLM Model:** {status_info['llm_model']}
- **API Base:** {status_info['api_base']}
- **Retrievers:** {', '.join(status_info['retrievers']) if isinstance(status_info['retrievers'], list) else status_info['retrievers']}
- **Max Search Results:** {status_info['max_search_results']}
- **Max Iterations:** {status_info['max_iterations']}

## Available Tools
- conduct-research: Comprehensive AI-powered research
- quick-research: Fast research with fewer sources
- generate-subtopics: Generate subtopics for research areas
- check-status: System status and configuration check

---

*Status check by GPT Researcher MCP Server*
"""
        
        return [{
            "type": "text",
            "text": status_text
        }]
        
    except Exception as e:
        error_msg = f"Status check failed: {str(e)}"
        send_progress_notification(f"❌ {error_msg}", 0.0)
        print(f"❌ {error_msg}", file=sys.stderr)
        return [{
            "type": "text",
            "text": f"Error: {error_msg}"
        }]

# MCP Server Implementation
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="conduct-research",
            description="Conduct comprehensive AI-powered research on any topic with progress updates",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Research topic or question"
                    },
                    "report_type": {
                        "type": "string",
                        "enum": SUPPORTED_REPORT_TYPES,
                        "default": "research_report",
                        "description": "Type of report to generate"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="quick-research",
            description="Conduct quick research with fewer sources for faster results (with progress updates)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Research topic or question"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="generate-subtopics",
            description="Generate subtopics for a research area",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Main research topic"
                    },
                    "max_subtopics": {
                        "type": "integer",
                        "minimum": 3,
                        "maximum": 10,
                        "default": 5,
                        "description": "Maximum number of subtopics to generate"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="check-status",
            description="Check GPT Researcher system status and configuration",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[dict]:
    """Handle tool calls."""
    print(f"🛠️ MCP Server: Received tool call '{name}' with args: {arguments}", file=sys.stderr, flush=True)
    
    try:
        result = None
        if name == "conduct-research":
            result = await conduct_research_task(arguments)
        elif name == "quick-research":
            result = await quick_research(arguments)
        elif name == "generate-subtopics":
            result = await generate_subtopics(arguments)
        elif name == "check-status":
            result = await check_system_status(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Debug: Log the result before returning
        if result:
            print(f"🛠️ MCP Server: Tool '{name}' completed successfully, returning {len(result)} items", file=sys.stderr, flush=True)
            if result and len(result) > 0 and 'text' in result[0]:
                text_length = len(result[0]['text'])
                print(f"🛠️ MCP Server: First result item has {text_length} characters", file=sys.stderr, flush=True)
        else:
            print(f"🛠️ MCP Server: Tool '{name}' returned empty/null result", file=sys.stderr, flush=True)
        
        return result
        
    except Exception as e:
        print(f"❌ MCP Server: Tool '{name}' failed with error: {e}", file=sys.stderr, flush=True)
        import traceback
        print(f"❌ MCP Server: Full traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
        raise

async def main():
    """Main function to run the MCP server"""
    global _write_stream
    
    try:
        # Detect if we're running as executable or Python script
        is_exe = detect_executable_mode()
        mode_str = "executable" if is_exe else "Python script"
        
        # Ensure UTF-8 encoding for stdout/stderr
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        
        print(f"🚀 Starting GPT Researcher MCP Server (Streaming) in {mode_str} mode...", file=sys.stderr)
        update_progress_file(f"Starting MCP server in {mode_str} mode", 0.05)
        
        # Initialize progress tracking for executable mode
        init_progress_tracking()
        
        # Check basic configuration
        config = Config()
        print(f"📊 LLM Provider: {config.smart_llm_provider}", file=sys.stderr)
        update_progress_file("Checking system configuration", 0.08)
        print(f"🔍 Retrievers: {', '.join(config.retrievers) if hasattr(config, 'retrievers') else 'Unknown'}", file=sys.stderr)
        
        async with stdio_server() as (read_stream, write_stream):
            # Store write stream globally for notifications
            _write_stream = write_stream
            await server.run(read_stream, write_stream, server.create_initialization_options())
            
    except Exception as e:
        print(f"❌ Failed to start MCP server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())