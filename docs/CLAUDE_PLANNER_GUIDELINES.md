# Claude.ai Planner Guidelines for Claude Code Workflow

This document provides feedback for Claude.ai to write better task definitions that optimize the Claude Code development workflow for the Hockey Coach AI Assistant project.

## **Context: Our Enhanced Workflow**

We've implemented an enhanced development workflow based on Claude Code best practices:
- **Explore-Plan-Code-Commit** methodology with course correction checkpoints
- **Custom slash commands** for common workflows (`/hockey-setup`, `/mcp-test`, `/web-validate`, etc.)
- **Test-first development** templates and visual validation patterns
- **Subagent opportunities** for parallel development
- **Comprehensive quality gates** and pre-commit validation

## **What Works Well (Keep Doing)**

### ✅ **Clear Task Structure**
Your "Task 1.3: Add Existing MCP Tool to Agent" format worked excellently:
- **Numbered tasks** create clear progression
- **Descriptive titles** with specific scope
- **Technical context** included in task descriptions

### ✅ **Specific Technical Requirements**
- Mentioning exact technologies: "OpenAI Agents SDK", "MCPServerStreamableHttp"
- Including integration points: "connect to existing hockey MCP server"
- Specifying success criteria: "tool logging so we know if agent called mcp tool"

### ✅ **Priority Guidance**
- Clear indication of what's critical vs nice-to-have
- Blocking issues clearly identified: "not being able to use it on the web app will be a blocker"

## **Areas for Improvement**

### 🔄 **Add Workflow Phase Indicators**

**Instead of:**
```
"Add feature X to the system"
```

**Try:**
```
"Task 2.1: Add Feature X (Explore-Plan-Code-Commit)
- EXPLORE: Research existing patterns in codebase
- PLAN: Design integration approach with checkpoints  
- CODE: Implement with test-first methodology
- COMMIT: Validate with /commit-prep before merge"
```

### 🔄 **Include Testing Requirements**

**Instead of:**
```
"Implement new API endpoint"
```

**Try:**
```
"Task 2.2: Implement New API Endpoint
- Write tests first (TDD approach)
- Include integration testing with existing services
- Add error handling scenarios
- Validate with /web-validate for UI integration"
```

### 🔄 **Specify Visual Validation Needs**

**For UI/Frontend tasks:**
```
"Task 2.3: Enhance Chat Interface
- Take before/after screenshots for docs/screenshots/
- Test responsive behavior (desktop + mobile)
- Follow visual mock targets in /templates/
- Validate against hockey-themed design guidelines"
```

### 🔄 **Define Course Correction Points**

**Instead of:**
```
"Build complex feature Y"
```

**Try:**
```
"Task 2.4: Build Complex Feature Y
CHECKPOINT 1: After exploration - 'Does the scope and approach look right?'
CHECKPOINT 2: Mid-implementation - 'Are we on the right track technically?'  
CHECKPOINT 3: Before finalization - 'Does this meet the requirements?'"
```

### 🔄 **Recommend Slash Commands**

**Add command suggestions:**
```
"Task 2.5: Database Integration Enhancement
- Start with /hockey-setup to verify environment
- Use /mcp-test to validate database connections
- Run /commit-prep before submitting changes"
```

### 🔄 **Include Subagent Opportunities**

**For complex tasks:**
```
"Task 2.6: Multi-Component Feature (Consider Subagents)
This task could benefit from parallel development:
- Agent 1: Backend API development
- Agent 2: Frontend UI components  
- Agent 3: Integration testing
- Agent 4: Documentation updates"
```

## **Optimal Task Definition Template**

```markdown
# Task X.Y: [Clear Descriptive Title] ([Workflow Type])

## Context
Brief description of what needs to be done and why.

## Technical Requirements  
- Specific technologies/frameworks to use
- Integration points with existing system
- Performance/quality requirements

## Success Criteria
- [ ] Functional requirement 1
- [ ] Functional requirement 2  
- [ ] Quality requirement (performance, security, etc.)
- [ ] Documentation updated

## Workflow Approach
**Type**: [Explore-Plan-Code-Commit | Test-First | Visual-Validation | Subagent-Parallel]

**Course Correction Checkpoints**:
1. After exploration: "Does the scope look right?"
2. Mid-implementation: "Technical approach on track?"
3. Before completion: "Meets all requirements?"

## Testing Strategy
- [ ] Unit tests for core functionality
- [ ] Integration tests for system connections
- [ ] Visual validation (if UI component)
- [ ] Manual testing scenarios

## Recommended Commands
- Pre-work: `/hockey-setup` or `/mcp-test`
- During development: Use TodoWrite for progress tracking
- Pre-commit: `/commit-prep`
- Validation: `/web-validate` or `/trace-check`

## Priority & Dependencies
**Priority**: [High | Medium | Low]
**Blocking**: [What this blocks or what blocks this]
**Dependencies**: [Required services, previous tasks, etc.]

## Subagent Opportunity
[If applicable: This task could benefit from parallel development with X agents working on Y components]
```

## **Communication Improvements**

