"""
Unit tests for telemetry system components.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from telemetry.config import TelemetryConfig
from telemetry.utils import (
    hash_content, 
    anonymize_path, 
    safe_json_serialize,
    format_duration,
    extract_environment_data
)


class TestTelemetryConfig(unittest.TestCase):
    """Test TelemetryConfig class."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def test_default_config(self):
        """Test default configuration values."""
        config = TelemetryConfig()
        
        self.assertTrue(config.enabled)  # Default is enabled
        self.assertEqual(config.max_session_files, 100)
        self.assertEqual(config.retention_days, 30)
        self.assertEqual(config.max_file_size_mb, 10)
        self.assertTrue(config.async_logging)
        
    def test_environment_override(self):
        """Test environment variable overrides."""
        with patch.dict(os.environ, {
            'TELEMETRY_ENABLED': 'false',
            'TELEMETRY_MAX_SESSIONS': '50',
            'TELEMETRY_RETENTION_DAYS': '14',
            'TELEMETRY_DEBUG': 'true'
        }):
            config = TelemetryConfig()
            
            self.assertFalse(config.enabled)
            self.assertEqual(config.max_session_files, 50)
            self.assertEqual(config.retention_days, 14)
            self.assertTrue(config.debug_mode)
    
    def test_ensure_directories(self):
        """Test directory creation."""
        with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': self.temp_dir}):
            config = TelemetryConfig()
            config.ensure_directories()
            
            # Check that all directories are created
            self.assertTrue(config.logs_dir.exists())
            self.assertTrue((config.logs_dir / "sessions").exists())
            self.assertTrue((config.logs_dir / "tools").exists())
            self.assertTrue((config.logs_dir / "performance").exists())
            self.assertTrue((config.logs_dir / "errors").exists())
            self.assertTrue(config.archive_dir.exists())
    
    def test_path_getters(self):
        """Test path getter methods."""
        config = TelemetryConfig()
        
        session_path = config.get_session_log_path("test-session")
        self.assertTrue(str(session_path).endswith("test-session.jsonl"))
        
        event_path = config.get_event_log_path("SessionStart")
        self.assertTrue(str(event_path).endswith("sessionstart.jsonl"))
        
        daily_path = config.get_daily_log_path("20250731")
        self.assertTrue(str(daily_path).endswith("daily_20250731.jsonl"))


class TestTelemetryUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_hash_content(self):
        """Test content hashing."""
        content = "test content"
        hash1 = hash_content(content)
        hash2 = hash_content(content)
        
        # Same content should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Different content should produce different hash
        hash3 = hash_content("different content")
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be reasonable length
        self.assertGreater(len(hash1), 10)
    
    def test_anonymize_path(self):
        """Test path anonymization."""
        project_root = "/Users/test/project"
        
        # Path within project
        internal_path = "/Users/test/project/src/main.py"
        anonymized = anonymize_path(internal_path, project_root)
        self.assertEqual(anonymized, "<project>/src/main.py")
        
        # Path in home directory
        home_path = "/Users/test/Documents/file.txt"
        with patch('pathlib.Path.home', return_value=Path("/Users/test")):
            anonymized = anonymize_path(home_path, project_root)
            self.assertEqual(anonymized, "<home>/Documents/file.txt")
    
    def test_safe_json_serialize(self):
        """Test safe JSON serialization."""
        # Test normal data
        data = {"key": "value", "number": 42}
        result = safe_json_serialize(data)
        self.assertIn("key", result)
        self.assertIn("value", result)
        
        # Test with datetime
        data_with_datetime = {
            "timestamp": datetime(2025, 1, 1, 12, 0, 0),
            "text": "test"
        }
        result = safe_json_serialize(data_with_datetime)
        self.assertIn("2025-01-01T12:00:00", result)
        
        # Test with problematic data
        class UnserializableObject:
            def __str__(self):
                return "unserializable"
        
        data_with_problem = {"obj": UnserializableObject()}
        result = safe_json_serialize(data_with_problem)
        # Should not raise exception and should contain something
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_format_duration(self):
        """Test duration formatting."""
        self.assertEqual(format_duration(500), "500ms")
        self.assertEqual(format_duration(1500), "1.5s")
        self.assertEqual(format_duration(65000), "1m 5.0s")
    
    def test_extract_environment_data(self):
        """Test environment data extraction."""
        with patch.dict(os.environ, {
            'CLAUDE_SESSION_ID': 'test-session',
            'CLAUDE_TOOL_NAME': 'Read',
            'CLAUDE_FILE_PATHS': '/path/to/file1.py /path/to/file2.py',
            'CLAUDE_USER_ID': 'user123'
        }):
            env_data = extract_environment_data()
            
            self.assertEqual(env_data['CLAUDE_SESSION_ID'], 'test-session')
            self.assertEqual(env_data['CLAUDE_TOOL_NAME'], 'Read')
            self.assertIsInstance(env_data['CLAUDE_FILE_PATHS'], list)
            self.assertEqual(len(env_data['CLAUDE_FILE_PATHS']), 2)
            # User ID should be hashed
            self.assertNotEqual(env_data['CLAUDE_USER_ID'], 'user123')
            self.assertEqual(len(env_data['CLAUDE_USER_ID']), 8)


