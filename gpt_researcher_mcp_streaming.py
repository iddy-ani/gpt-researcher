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
from datetime import datetime

# FORCE FREE SEARCH - Set environment before any imports
os.environ['RETRIEVER'] = 'custom'  # Use custom retriever with free search

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
    
except ImportError:
    FREE_SEARCH_AVAILABLE = False
    print("⚠️ Free web search not available", file=sys.stderr)

# Initialize the MCP server
server = Server("gpt-researcher")

# Global reference to write stream for notifications
_write_stream = None
_is_executable_mode = False

# Free search integration
def use_free_search_if_available(researcher):
    """Configure researcher to use our custom retriever with free search"""
    if FREE_SEARCH_AVAILABLE:
        try:
            # Force the researcher to use our custom retriever
            print(f"🔄 Forcing researcher to use custom retriever (free search)", file=sys.stderr)
            
            # Override the researcher's configuration to use custom retriever
            researcher.cfg.retriever = "custom"
            researcher.cfg.retrievers = ["custom"]
            
            # Set environment variable as backup
            import os
            os.environ['RETRIEVER'] = 'custom'
            
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

def send_progress_notification(message: str, progress: float = None):
    """Send a progress notification using the appropriate method"""
    if _is_executable_mode:
        send_progress_notification_stderr(message, progress)
    else:
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
        
        # Try to use free search if available
        free_search_enabled = use_free_search_if_available(researcher)
        if free_search_enabled:
            send_progress_notification("🆓 Using FREE web search (no API keys needed)", 0.15)
        else:
            send_progress_notification("📡 Using default search retrievers", 0.15)
        
        # Log configuration details for debugging
        config = researcher.cfg
        print(f"🔧 Research configuration:", file=sys.stderr)
        print(f"   Retrievers: {[r.__name__ for r in researcher.retrievers]}", file=sys.stderr)
        print(f"   Max iterations: {config.max_iterations}", file=sys.stderr)
        print(f"   Max search results per query: {config.max_search_results_per_query}", file=sys.stderr)
        print(f"   Report type: {report_type}", file=sys.stderr)
        print(f"   LLM Provider: {config.smart_llm_provider}", file=sys.stderr)
        
        send_progress_notification("⚙️ Configuring research parameters...", 0.2)
        
        # Conduct research with progress updates
        send_progress_notification("🌐 Conducting web research...", 0.3)
        research_result = await researcher.conduct_research()
        
        # Log research results for debugging
        context_length = len(researcher.get_research_context()) if hasattr(researcher, 'get_research_context') else 0
        sources_found = len(research_result) if research_result else 0
        urls_visited = len(researcher.visited_urls) if hasattr(researcher, 'visited_urls') else 0
        
        print(f"📊 Research completed:", file=sys.stderr)
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
        
        # Generate report
        report = await researcher.write_report()
        
        send_progress_notification("✅ Research completed successfully!", 1.0)
        
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
        
        return [{
            "type": "text",
            "text": response_text
        }]
        
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
        print(f"   Retrievers: {[r.__name__ for r in researcher.retrievers]}", file=sys.stderr)
        print(f"   Max iterations: {config.max_iterations}", file=sys.stderr)
        print(f"   Max search results per query: {config.max_search_results_per_query}", file=sys.stderr)
        print(f"   LLM Provider: {config.smart_llm_provider}", file=sys.stderr)
        
        send_progress_notification("🔎 Gathering initial sources...", 0.4)
        
        # Conduct research with detailed error tracking
        research_result = await researcher.conduct_research()
        
        # Log research results for debugging
        print(f"📊 Research completed:", file=sys.stderr)
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
        
        send_progress_notification("�📄 Generating quick report...", 0.8)
        
        # Generate report
        report = await researcher.write_report()
        
        send_progress_notification("✅ Quick research completed!", 1.0)
        
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
        
        return [{
            "type": "text",
            "text": response_text
        }]
        
    except Exception as e:
        error_msg = f"Quick research failed: {str(e)}"
        send_progress_notification(f"❌ {error_msg}", 0.0)
        print(f"❌ {error_msg}", file=sys.stderr)
        import traceback
        print(f"Full traceback: {traceback.format_exc()}", file=sys.stderr)
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
    if name == "conduct-research":
        return await conduct_research_task(arguments)
    elif name == "quick-research":
        return await quick_research(arguments)
    elif name == "generate-subtopics":
        return await generate_subtopics(arguments)
    elif name == "check-status":
        return await check_system_status(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

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
        
        # Check basic configuration
        config = Config()
        print(f"📊 LLM Provider: {config.smart_llm_provider}", file=sys.stderr)
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