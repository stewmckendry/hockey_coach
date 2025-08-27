# Thunder Playbook Servers

This directory contains the MCP (Model Context Protocol) servers and supporting infrastructure for the Thunder Playbook hockey coaching platform.

## Server Architecture

### Core Servers

- **`hockey_mcp.py`** - Main MCP server with comprehensive hockey knowledge base (1,509 lines)
  - Primary FastMCP server with stateless HTTP support
  - Provides tools for drill search, video clips, tactics, and coaching plans
  - Integrates with ChromaDB collections

- **`hockey_mcp_direct_api.py`** - Direct FastAPI wrapper (126 lines)
  - Simple HTTP API that wraps the hockey_mcp.py server
  - For development and testing purposes
  - Port 3003

- **`hockey_mcp_production_api.py`** - Production FastAPI server (170 lines)
  - Environment-aware production deployment
  - Supports both development and production configurations
  - Enhanced CORS and security features

### Specialized Services

- **`hockey_diagram_mcp/`** - Hockey diagram generation service
  - Programmatic tactical diagram generation
  - Coordinate mapping and zone grid systems
  - Comprehensive test suite in `tests/` subdirectory
  - Documentation in `docs/` subdirectory

- **`hockey_prompts_mcp/`** - Prompt templates service
  - Hockey-specific prompt templates
  - Practice planning prompts
  - Drill search and review templates

- **`hockey_agents/`** - Agent implementations
  - Season planning agent
  - Extensible agent framework

### Development Tools

- **`poc/`** - Proof of concept implementations
  - Testing different MCP connection patterns
  - Agent setup validation

- **`fastmcp_proxy.py`** - Proxy server for FastMCP
- **`start_hockey_mcp.sh`** - Quick start script for main server

## Quick Start

```bash
# Start main MCP server
python hockey_mcp.py

# Start direct API server  
python hockey_mcp_direct_api.py

# Start hockey diagram server
cd hockey_diagram_mcp && python server.py

# Start prompts server
cd hockey_prompts_mcp && python server.py
```

## Port Allocation

- 8000 - Main hockey_mcp.py server
- 3003 - Direct API server
- TBD - Production API server
- TBD - Diagram MCP server

## Dependencies

All servers require the virtual environment at `../spacy_env` to be activated:

```bash
cd .. && source spacy_env/bin/activate && cd thunder_playbook/servers
```