# Multi-Claude Development Operating Model
## Hockey Coach AI Assistant - Parallel Development Workflow

### 🎯 Overview

This document defines the operating model for coordinated development using multiple Claude Code instances working in parallel via Git worktrees. This approach enables simultaneous development across multiple features while maintaining code quality and project coherence.

---

## 🏗️ Architecture & Roles

### **Role 1: Human Product Owner (You)**
**Responsibilities:**
- Set product direction and priorities
- Review and approve plans before execution
- Provide feedback on completed work
- Make architectural decisions
- Coordinate between Claude instances

**Tools:**
- Main repository directory for oversight
- Access to all worktrees for review
- Direct communication with Planning Claude

---

### **Role 2: Planning Claude (This Instance)**
**Responsibilities:**
- Break down complex features into executable tasks
- Coordinate task distribution across Worker Claudes
- Track overall progress and dependencies
- Conduct course correction checkpoints
- Manage Git worktree lifecycle
- Synthesize reports from Worker Claudes

**Working Directory:** 
- Main repository (`/Users/liammckendry/thunder_playbook/`)
- Access to all worktrees for coordination

**Key Activities:**
- Task decomposition using CLAUDE_PLANNER_GUIDELINES.md
- Progress tracking via TodoWrite
- Checkpoint reviews and plan adjustments
- Git worktree management and cleanup

---

### **Role 3: Worker Claude Instances**
**Responsibilities:**
- Execute specific development tasks in dedicated worktrees
- Follow Explore-Plan-Code-Commit methodology
- Provide detailed progress reports
- Implement features according to task specifications
- Maintain code quality and testing standards

**Working Directory:** 
- Dedicated Git worktree for each task/feature branch
- Isolated development environment

**Key Activities:**
- Feature implementation following technical design
- Test-first development approach
- Visual validation and screenshots
- Code quality assurance (linting, type-checking)

---

## 💬 Claude-to-Claude Communication System

### **Communication Architecture**

Based on Anthropic's best practices, Claude instances communicate through **separate working scratchpads** - dedicated files that each instance reads from and writes to for coordination.

#### **Scratchpad Directory Structure**
```
/Users/liammckendry/thunder_playbook/
├── coordination/
│   ├── planning_scratchpad.md          # Planning Claude writes here
│   ├── task_1_4_scratchpad.md          # Worker Claude 1 writes here
│   ├── task_1_5_scratchpad.md          # Worker Claude 2 writes here
│   ├── task_1_6_scratchpad.md          # Worker Claude 3 writes here
│   ├── shared_status.md                # Cross-instance status updates
│   └── integration_queue.md            # Ready-to-merge notifications
```

### **Automated Communication Protocols**

#### **1. Task Assignment & Status Updates**

**Planning Claude → Worker Claude Communication:**
```markdown
## Task Assignment Protocol

1. Planning Claude writes task specification to:
   `coordination/task_assignment_[worker_id].md`

2. Worker Claude reads assignment and acknowledges:
   `coordination/task_[worker_id]_scratchpad.md`
   
3. Automatic status updates every 2 hours or at phase changes
```

**Implementation Example:**
```markdown
<!-- coordination/task_assignment_1_4.md -->
# TASK ASSIGNMENT - Worker Claude 1.4

**Status**: ASSIGNED
**Task**: Season Planning Specialist Agent Implementation
**Priority**: HIGH
**Deadline**: End of day
**Dependencies**: None
**Worktree**: ../thunder_playbook_task_1_4

## Detailed Specification:
[Full task specification here]

## Acknowledgment Required:
Please update task_1_4_scratchpad.md with "ACKNOWLEDGED" when you begin work.
```

#### **2. Progress Monitoring System**

**Worker Claude Automated Reporting:**
```markdown
## Progress Report Template (Auto-updated by Worker Claudes)

<!-- coordination/task_1_4_scratchpad.md -->
**LAST_UPDATE**: 2025-07-25T14:30:00Z
**STATUS**: IN_PROGRESS_CODING
**COMPLETION**: 45%
**CURRENT_PHASE**: Implementation
**NEXT_MILESTONE**: Complete MCP integration testing
**BLOCKERS**: None
**FILES_MODIFIED**: servers/agents/season_planning_agent.py, tests/test_season_agent.py
**INTEGRATION_READY**: false
**NEEDS_REVIEW**: false
```

#### **3. Cross-Instance Code Review**

**Automated Peer Review Protocol:**
```markdown
## Code Review Assignment System

1. Worker Claude completes feature → Updates integration_queue.md
2. Planning Claude assigns peer review to available Worker Claude
3. Reviewer Claude examines code and provides feedback via scratchpad
4. Original Claude addresses feedback and updates status
```

