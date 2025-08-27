#!/bin/bash
# Run single diagram test
# Usage:
#   ./run_single_test.sh API_KEY test_number
#   ./run_single_test.sh API_KEY "prompt text" [view]

cd /Users/liammckendry
source spacy_env/bin/activate
cd thunder_playbook/servers/hockey_diagram_mcp

export OPENAI_API_KEY="$1"

# Pass all remaining arguments to the Python script
shift  # Remove API_KEY from arguments
python test_single_diagram.py "$OPENAI_API_KEY" "$@"