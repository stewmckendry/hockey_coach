#!/bin/bash

# Simple notification wrapper for Claude Code hooks
# Can be called with arguments or read JSON from stdin

if [[ ! -t 0 ]]; then
    # Read JSON from stdin
    JSON_INPUT=$(cat)
    
    # Extract message from JSON using jq if available, otherwise use grep/sed
    if command -v jq >/dev/null 2>&1; then
        MESSAGE=$(echo "$JSON_INPUT" | jq -r '.message // ""')
        HOOK_EVENT=$(echo "$JSON_INPUT" | jq -r '.hook_event_name // ""')
    else
        # Fallback parsing without jq
        MESSAGE=$(echo "$JSON_INPUT" | grep -o '"message":"[^"]*"' | sed 's/"message":"\([^"]*\)"/\1/')
        HOOK_EVENT=$(echo "$JSON_INPUT" | grep -o '"hook_event_name":"[^"]*"' | sed 's/"hook_event_name":"\([^"]*\)"/\1/')
    fi
    
    # Clean up the message for better user experience
    case "$HOOK_EVENT" in
        "Notification")
            if [[ "$MESSAGE" == *"permission"* ]]; then
                MESSAGE="Waiting for your approval"
            fi
            TITLE="Claude Code - Approval Required"
            ;;
        "Stop")
            MESSAGE="Task completed"
            TITLE="Claude Code"
            ;;
        "PreToolUse")
            MESSAGE="Starting file operation"
            TITLE="Claude Code"
            ;;
        "PostToolUse")
            MESSAGE="File operation completed"
            TITLE="Claude Code"
            ;;
        *)
            MESSAGE="${MESSAGE:-Claude Code notification}"
            TITLE="Claude Code"
            ;;
    esac
else
    # Called with command line arguments
    TITLE="${1:-Claude Code}"
    MESSAGE="${2:-Notification}"
    
    # Check if the message looks like JSON and try to parse it
    if [[ "$MESSAGE" == "{"* ]]; then
        if command -v jq >/dev/null 2>&1; then
            HOOK_EVENT=$(echo "$MESSAGE" | jq -r '.hook_event_name // ""')
            JSON_MESSAGE=$(echo "$MESSAGE" | jq -r '.message // ""')
            
            # Use parsed message if available, otherwise generate based on hook event
            if [[ "$JSON_MESSAGE" != "" ]]; then
                MESSAGE="$JSON_MESSAGE"
            else
                case "$HOOK_EVENT" in
                    "Notification")
                        MESSAGE="Waiting for your approval"
                        TITLE="Claude Code - Approval Required"
                        ;;
                    "Stop")
                        MESSAGE="Task completed"
                        ;;
                    "PostToolUse")
                        MESSAGE="File operation completed"
                        ;;
                    *)
                        MESSAGE="Claude Code notification"
                        ;;
                esac
            fi
        fi
    fi
fi

# Use alert dialog instead of notification for better visibility
osascript -e 'display alert "'"$TITLE"'" message "'"$MESSAGE"'" as informational giving up after 10'