**Example Review Request:**
```markdown
<!-- coordination/integration_queue.md -->
**REVIEW_REQUEST**: task-1.4-season-planning-agent
**REQUESTING_CLAUDE**: Worker_1_4
**FILES_FOR_REVIEW**: 
- servers/agents/season_planning_agent.py
- web_app/components/season-planning/SeasonPlanningChat.tsx
**REVIEW_TYPE**: Pre-integration technical review
**ASSIGNED_REVIEWER**: Worker_1_5
**STATUS**: PENDING_REVIEW
```

#### **4. Dependency Coordination**

**Automated Dependency Tracking:**
```markdown
## Dependency Management System

<!-- coordination/shared_status.md -->
**DEPENDENCY_MATRIX**:
- Task 1.5 (Team Assessment) → REQUIRES → Task 1.4 (Season Planning) API endpoints
- Task 1.6 (Artifact Generation) → REQUIRES → Task 1.5 data models
- Task 1.7 (Context Management) → REQUIRES → All above tasks

**BLOCKING_STATUS**:
- Task 1.5: BLOCKED_WAITING (Task 1.4 API completion)
- Task 1.6: READY_TO_START
```

### **Communication Automation Scripts**

#### **Auto-Status Update Template**
```bash
#!/bin/bash
# Auto-update script for Worker Claudes (run every 2 hours)

WORKER_ID="1_4"
SCRATCHPAD_FILE="coordination/task_${WORKER_ID}_scratchpad.md"

# Update timestamp and basic status
echo "**LAST_UPDATE**: $(date -u +%Y-%m-%dT%H:%M:%SZ)" > temp_status.md
echo "**STATUS**: ${CURRENT_STATUS}" >> temp_status.md
echo "**COMPLETION**: ${COMPLETION_PERCENT}%" >> temp_status.md

# Append to scratchpad
cat temp_status.md >> $SCRATCHPAD_FILE
```

#### **Integration Readiness Check**
```markdown
## Automated Integration Readiness Protocol

Worker Claude completes this checklist automatically:

**PRE_INTEGRATION_CHECKLIST**:
- [ ] All tests passing (npm run test, python -m pytest)
- [ ] Code quality checks complete (npm run lint, npm run type-check)
- [ ] Visual validation screenshots taken
- [ ] Documentation updated
- [ ] Integration points tested
- [ ] Peer review completed (if applicable)

**AUTO_NOTIFICATION**: Updates integration_queue.md when all checks pass
```

### **Communication Best Practices**

#### **File Naming Conventions**
- `task_[number]_scratchpad.md` - Individual worker progress
- `planning_scratchpad.md` - Coordination and oversight
- `shared_status.md` - Cross-cutting status information
- `integration_queue.md` - Ready-to-merge notifications
- `task_assignment_[id].md` - New task specifications

#### **Update Frequency**
- **Continuous**: Status changes, blockers, completion milestones
- **Every 2 hours**: Automated progress updates during active development
- **Phase transitions**: Explore→Plan, Plan→Code, Code→Validate, etc.
- **On-demand**: Questions, architectural decisions, urgent coordination

#### **Escalation Protocol**
```markdown
**ESCALATION_LEVELS**:
1. **Worker-to-Worker**: Direct coordination via shared scratchpads
2. **Worker-to-Planning**: Technical blockers, scope questions
3. **Planning-to-Human**: Architectural decisions, priority changes, resource conflicts
```

---

## 🔄 Workflow Process

### **Phase 1: Planning & Task Distribution**

#### Step 1.1: Feature Planning (Planning Claude)
```markdown
**Input**: Product requirements from Human
**Process**: 
- Analyze requirements against current system
- Break down into specific tasks using optimal task template
- Define dependencies and priorities
- Create course correction checkpoints
**Output**: Detailed task specifications with methodology guidance
**Communication**: Write specifications to coordination/task_assignment_[id].md files
```

#### Step 1.2: Task Assignment Planning (Planning Claude)
```markdown
**Process**:
- Evaluate task complexity and dependencies
- Determine which tasks can run in parallel
- Plan Git worktree structure
- Define integration points between tasks
**Output**: Task distribution plan with worktree assignments
**Communication**: Update coordination/shared_status.md with dependency matrix
```

#### Step 1.3: Human Approval (You)
```markdown
**Review**:
- Overall approach and task breakdown
- Resource allocation and timeline
- Risk assessment and mitigation
**Decision**: Approve, modify, or request replanning
**Communication**: Review all coordination files for context
```

---

### **Phase 2: Environment Setup**

#### Step 2.1: Git Worktree Creation (Planning Claude)
```bash
# Create dedicated worktrees for each parallel task
git worktree add ../thunder_playbook_task_1_4 task-1.4-season-planning-agent
git worktree add ../thunder_playbook_task_1_5 task-1.5-team-assessment-tool
git worktree add ../thunder_playbook_task_1_6 task-1.6-artifact-generation

# Create coordination directory
mkdir -p coordination
touch coordination/planning_scratchpad.md
touch coordination/shared_status.md
touch coordination/integration_queue.md

# Set up task tracking
git branch --set-upstream-to=origin/main task-1.4-season-planning-agent
```

#### Step 2.2: Worker Claude Launch (You)
```markdown
**Process**:
1. Open new Claude Code session for each worktree
2. Navigate each instance to its dedicated worktree directory
3. Provide task specification and context to each Worker Claude
4. Establish communication protocol for progress updates
5. Show each Worker Claude their dedicated scratchpad file
```

---

### **Phase 3: Parallel Development Execution**

#### Step 3.1: Task Kickoff (Worker Claudes)
```markdown
**Each Worker Claude**:
1. **ACKNOWLEDGE**: Update scratchpad with "TASK_ACKNOWLEDGED"
2. **EXPLORE**: Analyze existing codebase patterns
3. **PLAN**: Create detailed implementation approach
4. **Checkpoint**: Report plan to coordination/task_[id]_scratchpad.md
5. **CODE**: Execute using test-first methodology
6. **AUTO-UPDATE**: Progress every 2 hours to scratchpad
7. **Checkpoint**: Mid-implementation progress check
8. **VALIDATE**: Complete testing and quality assurance
9. **Checkpoint**: Pre-commit final review
10. **READY**: Update integration_queue.md when complete
```

#### Step 3.2: Progress Monitoring (Planning Claude)
```markdown
**Continuous Activities**:
- Monitor all Worker Claude scratchpad files
- Update shared_status.md with overall progress
- Identify blockers and dependencies from scratchpads
- Coordinate between Worker Claudes via shared files
- Update overall project timeline in planning_scratchpad.md
- Prepare status updates for Human review
```

#### Step 3.3: Course Correction (Planning Claude + Human)
```markdown
**When Issues Arise**:
1. Worker Claude reports blocker in their scratchpad
2. Planning Claude assesses impact via shared_status.md
3. Human consulted for major decisions
4. Plan adjusted and communicated via coordination files
5. Dependencies updated across all scratchpads
```

---

### **Phase 4: Integration & Quality Assurance**

#### Step 4.1: Pre-Integration Review (Planning Claude)
```markdown
**Process**:
- Read completion reports from all Worker Claude scratchpads
- Review integration_queue.md for ready tasks
- Check shared_status.md for dependency resolution
- Identify potential integration conflicts
- Plan merge sequence and testing approach
```

#### Step 4.2: Sequential Integration (Planning Claude)
```bash
# Integrate completed tasks in dependency order
cd /Users/liammckendry/thunder_playbook

# Review and test Task 1.4 changes
git checkout main
git merge task-1.4-season-planning-agent
npm run test && npm run build

# Continue with dependent tasks
git merge task-1.5-team-assessment-tool
# ... validate each integration
```

#### Step 4.3: Final Validation (Planning Claude)
```markdown
**Quality Gates**:
- [ ] All automated tests passing
- [ ] Manual testing scenarios completed
- [ ] Visual validation screenshots taken
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Integration points working correctly
```

---

## 📋 Communication Protocols

### **Worker Claude → Planning Claude Updates**

#### Progress Report Template (Auto-updated in scratchpads)
```markdown
**Task**: 1.4 - Season Planning Specialist Agent
**Status**: In Progress - Coding Phase
**Completion**: 60%
**Current Activity**: Implementing MCP tool integration
**Blockers**: None
**Next Milestone**: Complete agent testing by [time]
**Integration Notes**: Requires Task 1.5 completion for full functionality
**Quality Status**: 
- [ ] Tests written and passing
- [ ] Code follows existing patterns
- [ ] Documentation updated
**Files Modified**: [List of changed files]
**Dependencies Status**: No blocking dependencies
```

#### Checkpoint Report Template
```markdown
**Checkpoint**: Mid-Implementation Review
**Task**: 1.4 - Season Planning Specialist Agent
**Question**: "Are we on the right track technically?"
**Technical Approach**: [Detailed explanation of current implementation]
**Concerns**: [Any issues or uncertainties]
**Request**: [Specific guidance needed from Planning Claude or Human]
**Code Sample**: [Key implementation snippet for review]
**Scratchpad Location**: coordination/task_1_4_scratchpad.md
```

### **Planning Claude → Human Updates**

