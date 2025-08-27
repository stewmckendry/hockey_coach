# Issue 2: Comprehensive Logging Hook System for Claude Code

## Overview
Implement a comprehensive logging system using Claude Code hooks to capture detailed telemetry data about development workflow, tool usage, performance metrics, and user interactions. This data will form the foundation for workflow analytics and optimization insights.

## Problem Statement
Currently, there's no systematic way to track and analyze Claude Code usage patterns, performance bottlenecks, error patterns, or development workflow efficiency. This lack of visibility prevents identification of optimization opportunities and workflow improvements.

## Solution Approach
Implement hooks for all 8 Claude Code events to capture comprehensive telemetry data in structured JSON format with rotation, archival, and privacy controls. Focus on actionable metrics that can drive workflow optimization.

## Technical Requirements

### Core Functionality
- **Complete Event Coverage**: Hook all 8 Claude Code events
- **Structured Logging**: JSON format with consistent schema
- **Performance Tracking**: Tool execution times and success rates
- **Session Management**: Track development sessions and context
- **Privacy Controls**: Anonymize or exclude sensitive data
- **Data Rotation**: Prevent unbounded log growth

### Event Coverage Matrix

| Event | Purpose | Data Captured |
|-------|---------|---------------|
| `SessionStart` | Session initialization | Session ID, project context, timestamp |
| `UserPromptSubmit` | User interaction tracking | Prompt content (optional), timestamp, context |
| `PreToolUse` | Tool preparation metrics | Tool type, parameters, session state |
| `PostToolUse` | Tool completion metrics | Results, duration, success/failure, errors |
| `SubagentStop` | Subagent usage patterns | Subagent type, task, duration, outcome |
| `Stop` | Session completion | Session summary, total duration, tool counts |
| `PreCompact` | Context management | Memory usage, compaction triggers |
| `Notification` | User approval patterns | Notification type, response time, decisions |

## Implementation Specifications

### File Structure
```
thunder_playbook/
├── .claude/
│   └── settings.json              # Hook configuration
├── telemetry/
│   ├── collector.py              # Main logging service
│   ├── models.py                 # Data schemas
│   ├── config.py                 # Configuration management
│   └── utils.py                  # Utility functions
├── logs/
│   ├── claude_telemetry/         # Main log directory
│   │   ├── sessions/             # Session-based logs
│   │   ├── tools/                # Tool usage logs
│   │   ├── performance/          # Performance metrics
│   │   └── errors/               # Error tracking
│   └── archive/                  # Rotated/archived logs
└── scripts/
    └── telemetry_hook.py         # Hook entry point
```

### 1. Hook Configuration
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/telemetry_hook.py SessionStart"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command", 
            "command": "python3 scripts/telemetry_hook.py UserPromptSubmit"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/telemetry_hook.py PreToolUse"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/telemetry_hook.py PostToolUse"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/telemetry_hook.py SubagentStop"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/telemetry_hook.py Stop"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/telemetry_hook.py PreCompact"
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/telemetry_hook.py Notification"
          }
        ]
      }
    ]
  }
}
```

### 2. Data Models and Schema
```python
# telemetry/models.py
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class BaseEvent(BaseModel):
    event_type: str
    timestamp: datetime
    session_id: str
    project_dir: str
    
class SessionStartEvent(BaseEvent):
    event_type: str = "SessionStart"
    user_id: Optional[str] = None  # Anonymized
    claude_version: Optional[str] = None
    project_context: Dict[str, Any] = {}

class UserPromptEvent(BaseEvent):
    event_type: str = "UserPromptSubmit"
    prompt_length: int
    prompt_hash: Optional[str] = None  # For deduplication
    prompt_content: Optional[str] = None  # Privacy controlled
    context: Dict[str, Any] = {}

class ToolUseEvent(BaseEvent):
    tool_name: str
    tool_input_size: int
    execution_duration_ms: Optional[int] = None
    success: Optional[bool] = None
    error_details: Optional[str] = None
    file_paths: List[str] = []
    
class SubagentEvent(BaseEvent):
    event_type: str = "SubagentStop"
    subagent_type: str
    task_description: str
    duration_ms: int
    outcome: str  # success, failure, partial
    
