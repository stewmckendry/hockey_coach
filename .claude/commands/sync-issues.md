---
description: "Sync GitHub issue status with Notion tracking database for U10 Hockey Team project"
argument-hint: "[issue-numbers]"
allowed-tools: ["Bash", "mcp__notion-remote__search", "mcp__notion-remote__fetch", "mcp__notion-remote__create-pages", "mcp__notion-remote__update-page", "mcp__notion-remote__create-database", "WebFetch", "TodoWrite", "Read", "Write"]
---

# Sync GitHub Issues with Notion

Synchronize GitHub issue status, comments, and progress with the Notion tracking database for the U10 Hockey Team site development project.

## 📋 WORKFLOW STEPS

### Phase 1: Parse Arguments and Setup
**🔍 Determine which issues to sync:**

1. **Check Arguments**: Parse `$ARGUMENTS` to determine scope:
   - No arguments: Sync all tracked issues (88-95)
   - Single number (e.g., "88"): Sync that specific issue
   - Range (e.g., "88-90"): Sync issues in that range
   - "all": Sync all tracked issues

2. **Initialize Tracking**: Create TodoWrite list for sync progress

### Phase 2: Locate or Create Notion Database
**📊 Ensure tracking infrastructure exists:**

1. **Find Tracking Page**: Search for "U10 Hockey Team Notion Site Development Plan"
   - Page ID: `2420cdbf-4977-819c-a24b-f3f50cccf501`

2. **Find or Create Database**: Look for "Issue Tracking" database
   - If not found, create with these properties:
     - Issue (title)
     - GitHub URL (url)
     - Status (select: Open, In Progress, Review, Blocked, Completed)
     - Assignee (rich_text)
     - Phase (select: Phase 1, Phase 2, Phase 3)
     - Last Updated (date)
     - Comments (number)
     - Progress (rich_text)
     - Priority (select: High, Medium, Low)

### Phase 3: Fetch GitHub Issue Data
**🔄 Retrieve current issue status:**

For each issue to sync:
1. **GitHub CLI Query**:
   ```bash
   gh issue view [issue-number] --repo stewmckendry/hockey_coach \
     --json number,title,state,assignees,body,comments,labels,url,createdAt,updatedAt
   ```

2. **Extract Key Information**:
   - Issue state (OPEN/CLOSED)
   - Assignees list
   - Comment count and latest comment
   - Progress indicators from body (checklist items)
   - Labels for priority determination

3. **Process Progress**:
   - Count completed checklist items: `- [x]`
   - Calculate percentage if checklist exists
   - Extract explicit progress mentions

### Phase 4: Sync to Notion
**📝 Update or create Notion records:**

1. **Search Existing Pages**: Query database for issue by GitHub URL

2. **Prepare Properties**:
   ```
   Status: Determine from state + comments + progress
   - CLOSED → "Completed"
   - Has blocking keywords → "Blocked"  
   - Has review keywords → "Review"
   - Has progress → "In Progress"
   - Otherwise → "Open"
   
   Phase: Based on issue number
   - 88-90 → "Phase 1: Foundation"
   - 91-93 → "Phase 2: Education Content"
   - 94-95 → "Phase 3: Interactive Features"
   
   Priority: From labels or defaults
   Progress: "X/Y tasks (Z%)" or status message
   ```

3. **Create or Update**:
   - If page exists: Update properties and content
   - If new: Create page with full issue details

### Phase 5: Generate Summary Report
**📊 Create sync status report:**

Format output as:
```markdown
## 📊 GitHub-Notion Sync Summary

**Synced**: [timestamp]
**Issues Processed**: X/Y

### Status Overview
- ✅ Completed: X issues
- 🟡 In Progress: X issues  
- 🔴 Blocked: X issues
- 🔵 Open: X issues

### Detailed Results
[For each issue]
- Issue #XX: [Status] - [Title]
  - Progress: [Progress info]
  - Last Update: [Date]
  - [Any notable changes]

### Actions Taken
- Created X new tracking pages
- Updated Y existing pages
- Found Z issues needing attention

[Link to Notion tracking page]
```

## 🚨 ERROR HANDLING

Handle these scenarios gracefully:
- GitHub API rate limits
- Notion API failures
- Missing or malformed issue data
- Database permission issues

## 📊 SUCCESS CRITERIA

The sync is complete when:
1. ✅ All requested issues have been processed
2. ✅ Notion database reflects current GitHub state
3. ✅ Summary report generated
4. ✅ Any errors logged with clear messages
5. ✅ User informed of next steps

## 🔄 CONTINUOUS IMPROVEMENT

After sync, analyze:
- Issues that are blocked or stalled
- Patterns in progress updates
- Opportunities to improve workflow
- Suggestions for process optimization

---

**Begin sync process with arguments**: `$ARGUMENTS`

Default scope: Issues 88-95 (U10 Hockey Team Notion Site)