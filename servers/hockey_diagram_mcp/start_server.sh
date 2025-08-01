#!/bin/bash
# Start script for hockey diagram MCP server

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$DIR/../../../spacy_env/bin/activate"

# Load environment variables if .env exists
if [ -f "$DIR/../../.env" ]; then
    export $(grep -v '^#' "$DIR/../../.env" | xargs)
fi

# Start the server
python "$DIR/server.py"