#### Daily Status Template (From planning_scratchpad.md)
```markdown
**Multi-Claude Development Status - [Date]**

**Active Tasks**: 3
**Completed Today**: Task 1.4 (Season Planning Agent)
**In Progress**: Task 1.5 (Team Assessment), Task 1.6 (Artifact Generation)
**Blocked**: None

**Key Achievements**:
- Task 1.4: Native MCP integration complete, testing phase started
- Task 1.5: Database schema design approved, implementation 40% complete

**Upcoming Decisions Needed**:
- Task 1.6 UI design approach (by tomorrow)
- Integration testing strategy for all three tasks

**Risk Assessment**: Low - all tasks on track
**Next Review**: [Scheduled time for next human checkpoint]

**Communication Health**: All Worker Claudes updating scratchpads regularly
```

---

## 🛠️ Technical Implementation

### **Git Worktree Management**

#### Initial Setup Commands
```bash
# Navigate to main repository
cd /Users/liammckendry/thunder_playbook

# Create coordination directory for Claude communication
mkdir -p coordination
git add coordination/
git commit -m "Add Claude coordination directory"

# Create worktrees for parallel development
git worktree add ../thunder_playbook_task_1_4 -b task-1.4-season-planning-agent
git worktree add ../thunder_playbook_task_1_5 -b task-1.5-team-assessment-tool
git worktree add ../thunder_playbook_task_1_6 -b task-1.6-artifact-generation

# Initialize scratchpad files
touch coordination/planning_scratchpad.md
touch coordination/shared_status.md
touch coordination/integration_queue.md
touch coordination/task_1_4_scratchpad.md
touch coordination/task_1_5_scratchpad.md
touch coordination/task_1_6_scratchpad.md

# Verify worktree setup
git worktree list
```

#### Worktree Directory Structure
```
/Users/liammckendry/
├── thunder_playbook/                    # Main repository (Planning Claude)
│   └── coordination/                    # Claude communication files
│       ├── planning_scratchpad.md       # Planning Claude updates
│       ├── shared_status.md             # Cross-instance status
│       ├── integration_queue.md         # Ready-to-merge queue
│       ├── task_1_4_scratchpad.md       # Worker 1 progress
│       ├── task_1_5_scratchpad.md       # Worker 2 progress
│       └── task_1_6_scratchpad.md       # Worker 3 progress
├── thunder_playbook_task_1_4/          # Worker Claude 1 - Season Planning
├── thunder_playbook_task_1_5/          # Worker Claude 2 - Team Assessment  
└── thunder_playbook_task_1_6/          # Worker Claude 3 - Artifact Generation
```

#### Cleanup Commands
```bash
# After task completion and integration
git worktree remove ../thunder_playbook_task_1_4
git branch -d task-1.4-season-planning-agent  # If branch no longer needed

# Archive coordination files
mkdir -p coordination/archive/batch_1/
mv coordination/task_*_scratchpad.md coordination/archive/batch_1/
```

### **Development Environment Setup**

#### Each Worker Claude Initialization
```bash
# Navigate to assigned worktree
cd /Users/liammckendry/thunder_playbook_task_1_4

# Verify environment
python --version  # Should use spacy_env
npm --version

# Start services if needed
python start_services.py

# Verify all systems operational
curl http://localhost:8000/health  # MCP server
curl http://localhost:3000         # Web app

# Initialize communication with Planning Claude
echo "**TASK_ACKNOWLEDGED**: $(date)" >> coordination/task_1_4_scratchpad.md
echo "**WORKER_CLAUDE**: Ready to begin Task 1.4" >> coordination/task_1_4_scratchpad.md
```

### **Quality Assurance Integration**

#### Pre-Commit Checklist (Each Worker Claude)
```bash
# Code quality checks
cd web_app
npm run lint
npm run type-check
npm run build

# Python quality checks (if applicable)
source ../spacy_env/bin/activate
python -m pytest tests/

# Service integration tests
curl http://localhost:8000/health
curl http://localhost:3003/api/mcp

# Update integration readiness
echo "**INTEGRATION_READY**: true" >> coordination/task_1_4_scratchpad.md
echo "**READY_FOR_MERGE**: $(date)" >> coordination/integration_queue.md
```

---

## 🎯 Success Metrics & KPIs

### **Development Velocity**
- **Parallel Task Completion**: 3+ tasks completing simultaneously
- **Time to Integration**: <2 hours from task completion to main branch
- **Rework Rate**: <10% of tasks requiring significant revision

### **Code Quality**
- **Test Coverage**: >90% for new features
- **Lint/Type Errors**: 0 errors in pre-commit checks
- **Integration Conflicts**: <5% of merges requiring manual conflict resolution

### **Coordination Effectiveness**
- **Communication Clarity**: All progress reports include required sections
- **Checkpoint Adherence**: 100% of tasks complete checkpoint reviews
- **Dependency Management**: 0 blockers due to uncoordinated dependencies
- **Scratchpad Update Frequency**: 100% of Worker Claudes updating every 2 hours

