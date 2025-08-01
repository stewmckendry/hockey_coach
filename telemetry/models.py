"""
Pydantic data models for telemetry events.

This module defines structured data models for all Claude Code events to ensure
consistent logging and analytics across the telemetry system.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid


class BaseEvent(BaseModel):
    """Base model for all telemetry events."""
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_dir: str = Field(default=".")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionStartEvent(BaseEvent):
    """Event logged when a Claude Code session starts."""
    event_type: str = Field(default="SessionStart")
    user_id: Optional[str] = None  # Anonymized user identifier
    claude_version: Optional[str] = None
    project_context: Dict[str, Any] = Field(default_factory=dict)
    git_branch: Optional[str] = None
    git_status: Optional[str] = None


class UserPromptEvent(BaseEvent):
    """Event logged when user submits a prompt."""
    event_type: str = Field(default="UserPromptSubmit")
    prompt_length: int = Field(default=0)  # Make it optional with default value
    prompt_hash: Optional[str] = None  # For deduplication without storing content
    prompt_content: Optional[str] = None  # Only if privacy controls allow
    context_length: Optional[int] = None
    has_file_uploads: bool = Field(default=False)
    upload_count: int = Field(default=0)


class ToolUseEvent(BaseEvent):
    """Event logged for tool usage (both pre and post)."""
    event_type: str  # "PreToolUse" or "PostToolUse"
    tool_name: str = Field(default="unknown")  # Provide default value
    tool_input_size: int = Field(default=0)
    execution_duration_ms: Optional[int] = None
    success: Optional[bool] = None
    error_details: Optional[str] = None
    file_paths: List[str] = Field(default_factory=list)
    output_size: Optional[int] = None
    memory_usage_mb: Optional[float] = None


class SubagentEvent(BaseEvent):
    """Event logged when a subagent completes."""
    event_type: str = Field(default="SubagentStop")
    subagent_type: str = Field(default="unknown")  # Provide default value
    task_description: str = Field(default="")  # Provide default value
    duration_ms: int = Field(default=0)  # Provide default value
    outcome: str = Field(default="unknown")  # success, failure, partial
    tools_used: List[str] = Field(default_factory=list)
    error_count: int = Field(default=0)
    retry_count: int = Field(default=0)


class SessionStopEvent(BaseEvent):
    """Event logged when a Claude Code session ends."""
    event_type: str = Field(default="Stop")
    total_duration_ms: int = Field(default=0)  # Provide default value
    total_tools_used: int = Field(default=0)  # Provide default value
    total_subagents: int = Field(default=0)  # Provide default value
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    error_count: int = Field(default=0)
    unique_tools: List[str] = Field(default_factory=list)
    most_used_tool: Optional[str] = None
    files_modified: List[str] = Field(default_factory=list)


class CompactionEvent(BaseEvent):
    """Event logged before context compaction."""
    event_type: str = Field(default="PreCompact")
    context_size_before: int = Field(default=0)  # Provide default value
    context_size_after: Optional[int] = None
    compaction_reason: str = Field(default="unknown")  # Provide default value
    tools_in_context: int = Field(default=0)
    time_since_last_compact_ms: Optional[int] = None


class NotificationEvent(BaseEvent):
    """Event logged for notification hooks."""
    event_type: str = Field(default="Notification")
    notification_type: str = Field(default="general")  # approval, completion, error, etc.
    message: str = Field(default="")  # Provide default value
    requires_user_action: bool = Field(default=False)
    response_time_ms: Optional[int] = None  # Time until user responds
    user_responded: Optional[bool] = None


# Event type mapping for dynamic creation
EVENT_MODELS = {
    "SessionStart": SessionStartEvent,
    "UserPromptSubmit": UserPromptEvent,
    "PreToolUse": ToolUseEvent,
    "PostToolUse": ToolUseEvent,
    "SubagentStop": SubagentEvent,
    "Stop": SessionStopEvent,
    "PreCompact": CompactionEvent,
    "Notification": NotificationEvent,
}


class TelemetryMetrics(BaseModel):
    """Aggregated metrics for telemetry analysis."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_events: int = Field(default=0)
    tool_usage_count: Dict[str, int] = Field(default_factory=dict)
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    avg_tool_duration_ms: float = Field(default=0.0)
    files_accessed: List[str] = Field(default_factory=list)
    performance_score: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }