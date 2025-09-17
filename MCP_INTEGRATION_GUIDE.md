# DataAgent MCP Integration Guide

This document explains how to configure and integrate Model Context Protocol (MCP) servers with the DataAgent application.

## Overview
DataAgent supports connecting to external MCP servers (such as weather-info) to provide tool-based capabilities. MCP servers are managed and called by the backend, and their tools are exposed to the user through the DataAgent UI.

## MCP Server Requirements
- The MCP server must implement the [Model Context Protocol (MCP)](https://github.com/anthropics/model-context-protocol) over standard input/output (stdio).
- The server must support the following JSON-RPC methods:
  - `initialize`
  - `tools/list`
  - `tools/call`
- Each tool must return a response in the format:
  ```json
  {
    "content": [
      {"type": "text", "text": "...your result..."}
      // ...other content types supported by MCP
    ],
    "isError": false
  }
  ```
- The server must use UTF-8 encoding for all stdio communication (important for Unicode/emoji support).

## Configuration File
MCP servers are configured in the file:
```
%APPDATA%\DataAgent\dataagent_mcp_config.json
```
Example configuration:
```json
{
  "servers": [
    {
      "name": "weather-info",
      "command": "C:\\Users\\ianimash\\source\\repos\\debugging\\dist\\weather-info.exe",
      "args": [],
      "enabled": true
    }
  ]
}
```
- `name`: Unique identifier for the MCP server.
- `command`: Full path to the executable or script.
- `args`: (Optional) List of command-line arguments.
- `enabled`: Set to `true` to enable the server.

## How DataAgent Uses MCP
1. **Startup:** DataAgent reads the config and starts each enabled MCP server as a subprocess.
2. **Initialization:** DataAgent sends the `initialize` request and expects a valid MCP handshake.
3. **Tool Discovery:** DataAgent calls `tools/list` to discover available tools.
4. **Tool Calls:** When a user requests a tool, DataAgent sends a `tools/call` request with the tool name and arguments.
5. **Response Handling:** DataAgent expects the tool response to include a `content` array with at least one `{ "type": "text", "text": ... }` item. This text is shown to the user.

## Best Practices for MCP Servers
- Always output UTF-8 to stdout/stderr.
- Return errors in the `content` array with `isError: true` if the tool fails.
- Keep tool names and input schemas clear and descriptive.
- Avoid blocking operations; respond quickly to requests.
- Log errors to stderr for debugging (these are captured by DataAgent).

## Troubleshooting
- If you see Unicode errors, ensure your MCP server and DataAgent both use UTF-8 encoding.
- If tool calls time out, check that your server is reading stdin and writing responses promptly.
- If the UI says "I don't have access to real-time data", check that your tool returns a valid `content` array with a text result.

## Example: Minimal MCP Tool Response
```json
{
  "content": [
    {"type": "text", "text": "The weather in London is sunny."}
  ],
  "isError": false
}
```

## See Also
- [Model Context Protocol Spec](https://github.com/anthropics/model-context-protocol)
- [weather-info MCP Example](./testing/weather-info-new.py)

---
For further help, contact the DataAgent maintainers.
