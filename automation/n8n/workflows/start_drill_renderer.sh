#!/bin/bash

# Start Drill Renderer v0.1

echo "Starting Drill Renderer v0.1..."
echo "Server will run on port 5002"
echo "Press Ctrl+C to stop"
echo ""

# Navigate to the workflow directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "../../../spacy_env" ]; then
    echo "Activating virtual environment..."
    source ../../../spacy_env/bin/activate
fi

# Start the renderer
python drill_renderer_v01.py