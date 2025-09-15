# MCP Integration Guide

## Overview

The TTS-LLM-STT pipeline now includes [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) support, allowing the voice assistant to connect to external MCP servers and access their tools without writing custom function handlers. This provides a standardized way to extend the assistant's capabilities with external services.

## What is MCP?

MCP is an open standard for enabling AI agents to interact with external data and tools. Instead of writing bespoke function call implementations for each external API, you can use MCP servers that provide bridges to those APIs.

## Features

- **Standardized Tool Access**: Connect to any MCP-compatible server
- **Dynamic Tool Discovery**: Automatically discover and register available tools
- **Voice + Visual Feedback**: MCP tool calls are logged and spoken
- **Configurable Servers**: Enable/disable MCP servers via environment variables
- **Extensible Architecture**: Easy to add new MCP servers

## Architecture

```
Voice Input → STT → LLM + MCP Tools → TTS → Voice Output
                    ↓
              MCP Servers
              ├── Filesystem
              ├── Database
              ├── Weather API
              └── Calendar
```

## Configuration

### Environment Variables

Add MCP server configuration to your `.env` file:

```bash
# MCP Server Configuration
MCP_FILESYSTEM_ENABLED=true
MCP_DATABASE_ENABLED=false
MCP_WEATHER_ENABLED=false
MCP_CALENDAR_ENABLED=false
```

### MCP Server Configuration

MCP servers are configured in `server/bots/mcp_config.py`:

```python
MCP_SERVERS = [
    MCPServerConfig(
        name="filesystem",
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem@latest", "/tmp"],
            env={"MCP_FILESYSTEM_ROOT": "/tmp"}
        ),
        description="File system operations (read, write, list files)"
    ),
    # Add more servers here...
]
```

## Available MCP Servers

### 1. Filesystem Server (Default)

**Description**: File system operations (read, write, list files)

**Installation**: Automatically installed via npm

**Configuration**:
```bash
MCP_FILESYSTEM_ENABLED=true
```

**Example Usage**:
- "List files in the current directory"
- "Read the contents of config.json"
- "Create a new file called notes.txt"

### 2. Database Server (Example)

**Description**: Database operations (query, insert, update)

**Configuration**:
```python
MCPServerConfig(
    name="database",
    server_params=StdioServerParameters(
        command="python",
        args=["-m", "mcp_server_database"],
        env={"DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///app.db")}
    ),
    description="Database operations (query, insert, update)"
)
```

### 3. Weather Server (Example)

**Description**: Real-time weather data from OpenWeatherMap

**Configuration**:
```python
MCPServerConfig(
    name="weather",
    server_params=StdioServerParameters(
        command="python",
        args=["-m", "mcp_server_weather"],
        env={"OPENWEATHER_API_KEY": os.getenv("OPENWEATHER_API_KEY")}
    ),
    description="Real-time weather data from OpenWeatherMap"
)
```

### 4. Calendar Server (Example)

**Description**: Google Calendar integration (events, scheduling)

**Configuration**:
```python
MCPServerConfig(
    name="calendar",
    server_params=StdioServerParameters(
        command="python",
        args=["-m", "mcp_server_calendar"],
        env={"GOOGLE_CALENDAR_CREDENTIALS": os.getenv("GOOGLE_CALENDAR_CREDENTIALS")}
    ),
    description="Google Calendar integration (events, scheduling)"
)
```

## Adding New MCP Servers

### Step 1: Install MCP Server

```bash
# For npm-based servers
npm install -g @modelcontextprotocol/server-name

# For Python-based servers
pip install mcp-server-name
```

### Step 2: Add Configuration

Add to `server/bots/mcp_config.py`:

```python
MCPServerConfig(
    name="your_server",
    server_params=StdioServerParameters(
        command="your_command",
        args=["arg1", "arg2"],
        env={"YOUR_ENV_VAR": "value"}
    ),
    description="Description of what this server does"
)
```

### Step 3: Enable via Environment

