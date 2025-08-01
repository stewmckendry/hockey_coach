"""
Configuration management for telemetry system.
"""

import os
from pathlib import Path
from typing import Optional


class TelemetryConfig:
    """Configuration class for telemetry collection and storage."""
    
    def __init__(self):
        # Base configuration
        self.enabled = os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"
        
        # Paths
        self.project_dir = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
        self.logs_dir = self.project_dir / "logs" / "claude_telemetry"
        self.archive_dir = self.project_dir / "logs" / "archive"
        
        # Retention settings
        self.max_session_files = int(os.getenv("TELEMETRY_MAX_SESSIONS", "100"))
        self.retention_days = int(os.getenv("TELEMETRY_RETENTION_DAYS", "30"))
        self.max_file_size_mb = int(os.getenv("TELEMETRY_MAX_FILE_SIZE", "10"))
        
        # Performance settings
        self.async_logging = os.getenv("TELEMETRY_ASYNC", "true").lower() == "true"
        self.buffer_size = int(os.getenv("TELEMETRY_BUFFER_SIZE", "1000"))
        
        # Debug settings
        self.debug_mode = os.getenv("TELEMETRY_DEBUG", "false").lower() == "true"
        
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.logs_dir,
            self.logs_dir / "sessions",
            self.logs_dir / "tools", 
            self.logs_dir / "performance",
            self.logs_dir / "errors",
            self.archive_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_session_log_path(self, session_id: str) -> Path:
        """Get the log file path for a specific session."""
        return self.logs_dir / "sessions" / f"{session_id}.jsonl"
    
    def get_event_log_path(self, event_type: str) -> Path:
        """Get the log file path for a specific event type."""
        return self.logs_dir / f"{event_type.lower()}.jsonl"
    
    def get_daily_log_path(self, date_str: str) -> Path:
        """Get the daily aggregated log file path."""
        return self.logs_dir / f"daily_{date_str}.jsonl"