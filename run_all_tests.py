#!/usr/bin/env python3
"""
Script to run all tests with the fixes applied.
"""

import subprocess
import os

def run_test(test_file, description):
    """Run a single test file and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print('-'*60)
    
    try:
        result = subprocess.run(
            ["python", test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ FAILED")
            if result.stderr:
                print("Error:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all test scripts."""
    
    # Make sure we're in the correct directory
    os.chdir("/Users/liammckendry/thunder_playbook_worktrees/issue-101")
    
    # Activate virtual environment
    activate_cmd = "source /Users/liammckendry/spacy_env/bin/activate"
    
    tests = [
        ("test_orientation_fix.py", "Left/Right Orientation Fix"),
        ("test_rendering_order.py", "Player Circle Rendering Order"),
        ("test_enhanced_arrows.py", "Enhanced Movement Arrows"),
        ("test_expanded_neutral_zone.py", "Expanded Neutral Zone View"),
        ("test_character_encoding.py", "Character Encoding Fix"),
        ("test_penalty_bench_positions.py", "Penalty Box and Bench Positions"),
        ("test_net_avoidance.py", "Movement Path Net Avoidance"),
        ("test_all_zones.py", "All Zones Validation"),
        ("test_all_formations.py", "All Preset Formations"),
    ]
    
    print("=" * 70)
    print("RUNNING ALL TESTS WITH FIXES")
    print("=" * 70)
    
    successful = 0
    failed = 0
    
    for test_file, description in tests:
        if os.path.exists(test_file):
            if run_test(test_file, description):
                successful += 1
            else:
                failed += 1
        else:
            print(f"\n⚠️  Test file not found: {test_file}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {successful + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! All fixes are working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")

if __name__ == "__main__":
    main()