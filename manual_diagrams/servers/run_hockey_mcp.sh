#!/bin/bash

# Hockey Diagram MCP Server Startup Script
# This script activates the virtual environment and runs the MCP server

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏒 Starting Hockey Diagram MCP Server...${NC}"

# Activate virtual environment
VENV_PATH="/Users/liammckendry/spacy_env"
if [ -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source "$VENV_PATH/bin/activate"
else
    echo "Warning: Virtual environment not found at $VENV_PATH"
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set Python path for imports
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/../src:$PYTHONPATH"

# Load environment variables from thunder_playbook if available
ENV_FILE="/Users/liammckendry/thunder_playbook/.env"
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Loading environment variables...${NC}"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Run the MCP server
echo -e "${GREEN}Launching MCP server on stdio...${NC}"
python "$SCRIPT_DIR/hockey_diagram_mcp.py"