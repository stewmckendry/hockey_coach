#!/usr/bin/env python3
import sys
import os

print("ENV_TEST_RESPONSE:Environment check")
print(f"DEBUG: Python executable: {sys.executable}")
print(f"DEBUG: Working dir: {os.getcwd()}")
print(f"DEBUG: PATH: {os.environ.get('PATH', 'NOT_SET')}")
print(f"DEBUG: PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT_SET')}")
print(f"DEBUG: Python path: {sys.path}")

# Check if we can import agents
try:
    import agents
    print("DEBUG: agents module imported successfully")
except ImportError as e:
    print(f"DEBUG: Cannot import agents: {e}")

# Try to run a simple OpenAI API test
try:
    import openai
    print("DEBUG: openai module imported successfully") 
except ImportError as e:
    print(f"DEBUG: Cannot import openai: {e}")

print("ENV_TEST_RESPONSE:All checks completed")