"""
Automatic trace logging for hockey diagram MCP tools.
Logs every tool call automatically to a local JSON file.
Supports multiple parallel sessions using thread-local storage.
"""

import json
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import functools
import os

# Thread-local storage for session management
_thread_local = threading.local()

class AutoTraceLogger:
    """Automatic trace logger that captures all tool calls."""
    
    def __init__(self, log_dir: str = None):
        """Initialize the trace logger.
        
        Args:
            log_dir: Directory to store trace logs (default: ./trace_logs)
        """
        if log_dir is None:
            log_dir = Path(__file__).parent.parent / "trace_logs"
        else:
            log_dir = Path(log_dir)
            
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Session storage (for cases where thread-local isn't suitable)
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def start_session(self, drill_request: str = None, session_id: str = None) -> str:
        """Start a new trace session.
        
        Args:
            drill_request: Description of the drill being created
            session_id: Optional session ID (auto-generated if not provided)
            
        Returns:
            Session ID for this trace
        """
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]
        
        session_data = {
            "session_id": session_id,
            "drill_request": drill_request or "Unknown drill",
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "tool_calls": [],
            "status": "in_progress"
        }
        
        # Store in thread-local
        _thread_local.session_id = session_id
        _thread_local.session_data = session_data
        
        # Also store in instance for retrieval
        self.sessions[session_id] = session_data
        
        # Write initial session file
        self._save_session(session_id, session_data)
        
        return session_id
    
    def get_current_session(self) -> Optional[str]:
        """Get the current session ID for this thread."""
        return getattr(_thread_local, 'session_id', None)
    
    def set_session(self, session_id: str) -> bool:
        """Set the active session for this thread.
        
        Args:
            session_id: Session ID to activate
            
        Returns:
            True if session exists and was activated
        """
        session_file = self.log_dir / f"session_{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            _thread_local.session_id = session_id
            _thread_local.session_data = session_data
            self.sessions[session_id] = session_data
            return True
        return False
    
    def log_tool_call(self, tool_name: str, args: Dict[str, Any], 
                      result: Any, phase: str = None, thought: str = None,
                      session_id: str = None) -> None:
        """Log a tool call automatically.
        
        Args:
            tool_name: Name of the tool being called
            args: Arguments passed to the tool
            result: Result returned by the tool
            phase: Optional phase of the workflow
            thought: Optional reasoning about this call
            session_id: Optional session ID (uses current thread session if not provided)
        """
        # Get session ID
        if session_id is None:
            session_id = self.get_current_session()
        
        if session_id is None:
            # No active session - create auto session
            session_id = self.start_session(f"Auto-session for {tool_name}")
        
        # Load session data
        session_data = self._load_session(session_id)
        if session_data is None:
            return
        
        # Determine phase automatically if not provided
        if phase is None:
            phase = self._infer_phase(tool_name)
        
        # Create tool call entry
        tool_call = {
            "timestamp": datetime.now().isoformat(),
            "step": len(session_data["tool_calls"]) + 1,
            "tool": tool_name,
            "args": self._serialize_args(args),
            "result_summary": self._summarize_result(result),
            "phase": phase
        }
        
        # Only add thought if explicitly provided
        if thought:
            tool_call["thought"] = thought
        
        # Add to session
        session_data["tool_calls"].append(tool_call)
        session_data["last_update"] = datetime.now().isoformat()
        
        # Save session
        self._save_session(session_id, session_data)
    
    def update_last_result(self, session_id: str, result: Any):
        """Update the result of the last tool call in a session.
        
        Args:
            session_id: Session ID
            result: Result to update
        """
        session_data = self._load_session(session_id)
        if session_data and session_data["tool_calls"]:
            session_data["tool_calls"][-1]["result_summary"] = self._summarize_result(result)
            self._save_session(session_id, session_data)
    
    def get_session_file_path(self, session_id: str) -> Path:
        """Get the file path for a session's trace log.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to the session trace file
        """
        return self.log_dir / f"session_{session_id}.json"
    
    def complete_session(self, session_id: str = None, success: bool = True,
                        lessons: str = None) -> Dict[str, Any]:
        """Complete a trace session.
        
        Args:
            session_id: Session ID (uses current thread session if not provided)
            success: Whether the diagram was successfully created
            lessons: Key insights learned
            
        Returns:
            Complete session data
        """
        if session_id is None:
            session_id = self.get_current_session()
        
        if session_id is None:
            return {"error": "No active session"}
        
        session_data = self._load_session(session_id)
        if session_data is None:
            return {"error": "Session not found"}
        
        # Update session status
        session_data["end_time"] = datetime.now().isoformat()
        session_data["status"] = "success" if success else "failed"
        session_data["lessons"] = lessons
        session_data["duration_seconds"] = self._calculate_duration(session_data)
        
        # Save final session
        self._save_session(session_id, session_data)
        
        # Clear thread-local if this was the active session
        if self.get_current_session() == session_id:
            _thread_local.session_id = None
            _thread_local.session_data = None
        
        return session_data
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all trace sessions."""
        sessions = []
        for session_file in self.log_dir.glob("session_*.json"):
            with open(session_file, 'r') as f:
                sessions.append(json.load(f))
        return sorted(sessions, key=lambda x: x.get("start_time", ""), reverse=True)
    
    def add_agent_annotations(self, annotations: List[Dict[str, str]], session_id: str = None) -> bool:
        """Add agent's chain of thought annotations to the trace.
        
        Args:
            annotations: List of dicts with 'step' and 'thought' keys
            session_id: Session ID (uses current thread session if not provided)
            
        Returns:
            True if annotations were added successfully
            
        Example:
            annotations = [
                {"step": 1, "thought": "User wants a 2v1 rush, searching for rush templates"},
                {"step": 2, "thought": "Found rush template, now building players for 2v1 scenario"},
                {"step": 3, "thought": "Validating to ensure proper spacing and hockey sense"}
            ]
        """
        if session_id is None:
            session_id = self.get_current_session()
        
        if session_id is None:
            return False
        
        session_data = self._load_session(session_id)
        if session_data is None:
            return False
        
        # Add annotations to matching tool calls
        for annotation in annotations:
            step_num = annotation.get("step")
            thought = annotation.get("thought")
            
            if step_num and thought:
                # Find the tool call with this step number
                for call in session_data.get("tool_calls", []):
                    if call["step"] == step_num:
                        call["agent_thought"] = thought
                        break
        
        # Save updated session
        self._save_session(session_id, session_data)
        return True
    
    def get_session_for_sheets(self, session_id: str = None) -> Dict[str, Any]:
        """Get session data formatted for Google Sheets upload.
        
        Args:
            session_id: Session ID (uses current thread session if not provided)
            
        Returns:
            Dictionary with rows ready for Sheets
        """
        if session_id is None:
            session_id = self.get_current_session()
        
        session_data = self._load_session(session_id)
        if session_data is None:
            return {"error": "Session not found"}
        
        rows = []
        for call in session_data.get("tool_calls", []):
            row = [
                call["timestamp"],
                session_id,
                session_data.get("drill_request", ""),
                str(call["step"]),
                call.get("phase", ""),
                call["tool"],
                call.get("agent_thought", ""),  # Use agent_thought if available
                json.dumps(call.get("args", {}))[:500],  # Truncate long args
                call.get("result_summary", "")[:500],  # Truncate long results
                session_data.get("status", ""),
                session_data.get("lessons", ""),
                session_data.get("duration_seconds", "")
            ]
            rows.append(row)
        
        return {
            "session_id": session_id,
            "rows": rows,
            "row_count": len(rows),
            "headers": [
                "Timestamp", "Session ID", "Drill Request", "Step", "Phase",
                "Tool", "Thought", "Args", "Result", "Status", "Lessons", "Duration"
            ]
        }
    
    def _load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from file."""
        session_file = self.log_dir / f"session_{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                return json.load(f)
        return self.sessions.get(session_id)
    
    def _save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Save session data to file."""
        session_file = self.log_dir / f"session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
    
    def _infer_phase(self, tool_name: str) -> str:
        """Infer workflow phase from tool name."""
        if "search" in tool_name or "find" in tool_name or "list" in tool_name:
            return "1_Discovery"
        elif "create" in tool_name or "build" in tool_name:
            return "2_Building"
        elif "validate" in tool_name:
            return "3_Validation"
        elif "generate" in tool_name or "preview" in tool_name:
            return "4_Generation"
        elif "save" in tool_name or "complete" in tool_name:
            return "5_Completion"
        else:
            return "0_Unknown"
    
    def _serialize_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize arguments for JSON storage."""
        serialized = {}
        for key, value in args.items():
            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                serialized[key] = value
            else:
                serialized[key] = str(value)
        return serialized
    
    def _summarize_result(self, result: Any) -> str:
        """Create a summary of the tool result."""
        if result is None:
            return "No result"
        elif isinstance(result, bool):
            return "Success" if result else "Failed"
        elif isinstance(result, dict):
            if "error" in result:
                return f"Error: {result['error']}"
            elif "valid" in result:
                return f"Valid: {result['valid']}"
            elif "name" in result:
                return f"Found: {result.get('name', 'Unknown')}"
            else:
                return f"Dict with {len(result)} keys"
        elif isinstance(result, list):
            return f"List with {len(result)} items"
        elif isinstance(result, str):
            return result[:100] + "..." if len(result) > 100 else result
        else:
            return str(result)[:100]
    
    def _calculate_duration(self, session_data: Dict[str, Any]) -> float:
        """Calculate session duration in seconds."""
        try:
            start = datetime.fromisoformat(session_data["start_time"])
            end = datetime.fromisoformat(session_data.get("end_time", datetime.now().isoformat()))
            return (end - start).total_seconds()
        except:
            return 0.0


# Global logger instance
_logger = AutoTraceLogger()


def auto_log(phase: str = None):
    """Decorator to automatically log tool calls.
    
    Args:
        phase: Optional phase name for this tool
        
    Example:
        @auto_log(phase="1_Discovery")
        def find_template(description: str) -> dict:
            # Tool implementation
            return result
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function name as tool name
            tool_name = func.__name__
            
            # Combine args and kwargs for logging
            all_args = {}
            if args and len(args) > 0:
                # Skip 'self' if this is a method
                start_idx = 1 if len(args) > 0 and hasattr(args[0], '__class__') else 0
                arg_names = func.__code__.co_varnames[start_idx:len(args)]
                all_args.update(dict(zip(arg_names, args[start_idx:])))
            all_args.update(kwargs)
            
            # Execute the tool
            try:
                result = func(*args, **kwargs)
                
                # Log the successful call
                _logger.log_tool_call(
                    tool_name=tool_name,
                    args=all_args,
                    result=result,
                    phase=phase
                )
                
                return result
                
            except Exception as e:
                # Log the failed call
                _logger.log_tool_call(
                    tool_name=tool_name,
                    args=all_args,
                    result={"error": str(e)},
                    phase=phase,
                    thought=f"Error in {tool_name}: {str(e)}"
                )
                raise
        
        return wrapper
    return decorator


# Convenience functions for direct use
def start_session(drill_request: str = None, session_id: str = None) -> str:
    """Start a new trace session."""
    return _logger.start_session(drill_request, session_id)

def set_session(session_id: str) -> bool:
    """Set the active session for this thread."""
    return _logger.set_session(session_id)

def get_current_session() -> Optional[str]:
    """Get the current session ID."""
    return _logger.get_current_session()

def complete_session(session_id: str = None, success: bool = True, lessons: str = None) -> Dict[str, Any]:
    """Complete a trace session."""
    return _logger.complete_session(session_id, success, lessons)

def get_session_for_sheets(session_id: str = None) -> Dict[str, Any]:
    """Get session data formatted for Google Sheets."""
    return _logger.get_session_for_sheets(session_id)

def add_agent_annotations(annotations: List[Dict[str, str]], session_id: str = None) -> bool:
    """Add agent's chain of thought annotations to the trace."""
    return _logger.add_agent_annotations(annotations, session_id)

def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all trace sessions."""
    return _logger.get_all_sessions()

def get_logger() -> AutoTraceLogger:
    """Get the singleton logger instance."""
    return _logger