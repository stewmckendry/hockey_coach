#!/usr/bin/env python3
"""
Telemetry hook entry point for Claude Code events.

This script is called by Claude Code hooks to collect and process telemetry data.
It handles all event types and provides performance-optimized data collection.
"""

import sys
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for telemetry hook."""
    start_time = time.time()
    
    try:
        # Parse command line arguments
        if len(sys.argv) < 2:
            print("Usage: telemetry_hook.py <event_type>", file=sys.stderr)
            sys.exit(1)
        
        event_type = sys.argv[1]
        
        # Quick exit if telemetry is disabled
        if os.getenv("TELEMETRY_ENABLED", "true").lower() != "true":
            sys.exit(0)
        
        # Import telemetry components (only if enabled)
        try:
            from telemetry.collector import TelemetryCollector
            from telemetry.config import TelemetryConfig
        except ImportError as e:
            # Graceful fallback if dependencies missing
            if os.getenv("TELEMETRY_DEBUG", "false").lower() == "true":
                print(f"Telemetry import failed: {e}", file=sys.stderr)
            sys.exit(0)
        
        # Collect hook data from Claude Code JSON input
        hook_data = collect_hook_data(event_type)
        
        # Initialize collector and collect event
        try:
            config = TelemetryConfig()
            collector = TelemetryCollector(config)
            
            success = collector.collect_event(event_type, hook_data)
            
            # CRITICAL: Ensure async events are flushed before exiting
            # Without this, events stay in the queue and are lost
            if config.async_logging:
                # Give background thread time to process the queue
                time.sleep(0.1)  # Small delay for async processing
                collector.shutdown()  # Flush remaining events
            
            # Performance monitoring
            duration_ms = (time.time() - start_time) * 1000
            if duration_ms > 100:  # Warn if over 100ms
                print(f"Warning: Hook took {duration_ms:.1f}ms", file=sys.stderr)
            
            sys.exit(0 if success else 1)
            
        except Exception as e:
            if os.getenv("TELEMETRY_DEBUG", "false").lower() == "true":
                import traceback
                print(f"Telemetry error: {e}", file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
            sys.exit(0)  # Don't fail Claude operations on telemetry errors
            
    except Exception as e:
        # Absolute fallback - never let telemetry break Claude
        if os.getenv("TELEMETRY_DEBUG", "false").lower() == "true":
            print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


def collect_hook_data(event_type: str) -> dict:
    """Collect data from Claude Code JSON input via stdin."""
    
    # Base event data
    hook_data = {
        "event_type": event_type,
        "timestamp": datetime.utcnow(),
        "project_dir": os.getenv("CLAUDE_PROJECT_DIR", str(Path.cwd())),
    }
    
    # Read JSON data from stdin (Claude Code passes this)
    claude_data = {}
    try:
        if not sys.stdin.isatty():
            stdin_content = sys.stdin.read().strip()
            if stdin_content:
                try:
                    claude_data = json.loads(stdin_content)
                    if os.getenv("TELEMETRY_DEBUG", "false").lower() == "true":
                        print(f"Claude data: {json.dumps(claude_data, indent=2)}", file=sys.stderr)
                except json.JSONDecodeError as e:
                    if os.getenv("TELEMETRY_DEBUG", "false").lower() == "true":
                        print(f"JSON decode error: {e}, content: {stdin_content[:100]}", file=sys.stderr)
                    hook_data["raw_input"] = stdin_content
    except Exception as e:
        if os.getenv("TELEMETRY_DEBUG", "false").lower() == "true":
            print(f"Error reading stdin: {e}", file=sys.stderr)
    
    # Extract session_id from Claude data or generate one
    hook_data["session_id"] = claude_data.get("session_id", str(uuid.uuid4())[:8])
    
    # Extract event-specific data from Claude Code JSON input
    if event_type == "UserPromptSubmit":
        hook_data.update(extract_user_prompt_data(claude_data))
    elif event_type == "PreToolUse":
        hook_data.update(extract_pre_tool_data(claude_data))
    elif event_type == "PostToolUse":
        hook_data.update(extract_post_tool_data(claude_data))
    elif event_type == "Stop":
        hook_data.update(extract_stop_data(claude_data))
    elif event_type == "SubagentStop":
        hook_data.update(extract_subagent_data(claude_data))
    elif event_type == "Notification":
        hook_data.update(extract_notification_data(claude_data))
    elif event_type == "PreCompact":
        hook_data.update(extract_compact_data(claude_data))
    elif event_type == "SessionStart":
        hook_data.update(extract_session_start_data(claude_data))
    
    return hook_data


def extract_user_prompt_data(claude_data: dict) -> dict:
    """Extract UserPromptSubmit-specific data from Claude input."""
    data = {}
    
    # According to official docs, UserPromptSubmit has "prompt" field
    prompt = claude_data.get("prompt", "")
    if prompt:
        data["prompt_length"] = len(prompt)
        data["prompt_hash"] = hash_content(prompt)
        # Store first 100 chars for debugging (can be disabled later)
        data["prompt_preview"] = prompt[:100] + "..." if len(prompt) > 100 else prompt
    else:
        data["prompt_length"] = 0
        data["prompt_preview"] = ""
    
    # Extract session metadata
    data["transcript_path"] = claude_data.get("transcript_path", "")
    data["cwd"] = claude_data.get("cwd", "")
    
    return data


def extract_pre_tool_data(claude_data: dict) -> dict:
    """Extract PreToolUse-specific data from Claude input."""
    data = {}
    
    # Direct fields from Claude Code JSON
    data["tool_name"] = claude_data.get("tool_name", "unknown")
    tool_input = claude_data.get("tool_input", {})
    data["tool_input_size"] = len(str(tool_input))
    
    # Extract specific tool parameters based on tool type
    if isinstance(tool_input, dict):
        # File operations
        file_path = tool_input.get("file_path") or tool_input.get("path")
        if file_path:
            data["file_paths"] = [anonymize_path(file_path)]
        elif tool_input.get("file_paths"):
            data["file_paths"] = [anonymize_path(p) for p in tool_input["file_paths"]]
        
        # Bash commands
        if data["tool_name"] == "Bash" and "command" in tool_input:
            data["command"] = tool_input["command"][:100] + "..." if len(tool_input.get("command", "")) > 100 else tool_input.get("command", "")
        
        # Search operations
        if data["tool_name"] in ["Grep", "Glob", "WebSearch"]:
            data["search_pattern"] = tool_input.get("pattern", tool_input.get("query", ""))[:50]
    
    return data


def extract_post_tool_data(claude_data: dict) -> dict:
    """Extract PostToolUse-specific data from Claude input."""
    data = {}
    
    # Direct fields from Claude Code JSON
    data["tool_name"] = claude_data.get("tool_name", "unknown")
    tool_input = claude_data.get("tool_input", {})
    data["tool_input_size"] = len(str(tool_input))
    
    # Tool response data
    tool_response = claude_data.get("tool_response", {})
    if tool_response:
        data["output_size"] = len(str(tool_response))
        # Check for success based on tool type
        if "success" in tool_response:
            data["success"] = tool_response["success"]
        elif "error" in tool_response:
            data["success"] = False
            data["error_details"] = str(tool_response["error"])[:200]
        else:
            data["success"] = True  # Assume success if no error
        
        # Extract specific response fields
        if data["tool_name"] == "Write" and "filePath" in tool_response:
            data["output_file"] = anonymize_path(tool_response["filePath"])
    
    # Extract file paths from input
    if isinstance(tool_input, dict):
        file_path = tool_input.get("file_path") or tool_input.get("path")
        if file_path:
            data["file_paths"] = [anonymize_path(file_path)]
        elif tool_input.get("file_paths"):
            data["file_paths"] = [anonymize_path(p) for p in tool_input["file_paths"]]
        
        # Include command for Bash tools
        if data["tool_name"] == "Bash" and "command" in tool_input:
            data["command"] = tool_input["command"][:100] + "..." if len(tool_input.get("command", "")) > 100 else tool_input.get("command", "")
    
    return data


def extract_stop_data(claude_data: dict) -> dict:
    """Extract Stop-specific data from Claude input."""
    data = {}
    
    data["stop_hook_active"] = claude_data.get("stop_hook_active", False)
    
    # Session summary data if available
    if "session_summary" in claude_data:
        summary = claude_data["session_summary"]
        data["total_tools_used"] = summary.get("tools_used", 0)
        data["total_duration_ms"] = summary.get("duration_ms", 0)
        data["success_rate"] = summary.get("success_rate", 0.0)
        data["error_count"] = summary.get("error_count", 0)
    
    return data


def extract_subagent_data(claude_data: dict) -> dict:
    """Extract SubagentStop-specific data from Claude input."""
    data = {}
    
    data["subagent_type"] = claude_data.get("subagent_type", "unknown")
    data["task_description"] = claude_data.get("task_description", "")
    data["outcome"] = claude_data.get("outcome", "unknown")
    data["stop_hook_active"] = claude_data.get("stop_hook_active", False)
    
    if "duration_ms" in claude_data:
        data["duration_ms"] = claude_data["duration_ms"]
    
    return data


def extract_notification_data(claude_data: dict) -> dict:
    """Extract Notification-specific data from Claude input."""
    data = {}
    
    # According to official docs, Notification has "message" field
    message = claude_data.get("message", "")
    data["message"] = message[:200] + "..." if len(message) > 200 else message
    data["notification_type"] = classify_notification(message)
    data["requires_user_action"] = is_approval_notification(message)
    
    # Include transcript path for potential analysis
    data["transcript_path"] = claude_data.get("transcript_path", "")
    
    return data


def extract_compact_data(claude_data: dict) -> dict:
    """Extract PreCompact-specific data from Claude input."""
    data = {}
    
    # According to official docs, PreCompact has "trigger" and "custom_instructions"
    data["trigger"] = claude_data.get("trigger", "unknown")  # "manual" or "auto"
    data["custom_instructions"] = claude_data.get("custom_instructions", "")[:100] if claude_data.get("custom_instructions") else ""
    data["transcript_path"] = claude_data.get("transcript_path", "")
    
    return data


def extract_session_start_data(claude_data: dict) -> dict:
    """Extract SessionStart-specific data from Claude input."""
    data = {}
    
    # According to official docs, SessionStart has "source" field
    data["source"] = claude_data.get("source", "startup")  # "startup" is default
    data["user_id"] = hash_user_id(os.getenv("USER", "unknown"))
    data["transcript_path"] = claude_data.get("transcript_path", "")
    data["cwd"] = claude_data.get("cwd", "")
    
    # Add git context using cwd
    git_info = get_git_info(claude_data.get("cwd", "."))
    data.update(git_info)
    
    return data


def hash_content(content: str) -> str:
    """Generate a hash of content for deduplication."""
    import hashlib
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


def hash_user_id(user_id: str) -> str:
    """Generate anonymized user identifier."""
    import hashlib
    return hashlib.sha256(user_id.encode('utf-8')).hexdigest()[:8]


def anonymize_path(file_path: str) -> str:
    """Anonymize file paths for privacy."""
    try:
        path_obj = Path(file_path)
        project_dir = os.getenv("CLAUDE_PROJECT_DIR", ".")
        
        # Try to make relative to project
        try:
            relative = path_obj.relative_to(Path(project_dir))
            return f"<project>/{relative}"
        except ValueError:
            # Try relative to home
            try:
                relative = path_obj.relative_to(Path.home())
                return f"<home>/{relative}"
            except ValueError:
                return f"<external>/{path_obj.name}"
    except Exception:
        return f"<unknown>/{Path(file_path).name}"


def classify_notification(message: str) -> str:
    """Classify notification type based on message content."""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["approval", "approve", "confirm", "permission"]):
        return "approval"
    elif any(word in message_lower for word in ["error", "failed", "exception"]):
        return "error"
    elif any(word in message_lower for word in ["completed", "finished", "done"]):
        return "completion"
    elif "waiting" in message_lower:
        return "waiting"
    else:
        return "general"


def is_approval_notification(message: str) -> bool:
    """Check if notification requires user action."""
    approval_keywords = [
        "approval", "approve", "confirm", "permission", 
        "authorize", "allow", "proceed", "continue"
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in approval_keywords)


def get_git_info(project_dir: str) -> dict:
    """Get git repository information safely."""
    git_info = {
        "git_branch": None,
        "git_status": None,
        "git_last_commit": None
    }
    
    try:
        import subprocess
        project_path = Path(project_dir)
        
        if not (project_path / ".git").exists():
            return git_info
            
        # Get current branch
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                git_info["git_branch"] = result.stdout.strip()
        except:
            pass
            
        # Get status summary
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                lines = [l for l in result.stdout.strip().split('\n') if l]
                if lines:
                    git_info["git_status"] = f"{len(lines)} files changed"
                else:
                    git_info["git_status"] = "clean"
        except:
            pass
            
        # Get last commit
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                git_info["git_last_commit"] = result.stdout.strip()
        except:
            pass
            
    except:
        pass
        
    return git_info


if __name__ == "__main__":
    main()