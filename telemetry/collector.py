"""
Main telemetry collector service for Claude Code workflow analytics.

This module handles the collection, processing, and storage of telemetry events
from Claude Code hooks with performance optimization and error handling.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading
from queue import Queue, Empty
import time

from .models import BaseEvent, EVENT_MODELS, TelemetryMetrics
from .config import TelemetryConfig
from .utils import (
    safe_json_serialize, 
    get_git_info, 
    get_system_info,
    cleanup_old_logs,
    rotate_log_file,
    extract_environment_data
)


class TelemetryCollector:
    """Main collector for telemetry events with async processing and error handling."""
    
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or TelemetryConfig()
        self.setup_logging()
        self.ensure_directories()
        
        # Performance optimization
        self._event_queue = Queue(maxsize=self.config.buffer_size)
        self._processing_thread = None
        self._shutdown_event = threading.Event()
        
        # Session tracking
        self._current_session_id = None
        self._session_metrics = {}
        
        # Start background processing if async enabled
        if self.config.async_logging:
            self.start_background_processing()
    
    def setup_logging(self) -> None:
        """Setup logging configuration for the telemetry system."""
        log_level = logging.DEBUG if self.config.debug_mode else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr),
                logging.FileHandler(self.config.logs_dir / "telemetry.log")
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.config.ensure_directories()
    
    def start_background_processing(self) -> None:
        """Start background thread for async event processing."""
        if self._processing_thread is None or not self._processing_thread.is_alive():
            self._processing_thread = threading.Thread(
                target=self._process_events_background,
                daemon=True
            )
            self._processing_thread.start()
            self.logger.debug("Background processing thread started")
    
    def _process_events_background(self) -> None:
        """Background thread worker for processing events."""
        while not self._shutdown_event.is_set():
            try:
                # Process events from queue with timeout
                try:
                    event_data = self._event_queue.get(timeout=1.0)
                    self._process_event_sync(event_data)
                    self._event_queue.task_done()
                except Empty:
                    continue
                    
            except Exception as e:
                self.logger.error(f"Background processing error: {e}")
                time.sleep(0.1)  # Brief pause on error
    
    def collect_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Main entry point for event collection.
        
        Args:
            event_type: Type of Claude Code event
            event_data: Raw event data from hook
            
        Returns:
            bool: Success status
        """
        start_time = time.time()
        
        try:
            if not self.config.enabled:
                return True
                
            # Enrich event data with system context
            enriched_data = self._enrich_event_data(event_type, event_data)
            
            # Add to processing queue or process synchronously
            if self.config.async_logging:
                try:
                    self._event_queue.put_nowait((event_type, enriched_data))
                    return True
                except:
                    # Queue full, process synchronously as fallback
                    return self._process_event_sync((event_type, enriched_data))
            else:
                return self._process_event_sync((event_type, enriched_data))
                
        except Exception as e:
            self.logger.error(f"Event collection failed for {event_type}: {e}")
            return False
        finally:
            # Performance monitoring
            duration_ms = (time.time() - start_time) * 1000
            if duration_ms > 50:  # Warn if over target latency
                self.logger.warning(f"Event collection took {duration_ms:.1f}ms (target: <50ms)")
    
    def _process_event_sync(self, event_tuple) -> bool:
        """Synchronously process a single event."""
        event_type, event_data = event_tuple
        
        try:
            # Create typed event object
            event = self._create_event(event_type, event_data)
            
            # Log to structured files
            self._log_event(event)
            
            # Update metrics
            self._update_metrics(event)
            
            # Check for maintenance tasks
            self._check_maintenance()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Event processing failed for {event_type}: {e}")
            return False
    
    def _enrich_event_data(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich event data with system context and metadata."""
        enriched = event_data.copy()
        
        # Add timestamp if not present
        if 'timestamp' not in enriched:
            enriched['timestamp'] = datetime.utcnow()
        
        # Add session ID if not present
        if 'session_id' not in enriched:
            enriched['session_id'] = self._get_or_create_session_id()
        
        # Add project directory
        if 'project_dir' not in enriched:
            enriched['project_dir'] = str(self.config.project_dir)
        
        # Add environment data
        env_data = extract_environment_data()
        enriched.update(env_data)
        
        # Add git context for session start
        if event_type == "SessionStart":
            git_info = get_git_info(str(self.config.project_dir))
            enriched.update(git_info)
            
            # Add system info
            system_info = get_system_info()
            enriched['system_info'] = system_info
        
        return enriched
    
    def _get_or_create_session_id(self) -> str:
        """Get current session ID or create new one."""
        if self._current_session_id is None:
            import uuid
            self._current_session_id = str(uuid.uuid4())
        return self._current_session_id
    
    def _create_event(self, event_type: str, data: Dict[str, Any]) -> BaseEvent:
        """Create typed event object from raw data."""
        event_class = EVENT_MODELS.get(event_type, BaseEvent)
        
        try:
            # Filter data to match model fields
            import inspect
            model_fields = inspect.signature(event_class.__init__).parameters.keys()
            filtered_data = {k: v for k, v in data.items() if k in model_fields}
            
            # Ensure event_type is set correctly
            filtered_data['event_type'] = event_type
            
            return event_class(**filtered_data)
        except Exception as e:
            self.logger.warning(f"Failed to create {event_type} event: {e}, using BaseEvent")
            # Fallback to BaseEvent with minimal data
            return BaseEvent(
                event_type=event_type,
                **{k: v for k, v in data.items() if k in ['timestamp', 'session_id', 'project_dir']}
            )
    
    def _log_event(self, event: BaseEvent) -> None:
        """Write event to appropriate log files."""
        event_dict = event.dict()
        event_json = safe_json_serialize(event_dict)
        
        # Session-based logging
        session_file = self.config.get_session_log_path(event.session_id)
        self._append_to_file(session_file, event_json)
        
        # Event-type logging  
        event_file = self.config.get_event_log_path(event.event_type)
        self._append_to_file(event_file, event_json)
        
        # Daily aggregated logging
        daily_file = self.config.get_daily_log_path(
            datetime.now().strftime('%Y%m%d')
        )
        self._append_to_file(daily_file, event_json)
    
    def _append_to_file(self, file_path: Path, content: str) -> None:
        """Safely append content to a log file."""
        try:
            # Check for rotation before writing
            if file_path.exists():
                rotate_log_file(file_path, self.config.max_file_size_mb)
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to write to {file_path}: {e}")
    
    def _update_metrics(self, event: BaseEvent) -> None:
        """Update session metrics with new event."""
        session_id = event.session_id
        
        if session_id not in self._session_metrics:
            self._session_metrics[session_id] = TelemetryMetrics(
                session_id=session_id,
                start_time=event.timestamp
            )
        
        metrics = self._session_metrics[session_id]
        metrics.total_events += 1
        
        # Update tool usage tracking
        if hasattr(event, 'tool_name') and event.tool_name:
            if event.tool_name not in metrics.tool_usage_count:
                metrics.tool_usage_count[event.tool_name] = 0
            metrics.tool_usage_count[event.tool_name] += 1
        
        # Update file access tracking
        if hasattr(event, 'file_paths') and event.file_paths:
            for file_path in event.file_paths:
                if file_path not in metrics.files_accessed:
                    metrics.files_accessed.append(file_path)
        
        # Handle session end
        if event.event_type == "Stop":
            metrics.end_time = event.timestamp
            self._finalize_session_metrics(session_id)
    
    def _finalize_session_metrics(self, session_id: str) -> None:
        """Finalize and persist session metrics."""
        try:
            metrics = self._session_metrics.get(session_id)
            if metrics:
                # Write metrics to file
                metrics_file = self.config.logs_dir / "performance" / f"{session_id}_metrics.json"
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    f.write(metrics.json(indent=2))
                
                # Clean up from memory
                del self._session_metrics[session_id]
                
        except Exception as e:
            self.logger.error(f"Failed to finalize session metrics: {e}")
    
    def _check_maintenance(self) -> None:
        """Periodic maintenance tasks."""
        # Simple rate-limiting: only run maintenance occasionally
        if not hasattr(self, '_last_maintenance'):
            self._last_maintenance = time.time()
            return
            
        if time.time() - self._last_maintenance < 300:  # 5 minutes
            return
            
        try:
            # Cleanup old logs
            cleaned = cleanup_old_logs(self.config.logs_dir, self.config.retention_days)
            if cleaned:
                self.logger.info(f"Cleaned up {len(cleaned)} old log files")
            
            self._last_maintenance = time.time()
            
        except Exception as e:
            self.logger.error(f"Maintenance tasks failed: {e}")
    
    def shutdown(self) -> None:
        """Gracefully shutdown the collector."""
        try:
            # Signal shutdown to background thread
            self._shutdown_event.set()
            
            # Process remaining events in queue
            if self.config.async_logging and self._processing_thread:
                # Give background thread time to finish
                self._processing_thread.join(timeout=5.0)
                
                # Process any remaining events synchronously
                while not self._event_queue.empty():
                    try:
                        event_data = self._event_queue.get_nowait()
                        self._process_event_sync(event_data)
                    except Empty:
                        break
            
            # Finalize any remaining session metrics
            for session_id in list(self._session_metrics.keys()):
                self._finalize_session_metrics(session_id)
                
            self.logger.info("Telemetry collector shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")