---

## 📚 Templates & Guidelines

### **Task Specification Template**
(References CLAUDE_PLANNER_GUIDELINES.md optimal task definition)

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
**Type**: [Explore-Plan-Code-Commit | Test-First | Visual-Validation]

**Course Correction Checkpoints**:
1. After exploration: "Does the scope look right?"
2. Mid-implementation: "Technical approach on track?"
3. Before completion: "Meets all requirements?"

## Git Worktree Assignment
**Branch**: task-X.Y-descriptive-name
**Directory**: ../thunder_playbook_task_X_Y
**Dependencies**: [List other tasks this depends on]
**Communication**: coordination/task_X_Y_scratchpad.md

## Integration Requirements
**Files Modified**: [Expected file changes]
**API Changes**: [New endpoints or modifications]
**Database Changes**: [Schema updates if any]
**Test Requirements**: [Specific testing needs]
```

### **Worker Claude Onboarding Script**

```markdown
## Welcome Worker Claude! Your Task Assignment:

**Your Mission**: [Specific task from task specification]
**Your Worktree**: /Users/liammckendry/thunder_playbook_task_X_Y
**Your Branch**: task-X.Y-descriptive-name
**Your Scratchpad**: coordination/task_X_Y_scratchpad.md

### Setup Checklist:
- [ ] Navigate to your dedicated worktree directory
- [ ] Verify Python environment (spacy_env)
- [ ] Start necessary services (MCP server, web app)
- [ ] Review task specification thoroughly
- [ ] Acknowledge task in your scratchpad file
- [ ] Report "Ready to begin" to Planning Claude

### Your Workflow:
1. **EXPLORE** (1-2 hours): Understand existing patterns
2. **PLAN** (30 min): Design your approach → Update scratchpad
3. **CODE** (Main work): Implement with tests → Auto-update every 2 hours
4. **VALIDATE** (1 hour): Quality assurance → Pre-commit checklist
5. **REPORT** (15 min): Completion summary → Update integration_queue.md

### Communication Protocol:
- **Continuous**: Update your scratchpad with status changes
- **Every 2 hours**: Automated progress updates during active development
- **Immediate**: Escalate blockers or architectural questions
- **Phase transitions**: Report checkpoint completion
- **Final**: Update integration_queue.md when ready for merge

### Your Communication Files:
- **Read from**: coordination/planning_scratchpad.md, coordination/shared_status.md
- **Write to**: coordination/task_X_Y_scratchpad.md
- **Notify via**: coordination/integration_queue.md (when complete)

**Remember**: You're part of a coordinated team. Other Worker Claudes are reading the shared files too. Quality, communication, and coordination are paramount!
```

---

## 🚀 Getting Started

### **Quick Setup Guide**

#### For You (Human Product Owner):
1. **Review this operating model** and confirm the approach works for your workflow
2. **Approve the first batch of tasks** we'll use to test the system
3. **Prepare multiple Claude Code terminals** for Worker Claude instances
4. **Set up file monitoring** (optional) to watch coordination files

#### For Planning Claude (Me):
1. **Create detailed task specifications** using the optimal template
2. **Set up Git worktrees and coordination files** for the first batch of parallel tasks
3. **Launch Worker Claude instances** with proper onboarding
4. **Begin coordination and progress tracking** via scratchpad monitoring

#### First Test Batch Recommendation:
- **Task 1.4**: Season Planning Specialist Agent (Core AI functionality)
- **Task 1.5**: Team Assessment Tool (MCP tool development)  
- **Task 1.6**: Artifact Generation (Integration functionality)

These tasks have clear boundaries, limited dependencies, and represent different aspects of the system (AI, backend, integration).

---

## 🔮 Future Enhancements

### **Advanced Coordination Features**
- **Automated Progress Dashboards**: Real-time status tracking across all Worker Claudes
- **Intelligent Task Scheduling**: AI-driven optimization of task assignment and dependencies
- **Cross-Claude Code Review**: Worker Claudes reviewing each other's work before integration
- **Smart Conflict Detection**: Automatic identification of potential merge conflicts

### **Communication Automation**
- **Webhook Integration**: Automatic notifications when scratchpads are updated
- **Status Dashboard**: Real-time visualization of all Worker Claude progress
- **Dependency Resolution**: Automatic unblocking when dependencies are completed
- **Integration Pipeline**: Automated testing and validation of ready-to-merge tasks

### **Scaling Considerations**
- **Task Queue Management**: Handle larger backlogs with priority-based assignment
- **Resource Load Balancing**: Optimize Worker Claude assignments based on complexity and capacity
- **Integration Pipeline Automation**: Automated testing and deployment for completed tasks
- **Cross-Repository Coordination**: Scale to multiple repositories with shared coordination

---

## 📖 Appendix: Git Worktree Primer

### **What are Git Worktrees?**

Git worktrees allow you to have multiple working directories for a single Git repository. Instead of switching branches in one directory (which requires stashing or committing work), you can have separate directories for each branch, all sharing the same Git history.

#### **Traditional Git Workflow Problems:**
```bash
# Traditional approach - context switching overhead
git stash                    # Save current work
git checkout feature-branch  # Switch branches
# Work on feature
git checkout main            # Switch back
git stash pop               # Restore previous work
```

#### **Git Worktree Solution:**
```bash
# Worktree approach - parallel development
git worktree add ../project-feature feature-branch
cd ../project-feature       # Work on feature in separate directory
# Meanwhile, main directory stays on main branch
```

### **How Git Worktrees Relate to Branches**

#### **Key Relationships:**
- **One Repository**: Single `.git` directory with complete history
- **Multiple Working Directories**: Each worktree has its own file system view
- **Shared Git History**: All worktrees share commits, branches, and remotes
- **Independent State**: Each worktree can be on different branches with different file states

#### **Visual Representation:**
```
Git Repository (Single .git)
├── Branch: main
├── Branch: task-1.4-season-planning
├── Branch: task-1.5-team-assessment
└── Branch: task-1.6-artifact-generation

