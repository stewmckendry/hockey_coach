#!/bin/bash

# Clean MCP Server runner for stdio mode - NO OUTPUT TO STDOUT
# All output must be JSON for MCP protocol

# Activate virtual environment silently
source /Users/liammckendry/spacy_env/bin/activate 2>/dev/null

# Set Python path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/../src"

# Load environment variables silently
if [ -f "/Users/liammckendry/thunder_playbook/.env" ]; then
    export $(grep -v '^#' /Users/liammckendry/thunder_playbook/.env | xargs) 2>/dev/null
fi

# Run the Python script directly - it handles stdio mode properly
exec python "$SCRIPT_DIR/run_mcp_stdio.py"