#!/bin/bash

# Script to view the latest MCP server log file

LOG_DIR="/Users/liammckendry/hockey_coach_issue-111/manual_diagrams/logs"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Find the most recent log file
LATEST_LOG=$(ls -t "$LOG_DIR"/hockey_diagram_mcp_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "No log files found in $LOG_DIR"
    echo "Start the MCP server first to generate logs"
    exit 1
fi

echo "Viewing log file: $LATEST_LOG"
echo "Press Ctrl+C to stop"
echo "========================================="

# Tail the log file with follow mode
tail -f "$LATEST_LOG"