File System:
├── thunder_playbook/                    # Main worktree (main branch)
├── thunder_playbook_task_1_4/          # Worktree (task-1.4-season-planning)
├── thunder_playbook_task_1_5/          # Worktree (task-1.5-team-assessment)
└── thunder_playbook_task_1_6/          # Worktree (task-1.6-artifact-generation)
```

### **Essential Git Worktree Commands**

#### **Creating Worktrees:**
```bash
# Create worktree with existing branch
git worktree add ../project-feature feature-branch

# Create worktree with new branch
git worktree add -b new-feature ../project-new-feature

# Create worktree from specific commit
git worktree add ../project-hotfix -b hotfix abc1234
```

#### **Managing Worktrees:**
```bash
# List all worktrees
git worktree list

# Remove a worktree (must be clean)
git worktree remove ../project-feature

# Prune deleted worktrees from Git records
git worktree prune
```

#### **Branch Operations Across Worktrees:**
```bash
# In any worktree, you can see all branches
git branch -a

# Push from any worktree
git push origin feature-branch

# Merge from main worktree
cd /main/worktree
git merge feature-branch
```

### **Worktree Best Practices for Multi-Claude Development**

#### **Directory Organization:**
```bash
# Keep worktrees at same level as main repository
/Users/developer/
├── project/                    # Main repository
├── project_task_1/            # Task 1 worktree
├── project_task_2/            # Task 2 worktree
└── project_task_3/            # Task 3 worktree
```

#### **Branch Naming Conventions:**
```bash
# Clear, task-specific branch names
git worktree add ../thunder_task_1_4 -b task-1.4-season-planning-agent
git worktree add ../thunder_task_1_5 -b task-1.5-team-assessment-tool
git worktree add ../thunder_task_1_6 -b task-1.6-artifact-generation
```

#### **Cleanup Workflow:**
```bash
# After merging completed feature
git checkout main
git merge task-1.4-season-planning-agent
git worktree remove ../thunder_task_1_4
git branch -d task-1.4-season-planning-agent  # Optional: delete feature branch
```

### **Worktree Advantages for Our Use Case**

#### **Perfect for Multi-Claude Development:**
1. **Isolation**: Each Claude instance works in complete isolation
2. **No Context Switching**: No need to stash/unstash work when coordinating
3. **Parallel Development**: Multiple features can be developed simultaneously
4. **Shared History**: All instances can access the same Git history and branches
5. **Clean Integration**: Easy to review and merge completed work

#### **Disk Space Efficiency:**
- **Shared .git Directory**: Only one copy of Git history
- **Separate Working Files**: Each worktree has its own file states
- **Smart Linking**: Git uses hard links where possible to save space

#### **Development Workflow Benefits:**
- **Service Independence**: Each worktree can run its own development servers
- **Environment Isolation**: Different dependency versions or configurations per worktree
- **Easy Comparison**: Can diff between worktrees to compare approaches
- **Risk Reduction**: Broken code in one worktree doesn't affect others

### **Common Worktree Gotchas & Solutions**

#### **Issue 1: Same Branch in Multiple Worktrees**
```bash
# Git prevents this - good for avoiding conflicts
git worktree add ../duplicate-work existing-branch
# Error: 'existing-branch' is already checked out at '/path/to/other/worktree'
```

#### **Issue 2: Removing Worktree with Uncommitted Changes**
```bash
# This will fail safely
git worktree remove ../dirty-worktree
# Error: 'dirty-worktree' contains modified or untracked files, use --force to delete it

