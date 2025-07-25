"""
Validation script to check if OpenAI Agents SDK is properly installed and configured.
"""

import sys
import os
from pathlib import Path

def validate_installation():
    """Validate that all required packages and configurations are present"""
    
    print("🔍 Validating OpenAI Agents SDK Setup")
    print("=" * 40)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version OK")
    
    # Check package installations
    required_packages = [
        ('agents', 'agents'),
        ('openai', 'openai'), 
        ('python-dotenv', 'dotenv')
    ]
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} installed")
        except ImportError:
            print(f"❌ {package_name} not installed")
            return False
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OPENAI_API_KEY found")
    else:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    # Check file structure
    poc_path = Path(__file__).parent
    agents_path = poc_path / "poc_agents"
    
    if agents_path.exists():
        print("✅ poc/poc_agents directory exists")
    else:
        print("❌ poc/poc_agents directory missing")
        return False
    
    print("\n🎉 All validations passed!")
    return True

if __name__ == "__main__":
    success = validate_installation()
    if not success:
        print("\n🔧 Please fix the issues above before running the agent test.")
        sys.exit(1)
    else:
        print("\n🚀 Ready to run: python test_agent_cli.py")