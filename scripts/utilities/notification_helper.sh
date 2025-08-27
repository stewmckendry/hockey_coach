#!/bin/bash

# Claude Code macOS Notification Helper
# Provides hybrid notification support using osascript (built-in) and terminal-notifier (optional)
# GitHub Issue: https://github.com/stewmckendry/hockey_coach/issues/77

set -euo pipefail

# Configuration defaults
DEFAULT_TITLE="Claude Code"
DEFAULT_SOUND="Glass"
DEBUG_MODE=${DEBUG_MODE:-false}

# Logging function
log() {
    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
    fi
}

# Check if terminal-notifier is available
has_terminal_notifier() {
    command -v terminal-notifier >/dev/null 2>&1
}

# Send notification using osascript (fallback method)
send_osascript_notification() {
    local title="$1"
    local message="$2"
    local sound="${3:-$DEFAULT_SOUND}"
    
    log "Sending osascript notification: title='$title', message='$message', sound='$sound'"
    
    # Always use alert dialog for reliability (notifications may be blocked)
    # Escape special characters for osascript
    local escaped_title=$(printf '%s' "$title" | sed 's/"/\\"/g')
    local escaped_message=$(printf '%s' "$message" | sed 's/"/\\"/g')
    osascript -e "display alert \"$escaped_title\" message \"$escaped_message\" as informational giving up after 15"
}

# Send notification using terminal-notifier (enhanced method)
send_terminal_notifier_notification() {
    local title="$1"
    local message="$2"
    local sound="${3:-$DEFAULT_SOUND}"
    
    log "Sending terminal-notifier notification: title='$title', message='$message', sound='$sound'"
    
    terminal-notifier \
        -title "$title" \
        -message "$message" \
        -sound "$sound" \
        -group "claude-code-approval" \
        -sender "com.anthropic.claude-code" \
        -timeout 30
}

# Main notification function with hybrid approach
send_notification() {
    local title="${1:-$DEFAULT_TITLE}"
    local message="${2:-Claude Code requires your attention}"
    local sound="${3:-$DEFAULT_SOUND}"
    
    # Validate inputs
    if [[ -z "$message" ]]; then
        log "Error: Message cannot be empty"
        exit 1
    fi
    
    log "Attempting to send notification: title='$title', message='$message'"
    
    # Try terminal-notifier first (if available), fall back to osascript
    if has_terminal_notifier; then
        log "Using terminal-notifier (enhanced method)"
        if ! send_terminal_notifier_notification "$title" "$message" "$sound"; then
            log "terminal-notifier failed, falling back to osascript"
            send_osascript_notification "$title" "$message" "$sound"
        fi
    else
        log "terminal-notifier not available, using osascript (fallback method)"
        send_osascript_notification "$title" "$message" "$sound"
    fi
    
    log "Notification sent successfully"
}

# Parse command line arguments
parse_args() {
    local title="$DEFAULT_TITLE"
    local message=""
    local sound="$DEFAULT_SOUND"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--title)
                title="$2"
                shift 2
                ;;
            -m|--message)
                message="$2"
                shift 2
                ;;
            -s|--sound)
                sound="$2"
                shift 2
                ;;
            --debug)
                DEBUG_MODE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                # If no flags, treat first argument as message
                if [[ -z "$message" ]]; then
                    message="$1"
                fi
                shift
                ;;
        esac
    done
    
    send_notification "$title" "$message" "$sound"
}

# Show help information
show_help() {
    cat <<EOF
Claude Code macOS Notification Helper

Usage: $0 [OPTIONS] [MESSAGE]

OPTIONS:
    -t, --title TITLE       Notification title (default: "$DEFAULT_TITLE")
    -m, --message MESSAGE   Notification message (required)
    -s, --sound SOUND       Notification sound (default: "$DEFAULT_SOUND")
    --debug                 Enable debug logging
    -h, --help              Show this help message

EXAMPLES:
    $0 "Approval required for file changes"
    $0 -t "Claude Code" -m "Please review the proposed changes" -s "Ping"
    $0 --title "Hockey Coach" --message "Practice plan ready for review"

SOUNDS:
    Common macOS notification sounds: Basso, Blow, Bottle, Frog, Funk, Glass,
    Hero, Morse, Ping, Pop, Purr, Sosumi, Submarine, Tink

ENVIRONMENT VARIABLES:
    DEBUG_MODE=true         Enable debug logging
EOF
}

# Smart filtering for approval-related notifications
is_approval_request() {
    local message="$1"
    
    # Keywords that indicate an approval request
    local approval_keywords=(
        "approval"
        "approve"
        "confirm"
        "permission"
        "authorize"
        "allow"
        "proceed"
        "continue"
        "review"
        "accept"
    )
    
    local message_lower
    message_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')
    
    for keyword in "${approval_keywords[@]}"; do
        if [[ "$message_lower" == *"$keyword"* ]]; then
            log "Approval keyword '$keyword' detected in message"
            return 0
        fi
    done
    
    return 1
}

# Enhanced notification for approval requests
send_approval_notification() {
    local message="${1:-Approval required}"
    local title="Claude Code - Approval Required"
    local sound="Glass"
    
    log "Sending approval-specific notification"
    
    # Use more attention-grabbing settings for approvals
    if has_terminal_notifier; then
        terminal-notifier \
            -title "$title" \
            -message "$message" \
            -sound "$sound" \
            -group "claude-code-approval" \
            -sender "com.anthropic.claude-code" \
            -timeout 0 \
            -appIcon "https://claude.ai/favicon.ico" \
            -contentImage "https://claude.ai/favicon.ico"
    else
        send_osascript_notification "$title" "$message" "$sound"
    fi
}

# Main execution
main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 1
    fi
    
    # If called with stdin, read message from stdin
    if [[ ! -t 0 ]]; then
        local message
        message=$(cat)
        if is_approval_request "$message"; then
            send_approval_notification "$message"
        else
            send_notification "$DEFAULT_TITLE" "$message"
        fi
    else
        parse_args "$@"
    fi
}

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi