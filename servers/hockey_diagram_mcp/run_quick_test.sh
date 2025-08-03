#!/bin/bash
# Quick test runner with virtual environment

cd /Users/liammckendry
source spacy_env/bin/activate
cd thunder_playbook/servers/hockey_diagram_mcp

export OPENAI_API_KEY="$1"
python quick_test_diagrams.py