# TASK ASSIGNMENT - Worker Claude 1.5

**Status**: ASSIGNED
**Task**: Team Assessment Tool Implementation
**Priority**: HIGH
**Dependencies**: None
**Worktree**: ../thunder_playbook_task_1_5
**Branch**: task-1.5-team-assessment-tool

---

## Detailed Task Specification

### Context
Create a new MCP tool for comprehensive team assessment functionality. This tool will analyze team composition, skill levels, and coaching context to provide personalized recommendations for season planning and practice development.

### Technical Requirements
- **MCP Tool Development**: New tool using FastMCP framework patterns
- **Hockey MCP Server Integration**: Add to existing server architecture
- **Data Models**: Team assessment and analysis data structures
- **ChromaDB Integration**: Store and retrieve assessment data efficiently
- **Agent Integration**: Enable intelligent assessment recommendations via MCP

### Success Criteria
- [ ] New MCP tool works correctly within existing server
- [ ] Agent calls tool appropriately for team assessment queries
- [ ] Assessment data is stored and retrieved accurately
- [ ] Tool provides meaningful coaching recommendations
- [ ] Integration testing passes with existing MCP infrastructure
- [ ] CLI and web testing demonstrates functionality

---

## Workflow Approach

### EXPLORE + PLAN PHASE (Autonomous)
**Work autonomously through:**

1. **Research User-Agent Experience**
   - Study `docs/user_journey_map.md` for team assessment needs
   - Define assessment workflow and data collection approach
   - Identify key assessment questions and coaching outputs

2. **Research Technical Design & System Alignment**
   - Review existing MCP tools in `servers/hockey_mcp.py`
   - Study MCP tool patterns and FastMCP framework usage
   - Plan ChromaDB integration and data storage approach

3. **Research OpenAI Agents SDK Integration**
   - Understand how agents will call this MCP tool
   - Study existing tool usage patterns from POC
   - Plan tool parameter design and response format

4. **Synthesize into Implementation Plan**
   - Design tool interface and parameters
   - Plan data models and storage strategy
   - Design development and testing approach

**CHECKPOINT**: Present **Draft + Questions** for iteration

```markdown
## EXPLORE + PLAN COMPLETE - DRAFT + QUESTIONS

### DRAFT: Complete Implementation Plan
[Comprehensive plan covering assessment workflow, technical approach, MCP integration, data design, development sequence]

### QUESTIONS FOR HUMAN FEEDBACK:
1. [Key assumption about assessment process]
2. [Key assumption about data storage approach]  
3. [Key assumption about MCP tool interface]
4. [Key assumption about agent integration]
5. [Any scope or priority clarifications needed]

### READY FOR: Human feedback → Iteration → Approval to build
```

---

### BUILD PHASE (Autonomous with Exception Handling)
**Work autonomously through implementation**

**Pause/Question only when:**
- MCP integration complexity requiring architectural decision
- Data model design needing validation
- ChromaDB integration issues requiring guidance  
- Ready for human testing/validation

**Otherwise, execute the approved plan autonomously**

**CHECKPOINT**: Present **Testing Ready** for validation

```markdown
## BUILD COMPLETE - READY FOR TESTING

### IMPLEMENTED:
- [MCP tool functionality completed]
- [Data models and storage working]
- [Agent integration points tested]

### READY FOR HUMAN TESTING:
- [Specific assessment scenarios to test]
- [How to test the MCP tool directly]
- [Expected assessment outputs to verify]

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
   # Test MCP server with new tool
   curl http://localhost:8000/health
   # Test tool functionality
   python -m pytest tests/ (new tests)
   # Verify agent integration
   python servers/poc/test_mcp_connection.py
   ```

2. **Prepare Integration Submission**
   - Update `coordination/integration_queue.md` with completion details
   - Document new MCP tool interface and usage
   - Note integration points with existing system

3. **Technical Integration Steps**
   ```bash
   git add . && git commit -m "Complete Task 1.5: Team Assessment Tool"
   git fetch origin main && git rebase origin/main
   git push origin task-1.5-team-assessment-tool
   ```

4. **Request Integration**
   - Update integration queue with "READY_FOR_INTEGRATION" status
   - Provide MCP server restart instructions if needed
   - Request code review if needed

**CHECKPOINT**: Integration request submitted

---

### WRAP-UP PHASE (After Integration Complete)
**Complete autonomously after Planning Claude integrates**

---

## Key Research References

### MCP Architecture:
- `servers/hockey_mcp.py` - Existing MCP tools and patterns
- `servers/tools/` - Tool implementation patterns (if any exist)
- `utils/chroma_utils.py` - ChromaDB integration patterns

### System Architecture:
- `docs/technical_design.md` - Overall system design
- `docs/user_journey_map.md` - Assessment requirements
- `docs/POC_DOCUMENTATION.md` - MCP integration patterns

### Agent Integration:
- `servers/poc/poc_agents/web_native_mcp_agent.py` - How agents use MCP tools
- `servers/poc/test_mcp_connection.py` - MCP testing patterns

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

---

## Ready to Begin?

**Working Style**: Be autonomous and efficient. Focus on creating a robust MCP tool that enhances the hockey coaching system. Present checkpoints only when you need human input or approval.

The Planning Claude is monitoring your progress!