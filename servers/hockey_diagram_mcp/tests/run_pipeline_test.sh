#!/bin/bash
# Run detailed pipeline tests with virtual environment

cd /Users/liammckendry
source spacy_env/bin/activate
cd thunder_playbook/servers/hockey_diagram_mcp

export OPENAI_API_KEY="$1"
BATCH_NAME="${2:-batch_1_views}"

python test_pipeline_detailed.py "$OPENAI_API_KEY" "$BATCH_NAME"