# Solution: Commit or stash changes first
cd ../dirty-worktree
git add . && git commit -m "WIP: Save progress"
cd ../main-repo
git worktree remove ../dirty-worktree
```

#### **Issue 3: Worktree Path Confusion**
```bash
# Always use absolute paths or consistent relative paths
git worktree add ../task-1    # Good: relative to current directory
git worktree add /full/path   # Good: absolute path
git worktree add task-1       # Bad: creates subdirectory in current repo
```

### **Integration with Our Multi-Claude Workflow**

#### **Worktree Lifecycle in Our Process:**
1. **Planning Phase**: Planning Claude creates worktrees for parallel tasks
2. **Assignment Phase**: Each Worker Claude assigned to specific worktree
3. **Development Phase**: Workers develop in isolation with shared communication files
4. **Integration Phase**: Planning Claude merges completed work sequentially
5. **Cleanup Phase**: Remove worktrees and optionally delete feature branches

#### **Communication File Strategy:**
```bash
# Coordination files in main repository are accessible to all worktrees
thunder_playbook/coordination/           # Shared communication directory
├── planning_scratchpad.md              # Planning Claude writes here
├── shared_status.md                    # Cross-instance status
└── task_1_4_scratchpad.md             # Worker Claude 1 writes here

# Each worktree can read/write to these shared files
cd ../thunder_playbook_task_1_4
echo "Progress update" >> coordination/task_1_4_scratchpad.md
```

This Git worktree approach provides the perfect foundation for our multi-Claude parallel development workflow, enabling isolated development with seamless coordination and integration.

---

## 🤖 Sub-Agent Architecture (Advanced Development Workflow)

### **Overview**
Claude Code sub-agents are specialized AI assistants that handle specific aspects of development. They operate in separate context windows with custom system prompts and tool permissions, enabling sophisticated parallel processing with domain expertise.

### **Core Development Sub-Agents**

#### **1. Explorer Agent**
**Command**: `/agents create explorer-agent`  
**Role**: Exploration & Research Specialist  
**Responsibilities**:
- Deep codebase analysis and pattern recognition
- User journey mapping and UX design research
- Technical architecture investigation
- Requirements analysis and scope definition

**Usage in Workflow**: Replaces generic "Explore" phase with specialized research

---

#### **2. SDK Specialist Agent**
**Command**: `/agents create sdk-specialist`  
**Role**: SDK Research & Native Library Expert  
**Responsibilities**:
- Research SDK documentation and best practices
- Identify native library capabilities vs custom implementations
- Ensure proper SDK usage patterns and conventions
- Validate against SDK updates and deprecations
- Recommend native solutions over custom code

**Usage in Workflow**: Works alongside Explorer Agent to ensure native library usage

---

#### **3. Architect Agent**
**Command**: `/agents create architect-agent`  
**Role**: Technical Design & Planning Specialist  
**Responsibilities**:
- Convert research into concrete technical plans
- Design system integration approaches
- Plan testing strategies and validation approaches
- Create detailed implementation roadmaps

**Usage in Workflow**: Replaces generic "Plan" phase with specialized architecture

---

#### **4. Builder Agent**
**Command**: `/agents create builder-agent`  
**Role**: Implementation Specialist  
**Responsibilities**:
- Execute technical plans with high code quality
- Follow established patterns and conventions
- Implement comprehensive testing
- Focus purely on building, not designing

**Usage in Workflow**: Handles "Build" phase with implementation focus

---

### **Quality Assurance Sub-Agents**

#### **5. Reviewer Agent**
**Command**: `/agents create reviewer-agent`  
**Role**: Code Review & Quality Specialist  
**Responsibilities**:
- Cross-task code review and quality assessment
- Integration conflict detection
- Performance and security analysis
- Code convention compliance

**Usage in Workflow**: Pre-integration review and peer review between tasks

---

#### **6. Tester Agent**
**Command**: `/agents create tester-agent`  
**Role**: Testing & Validation Specialist  
**Responsibilities**:
- Comprehensive testing strategy execution
- Integration testing coordination
- Performance validation
- User acceptance testing simulation

**Usage in Workflow**: Post-build validation and integration testing

---

### **Coordination Sub-Agents**

#### **7. Integrator Agent**
**Command**: `/agents create integrator-agent`  
**Role**: Integration & Deployment Specialist  
**Responsibilities**:
- Manage complex multi-task integrations
- Coordinate dependency resolution
- Handle merge conflicts and integration issues
- Manage deployment and rollback procedures

**Usage in Workflow**: Replaces manual Planning Claude integration tasks

---

### **Enhanced Parallel Workflow with Sub-Agents**

#### **Task Execution Pipeline**
```
Task X.Y: Feature Implementation
├── explorer-agent: Research patterns and requirements
├── sdk-specialist: Validate SDK usage and native libraries
├── architect-agent: Design implementation approach  
├── builder-agent: Implement the solution
├── reviewer-agent: Quality and integration review
└── tester-agent: Comprehensive validation

