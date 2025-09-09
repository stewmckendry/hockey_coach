#!/bin/bash
# Integration test script runner with virtual environment activation

# Navigate to parent directory and activate virtual environment
cd /Users/liammckendry
source spacy_env/bin/activate
cd thunder_playbook/servers/hockey_diagram_mcp

# Set API key
export OPENAI_API_KEY="$1"

# Run the integration test
python test_two_stage_integration.py