class SessionStopEvent(BaseEvent):
    event_type: str = "Stop"
    total_duration_ms: int
    total_tools_used: int
    total_subagents: int
    success_rate: float
    error_count: int
```

### 3. Telemetry Collector Service
```python
# telemetry/collector.py
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from .models import BaseEvent
from .config import TelemetryConfig

class TelemetryCollector:
    def __init__(self, config: TelemetryConfig):
        self.config = config
        self.setup_logging()
        self.ensure_directories()
    
    def collect_event(self, event_type: str, event_data: Dict[str, Any]):
        """Main entry point for event collection"""
        try:
            # Create event object
            event = self._create_event(event_type, event_data)
            
            # Log to structured files
            self._log_event(event)
            
            # Update metrics
            self._update_metrics(event)
            
            # Check for rotation
            self._check_rotation()
            
        except Exception as e:
            logging.error(f"Telemetry collection failed: {e}")
    
    def _create_event(self, event_type: str, data: Dict[str, Any]) -> BaseEvent:
        """Create typed event object"""
        event_classes = {
            "SessionStart": SessionStartEvent,
            "UserPromptSubmit": UserPromptEvent,
            "PreToolUse": ToolUseEvent,
            "PostToolUse": ToolUseEvent,
            "SubagentStop": SubagentEvent,
            "Stop": SessionStopEvent,
        }
        
        event_class = event_classes.get(event_type, BaseEvent)
        return event_class(**data)
    
    def _log_event(self, event: BaseEvent):
        """Write event to appropriate log files"""
        # Session-based logging
        session_file = self.config.logs_dir / "sessions" / f"{event.session_id}.jsonl"
        self._append_to_file(session_file, event.dict())
        
        # Event-type logging
        event_file = self.config.logs_dir / f"{event.event_type.lower()}.jsonl"
        self._append_to_file(event_file, event.dict())
        
        # Daily aggregated logging
        daily_file = self.config.logs_dir / f"daily_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self._append_to_file(daily_file, event.dict())
```

### 4. Configuration Management
```python
# telemetry/config.py
from pathlib import Path
from typing import Optional
import os

class TelemetryConfig:
    def __init__(self):
        # Base configuration
        self.enabled = os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"
        self.privacy_mode = os.getenv("TELEMETRY_PRIVACY_MODE", "medium")
        
        # Paths
        self.project_dir = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
        self.logs_dir = self.project_dir / "logs" / "claude_telemetry"
        self.archive_dir = self.project_dir / "logs" / "archive"
        
        # Retention settings
        self.max_session_files = int(os.getenv("TELEMETRY_MAX_SESSIONS", "100"))
        self.retention_days = int(os.getenv("TELEMETRY_RETENTION_DAYS", "30"))
        self.max_file_size_mb = int(os.getenv("TELEMETRY_MAX_FILE_SIZE", "10"))
        
        # Privacy settings
        self.include_prompts = self._should_include_prompts()
        self.anonymize_paths = os.getenv("TELEMETRY_ANONYMIZE_PATHS", "true").lower() == "true"
        
    def _should_include_prompts(self) -> bool:
        """Determine if prompts should be included based on privacy mode"""
        privacy_mode = self.privacy_mode.lower()
        return {
            "high": False,      # No prompts, anonymized data only
            "medium": True,     # Prompts hashed, limited content
            "low": True,        # Full prompts included
        }.get(privacy_mode, False)
```

### 5. Hook Entry Point Script
```python
#!/usr/bin/env python3
# scripts/telemetry_hook.py
import sys
import json
import os
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from telemetry.collector import TelemetryCollector
from telemetry.config import TelemetryConfig