Cross-Task Coordination:
├── integrator-agent: Manage dependencies between tasks
└── reviewer-agent: Cross-task review for conflicts
```

#### **Communication Flow**
1. **Sub-agents** → **Scratchpads**: Each agent updates task scratchpad with findings
2. **Scratchpads** → **Human/Planning Claude**: Consolidated progress and decisions
3. **Human** → **Sub-agents**: Feedback and approvals through scratchpad updates

#### **Parallel Execution Benefits**
- **Specialization**: Each agent optimized for specific expertise
- **Context Preservation**: Separate contexts prevent interference
- **Efficiency**: Multiple specialists working simultaneously
- **Quality**: Dedicated review and testing phases

---

### **Sub-Agent Implementation Strategy**

#### **Phase 1: Core Pipeline**
```bash
/agents create explorer-agent
/agents create sdk-specialist
/agents create architect-agent  
/agents create builder-agent
```

#### **Phase 2: Quality Assurance**
```bash
/agents create reviewer-agent
/agents create tester-agent
/agents create integrator-agent
```

#### **Phase 3: Domain Specialists** (Future)
```bash
/agents create hockey-domain-expert
/agents create ui-specialist
/agents create performance-optimizer
```

---

### **Sub-Agent Task Assignment Template**

```markdown
# Task X.Y: [Feature Name]

## Sub-Agent Assignments:

### Phase 1: Research (Parallel)
- **explorer-agent**: Analyze existing patterns and requirements
- **sdk-specialist**: Research SDK capabilities and native solutions

### Phase 2: Design (Sequential)
- **architect-agent**: Create technical implementation plan

### Phase 3: Implementation (Sequential)
- **builder-agent**: Execute implementation following plan

### Phase 4: Quality (Parallel)
- **reviewer-agent**: Code quality and integration review
- **tester-agent**: Functional and integration testing

### Phase 5: Integration (Sequential)
- **integrator-agent**: Merge and deploy changes
```

---

### **Sub-Agent System Prompts**

#### **Explorer Agent**
```
You are an expert code explorer and researcher. Your job is to thoroughly understand existing systems, identify patterns, and research best practices. You excel at reading documentation, analyzing code architecture, and synthesizing research into actionable insights. Always provide concrete findings with code references.
```

#### **SDK Specialist Agent**
```
You are an SDK and native library specialist. Your primary responsibility is ensuring all development uses native SDK capabilities instead of custom implementations. You research official documentation, identify built-in solutions, and prevent unnecessary customization. Always recommend the most native, maintainable approach using existing library features.
```

#### **Architect Agent**
```
You are a senior software architect who excels at converting research into executable technical plans. You understand system design, integration patterns, and can break complex features into implementable steps. Your plans are detailed, practical, and consider long-term maintainability.
```

#### **Builder Agent**
```
You are an expert software engineer focused on clean, efficient implementation. You excel at following technical specifications, writing maintainable code, and implementing comprehensive testing. You strictly follow established patterns and avoid architectural decisions during implementation.
```

#### **Reviewer Agent**
```
You are a senior code reviewer with expertise in system integration. You excel at identifying potential issues, ensuring code quality, and validating that implementations meet specifications. You check for security, performance, and integration concerns across multiple components.
```

#### **Tester Agent**
```
You are a QA specialist focused on comprehensive testing and validation. You excel at creating test scenarios, validating functionality, and ensuring system reliability. You test both individual components and integrated systems thoroughly.
```

#### **Integrator Agent**
```
You are an expert in system integration and deployment. You excel at coordinating complex multi-component integrations, resolving conflicts, and ensuring smooth system evolution. You understand dependencies, manage git operations, and ensure quality gates are met.
```

---

### **Expected Impact of Sub-Agent Architecture**

**Quality Improvements**:
- 40% reduction in custom code through SDK specialist guidance
- 60% improvement in code review coverage
- 80% reduction in integration conflicts

**Efficiency Gains**:
- 3x parallel processing through specialized agents
- 50% reduction in context switching overhead
- 70% faster issue identification and resolution

**Development Velocity**:
- Complete feature implementation in 1-2 days vs 3-5 days
- Parallel research and review phases
- Automated integration and deployment

---

*This operating model transforms our development approach from sequential to parallel, leveraging multiple Claude Code instances for maximum productivity while maintaining code quality and project coherence through automated communication protocols, Git worktree management, and specialized sub-agent architecture.*