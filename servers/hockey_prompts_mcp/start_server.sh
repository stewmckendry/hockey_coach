#!/bin/bash

# Hockey Practice Planning Prompts MCP Server Startup Script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Find the project root
PROJECT_ROOT="$SCRIPT_DIR/../.."

# Navigate to parent directory for virtual environment
cd "$PROJECT_ROOT/.." || exit 1

# Check if virtual environment exists
if [ -d "spacy_env" ]; then
    source spacy_env/bin/activate
else
    # Error to stderr so it doesn't interfere with stdio
    echo "❌ Virtual environment not found at spacy_env" >&2
    echo "Please ensure you're running from the thunder_playbook directory" >&2
    exit 1
fi

# Navigate back to the server directory
cd "$SCRIPT_DIR" || exit 1

# Set environment variables for MCP compatibility
export MCP_TRANSPORT=stdio
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Start the server using exec to replace the shell process
exec python "$SCRIPT_DIR/server.py"