def main():
    if len(sys.argv) < 2:
        print("Usage: telemetry_hook.py <event_type>", file=sys.stderr)
        sys.exit(1)
    
    event_type = sys.argv[1]
    
    # Load hook data from environment and stdin
    hook_data = {
        "session_id": os.getenv("CLAUDE_SESSION_ID", "unknown"),
        "project_dir": os.getenv("CLAUDE_PROJECT_DIR", "."),
        "tool_name": os.getenv("CLAUDE_TOOL_NAME"),
        "file_paths": os.getenv("CLAUDE_FILE_PATHS", "").split(),
        "notification": os.getenv("CLAUDE_NOTIFICATION"),
        "timestamp": datetime.utcnow(),
    }
    
    # Try to read JSON data from stdin
    try:
        stdin_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
        hook_data.update(stdin_data)
    except json.JSONDecodeError:
        pass  # Not all hooks provide JSON data
    
    # Initialize collector and collect event
    config = TelemetryConfig()
    if config.enabled:
        collector = TelemetryCollector(config)
        collector.collect_event(event_type, hook_data)

if __name__ == "__main__":
    main()
```

## Key Metrics to Track

### Development Workflow Metrics
- **Cycle Time**: Time from first tool use to session completion
- **Tool Usage Patterns**: Most/least used tools, success rates
- **Error Frequency**: Common failure points and recovery patterns
- **Session Duration**: Typical session lengths and productive periods
- **Context Switching**: Frequency of subagent usage and task changes

### Performance Metrics
- **Tool Execution Time**: Average, median, 95th percentile durations
- **Memory Usage**: Context compaction frequency and triggers
- **Throughput**: Tools per session, sessions per day
- **Success Rates**: Tool success/failure ratios by type

### User Experience Metrics
- **Approval Response Time**: Time from notification to user response
- **Iteration Patterns**: Retry frequency and refinement cycles
- **Prompt Complexity**: Length, iteration, and refinement patterns
- **Feature Adoption**: Usage of new tools and capabilities

## Privacy and Security

### Privacy Modes
- **High Privacy**: No prompts, anonymized paths, basic metrics only
- **Medium Privacy**: Hashed prompts, anonymized sensitive data
- **Low Privacy**: Full logging for personal development optimization

### Data Anonymization
- **User Identification**: Hash or remove personal identifiers
- **File Paths**: Replace sensitive path components with placeholders
- **Prompt Content**: Hash for deduplication while preserving privacy
- **Timestamps**: Preserve for analysis while anonymizing absolute times

### Security Measures
- **Local Storage**: All data stays on user's machine
- **Encryption**: Optional encryption for sensitive logs
- **Access Control**: Proper file permissions on log directories
- **Data Retention**: Automatic cleanup of old logs

## Testing Strategy

### Unit Tests
- **Event Creation**: Test all event model validation
- **Data Collection**: Verify proper logging for each hook type
- **Configuration**: Test all privacy and configuration options
- **File Management**: Test rotation, archival, and cleanup

### Integration Tests
- **Hook Integration**: Test all hooks with actual Claude Code usage
- **Performance Impact**: Measure latency added to operations
- **Error Handling**: Test behavior when logging fails
- **Data Integrity**: Verify logged data accuracy and completeness

### Privacy Tests
- **Data Anonymization**: Verify sensitive data is properly anonymized
- **Configuration Compliance**: Test all privacy mode combinations
- **Data Retention**: Verify automatic cleanup works correctly

## Success Criteria
- ✅ All 8 Claude Code events successfully logged
- ✅ <50ms average latency impact on Claude operations
- ✅ Structured JSON logs with consistent schema
- ✅ Configurable privacy controls working correctly
- ✅ Automatic log rotation preventing disk space issues
- ✅ 99% data capture rate (no missed events)
- ✅ Zero sensitive data leakage in anonymized mode

## Implementation Timeline
- **Day 1-2**: Core telemetry collector and data models
- **Day 3-4**: Hook configuration and entry point script
- **Day 5-6**: Privacy controls and data anonymization
- **Day 7-8**: Testing, error handling, and documentation

## Dependencies
- **Python 3.8+**: For Pydantic models and JSON handling
- **Claude Code**: Version with comprehensive hook support
- **File System**: Write permissions for log directories
- **Virtual Environment**: Thunder Playbook's spacy_env

## Future Enhancements
- **Real-time Dashboard**: Live monitoring of telemetry data
- **Export Capabilities**: Integration with external analytics tools
- **Machine Learning**: Pattern recognition and anomaly detection
- **Team Analytics**: Multi-user aggregation and benchmarking
- **Custom Metrics**: User-defined KPIs and tracking goals