class TestTelemetryIntegration(unittest.TestCase):
    """Integration tests for telemetry system."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def test_hook_script_execution(self):
        """Test that hook script executes without errors."""
        hook_script = Path(__file__).parent.parent / "scripts" / "telemetry_hook.py"
        
        # Test with telemetry disabled to avoid side effects
        env = os.environ.copy()
        env.update({
            'TELEMETRY_ENABLED': 'false',
            'TELEMETRY_DEBUG': 'true',
            'CLAUDE_PROJECT_DIR': self.temp_dir
        })
        
        import subprocess
        result = subprocess.run([
            sys.executable, str(hook_script), "SessionStart"
        ], env=env, capture_output=True, text=True, timeout=10)
        
        # Should exit cleanly even when disabled
        self.assertEqual(result.returncode, 0)
    
    def test_hook_script_invalid_args(self):
        """Test hook script with invalid arguments."""
        hook_script = Path(__file__).parent.parent / "scripts" / "telemetry_hook.py"
        
        import subprocess
        result = subprocess.run([
            sys.executable, str(hook_script)  # No event type
        ], capture_output=True, text=True, timeout=10)
        
        # Should fail with usage message
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stderr)


class TestEventModels(unittest.TestCase):
    """Test event model functionality."""
    
    def test_event_models_import(self):
        """Test that event models can be imported without dependencies."""
        # This test only runs if dependencies are available
        try:
            from telemetry.models import (
                BaseEvent, SessionStartEvent, UserPromptEvent,
                ToolUseEvent, EVENT_MODELS
            )
            
            # Test basic event creation
            base_event = BaseEvent(event_type="Test")  
            self.assertEqual(base_event.event_type, "Test")
            self.assertIsInstance(base_event.timestamp, datetime)
            
            # Test session start event
            session_event = SessionStartEvent(session_id="test-123")
            self.assertEqual(session_event.event_type, "SessionStart")
            self.assertEqual(session_event.session_id, "test-123")
            
            # Test event model mapping
            self.assertIn("SessionStart", EVENT_MODELS)
            self.assertEqual(EVENT_MODELS["SessionStart"], SessionStartEvent)
            
        except ImportError:
            self.skipTest("Pydantic not available - skipping model tests")


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(loader.loadTestsFromTestCase(TestTelemetryConfig))
    suite.addTest(loader.loadTestsFromTestCase(TestTelemetryUtils))
    suite.addTest(loader.loadTestsFromTestCase(TestTelemetryIntegration))
    suite.addTest(loader.loadTestsFromTestCase(TestEventModels))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)