#!/bin/bash
# Telemetry wrapper script to handle virtual environment setup

# Set working directory to project root
cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment
source ../spacy_env/bin/activate 2>/dev/null || {
    # Fallback: try system python with graceful failure
    if ! python3 -c "import pydantic" 2>/dev/null; then
        # Telemetry dependency missing, exit gracefully
        exit 0
    fi
}

# Execute telemetry hook with all arguments
exec python3 scripts/telemetry_hook.py "$@"