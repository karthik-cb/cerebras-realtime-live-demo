# Ferryhopper MCP Integration Guide

This guide explains how to integrate Ferryhopper's Model Context Protocol (MCP) server with your TTS-LLM-STT voice assistant for ferry trip planning and booking.

## 🎯 Overview

The Ferryhopper MCP server provides access to ferry trip planning tools through natural language, enabling your voice assistant to:
- Search for ferry routes across 33 countries and 190+ ferry operators
- Get real-time ferry itineraries with indicative prices
- Find ports and connections across Europe and the Mediterranean
- Provide direct booking links to Ferryhopper.com

## 🔧 Setup Instructions

### 1. Environment Configuration

Add Ferryhopper MCP configuration to your `.env` file:

```bash
# Ferryhopper Configuration
# No API keys required - public service
# Ferryhopper provides ferry trip planning across Europe and Mediterranean

# Enable Ferryhopper MCP Server
MCP_FERRYHOPPER_ENABLED=true
```

### 2. MCP Server Configuration

The Ferryhopper MCP server is already configured in `server/bots/mcp_config.py`:

```python
MCPServerConfig(
    name="ferryhopper",
    server_params="https://mcp.ferryhopper.com/mcp",
    description="Ferry trip planning across 33 countries and 190+ ferry operators - search routes, schedules, and get booking links",
    is_remote=True
)
```

### 3. No Authentication Required

Unlike PayPal, Ferryhopper is a public service that doesn't require API keys or authentication. The integration automatically connects to their public MCP server.

## 🚀 Available Ferryhopper Tools

Based on the [Ferryhopper MCP documentation](https://ferryhopper.github.io/fh-mcp/), your voice assistant can:

### Port Search
- **Get Ports**: Retrieve a list of global ports and their details
- **Port Discovery**: Find ports by name, location, or region

### Trip Search
- **Search Trips**: Find available ferry trips between two ports on specific dates
- **Route Planning**: Get schedules, prices, and vessel information
- **Multi-leg Journeys**: Plan complex ferry routes

### Booking Integration
- **Redirect to Booking**: Get direct links to Ferryhopper.com for booking and payment
- **Trip Details**: Access detailed information about specific ferry services

## 🎤 Example Voice Interactions

### Basic Ferry Search
*"What ferries depart from Piraeus to Aegina on Saturday morning?"*

*"Help me find a ferry from Ibiza to Barcelona on July 11th for 2 adults and 1 child."*

### Route Planning
*"I want to visit an island within 3 hours of Athens tomorrow and return the next day — what are my options?"*

*"Show me ferry connections from Santorini to Mykonos next week."*

### Port Discovery
*"What ports are available in the Greek islands?"*

*"Find ferry ports near Barcelona."*

## 🔧 Technical Implementation

### Integration Architecture
```
Voice Input → STT → LLM + Ferryhopper MCP Tools → TTS → Voice Output
                    ↓
              Ferryhopper MCP Server
              (https://mcp.ferryhopper.com/mcp)
```

### Bot Pipeline Integration

The integration is handled in both WebRTC and HTTP bot pipelines:

1. **WebRTC Bot** (`server/bots/webrtc/bot_pipeline.py`):
   - Detects Ferryhopper MCP server configuration
   - Connects to remote MCP server without authentication
   - Registers available tools with the LLM
   - Handles connection errors gracefully

2. **HTTP Bot** (`server/bots/http/bot.py`):
   - Uses standard MCP client for remote server connection
   - Integrates Ferryhopper tools with other MCP services
   - Provides consistent tool access across interfaces

### System Prompts

Both bot pipelines include Ferryhopper-specific instructions:

- Ferry trip planning capabilities
- Tool usage guidance for ferry searches
- Integration with other MCP services

## 🌍 Coverage Areas

Ferryhopper covers ferry routes across:

- **Mediterranean**: Greece, Italy, Spain, France, Croatia, Turkey
- **Northern Europe**: UK, Ireland, Netherlands, Denmark, Sweden, Norway
- **Adriatic**: Italy, Croatia, Montenegro, Albania
- **Aegean**: Greek islands, Turkey
- **Baltic**: Finland, Estonia, Latvia, Lithuania
- **And more**: 33 countries total with 190+ ferry operators

## 🎯 Use Cases for Your Demo

### Travel Planning Assistant
- Help users plan island-hopping trips
- Find last-minute ferry connections
- Compare ferry schedules and prices

### Multi-modal Integration
- Voice input for trip requirements
- Text output with detailed schedules
- Web redirects for booking completion

### Real-world Business Applications
- Travel agency automation
- Hotel concierge services
- Tourism information systems

## 🔍 Troubleshooting

### Connection Issues
If Ferryhopper MCP server is unavailable:
- Check internet connectivity
- Verify the MCP server URL is accessible
- Review server logs for connection errors

### Tool Discovery
If Ferryhopper tools aren't appearing:
- Ensure `MCP_FERRYHOPPER_ENABLED=true` in your `.env` file
- Check that the MCP server configuration is correct
- Verify the bot pipeline is loading the configuration

### Performance
- Ferryhopper is a public service, so response times may vary
- Consider implementing timeout handling for better user experience
- Cache frequently requested routes if needed

## 📚 Additional Resources

- [Ferryhopper MCP Documentation](https://ferryhopper.github.io/fh-mcp/)
- [Ferryhopper.com](https://www.ferryhopper.com/) - Main booking platform
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

## 🚀 Next Steps

1. **Enable the Integration**: Set `MCP_FERRYHOPPER_ENABLED=true` in your `.env` file
2. **Test Voice Interactions**: Try the example prompts above
3. **Explore Advanced Features**: Test multi-leg journeys and complex route planning
4. **Monitor Performance**: Check logs for connection status and response times

The Ferryhopper integration adds powerful travel planning capabilities to your voice assistant, making it a compelling demo for AI-powered travel assistance and real-world tool integration.
