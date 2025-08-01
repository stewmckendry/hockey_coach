"""
Utility functions for telemetry system.
"""

import json
import hashlib
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging


def hash_content(content: str, algorithm: str = "sha256") -> str:
    """Generate a hash of content for deduplication without storing sensitive data."""
    hasher = hashlib.new(algorithm)
    hasher.update(content.encode('utf-8'))
    return hasher.hexdigest()


def anonymize_path(path: str, project_root: str) -> str:
    """Anonymize file paths to protect sensitive information."""
    try:
        # Convert to Path objects for better handling
        path_obj = Path(path)
        root_obj = Path(project_root)
        
        # Try to make path relative to project root
        try:
            relative_path = path_obj.relative_to(root_obj)
            return f"<project>/{relative_path}"
        except ValueError:
            # Path is outside project root
            # Replace user home directory with <home>
            home = Path.home()
            try:
                relative_to_home = path_obj.relative_to(home)
                return f"<home>/{relative_to_home}"
            except ValueError:
                # Path is not in home directory either
                # Just return filename for maximum privacy
                return f"<external>/{path_obj.name}"
                
    except Exception:
        # If any error occurs, just return the filename
        return f"<unknown>/{Path(path).name}"


def safe_json_serialize(data: Dict[str, Any]) -> str:
    """Safely serialize data to JSON, handling datetime and other problematic types."""
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    try:
        return json.dumps(data, default=json_serializer, ensure_ascii=False)
    except Exception as e:
        # Fallback serialization
        safe_data = {
            "error": "serialization_failed",
            "error_details": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "original_keys": list(data.keys()) if isinstance(data, dict) else "not_dict"
        }
        return json.dumps(safe_data)


def get_git_info(project_dir: str) -> Dict[str, Optional[str]]:
    """Get git repository information safely."""
    git_info = {
        "branch": None,
        "status": None,
        "last_commit": None
    }
    
    try:
        import subprocess
        project_path = Path(project_dir)
        
        # Check if git repo exists
        if not (project_path / ".git").exists():
            return git_info
            
        # Get current branch
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                git_info["branch"] = result.stdout.strip()
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
            
        # Get status (just summary)
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    git_info["status"] = f"{len(lines)} files changed"
                else:
                    git_info["status"] = "clean"
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
            
        # Get last commit hash (short)
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                git_info["last_commit"] = result.stdout.strip()
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
            
    except ImportError:
        # subprocess not available
        pass
    except Exception:
        # Any other error
        pass
        
    return git_info


def get_system_info() -> Dict[str, Any]:
    """Get basic system information for context."""
    info = {
        "platform": sys.platform,
        "python_version": sys.version.split()[0],
        "working_directory": os.getcwd(),
    }
    
    try:
        import platform
        info["os_name"] = platform.system()
        info["os_version"] = platform.release()
    except ImportError:
        pass
    
    return info


def cleanup_old_logs(logs_dir: Path, retention_days: int) -> List[str]:
    """Clean up old log files based on retention policy."""
    cleaned_files = []
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    try:
        for log_file in logs_dir.rglob("*.jsonl"):
            try:
                # Check file modification time
                file_modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_modified < cutoff_date:
                    # Move to archive before deleting (optional)
                    archive_dir = logs_dir.parent / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    
                    archive_path = archive_dir / f"{log_file.stem}_{file_modified.strftime('%Y%m%d')}.jsonl"
                    log_file.rename(archive_path)
                    cleaned_files.append(str(log_file))
                    
            except Exception as e:
                logging.warning(f"Failed to process log file {log_file}: {e}")
                
    except Exception as e:
        logging.error(f"Log cleanup failed: {e}")
        
    return cleaned_files


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes."""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except Exception:
        return 0.0


def rotate_log_file(file_path: Path, max_size_mb: float) -> bool:
    """Rotate log file if it exceeds maximum size."""
    try:
        if get_file_size_mb(file_path) > max_size_mb:
            # Create rotated filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_name = f"{file_path.stem}_{timestamp}.jsonl"
            rotated_path = file_path.parent / rotated_name
            
            # Move current file to rotated name
            file_path.rename(rotated_path)
            return True
    except Exception as e:
        logging.error(f"Log rotation failed for {file_path}: {e}")
        
    return False


def format_duration(duration_ms: int) -> str:
    """Format duration in milliseconds to human-readable string."""
    if duration_ms < 1000:
        return f"{duration_ms}ms"
    elif duration_ms < 60000:
        return f"{duration_ms / 1000:.1f}s"
    else:
        minutes = duration_ms // 60000
        seconds = (duration_ms % 60000) / 1000
        return f"{minutes}m {seconds:.1f}s"


def extract_environment_data() -> Dict[str, Any]:
    """Extract relevant environment data for telemetry."""
    env_data = {}
    
    # Claude-specific environment variables
    claude_vars = [
        "CLAUDE_SESSION_ID",
        "CLAUDE_PROJECT_DIR", 
        "CLAUDE_TOOL_NAME",
        "CLAUDE_FILE_PATHS",
        "CLAUDE_NOTIFICATION",
        "CLAUDE_USER_ID"
    ]
    
    for var in claude_vars:
        value = os.getenv(var)
        if value:
            # Anonymize sensitive data
            if var == "CLAUDE_FILE_PATHS":
                paths = value.split()
                project_dir = os.getenv("CLAUDE_PROJECT_DIR", ".")
                env_data[var] = [anonymize_path(p, project_dir) for p in paths]
            elif var == "CLAUDE_USER_ID":
                env_data[var] = hash_content(value)[:8]  # Short hash for anonymity
            else:
                env_data[var] = value
                
    return env_data