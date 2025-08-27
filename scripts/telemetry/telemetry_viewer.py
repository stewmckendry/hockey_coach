#!/usr/bin/env python3
"""
Telemetry viewer utility for Claude Code session-based logs.

This script provides functionality to view, search, and analyze telemetry data
organized by Claude Code sessions.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse
from collections import defaultdict


def list_sessions(sessions_dir: Path, limit: int = 20) -> List[Dict]:
    """List available sessions with basic info."""
    sessions = []
    
    for session_file in sorted(sessions_dir.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
        session_id = session_file.stem
        
        # Read first and last events
        with open(session_file, 'r') as f:
            lines = f.readlines()
            if lines:
                first_event = json.loads(lines[0])
                last_event = json.loads(lines[-1])
                
                sessions.append({
                    'session_id': session_id,
                    'start_time': first_event.get('timestamp', 'Unknown'),
                    'end_time': last_event.get('timestamp', 'Unknown'),
                    'event_count': len(lines),
                    'file_size': session_file.stat().st_size,
                    'project_dir': first_event.get('project_dir', 'Unknown')
                })
    
    return sessions


def view_session(session_file: Path, event_filter: Optional[str] = None) -> None:
    """View all events in a session, optionally filtered by event type."""
    print(f"\n=== Session: {session_file.stem} ===\n")
    
    with open(session_file, 'r') as f:
        for line in f:
            event = json.loads(line)
            
            if event_filter and event.get('event_type') != event_filter:
                continue
            
            # Format timestamp
            timestamp = event.get('timestamp', 'Unknown')
            if timestamp != 'Unknown':
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            # Display event
            print(f"[{timestamp}] {event.get('event_type', 'Unknown')}")
            
            # Show key fields based on event type
            event_type = event.get('event_type', '')
            
            if event_type == 'PreToolUse' or event_type == 'PostToolUse':
                tool_name = event.get('tool_name', 'Unknown')
                print(f"  Tool: {tool_name}")
                if event.get('execution_duration_ms'):
                    print(f"  Duration: {event['execution_duration_ms']}ms")
                
            elif event_type == 'UserPromptSubmit':
                prompt_length = event.get('prompt_length', 0)
                print(f"  Prompt Length: {prompt_length} chars")
                
            elif event_type == 'Notification':
                message = event.get('message', '')[:100]
                print(f"  Message: {message}...")
                
            print()


def analyze_session(session_file: Path) -> Dict:
    """Analyze a session and provide statistics."""
    stats = {
        'event_counts': defaultdict(int),
        'tool_usage': defaultdict(int),
        'total_duration_ms': 0,
        'errors': 0,
        'files_accessed': set()
    }
    
    events = []
    with open(session_file, 'r') as f:
        for line in f:
            event = json.loads(line)
            events.append(event)
            
            # Count event types
            stats['event_counts'][event.get('event_type', 'Unknown')] += 1
            
            # Track tool usage
            if event.get('tool_name'):
                stats['tool_usage'][event['tool_name']] += 1
            
            # Track errors
            if event.get('error_details') or event.get('success') is False:
                stats['errors'] += 1
            
            # Track file access
            if event.get('file_paths'):
                for fp in event['file_paths']:
                    stats['files_accessed'].add(fp)
    
    # Calculate session duration
    if events:
        try:
            start_time = datetime.fromisoformat(events[0]['timestamp'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(events[-1]['timestamp'].replace('Z', '+00:00'))
            stats['total_duration_ms'] = int((end_time - start_time).total_seconds() * 1000)
        except:
            pass
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='View and analyze Claude Code telemetry sessions')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List sessions command
    list_parser = subparsers.add_parser('list', help='List available sessions')
    list_parser.add_argument('-n', '--limit', type=int, default=20, help='Number of sessions to show')
    
    # View session command
    view_parser = subparsers.add_parser('view', help='View events in a session')
    view_parser.add_argument('session_id', help='Session ID to view')
    view_parser.add_argument('-e', '--event', help='Filter by event type')
    
    # Analyze session command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze session statistics')
    analyze_parser.add_argument('session_id', help='Session ID to analyze')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search across all sessions')
    search_parser.add_argument('term', help='Search term')
    search_parser.add_argument('-n', '--limit', type=int, default=10, help='Max results')
    
    args = parser.parse_args()
    
    # Determine telemetry directory
    telemetry_dir = Path(__file__).parent.parent / "logs" / "claude_telemetry"
    sessions_dir = telemetry_dir / "sessions"
    
    if not sessions_dir.exists():
        print(f"Error: Sessions directory not found at {sessions_dir}")
        sys.exit(1)
    
    # Execute command
    if args.command == 'list':
        sessions = list_sessions(sessions_dir, args.limit)
        
        print(f"\nShowing {len(sessions)} most recent sessions:\n")
        print(f"{'Session ID':<40} {'Start Time':<20} {'Events':<8} {'Project'}")
        print("-" * 100)
        
        for session in sessions:
            print(f"{session['session_id']:<40} {session['start_time'][:19]:<20} "
                  f"{session['event_count']:<8} {session['project_dir']}")
    
    elif args.command == 'view':
        session_file = sessions_dir / f"{args.session_id}.jsonl"
        if not session_file.exists():
            print(f"Error: Session {args.session_id} not found")
            sys.exit(1)
        
        view_session(session_file, args.event)
    
    elif args.command == 'analyze':
        session_file = sessions_dir / f"{args.session_id}.jsonl"
        if not session_file.exists():
            print(f"Error: Session {args.session_id} not found")
            sys.exit(1)
        
        stats = analyze_session(session_file)
        
        print(f"\n=== Session Analysis: {args.session_id} ===\n")
        
        print("Event Type Distribution:")
        for event_type, count in sorted(stats['event_counts'].items()):
            print(f"  {event_type:<20}: {count}")
        
        print(f"\nTotal Events: {sum(stats['event_counts'].values())}")
        print(f"Session Duration: {stats['total_duration_ms'] / 1000:.1f}s")
        print(f"Errors: {stats['errors']}")
        
        if stats['tool_usage']:
            print("\nTool Usage:")
            for tool, count in sorted(stats['tool_usage'].items()):
                print(f"  {tool:<20}: {count}")
        
        if stats['files_accessed']:
            print(f"\nFiles Accessed: {len(stats['files_accessed'])}")
    
    elif args.command == 'search':
        print(f"\nSearching for '{args.term}' across all sessions...\n")
        
        matches = 0
        for session_file in sessions_dir.glob("*.jsonl"):
            with open(session_file, 'r') as f:
                for line_no, line in enumerate(f, 1):
                    if args.term.lower() in line.lower():
                        event = json.loads(line)
                        print(f"Session: {session_file.stem}")
                        print(f"  Line {line_no}: {event.get('event_type')} at {event.get('timestamp')}")
                        print(f"  Context: {line.strip()[:200]}...")
                        print()
                        
                        matches += 1
                        if matches >= args.limit:
                            print(f"\nShowing first {args.limit} matches. Use -n to see more.")
                            return
        
        print(f"\nFound {matches} matches.")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()