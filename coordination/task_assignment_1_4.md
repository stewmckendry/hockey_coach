# TASK ASSIGNMENT - Worker Claude 1.4

**Status**: ASSIGNED
**Task**: Season Planning Specialist Agent Implementation  
**Priority**: HIGH
**Dependencies**: None
**Worktree**: ../thunder_playbook_task_1_4
**Branch**: task-1.4-season-planning-agent

---

## Detailed Task Specification

### Context
Build a specialized OpenAI agent focused exclusively on season planning conversations for hockey coaches. This agent will replace generic coaching interactions with guided, structured season planning workflows that help coaches create comprehensive season plans through conversation.

### Technical Requirements
- **OpenAI Agents SDK Integration**: Use existing patterns from POC (servers/poc/)
- **Specialized Instructions**: Hockey season planning focused conversation flow
- **MCP Tool Integration**: Connect to existing hockey MCP server tools
- **Context Management**: Maintain conversation state across multiple interactions
- **CLI Testing**: Comprehensive testing framework for agent validation

### Success Criteria
- [ ] Agent focuses exclusively on season planning topics (doesn't drift to other coaching areas)
- [ ] Asks appropriate follow-up questions about team context (age, skill level, goals)
- [ ] Maintains conversation context across multiple interactions
- [ ] Successfully integrates with existing MCP hockey knowledge tools
- [ ] CLI testing demonstrates focused, coherent behavior
- [ ] Web integration functional and responsive

---

## Workflow Approach

### EXPLORE + PLAN PHASE (Autonomous)
**Work autonomously through:**

1. **Research User-Agent Experience**
   - Study `docs/user_journey_map.md` Phase 1 (Season Setup)
   - Define conversation flow and agent behavior
   - Identify key questions agent should ask coaches

2. **Research Technical Design & System Alignment**
   - Review `docs/technical_design.md` and system architecture
   - Study existing agent patterns in `servers/poc/poc_agents/`
   - Plan integration with MCP tools and ChromaDB

3. **Research OpenAI Agents SDK Native Usage**
   - Research SDK capabilities and patterns
   - Study POC implementation for native SDK usage
   - Plan SDK integration approach

4. **Synthesize into Implementation Plan**
   - Convert research into concrete technical plan
   - Design code structure and development sequence
   - Plan testing and validation approach

**CHECKPOINT**: Present **Draft + Questions** for iteration

```markdown
## EXPLORE + PLAN COMPLETE - DRAFT + QUESTIONS

### DRAFT: Complete Implementation Plan
[Comprehensive plan covering UX design, technical approach, SDK usage, code structure, development sequence]

### QUESTIONS FOR HUMAN FEEDBACK:
1. [Key assumption about user experience]
2. [Key assumption about technical approach]  
3. [Key assumption about SDK integration]
4. [Key assumption about system integration]
5. [Any scope or priority clarifications needed]

### READY FOR: Human feedback → Iteration → Approval to build
```

---

### BUILD PHASE (Autonomous with Exception Handling)
**Work autonomously through implementation**

**Pause/Question only when:**
- Technical blocker that needs architectural decision
- Unexpected integration issue requiring guidance  
- Test results that need interpretation
- Ready for human testing/validation

**Otherwise, execute the approved plan autonomously**

**CHECKPOINT**: Present **Testing Ready** for validation

```markdown
## BUILD COMPLETE - READY FOR TESTING

### IMPLEMENTED:
- [List of completed components]
- [Integration points working]
- [CLI tests passing]

### READY FOR HUMAN TESTING:
- [Specific testing scenarios to validate]
- [How to test the implementation]
- [Expected behavior to verify]

### QUESTIONS (if any):
- [Any issues encountered during build]
- [Any deviations from plan that needed adjustment]

### READY FOR: Human testing → Green light → Submit work
```

---

### SUBMIT YOUR WORK PHASE (After Human Green Light)

**Work autonomously through submission process:**

1. **Pre-Integration Quality Checks**
   ```bash
   # Run all quality gates
   cd web_app && npm run lint && npm run type-check && npm run build
   python -m pytest tests/ (if applicable)
   curl http://localhost:8000/health  # Verify services still work
   ```

2. **Prepare Integration Submission**
   - Update `coordination/integration_queue.md` with completion details
   - Document files changed, integration notes, testing completed
   - Note any dependencies or special considerations for Planning Claude

3. **Technical Integration Steps**
   ```bash
   # Commit final changes
   git add . && git commit -m "Complete Task 1.4: Season Planning Specialist Agent"
   
   # Check for main branch updates
   git fetch origin main
   git rebase origin/main  # Handle any conflicts if needed
   
   # Push branch for integration
   git push origin task-1.4-season-planning-agent
   ```

4. **Request Integration**
   - Update integration queue with "READY_FOR_INTEGRATION" status
   - Provide merge instructions and any conflict resolution notes
   - Request code review if needed

**CHECKPOINT**: Integration request submitted

```markdown
## WORK SUBMITTED - INTEGRATION REQUESTED

### INTEGRATION READY:
- [ ] All quality checks passed
- [ ] Branch pushed and ready for merge
- [ ] Integration queue updated
- [ ] Documentation complete

### INTEGRATION NOTES:
- [Files changed and their purpose]
- [Any merge considerations or conflicts resolved]
- [Testing completed and results]
- [Dependencies or follow-up tasks]

### TECHNICAL DETAILS:
- Branch: task-1.4-season-planning-agent
- Commit: [latest commit hash]
- Conflicts: [none/resolved/notes]
- Review needed: [yes/no - specify if technical review required]

### READY FOR: Planning Claude integration → Task completion
```

---

### WRAP-UP PHASE (After Integration Complete)
**Complete autonomously after Planning Claude integrates:**
- Archive task scratchpad
- Update shared status dashboard
- Document lessons learned
- Task marked complete

---

## Key Research References

### System Architecture:
- `docs/technical_design.md` - Overall system design
- `docs/user_journey_map.md` - User experience requirements
- `docs/POC_DOCUMENTATION.md` - Existing agent implementation

### Code Patterns:
- `servers/poc/poc_agents/web_native_mcp_agent.py` - MCP integration
- `servers/poc/poc_agents/native_mcp_agent.py` - SDK usage
- `servers/hockey_mcp.py` - Available MCP tools
- `servers/poc/agent_http_server.py` - Web integration

### Testing References:
- `servers/poc/test_agent_cli.py` - CLI testing patterns
- `servers/poc/test_mcp_connection.py` - MCP testing

---

## Communication Protocol

### Autonomous Phases:
- **Regular Progress Updates**: Update scratchpad with current activity
- **No interruptions**: Work through research and implementation autonomously

### Checkpoint Communications:
- **Draft + Questions**: After Explore + Plan phase complete
- **Testing Ready**: After Build phase complete
- **Work Submitted**: After integration preparation complete
- **Exception Questions**: Only when blocked or need guidance during any phase

### Scratchpad Updates:
- Current phase and progress
- Files being worked on
- Any autonomous decisions made
- Checkpoint presentations when ready

---

## Ready to Begin?

**Next Steps**:
1. Navigate to your worktree: `cd ../thunder_playbook_task_1_4`
2. Acknowledge this task in `coordination/task_1_4_scratchpad.md`
3. **Work autonomously** through Explore + Plan phases
4. Present **Draft + Questions** when ready for feedback
5. After approval, **work autonomously** through Build phase
6. Present **Testing Ready** when ready for validation
7. After green light, **submit your work** through integration process
8. **Wrap up** after Planning Claude completes integration

**Working Style**: Be autonomous and efficient. Handle the full development lifecycle including technical integration. Present checkpoints only when you need human input or approval. Move fast with confidence.

The Planning Claude is monitoring your progress and will handle the final integration into main branch!