### 🔄 **Be Explicit About Methodology**
```
"Use test-first development approach for this feature"
"This requires visual validation with screenshots"  
"Consider using subagents for parallel backend/frontend work"
```

### 🔄 **Reference Existing Patterns**
```
"Follow the same pattern as the existing tracing integration"
"Use the hockey-themed design guidelines in /templates/"
"Mirror the approach used in Task 1.3 for MCP integration"
```

### 🔄 **Include Context About Tools**
```
"This will integrate with the existing ChromaDB collections"
"Should work with the current MCP server on port 8000"
"Needs to maintain compatibility with OpenAI tracing"
```

## **Meta-Communication Tips**

### 📋 **Task Sequence Planning**
When giving multiple tasks, consider:
```
"These tasks build on each other:
- Task 2.1: Foundation (required first)
- Task 2.2: Core functionality (depends on 2.1)
- Task 2.3: UI enhancement (can parallel with 2.2)
- Task 2.4: Integration testing (requires 2.1-2.3)"
```

### 📋 **Complexity Indicators**
```
"Simple task (1-2 hours): Single component modification"
"Medium task (half day): Multi-component integration"  
"Complex task (1-2 days): New feature with testing and docs"
"Epic task (multiple days): Consider breaking into subtasks"
```

## **Project-Specific Context**

### 🏒 **Hockey Coach AI Assistant Architecture**
When creating tasks, reference these key components:
- **MCP Server** (`servers/hockey_mcp.py`) - 4 hockey coaching tools on port 8000
- **Agent HTTP Server** (`servers/poc/agent_http_server.py`) - Bridge on port 8002
- **Next.js Web App** (`web_app/`) - Frontend with server-side AI integration on port 3000
- **ChromaDB** - 8 hockey knowledge collections (drills, tactics, LTAD, etc.)
- **OpenAI Tracing** - Automatic trace recording with dashboard URLs

### 🏒 **Available Custom Slash Commands**
Reference these in task definitions when appropriate:
- `/hockey-setup` - Complete development environment setup
- `/mcp-test` - MCP server and tool testing
- `/web-validate` - Full web integration testing with screenshots
- `/trace-check` - OpenAI tracing functionality verification
- `/commit-prep` - Pre-commit quality assurance checklist

### 🏒 **Domain-Specific Considerations**
- Age group specificity (U8-U18) in hockey content
- Position-specific skills (forwards, defense, goalies)
- Skill progression pathways (LTAD - Long Term Athlete Development)
- Practice planning considerations (ice time, equipment, safety)

## **Examples of Well-Defined Tasks**

### **Example 1: Simple Enhancement**
```
Task 2.1: Add Age Group Filter to Drill Search (Explore-Plan-Code-Commit)

Context: Users need to filter hockey drills by specific age groups for more targeted coaching advice.

Technical Requirements:
- Extend search_hockey_knowledge MCP tool with age_group parameter
- Update web UI with age group dropdown
- Maintain backwards compatibility with existing searches

Success Criteria:
- [ ] MCP tool accepts age_group filter parameter
- [ ] Web UI shows age group selection
- [ ] Search results filtered appropriately
- [ ] Existing functionality unchanged

Workflow: Explore-Plan-Code-Commit with visual validation

Testing Strategy:
- Unit tests for MCP tool parameter handling
- UI tests for dropdown functionality
- Integration tests for filtered search results

Recommended Commands: /mcp-test, /web-validate, /commit-prep
```

### **Example 2: Complex Feature**
```
Task 2.2: Real-time Practice Timer with Live Coaching Suggestions (Subagent-Parallel)

Context: Coaches need a live practice timer that provides real-time coaching suggestions based on current drill progress.

Technical Requirements:
- WebSocket integration for real-time updates
- Practice plan state management
- Mobile-responsive timer interface
- Integration with existing MCP coaching tools

Subagent Opportunity:
- Agent 1: WebSocket backend and state management
- Agent 2: React timer UI components with mobile optimization
- Agent 3: MCP tool integration for live suggestions
- Agent 4: Testing and visual validation

Course Correction Checkpoints:
1. After exploration: "WebSocket architecture and state design approved?"
2. Mid-implementation: "Real-time updates working across components?"
3. Before completion: "Mobile experience and performance acceptable?"

Recommended Commands: /hockey-setup, /web-validate (extensive), /commit-prep
```

## **Key Success Factors**

The most important insight: **Claude Code performs best with clear targets and explicit methodology guidance**. 

Your task definitions should include not just *what* to build, but *how* to approach building it using our enhanced workflow patterns.

### **Critical Elements for Every Task:**
1. **Clear scope and boundaries**
2. **Explicit methodology recommendation**
3. **Course correction checkpoints for complex tasks**
4. **Testing and validation requirements**
5. **Reference to existing patterns and tools**
6. **Priority and dependency information**

This approach transforms our collaboration from "task execution" to "strategic development partnership" with better planning, testing, and validation cycles that leverage Claude Code's full capabilities.

---

*This document should be shared with Claude.ai to improve task planning and definition quality for optimal Claude Code workflow integration.*