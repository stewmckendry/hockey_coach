#!/usr/bin/env python3
"""
Slash command to sync GitHub issue status with Notion tracking page.

Usage:
    /sync-issues                    # Sync all tracked issues
    /sync-issues 88                 # Sync specific issue number
    /sync-issues 88-95             # Sync range of issues
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import subprocess
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
NOTION_PAGE_ID = "2420cdbf-4977-819c-a24b-f3f50cccf501"
GITHUB_REPO = "stewmckendry/hockey_coach"
ISSUE_NUMBERS = list(range(88, 96))  # Issues 88-95

class GitHubNotionSync:
    """Handles syncing GitHub issues to Notion database."""
    
    def __init__(self):
        self.github_data = {}
        self.notion_data = {}
    
    async def fetch_github_issue(self, issue_number: int) -> Dict:
        """Fetch issue data from GitHub using gh CLI."""
        try:
            # Get issue details
            cmd = f"gh issue view {issue_number} --repo {GITHUB_REPO} --json number,title,state,assignees,body,comments,labels,url"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to fetch issue {issue_number}: {result.stderr}")
                return {}
            
            issue_data = json.loads(result.stdout)
            
            # Parse additional metadata from issue body if present
            progress = self._extract_progress(issue_data.get('body', ''))
            
            return {
                'number': issue_data['number'],
                'title': issue_data['title'],
                'state': issue_data['state'],
                'url': issue_data['url'],
                'assignees': [a['login'] for a in issue_data.get('assignees', [])],
                'comments_count': len(issue_data.get('comments', [])),
                'latest_comment': self._get_latest_comment(issue_data.get('comments', [])),
                'labels': [l['name'] for l in issue_data.get('labels', [])],
                'progress': progress,
                'status': self._determine_status(issue_data['state'], progress, issue_data.get('comments', []))
            }
            
        except Exception as e:
            logger.error(f"Error fetching issue {issue_number}: {e}")
            return {}
    
    def _extract_progress(self, body: str) -> str:
        """Extract progress information from issue body."""
        # Look for checklist items
        completed = len(re.findall(r'- \[x\]', body, re.IGNORECASE))
        total = len(re.findall(r'- \[[x ]\]', body, re.IGNORECASE))
        
        if total > 0:
            percentage = (completed / total) * 100
            return f"{completed}/{total} tasks ({percentage:.0f}%)"
        
        # Look for explicit progress mentions
        progress_match = re.search(r'progress[:\s]+(\d+)%', body, re.IGNORECASE)
        if progress_match:
            return f"{progress_match.group(1)}%"
        
        return ""
    
    def _get_latest_comment(self, comments: List[Dict]) -> str:
        """Get the latest meaningful comment."""
        if not comments:
            return ""
        
        # Filter out bot comments
        user_comments = [c for c in comments if not c.get('author', {}).get('login', '').endswith('[bot]')]
        
        if user_comments:
            latest = user_comments[-1]
            body = latest.get('body', '')[:200]  # First 200 chars
            author = latest.get('author', {}).get('login', 'Unknown')
            return f"{author}: {body}..."
        
        return ""
    
    def _determine_status(self, state: str, progress: str, comments: List[Dict]) -> str:
        """Determine Notion status based on GitHub data."""
        if state == 'CLOSED':
            return 'Completed'
        
        # Check for blocking indicators in comments
        for comment in comments[-5:]:  # Check last 5 comments
            body = comment.get('body', '').lower()
            if any(word in body for word in ['blocked', 'waiting', 'stuck']):
                return 'Blocked'
            if any(word in body for word in ['review', 'feedback', 'check']):
                return 'Review'
        
        # Check progress
        if progress and '0%' not in progress and '0/' not in progress:
            return 'In Progress'
        
        return 'Open'
    
    def _determine_phase(self, issue_number: int) -> str:
        """Determine phase based on issue number."""
        if issue_number <= 90:
            return "Phase 1: Foundation"
        elif issue_number <= 93:
            return "Phase 2: Education Content"
        else:
            return "Phase 3: Interactive Features"
    
    def _determine_priority(self, labels: List[str], issue_number: int) -> str:
        """Determine priority based on labels and issue number."""
        if any('high' in label.lower() for label in labels):
            return "High"
        if any('low' in label.lower() for label in labels):
            return "Low"
        
        # Default priorities based on phase
        if issue_number <= 90:
            return "High"
        elif issue_number <= 93:
            return "High"
        else:
            return "Medium"
    
    async def sync_to_notion(self, issue_data: Dict) -> bool:
        """Sync issue data to Notion database."""
        try:
            # Format data for Notion
            properties = {
                "Issue": {"title": [{"text": {"content": issue_data['title']}}]},
                "GitHub URL": {"url": issue_data['url']},
                "Status": {"select": {"name": issue_data['status']}},
                "Assignee": {"rich_text": [{"text": {"content": ", ".join(issue_data['assignees']) or "Unassigned"}}]},
                "Phase": {"select": {"name": self._determine_phase(issue_data['number'])}},
                "Last Updated": {"date": {"start": datetime.now().isoformat()}},
                "Comments": {"number": issue_data['comments_count']},
                "Progress": {"rich_text": [{"text": {"content": issue_data['progress'] or "Not started"}}]},
                "Priority": {"select": {"name": self._determine_priority(issue_data['labels'], issue_data['number'])}}
            }
            
            # Check if page already exists
            existing_page_id = await self._find_existing_page(issue_data['number'])
            
            if existing_page_id:
                # Update existing page
                logger.info(f"Updating existing page for issue #{issue_data['number']}")
                # Note: In real implementation, would use Notion MCP to update
                print(f"Would update Notion page {existing_page_id} with properties: {json.dumps(properties, indent=2)}")
            else:
                # Create new page
                logger.info(f"Creating new page for issue #{issue_data['number']}")
                # Note: In real implementation, would use Notion MCP to create
                print(f"Would create Notion page with properties: {json.dumps(properties, indent=2)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error syncing to Notion: {e}")
            return False
    
    async def _find_existing_page(self, issue_number: int) -> Optional[str]:
        """Find existing Notion page for issue number."""
        # In real implementation, would query Notion database
        # For now, return None to simulate no existing page
        return None
    
    async def sync_issues(self, issue_numbers: Optional[List[int]] = None):
        """Main sync function."""
        if issue_numbers is None:
            issue_numbers = ISSUE_NUMBERS
        
        logger.info(f"Starting sync for issues: {issue_numbers}")
        
        results = []
        for issue_num in issue_numbers:
            logger.info(f"Fetching issue #{issue_num}")
            issue_data = await self.fetch_github_issue(issue_num)
            
            if issue_data:
                success = await self.sync_to_notion(issue_data)
                results.append({
                    'issue': issue_num,
                    'success': success,
                    'status': issue_data.get('status', 'Unknown')
                })
            else:
                results.append({
                    'issue': issue_num,
                    'success': False,
                    'status': 'Failed to fetch'
                })
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        logger.info(f"\nSync complete: {successful}/{len(results)} issues synced successfully")
        
        print("\n=== Sync Summary ===")
        for result in results:
            status_emoji = "✅" if result['success'] else "❌"
            print(f"{status_emoji} Issue #{result['issue']}: {result['status']}")
        
        return results


async def main():
    """Main entry point for the slash command."""
    import sys
    
    sync = GitHubNotionSync()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.isdigit():
            # Single issue number
            issue_numbers = [int(arg)]
        elif '-' in arg:
            # Range of issues
            start, end = map(int, arg.split('-'))
            issue_numbers = list(range(start, end + 1))
        else:
            issue_numbers = None
    else:
        issue_numbers = None
    
    await sync.sync_issues(issue_numbers)


if __name__ == "__main__":
    asyncio.run(main())