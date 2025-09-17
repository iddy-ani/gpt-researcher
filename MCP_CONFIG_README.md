# MCP Configuration Files

This directory contains configuration files for integrating GPT Researcher as an MCP (Model Context Protocol) server with DataAgent or other MCP-compatible clients.

## Configuration Files

### `dataagent_mcp_config_streaming.json`
**Recommended configuration** for the streaming version of GPT Researcher MCP server.

**Features:**
- Real-time progress notifications
- Streaming responses
- Enhanced performance
- Full MCP protocol compliance

**Usage:**
1. Copy this file to `%APPDATA%\DataAgent\dataagent_mcp_config.json`
2. Update the path to match your executable location
3. Restart DataAgent

```json
{
  "servers": [
    {
      "name": "gpt-researcher-streaming",
      "command": "C:\\path\\to\\your\\gpt-researcher-mcp-streaming.exe",
      "args": [],
      "enabled": true
    }
  ]
}
```

## Environment Variables

Ensure these environment variables are set before running the executable:

```bash
# Required - Intel EGPT API Key
set EGPT_API_KEY=your_intel_api_key_here

# Required - Intel EGPT API Base URL
set OPENAI_BASE_URL=https://expertgpt.apps1-ir-int.icloud.intel.com/v1

# Optional - Configure retrievers (default: duckduckgo)
set RETRIEVER=duckduckgo
```

## Available Tools

The MCP server provides these research tools:

- **quick_research(query: string)** - Fast research on any topic (2-5 minutes)
- **detailed_research(query: string)** - Comprehensive research reports (5-10 minutes)
- **status()** - Check server operational status

## Building the Executable

To build the executable from source:

```bash
python build_mcp_streaming.py
```

This will create:
- `dist/gpt-researcher-mcp-streaming.exe` (111.9 MB standalone executable)
- `gpt-researcher-mcp-streaming.spec` (PyInstaller specification file)

## Troubleshooting

### Common Issues

1. **"EGPT_API_KEY not set"**
   - Ensure the environment variable is set correctly
   - Restart the executable after setting environment variables

2. **"No search results"**
   - Check internet connectivity
   - Verify the DuckDuckGo service is accessible

3. **"MCP protocol error"**
   - Ensure you're using a compatible MCP client
   - Check that the executable is not blocked by antivirus software

### Testing the Executable

Use the provided test script to verify functionality:

```bash
python test_executable_research.py
```

This will test:
- MCP protocol compliance
- Research functionality
- Progress notifications
- Report generation

## Support

For issues and questions:
- Check the main [README.md](README.md) for general setup
- Review the [MCP Integration Guide](https://docs.gptr.dev/docs/gpt-researcher/retrievers/mcp-configs)
- Open an issue on GitHub for bug reports