#!/bin/bash

# Hockey Diagram MCP Server Startup Script
# This script activates the virtual environment and runs the MCP server
# Updated to run v3 with atomic pipeline

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
VERSION="${1:-v3}"  # Default to v3

echo -e "${GREEN}🏒 Starting Hockey Diagram MCP Server (${VERSION})...${NC}"

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

# Run the appropriate MCP server version
case "$VERSION" in
    v1)
        echo -e "${BLUE}Running v1 (original) server...${NC}"
        python "$SCRIPT_DIR/hockey_diagram_mcp.py"
        ;;
    v2)
        echo -e "${BLUE}Running v2 (enhanced) server...${NC}"
        python "$SCRIPT_DIR/hockey_diagram_mcp_v2.py"
        ;;
    v3)
        echo -e "${BLUE}Running v3 (atomic pipeline) server...${NC}"
        echo -e "${YELLOW}📊 Pipeline Stage 1: Query Analysis ready${NC}"
        python "$SCRIPT_DIR/hockey_diagram_mcp_v3.py"
        ;;
    *)
        echo "Unknown version: $VERSION"
        echo "Usage: $0 [v1|v2|v3]"
        echo "  v1 - Original server"
        echo "  v2 - Enhanced 11-tool server"
        echo "  v3 - Atomic pipeline server (default)"
        exit 1
        ;;
esac