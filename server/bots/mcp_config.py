"""
MCP Server Configuration

This module defines MCP server configurations that can be used with the TTS-LLM-STT pipeline.
Add new MCP server configurations here to extend the voice assistant's capabilities.
"""

from mcp import StdioServerParameters
from typing import List, Dict, Any, Union
import os

class MCPServerConfig:
    """Configuration for an MCP server"""
    
    def __init__(self, name: str, server_params: Union[StdioServerParameters, str], description: str = "", is_remote: bool = False):
        self.name = name
        self.server_params = server_params
        self.description = description
        self.is_remote = is_remote

# Available MCP server configurations
MCP_SERVERS = [
    # Filesystem MCP Server
    MCPServerConfig(
        name="filesystem",
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem@latest", "/tmp"],
            env={"MCP_FILESYSTEM_ROOT": "/tmp"}
        ),
        description="File system operations (read, write, list files)",
        is_remote=False
    ),
    
    # PayPal Sandbox MCP Server (Remote)
    MCPServerConfig(
        name="paypal_sandbox",
        server_params="https://mcp.sandbox.paypal.com/sse",
        description="PayPal business tools (invoices, payments, subscriptions) - Sandbox environment",
        is_remote=True
    ),
    
    # PayPal Production MCP Server (Remote)
    MCPServerConfig(
        name="paypal_production",
        server_params="https://mcp.paypal.com/sse",
        description="PayPal business tools (invoices, payments, subscriptions) - Production environment",
        is_remote=True
    ),
    
    # Ferryhopper MCP Server (Remote)
    MCPServerConfig(
        name="ferryhopper",
        server_params="https://mcp.ferryhopper.com/mcp",
        description="Ferry trip planning across 33 countries and 190+ ferry operators - search routes, schedules, and get booking links",
        is_remote=True
    ),
    
    # Database MCP Server (example)
    # MCPServerConfig(
    #     name="database",
    #     server_params=StdioServerParameters(
    #         command="python",
    #         args=["-m", "mcp_server_database"],
    #         env={"DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///app.db")}
    #     ),
    #     description="Database operations (query, insert, update)"
    # ),
    
    # Weather MCP Server (example)
    # MCPServerConfig(
    #     name="weather",
    #     server_params=StdioServerParameters(
    #         command="python",
    #         args=["-m", "mcp_server_weather"],
    #         env={"OPENWEATHER_API_KEY": os.getenv("OPENWEATHER_API_KEY")}
    #     ),
    #     description="Real-time weather data from OpenWeatherMap"
    # ),
    
    # Calendar MCP Server (example)
    # MCPServerConfig(
    #     name="calendar",
    #     server_params=StdioServerParameters(
    #         command="python",
    #         args=["-m", "mcp_server_calendar"],
    #         env={"GOOGLE_CALENDAR_CREDENTIALS": os.getenv("GOOGLE_CALENDAR_CREDENTIALS")}
    #     ),
    #     description="Google Calendar integration (events, scheduling)"
    # ),
]

def get_enabled_mcp_servers() -> List[MCPServerConfig]:
    """Get list of enabled MCP servers based on environment variables"""
    enabled_servers = []
    
    for server in MCP_SERVERS:
        # Check if server is enabled via environment variable
        env_var = f"MCP_{server.name.upper()}_ENABLED"
        if os.getenv(env_var, "false").lower() == "true":
            enabled_servers.append(server)
        # Default to enabling filesystem server if no specific config
        elif server.name == "filesystem" and not any(s.name == "filesystem" for s in enabled_servers):
            enabled_servers.append(server)
    
    return enabled_servers

def get_mcp_server_by_name(name: str) -> MCPServerConfig:
    """Get MCP server configuration by name"""
    for server in MCP_SERVERS:
        if server.name == name:
            return server
    raise ValueError(f"MCP server '{name}' not found")

# Environment variable examples for enabling MCP servers:
# MCP_FILESYSTEM_ENABLED=true
# MCP_PAYPAL_SANDBOX_ENABLED=true
# MCP_PAYPAL_PRODUCTION_ENABLED=false
# MCP_FERRYHOPPER_ENABLED=true
# MCP_DATABASE_ENABLED=true
# MCP_WEATHER_ENABLED=true
# MCP_CALENDAR_ENABLED=true

# PayPal-specific environment variables:
# PAYPAL_CLIENT_ID=your_paypal_client_id
# PAYPAL_CLIENT_SECRET=your_paypal_client_secret
# PAYPAL_ENVIRONMENT=SANDBOX  # or PRODUCTION
