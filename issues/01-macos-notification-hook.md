# Issue 1: macOS Notification Hook for Claude Code Approvals

## Overview
Implement a Claude Code hook system that sends macOS native notifications when Claude Code requires user approval for actions. This provides immediate awareness when Claude is waiting for input without requiring constant terminal monitoring.

## Problem Statement
Currently, when Claude Code needs approval for tool use or other actions, users must actively monitor the terminal. This creates workflow interruptions and reduces productivity, especially during long-running tasks or when multitasking.

## Solution Approach
Configure Claude Code hooks to detect approval requests and send native macOS notifications using a hybrid approach with osascript (built-in) and terminal-notifier (enhanced features).

## Technical Requirements

### Core Functionality
- **Hook Integration**: Configure Claude Code `Notification` event hook
- **Native macOS Support**: Use osascript for universal compatibility
- **Enhanced Features**: Detect and use terminal-notifier when available
- **Smart Filtering**: Only notify on approval requests, not all notifications
- **User Control**: Configuration options for notification preferences

### Implementation Details

#### Hook Configuration
- **File Location**: `.claude/settings.json` (project-level)
- **Hook Event**: `Notification` 
- **Trigger Condition**: Filter for approval-related notifications
- **Command Execution**: Shell script with notification logic

#### Notification System
- **Primary Method**: osascript (no dependencies)
- **Fallback Enhancement**: terminal-notifier (if available)
- **Message Format**: Clear, actionable notification text
- **Visual Indicators**: Status icons (⚠️ for approval needed)
- **Sound Options**: Configurable sound preferences

#### Configuration Options
- **Enable/Disable**: `HOCKEY_NOTIFICATIONS=true/false`
- **Notification Level**: `APPROVAL_ONLY`, `ERRORS`, `ALL`
- **Sound Preferences**: `default`, `none`, custom sound names
- **Group Management**: Prevent notification spam

## File Structure
```
thunder_playbook/
├── .claude/
│   └── settings.json                 # Hook configuration
├── scripts/
│   └── notification_helper.sh       # Notification logic
└── docs/
    └── NOTIFICATION_SETUP.md        # Setup instructions
```

## Implementation Specifications

### 1. Claude Code Hook Configuration
```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/notification_helper.sh \"$CLAUDE_NOTIFICATION\""
          }
        ]
      }
    ]
  }
}
```

### 2. Notification Helper Script
```bash
#!/bin/bash
# scripts/notification_helper.sh

# Configuration from environment variables
HOCKEY_NOTIFICATIONS=${HOCKEY_NOTIFICATIONS:-true}
NOTIFICATION_LEVEL=${NOTIFICATION_LEVEL:-APPROVAL_ONLY}
NOTIFICATION_SOUND=${NOTIFICATION_SOUND:-default}

# Exit if notifications disabled
[ "$HOCKEY_NOTIFICATIONS" != "true" ] && exit 0

# Parse notification message
message="$1"
title="⚠️ Claude Code"

# Filter for approval requests only
if [[ "$message" =~ "approve|permission|allow|confirm" ]]; then
    # Send notification using best available method
    if command -v terminal-notifier >/dev/null 2>&1; then
        terminal-notifier -message "$message" -title "$title" \
                         -group "claude-code-approvals" \
                         -sound "$NOTIFICATION_SOUND"
    else
        osascript -e "display notification \"$message\" with title \"$title\" sound name \"$NOTIFICATION_SOUND\""
    fi
fi
```

### 3. Installation and Setup
1. **Create hook configuration** in `.claude/settings.json`
2. **Create notification script** at `scripts/notification_helper.sh`
3. **Make script executable**: `chmod +x scripts/notification_helper.sh`
4. **Configure environment variables** (optional)
5. **Test notifications** with sample approval scenarios

## Testing Strategy

### Unit Tests
- **Hook Trigger**: Verify notification events trigger correctly
- **Message Filtering**: Test approval detection logic
- **System Integration**: Validate osascript and terminal-notifier calls
- **Configuration**: Test all environment variable combinations

### Integration Tests
- **Claude Code Integration**: Test with actual approval scenarios
- **macOS Compatibility**: Test across different macOS versions
- **Performance Impact**: Measure latency added to Claude operations
- **Error Handling**: Test behavior when notification systems fail

### User Acceptance Testing
- **Notification Timing**: Verify notifications appear when approvals needed
- **Message Clarity**: Ensure notification text is clear and actionable
- **Sound Appropriateness**: Test default and custom sound options
- **Non-Intrusive**: Confirm notifications don't disrupt workflow

## Success Criteria
- ✅ Notifications appear within 1 second of approval request
- ✅ Zero false positives (non-approval notifications filtered out)
- ✅ Works on all macOS versions 10.14+
- ✅ <100ms latency impact on Claude Code operations
- ✅ User can easily enable/disable notifications
- ✅ Clear, actionable notification messages

## Dependencies
- **Required**: macOS with osascript (built-in)
- **Optional**: terminal-notifier (via Homebrew or gem)
- **Claude Code**: Version with hook support
- **Permissions**: macOS notification permissions for Terminal/Claude

## Implementation Timeline
- **Day 1**: Hook configuration and basic osascript integration
- **Day 2**: Enhanced terminal-notifier support and filtering logic
- **Day 3**: Testing, error handling, and documentation
- **Day 4**: Integration testing and user configuration options

## Future Enhancements
- **Custom notification templates** for different approval types
- **Action buttons** for approve/deny directly from notification
- **Integration with other notification systems** (Slack, email)
- **Analytics tracking** of approval patterns and response times
- **Smart scheduling** to respect do-not-disturb preferences

## Risk Mitigation
- **Fallback Strategy**: osascript ensures universal macOS compatibility
- **Performance Impact**: Minimal overhead with background execution
- **Permission Issues**: Clear setup instructions for notification permissions
- **Spam Prevention**: Smart filtering prevents notification overload
- **User Control**: Easy disable mechanism for users who prefer terminal monitoring