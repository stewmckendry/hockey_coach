#!/bin/bash
# Start script for hockey diagram MCP server

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment (absolute path to handle worktree)
source "/Users/liammckendry/spacy_env/bin/activate"

# Load environment variables if .env exists
if [ -f "$DIR/../../.env" ]; then
    export $(grep -v '^#' "$DIR/../../.env" | xargs)
fi

# Set a dummy API key if none exists (for MCP tool discovery)
if [ -z "$OPENAI_API_KEY" ]; then
    export OPENAI_API_KEY="dummy-key-for-mcp-discovery"
fi

# Start the server
python "$DIR/server.py"