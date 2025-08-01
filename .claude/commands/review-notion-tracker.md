---
description: "Review Notion development tracking page and sub-pages for current project status and context"
argument-hint: "[focus-area]"
allowed-tools: ["mcp__notion-remote__fetch", "mcp__notion-remote__search", "TodoWrite", "Read", "Write"]
---

# Review Notion Development Tracker

Review the Notion development tracking page and all sub-pages to understand current project status, completed work, and implementation context before starting new development work.

## 📋 WORKFLOW STEPS

### Phase 1: Main Tracking Page Analysis
**📊 Fetch and analyze the primary development tracking page:**

1. **Fetch Main Tracking Page**:
   ```
   mcp__notion-remote__fetch: id = "2420cdbf-4977-819c-a24b-f3f50cccf501"
   ```
   - **Page**: U10 Hockey Team Notion Site Development Plan
   - **URL**: https://www.notion.so/2420cdbf4977819ca24bf3f50cccf501

2. **Extract Key Information**:
   - Current implementation phases and progress
   - Embedded databases and their purposes
   - Site architecture overview
   - Content creation workflow status
   - Available tools and integrations
   - U10 content standards and guidelines

3. **Identify Sub-Pages and Databases**: From the main page, note:
   - Issue Tracking Database (inline database)
   - Content Pages Database (inline database)
   - Any linked project pages
   - Resource links to GitHub issues and documentation

### Phase 2: Database Analysis
**🗄️ Review tracking databases for current status:**

1. **Issue Tracking Database**:
   ```
   mcp__notion-remote__fetch: id = "51302ace3fe44297b7524c6b9c5e08cf"
   ```
   - **Purpose**: Track GitHub issues #88-95 progress
   - **Extract**: Current issue statuses, priorities, progress indicators
   - **Note**: Completed work, blocked items, dependencies

2. **Content Pages Database** (if specified in main page):
   ```
   mcp__notion-remote__fetch: id = "[content-database-id-from-main-page]"
   ```
   - **Purpose**: Track content creation and publishing status
   - **Extract**: Published content, draft status, content gaps

### Phase 3: Related Project Pages
**📄 Review key project implementation pages:**

1. **Search for Related Pages**:
   ```
   mcp__notion-remote__search: query = "Ted Reeves Thunder U10 hockey team workspace"
   ```

2. **Team Hub Page** (if found from Issue #88 comments):
   ```
   mcp__notion-remote__fetch: id = "2420cdbf-4977-8191-8758-fe9b9ccf418b"
   ```
   - **Purpose**: Main team site created in Issue #88
   - **Extract**: Current team structure, navigation, available features

3. **Hockey Education Center** (if found):
   ```
   mcp__notion-remote__fetch: id = "2420cdbf-4977-810b-8308-dd93f9d037ed"
   ```
   - **Purpose**: Educational content structure
   - **Extract**: Content organization, existing materials

### Phase 4: Context Analysis and Summary
**🧠 Synthesize information for development context:**

1. **Project Status Assessment**:
   - **Completed Work**: What foundations are already in place
   - **Current Phase**: Which implementation phase is active
   - **Available Resources**: Databases, pages, and integrations ready for use
   - **Established Patterns**: Content structures and workflows to follow

2. **Implementation Context**:
   - **Team Information**: Current team setup (Ted Reeves Thunder U10)
   - **Content Standards**: U10-specific guidelines (70% visual, Grade 3-4 reading)
   - **Technical Stack**: Available MCP integrations and tools
   - **Workflow Patterns**: Established content creation processes

3. **Development Readiness**:
   - **Infrastructure**: What's ready for immediate use
   - **Dependencies**: What needs to be completed first
   - **Opportunities**: Where new work can build on existing foundations
   - **Gaps**: What still needs to be implemented

### Phase 5: Focused Review (Optional)
**🎯 Deep dive into specific areas based on focus argument:**

If `$ARGUMENTS` specifies focus area:

- **"content"**: Deep dive into content databases and published materials
- **"infrastructure"**: Focus on technical setup and integrations  
- **"team"**: Analyze team-specific pages and configurations
- **"workflow"**: Review content creation and publishing processes

**Additional Searches Based on Focus**:
```
mcp__notion-remote__search: query = "[focus-area] U10 hockey team development"
```

## 📊 OUTPUT FORMAT

Generate a comprehensive development context summary:

```markdown
# Notion Development Tracker Review

**Reviewed**: [timestamp]
**Focus**: [focus-area or "General"]

## 🏗️ Project Infrastructure Status

### Completed Foundations
- [List established infrastructure from tracking page]
- [Note completed issues and their deliverables]
- [Highlight available databases and integrations]

### Current Phase: [Phase from tracking page]
- **Active Issues**: [List in-progress items]
- **Next Priorities**: [List pending high-priority items]
- **Blockers**: [Note any blocked items]

## 🎯 Team Context: Ted Reeves Thunder U10

### Team Setup
- [Extract team details from completed work]
- [Note coaching philosophy and approach]
- [List practice schedule and logistics]

### Content Standards
- **Age Group**: U10 (9-10 years)
- **Visual Ratio**: 70% images/video, 30% text
- **Reading Level**: Grade 3-4
- **Attention Span**: 10-15 minute modules

## 🛠️ Available Development Resources

### Established Infrastructure
- [List databases ready for use]
- [Note content templates and structures]
- [Highlight integration points]

### MCP Tool Integrations
- [List configured MCP servers from tracking page]
- [Note specific tools available]

## 🔄 Established Workflows

### Content Creation Process
1. [Extract workflow from tracking page]
2. [Note quality standards and review process]

### Implementation Patterns
- [Note established code patterns from completed issues]
- [Highlight reusable components]

## 💡 Development Recommendations

### Immediate Opportunities
- [Based on completed work, suggest next logical steps]
- [Identify where new work can build on existing foundations]

### Implementation Approach
- [Recommend specific patterns to follow]
- [Suggest integration points to use]
- [Note team context to consider]

### Resource Utilization
- [Recommend which databases to update]
- [Suggest which templates to follow]
- [Note which tools to integrate]

---

*Review based on Notion development tracker analysis*
```

## 🚨 ERROR HANDLING

Handle these scenarios gracefully:
- **Page Not Found**: Check if page ID has changed, search by title
- **Access Denied**: Note permission issues and suggest verification
- **Database Empty**: Report if tracking databases have no content
- **Missing Sub-Pages**: Continue with available information

## 📈 USAGE EXAMPLES

```bash
# General review of all tracker content
/review-notion-tracker

# Focus on content-related tracking
/review-notion-tracker content

# Focus on technical infrastructure
/review-notion-tracker infrastructure

# Focus on team-specific setup
/review-notion-tracker team
```

## 🎯 SUCCESS CRITERIA

The review is complete when:
1. ✅ Main tracking page analyzed for current status
2. ✅ All embedded databases reviewed for progress
3. ✅ Key sub-pages fetched and analyzed
4. ✅ Development context summary generated
5. ✅ Implementation recommendations provided
6. ✅ Team and content standards documented

## 🔄 INTEGRATION WITH OTHER COMMANDS

This command provides context for:
- **`/implement-feature`**: Understanding current project state before implementation
- **`/review-open-issues`**: Knowing what infrastructure is available for recommendations
- **Content Creation Commands**: Understanding established team context and standards

---

**Begin Notion tracker review with focus**: `$ARGUMENTS`

**Main Tracking Page ID**: `2420cdbf-4977-819c-a24b-f3f50cccf501`