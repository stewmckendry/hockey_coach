#!/usr/bin/env python3
"""
Test Session Demo File
Created during test session to demonstrate basic functionality and file reading capabilities.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

def test_project_structure():
    """Test that key project directories and files exist."""
    print("🧪 Testing project structure...")
    
    required_paths = [
        "servers/hockey_mcp.py",
        "models",
        "chroma_load",
        "utils/chroma_utils.py",
        "start_services.py",
        "CLAUDE.md",
        "README.md"
    ]
    
    results = {}
    for path in required_paths:
        full_path = PROJECT_ROOT / path
        exists = full_path.exists()
        results[path] = exists
        status = "✅" if exists else "❌"
        print(f"   {status} {path}")
    
    return results

def test_hockey_knowledge_collections():
    """Test hockey knowledge collection directories exist."""
    print("\n🏒 Testing hockey knowledge collections...")
    
    collections = [
        "chroma_load/processed/drills",
        "chroma_load/processed/ltad", 
        "chroma_load/processed/tactics",
        "chroma_load/processed/rules",
        "chroma_load/processed/nhl_interviews"
    ]
    
    results = {}
    for collection in collections:
        full_path = PROJECT_ROOT / collection
        exists = full_path.exists()
        results[collection] = exists
        status = "✅" if exists else "❌"
        print(f"   {status} {collection}")
    
    return results

def test_web_app_structure():
    """Test web application structure."""
    print("\n🌐 Testing web app structure...")
    
    web_paths = [
        "web_app/package.json",
        "web_app/app",
        "web_app/components",
        "web_app/lib",
        "web_app/hooks"
    ]
    
    results = {}
    for path in web_paths:
        full_path = PROJECT_ROOT / path
        exists = full_path.exists()
        results[path] = exists
        status = "✅" if exists else "❌"
        print(f"   {status} {path}")
    
    return results

def test_model_imports():
    """Test that model imports work correctly."""
    print("\n🔧 Testing model imports...")
    
    try:
        # Test basic imports without requiring database connections
        from models import ltad, conduct, dryland_models
        print("   ✅ Model imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ Model import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error importing models: {e}")
        return False

def test_utilities():
    """Test utility functions are accessible."""
    print("\n🛠 Testing utilities...")
    
    try:
        from utils import chroma_utils, datetime_tools
        print("   ✅ Utility imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ Utility import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error importing utilities: {e}")
        return False

def run_all_tests():
    """Run all test functions and provide summary."""
    print("🚀 Hockey Coach Playbook - Test Session Demo")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    test_results['structure'] = test_project_structure()
    test_results['collections'] = test_hockey_knowledge_collections() 
    test_results['web_app'] = test_web_app_structure()
    test_results['models'] = test_model_imports()
    test_results['utilities'] = test_utilities()
    
    # Summary
    print("\n📊 Test Summary")
    print("-" * 30)
    
    structure_passed = all(test_results['structure'].values())
    collections_passed = all(test_results['collections'].values())
    web_passed = all(test_results['web_app'].values())
    models_passed = test_results['models']
    utils_passed = test_results['utilities']
    
    print(f"Project Structure: {'✅ PASS' if structure_passed else '❌ FAIL'}")
    print(f"Hockey Collections: {'✅ PASS' if collections_passed else '❌ FAIL'}")
    print(f"Web App Structure: {'✅ PASS' if web_passed else '❌ FAIL'}")
    print(f"Model Imports: {'✅ PASS' if models_passed else '❌ FAIL'}")
    print(f"Utility Imports: {'✅ PASS' if utils_passed else '❌ FAIL'}")
    
    overall_pass = all([structure_passed, collections_passed, web_passed, models_passed, utils_passed])
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_pass else '❌ SOME TESTS FAILED'}")
    
    return test_results

if __name__ == "__main__":
    results = run_all_tests()
    
    # Exit with appropriate code
    if all(isinstance(v, dict) and all(v.values()) for v in results.values() if isinstance(v, dict)) and \
       all(v for v in results.values() if isinstance(v, bool)):
        sys.exit(0)
    else:
        sys.exit(1)