#!/usr/bin/env python3
"""
/sync-issues - Sync GitHub issues with Notion tracking database

This command fetches GitHub issue status and updates the Notion tracking page.
"""

import asyncio
import json
import subprocess
from typing import List, Dict, Optional
from datetime import datetime
import re

# Import MCP client functionality
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from servers.poc.test_mcp_connection import call_mcp_tool

# Configuration
NOTION_DATABASE_ID = "2420cdbf-4977-819c-a24b-f3f50cccf501"  # Update with actual database ID
GITHUB_REPO = "stewmckendry/hockey_coach"
TRACKED_ISSUES = list(range(88, 96))  # Issues 88-95


class SyncIssuesCommand:
    """Slash command to sync GitHub issues with Notion."""
    
    def __init__(self):
        self.stats = {
            'synced': 0,
            'created': 0,
            'updated': 0,
            'failed': 0
        }
    
    async def execute(self, args: str = "") -> str:
        """
        Execute the sync command.
        
        Args:
            args: Optional arguments like "88" or "88-95"
        
        Returns:
            Status message
        """
        print("🔄 Starting GitHub-Notion sync...")
        
        # Parse issue numbers
        issue_numbers = self._parse_issue_numbers(args)
        
        # First, fetch existing Notion pages
        existing_pages = await self._fetch_existing_notion_pages()
        
        # Sync each issue
        results = []
        for issue_num in issue_numbers:
            result = await self._sync_single_issue(issue_num, existing_pages)
            results.append(result)
            
            if result['success']:
                self.stats['synced'] += 1
                if result['action'] == 'created':
                    self.stats['created'] += 1
                else:
                    self.stats['updated'] += 1
            else:
                self.stats['failed'] += 1
        
        return self._generate_summary(results)
    
    def _parse_issue_numbers(self, args: str) -> List[int]:
        """Parse issue numbers from command arguments."""
        if not args:
            return TRACKED_ISSUES
        
        args = args.strip()
        if args.isdigit():
            return [int(args)]
        elif '-' in args:
            start, end = map(int, args.split('-'))
            return list(range(start, end + 1))
        else:
            return TRACKED_ISSUES
    
    async def _fetch_existing_notion_pages(self) -> Dict[int, str]:
        """Fetch existing Notion pages to avoid duplicates."""
        # In production, would query Notion database
        # For now, return empty dict
        return {}
    
    async def _sync_single_issue(self, issue_num: int, existing_pages: Dict[int, str]) -> Dict:
        """Sync a single GitHub issue to Notion."""
        try:
            # Fetch GitHub issue data
            issue_data = await self._fetch_github_issue(issue_num)
            if not issue_data:
                return {
                    'issue': issue_num,
                    'success': False,
                    'error': 'Failed to fetch from GitHub'
                }
            
            # Prepare Notion properties
            properties = self._prepare_notion_properties(issue_data)
            
            # Check if page exists
            if issue_num in existing_pages:
                # Update existing page
                page_id = existing_pages[issue_num]
                success = await self._update_notion_page(page_id, properties)
                action = 'updated'
            else:
                # Create new page
                success = await self._create_notion_page(properties, issue_data)
                action = 'created'
            
            return {
                'issue': issue_num,
                'success': success,
                'action': action,
                'title': issue_data['title'],
                'status': properties['Status']['select']['name']
            }
            
        except Exception as e:
            return {
                'issue': issue_num,
                'success': False,
                'error': str(e)
            }
    
    async def _fetch_github_issue(self, issue_num: int) -> Optional[Dict]:
        """Fetch issue data from GitHub."""
        try:
            cmd = f"gh issue view {issue_num} --repo {GITHUB_REPO} --json number,title,state,assignees,body,comments,labels,url,createdAt,updatedAt"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to fetch issue {issue_num}: {result.stderr}")
                return None
            
            data = json.loads(result.stdout)
            
            # Process the data
            return {
                'number': data['number'],
                'title': data['title'],
                'state': data['state'],
                'url': data['url'],
                'assignees': [a['login'] for a in data.get('assignees', [])],
                'comments_count': len(data.get('comments', [])),
                'labels': [l['name'] for l in data.get('labels', [])],
                'created_at': data.get('createdAt', ''),
                'updated_at': data.get('updatedAt', ''),
                'body': data.get('body', ''),
                'latest_comment': self._get_latest_comment(data.get('comments', []))
            }
            
        except Exception as e:
            print(f"❌ Error fetching issue {issue_num}: {e}")
            return None
    
    def _get_latest_comment(self, comments: List[Dict]) -> str:
        """Extract latest meaningful comment."""
        if not comments:
            return ""
        
        # Filter bot comments and get latest
        user_comments = [c for c in comments if not c.get('author', {}).get('login', '').endswith('[bot]')]
        
        if user_comments:
            latest = user_comments[-1]
            body = latest.get('body', '')[:150]
            author = latest.get('author', {}).get('login', 'Unknown')
            return f"{author}: {body}"
        
        return ""
    
    def _prepare_notion_properties(self, issue_data: Dict) -> Dict:
        """Prepare properties for Notion page."""
        # Determine status
        status = self._determine_status(issue_data)
        
        # Determine phase
        phase = self._determine_phase(issue_data['number'])
        
        # Extract progress
        progress = self._extract_progress(issue_data['body'])
        
        # Determine priority
        priority = self._determine_priority(issue_data['labels'], issue_data['number'])
        
        return {
            "Issue": {"title": [{"text": {"content": f"#{issue_data['number']}: {issue_data['title']}"}}]},
            "GitHub URL": {"url": issue_data['url']},
            "Status": {"select": {"name": status}},
            "Assignee": {"rich_text": [{"text": {"content": ", ".join(issue_data['assignees']) or "Unassigned"}}]},
            "Phase": {"select": {"name": phase}},
            "Last Updated": {"date": {"start": issue_data['updated_at']}},
            "Comments": {"number": issue_data['comments_count']},
            "Progress": {"rich_text": [{"text": {"content": progress}}]},
            "Priority": {"select": {"name": priority}}
        }
    
    def _determine_status(self, issue_data: Dict) -> str:
        """Determine Notion status from GitHub data."""
        if issue_data['state'] == 'CLOSED':
            return 'Completed'
        
        # Check for keywords in latest comment
        latest = issue_data.get('latest_comment', '').lower()
        if any(word in latest for word in ['blocked', 'waiting', 'stuck']):
            return 'Blocked'
        if any(word in latest for word in ['review', 'feedback']):
            return 'Review'
        
        # Check body for progress
        body = issue_data.get('body', '').lower()
        if '- [x]' in body or 'in progress' in body:
            return 'In Progress'
        
        return 'Open'
    
    def _determine_phase(self, issue_num: int) -> str:
        """Determine phase based on issue number."""
        if issue_num <= 90:
            return "Phase 1: Foundation"
        elif issue_num <= 93:
            return "Phase 2: Education Content"
        else:
            return "Phase 3: Interactive Features"
    
    def _extract_progress(self, body: str) -> str:
        """Extract progress from issue body."""
        if not body:
            return "Not started"
        
        # Count checklist items
        completed = len(re.findall(r'- \[x\]', body, re.IGNORECASE))
        total = len(re.findall(r'- \[[x ]\]', body, re.IGNORECASE))
        
        if total > 0:
            percentage = (completed / total) * 100
            return f"{completed}/{total} ({percentage:.0f}%)"
        
        return "In planning"
    
    def _determine_priority(self, labels: List[str], issue_num: int) -> str:
        """Determine priority."""
        # Check labels first
        for label in labels:
            if 'high' in label.lower():
                return "High"
            elif 'low' in label.lower():
                return "Low"
        
        # Default by phase
        if issue_num <= 93:
            return "High"
        return "Medium"
    
    async def _create_notion_page(self, properties: Dict, issue_data: Dict) -> bool:
        """Create new Notion page."""
        try:
            # Add content to the page
            content = f"""# Issue #{issue_data['number']}

## Description
{issue_data.get('body', 'No description provided.')}

## Latest Activity
{issue_data.get('latest_comment', 'No comments yet.')}

## Links
- [View on GitHub]({issue_data['url']})
"""
            
            # In production, would use Notion MCP to create page
            # For demo, just print
            print(f"✅ Would create Notion page for issue #{issue_data['number']}")
            print(f"   Properties: {json.dumps(properties, indent=2)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create Notion page: {e}")
            return False
    
    async def _update_notion_page(self, page_id: str, properties: Dict) -> bool:
        """Update existing Notion page."""
        try:
            # In production, would use Notion MCP to update page
            print(f"✅ Would update Notion page {page_id}")
            print(f"   Properties: {json.dumps(properties, indent=2)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update Notion page: {e}")
            return False
    
    def _generate_summary(self, results: List[Dict]) -> str:
        """Generate summary message."""
        summary = "## 📊 GitHub-Notion Sync Summary\n\n"
        
        # Statistics
        summary += f"**Total Issues**: {len(results)}\n"
        summary += f"**Synced**: {self.stats['synced']} ✅\n"
        summary += f"**Created**: {self.stats['created']} 🆕\n"
        summary += f"**Updated**: {self.stats['updated']} 🔄\n"
        summary += f"**Failed**: {self.stats['failed']} ❌\n\n"
        
        # Details
        summary += "### Issue Status\n"
        for result in results:
            if result['success']:
                emoji = "🆕" if result['action'] == 'created' else "🔄"
                summary += f"- {emoji} **Issue #{result['issue']}**: {result['status']} - {result['title'][:50]}...\n"
            else:
                summary += f"- ❌ **Issue #{result['issue']}**: {result.get('error', 'Unknown error')}\n"
        
        summary += f"\n✨ Sync completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return summary


# Slash command entry point
async def slash_sync_issues(args: str = "") -> str:
    """
    /sync-issues - Sync GitHub issues with Notion
    
    Usage:
        /sync-issues              # Sync all tracked issues (88-95)
        /sync-issues 88          # Sync single issue
        /sync-issues 88-90       # Sync range of issues
    """
    command = SyncIssuesCommand()
    return await command.execute(args)


if __name__ == "__main__":
    # Test the command
    import sys
    args = sys.argv[1] if len(sys.argv) > 1 else ""
    result = asyncio.run(slash_sync_issues(args))
    print(result)