#!/usr/bin/env python3
"""
Performance test for telemetry system to ensure <50ms latency impact.
"""

import sys
import os
import time
import statistics
import subprocess
from pathlib import Path

def test_hook_performance():
    """Test hook execution performance."""
    print("=== Telemetry Performance Test ===")
    
    hook_script = Path(__file__).parent / "telemetry_hook.py"
    project_root = Path(__file__).parent.parent
    
    # Test configuration
    test_env = os.environ.copy()
    test_env.update({
        'TELEMETRY_ENABLED': 'true',
        'TELEMETRY_DEBUG': 'false',  # Disable debug for realistic performance
        'CLAUDE_PROJECT_DIR': str(project_root),
        'CLAUDE_SESSION_ID': 'perf-test-session',
        'CLAUDE_TOOL_NAME': 'Read'
    })
    
    # Test different event types
    event_types = ["SessionStart", "UserPromptSubmit", "Stop"]
    results = {}
    
    for event_type in event_types:
        print(f"\nTesting {event_type} event...")
        times = []
        
        # Run multiple iterations for statistical accuracy
        for i in range(20):
            start_time = time.time()
            
            try:
                result = subprocess.run([
                    sys.executable, str(hook_script), event_type
                ], env=test_env, capture_output=True, text=True, timeout=5)
                
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                times.append(duration_ms)
                
                if result.returncode != 0:
                    print(f"  Warning: Hook failed on iteration {i+1}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"  Warning: Hook timed out on iteration {i+1}")
                times.append(5000)  # 5 second timeout as penalty
        
        # Calculate statistics
        if times:
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)
            p95_time = sorted(times)[int(0.95 * len(times))]
            max_time = max(times)
            
            results[event_type] = {
                'avg': avg_time,
                'median': median_time,
                'p95': p95_time,
                'max': max_time,
                'samples': len(times)
            }
            
            print(f"  Average: {avg_time:.1f}ms")
            print(f"  Median:  {median_time:.1f}ms") 
            print(f"  P95:     {p95_time:.1f}ms")
            print(f"  Max:     {max_time:.1f}ms")
            
            # Check performance requirements
            if avg_time > 50:
                print(f"  ❌ FAIL: Average time {avg_time:.1f}ms exceeds 50ms target")
            else:
                print(f"  ✅ PASS: Average time {avg_time:.1f}ms within 50ms target")
                
            if p95_time > 100:
                print(f"  ⚠️  WARN: P95 time {p95_time:.1f}ms exceeds 100ms")
    
    # Overall results
    print(f"\n=== Performance Summary ===")
    overall_times = []
    for event_type, stats in results.items():
        overall_times.extend([stats['avg']])
        
    if overall_times:
        overall_avg = statistics.mean(overall_times)
        print(f"Overall average latency: {overall_avg:.1f}ms")
        
        if overall_avg <= 50:
            print("✅ PERFORMANCE TARGET MET: Average latency ≤ 50ms")
            return True
        else:
            print("❌ PERFORMANCE TARGET MISSED: Average latency > 50ms")
            return False
    
    return False

def test_concurrent_hooks():
    """Test performance under concurrent hook execution."""
    print(f"\n=== Concurrent Performance Test ===")
    
    hook_script = Path(__file__).parent / "telemetry_hook.py"
    project_root = Path(__file__).parent.parent
    
    test_env = os.environ.copy()
    test_env.update({
        'TELEMETRY_ENABLED': 'true',
        'TELEMETRY_DEBUG': 'false',
        'CLAUDE_PROJECT_DIR': str(project_root),
        'CLAUDE_SESSION_ID': 'concurrent-test-session'
    })
    
    import concurrent.futures
    
    def run_hook(event_type):
        """Run a single hook and return execution time."""
        start_time = time.time()
        try:
            result = subprocess.run([
                sys.executable, str(hook_script), event_type
            ], env=test_env, capture_output=True, text=True, timeout=10)
            end_time = time.time()
            return (end_time - start_time) * 1000, result.returncode == 0
        except Exception:
            return 10000, False  # 10s penalty for failures
    
    # Test concurrent execution
    tasks = ["SessionStart", "UserPromptSubmit", "Stop"] * 5  # 15 concurrent hooks
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_hook, event_type) for event_type in tasks]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = (time.time() - start_time) * 1000
    
    times = [r[0] for r in results]
    successes = [r[1] for r in results]
    
    print(f"Concurrent execution of {len(tasks)} hooks:")
    print(f"  Total time: {total_time:.1f}ms")
    print(f"  Average per hook: {statistics.mean(times):.1f}ms")
    print(f"  Success rate: {sum(successes)}/{len(successes)} ({100*sum(successes)/len(successes):.1f}%)")
    
    return sum(successes) >= len(successes) * 0.8  # 80% success rate

if __name__ == "__main__":
    print("Starting telemetry performance tests...\n")
    
    perf_success = test_hook_performance()
    concurrent_success = test_concurrent_hooks()
    
    print(f"\n=== Final Results ===")
    print(f"Performance test: {'PASS' if perf_success else 'FAIL'}")
    print(f"Concurrent test:  {'PASS' if concurrent_success else 'FAIL'}")
    
    if perf_success and concurrent_success:
        print("🎉 All performance tests passed!")
        sys.exit(0)
    else:
        print("❌ Some performance tests failed")
        sys.exit(1)