Add to your `.env` file:

```bash
MCP_YOUR_SERVER_ENABLED=true
```

### Step 4: Restart Server

```bash
python3 sesame.py run
```

## Usage Examples

### Voice Chat (WebRTC)

1. **Start voice chat**: Click "Real-Time Voice AI Agent"
2. **Ask for file operations**: "List the files in my home directory"
3. **Watch the logs**: MCP tool calls are logged in the server
4. **Get voice response**: The assistant speaks the results

### Text Chat (HTTP)

1. **Use text interface**: Type file operation requests
2. **MCP tools are called**: Check server logs for tool execution
3. **Get text response**: Results are returned in the chat

## Example Conversations

### File Operations

**Voice Input:**
> "Show me what files are in the /tmp directory"

**Server Logs:**
```
🔧 Connecting to MCP server: filesystem
✅ MCP filesystem server connected successfully
📝 File system operations (read, write, list files)
🔧 Function calls started: ['list_files']
🔧 Calling function: list_files with args: {'path': '/tmp'}
```

**Voice Output:**
> "I'll check the files in the /tmp directory for you. Here are the files I found: [list of files]"

### Database Operations

**Voice Input:**
> "Query the users table to find all active users"

**Server Logs:**
```
🔧 Connecting to MCP server: database
✅ MCP database server connected successfully
📝 Database operations (query, insert, update)
🔧 Function calls started: ['query_database']
🔧 Calling function: query_database with args: {'query': 'SELECT * FROM users WHERE active = true'}
```

## Troubleshooting

### MCP Server Not Available

**Error**: `⚠️ MCP filesystem server not available: [error]`

**Solutions**:
1. Check if the MCP server is installed
2. Verify the server configuration in `mcp_config.py`
3. Check environment variables
4. Ensure the server command is available in PATH

### Tools Not Registered

**Error**: No tools available from MCP server

**Solutions**:
1. Check MCP server logs for errors
2. Verify server is running correctly
3. Check if server implements the required MCP protocol
4. Test the MCP server independently

### Permission Issues

**Error**: Permission denied when accessing files

**Solutions**:
1. Check file/directory permissions
2. Verify MCP server has appropriate access
3. Run with appropriate user permissions

## Development

### Testing MCP Servers

Test MCP servers independently:

```bash
# Test filesystem server
npx @modelcontextprotocol/server-filesystem@latest /tmp

# Test with MCP client
python -c "
from pipecat.services.mcp_service import MCPClient
from mcp import StdioServerParameters
client = MCPClient(StdioServerParameters('npx', ['-y', '@modelcontextprotocol/server-filesystem@latest', '/tmp']))
tools = await client.register_tools(llm)
print(tools)
"
```

### Adding Custom MCP Servers

1. **Create MCP server**: Follow MCP protocol specifications
2. **Add configuration**: Update `mcp_config.py`
3. **Test integration**: Verify tools are registered correctly
4. **Update documentation**: Add usage examples

## Security Considerations

- **Sandboxing**: MCP servers run in separate processes
- **Permissions**: Limit file system access to necessary directories
- **Authentication**: Use appropriate API keys for external services
- **Validation**: Validate all inputs to MCP tools
- **Logging**: Monitor MCP tool usage for security

## Performance

- **Connection Pooling**: MCP clients are reused across requests
- **Error Handling**: Graceful fallback when MCP servers are unavailable
- **Logging**: Comprehensive logging for debugging and monitoring
- **Resource Management**: Proper cleanup of MCP connections

## References

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Pipecat MCP Client](https://docs.pipecat.ai/server/utilities/mcp/mcp)
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)

## Next Steps

1. **Add More Servers**: Integrate additional MCP servers for more capabilities
2. **Custom Servers**: Create custom MCP servers for specific use cases
3. **UI Integration**: Add MCP tool status to the web interface
4. **Analytics**: Track MCP tool usage and performance
5. **Documentation**: Create user guides for specific MCP tools
