"""
Basic setup test for Hockey Diagram Agent components.
Tests what can be tested without full virtual environment.
"""

import sys
import os
from pathlib import Path

def test_file_structure():
    """Test that all required files exist."""
    print("📁 Checking file structure...")
    
    current_dir = Path(__file__).parent
    required_files = [
        "hockey_diagram_agent.py",
        "agent_instructions.py", 
        "server.py",
        "two_stage_parser.py",
        "generator.py",
        "zone_grid.py"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = current_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_python_syntax():
    """Test Python syntax of key files."""
    print("\n🐍 Checking Python syntax...")
    
    files_to_check = [
        "hockey_diagram_agent.py",
        "agent_instructions.py"
    ]
    
    syntax_errors = []
    for file in files_to_check:
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            # Try to compile the code
            compile(content, file, 'exec')
            print(f"✅ {file} - syntax OK")
        except SyntaxError as e:
            print(f"❌ {file} - syntax error: {e}")
            syntax_errors.append((file, str(e)))
        except FileNotFoundError:
            print(f"❌ {file} - file not found")
            syntax_errors.append((file, "file not found"))
    
    return len(syntax_errors) == 0

def test_import_availability():
    """Test what can be imported."""
    print("\n📦 Checking imports...")
    
    # Test basic imports
    tests = [
        ("asyncio", "asyncio"),
        ("logging", "logging"),
        ("pathlib", "pathlib.Path"),
        ("typing", "typing.Dict"),
    ]
    
    import_success = []
    for name, import_path in tests:
        try:
            __import__(import_path.split('.')[0])
            print(f"✅ {name}")
            import_success.append(name)
        except ImportError:
            print(f"❌ {name} - not available")
    
    # Test optional advanced imports
    advanced_tests = [
        ("OpenAI Agents SDK", "agents"),
        ("OpenAI SDK", "openai"),
        ("FastMCP", "mcp.server.fastmcp"),
        ("Pydantic", "pydantic")
    ]
    
    print("\n🔬 Checking advanced dependencies:")
    for name, module in advanced_tests:
        try:
            __import__(module.split('.')[0])
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️ {name} - not available (may need virtual environment)")
    
    return len(import_success) >= 3

def test_agent_instructions():
    """Test agent instructions can be loaded."""
    print("\n📋 Testing agent instructions...")
    
    try:
        with open("agent_instructions.py", 'r') as f:
            content = f.read()
        
        # Check for key components
        checks = [
            ("EXPERT_INSTRUCTIONS", "EXPERT_INSTRUCTIONS" in content),
            ("Tool descriptions", "parse_hockey_formation" in content),
            ("Process flow", "Process Flow" in content),
            ("Example interactions", "Example Interactions" in content)
        ]
        
        all_passed = True
        for check_name, condition in checks:
            if condition:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("❌ agent_instructions.py not found")
        return False

def test_mcp_tools():
    """Test MCP server tools definition."""
    print("\n🛠️ Testing MCP server tools...")
    
    try:
        with open("server.py", 'r') as f:
            content = f.read()
        
        # Check for key tools
        tools = [
            "parse_hockey_formation", 
            "generate_diagram_from_spec",
            "create_hockey_diagram",
            "get_agent_status"
        ]
        
        all_found = True
        for tool in tools:
            if f"async def {tool}" in content:
                print(f"✅ {tool}")
            else:
                print(f"❌ {tool} - not found")
                all_found = False
        
        return all_found
        
    except FileNotFoundError:
        print("❌ server.py not found")
        return False

def main():
    """Run all basic tests."""
    print("🧪 Hockey Diagram Agent - Basic Setup Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("Import Availability", test_import_availability),
        ("Agent Instructions", test_agent_instructions),
        ("MCP Tools", test_mcp_tools)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    success_rate = (passed / total) * 100
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("✅ Basic setup is complete!")
    else:
        print(f"📊 {passed}/{total} tests passed ({success_rate:.1f}%)")
        print("⚠️ Some issues found - check logs above")
    
    print(f"\n💡 Next steps:")
    print("1. Ensure virtual environment is activated: source ../../spacy_env/bin/activate")
    print("2. Install missing dependencies if needed")
    print("3. Test with full agent integration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)