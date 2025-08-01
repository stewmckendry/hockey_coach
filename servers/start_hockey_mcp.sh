#!/bin/bash

# Hockey MCP Server Startup Script
# This script starts the hockey MCP server in a way compatible with Claude MCP integration

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Virtual environment path
VENV_PATH="/Users/liammckendry/spacy_env"

# Activate virtual environment and run the hockey MCP server
cd "$PROJECT_ROOT"
source "$VENV_PATH/bin/activate"

# Set environment variables for MCP compatibility
export MCP_TRANSPORT=stdio
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Start the hockey MCP server
exec python "$PROJECT_ROOT/servers/hockey_mcp.py"