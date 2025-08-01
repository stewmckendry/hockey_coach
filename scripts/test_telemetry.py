#!/usr/bin/env python3
"""
Test script for telemetry system functionality.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_functionality():
    """Test basic telemetry functionality without dependencies."""
    print("=== Testing Telemetry System ===")
    
    # Test 1: Hook script execution
    print("\n1. Testing hook script...")
    hook_script = project_root / "scripts" / "telemetry_hook.py"
    if hook_script.exists():
        print(f"✓ Hook script exists at {hook_script}")
        print(f"✓ Script is executable: {os.access(hook_script, os.X_OK)}")
    else:
        print("✗ Hook script not found")
        return False
    
    # Test 2: Directory structure
    print("\n2. Testing directory structure...")
    telemetry_dir = project_root / "telemetry"
    logs_dir = project_root / "logs" / "claude_telemetry"
    
    required_files = [
        telemetry_dir / "__init__.py",
        telemetry_dir / "models.py", 
        telemetry_dir / "config.py",
        telemetry_dir / "collector.py",
        telemetry_dir / "utils.py"
    ]
    
    for file_path in required_files:
        if file_path.exists():
            print(f"✓ {file_path.name} exists")
        else:
            print(f"✗ {file_path.name} missing")
            return False
    
    # Test 3: Log directories
    expected_dirs = [
        logs_dir,
        logs_dir / "sessions",
        logs_dir / "tools",  
        logs_dir / "performance",
        logs_dir / "errors"
    ]
    
    for dir_path in expected_dirs:
        if dir_path.exists():
            print(f"✓ {dir_path.name} directory exists")
        else:
            print(f"✗ {dir_path.name} directory missing")
            return False
    
    # Test 4: Import test (without Pydantic dependencies)
    print("\n3. Testing imports...")
    try:
        # Test basic imports that don't require external dependencies
        from telemetry.config import TelemetryConfig
        print("✓ Config import successful")
        
        config = TelemetryConfig()
        print(f"✓ Config created (enabled: {config.enabled})")
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Test 5: Hook script basic execution
    print("\n4. Testing hook script execution...")
    os.environ["TELEMETRY_DEBUG"] = "true"
    os.environ["TELEMETRY_ENABLED"] = "false"  # Disable actual logging for test
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, str(hook_script), "SessionStart"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Hook script executes without error")
        else:
            print(f"✗ Hook script failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Hook execution test failed: {e}")
        return False
    
    print("\n=== All Basic Tests Passed! ===")
    return True

def test_with_dependencies():
    """Test telemetry with full dependencies."""
    print("\n=== Testing with Dependencies ===")
    
    try:
        from telemetry.models import SessionStartEvent, EVENT_MODELS
        from telemetry.collector import TelemetryCollector
        print("✓ All imports successful")
        
        # Test event creation
        event = SessionStartEvent(session_id="test-session")
        print(f"✓ Event created: {event.event_type}")
        
        # Test collector initialization  
        collector = TelemetryCollector()
        print("✓ Collector initialized")
        
        return True
        
    except ImportError as e:
        print(f"✗ Dependency test failed: {e}")
        print("  Install dependencies with: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    
    if success:
        test_with_dependencies()
    
    print(f"\nTest completed: {'SUCCESS' if success else 'FAILED'}")