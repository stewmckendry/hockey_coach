# Slash Commands Manifest
## Hockey Coach AI Assistant - Claude Code Automation

This document provides a complete inventory of all slash commands for the Hockey Coach AI Assistant project, organized by status and impact.

---

## 🎯 EXISTING COMMANDS (Implemented)

### `/hockey-setup` - Complete Development Environment Setup
**Who**: Any Claude instance  
**When**: Project startup, environment reset  
**What**: 
- Activate Python environment (spacy_env)
- Verify environment variables (OPENAI_API_KEY, CHROMA_*)
- Start all core services (MCP server, API wrapper, web app, POC components)
- Run health checks on all services
- Execute integration test

**Why**: 
- Eliminates 20+ manual setup commands
- Ensures consistent environment across all instances
- Validates full system functionality before development
- **Impact**: HIGH - Essential for project initialization

---

### `/commit-prep` - Pre-Commit Quality Assurance
**Who**: Any Claude instance  
**When**: Before git commits  
**What**:
- Run complete code quality checks (ESLint, TypeScript, build tests)
- Execute Python tests and MCP integration validation
- Verify all services healthy and functional
- Check documentation currency
- Review git status and staged changes
- Security scan for sensitive data

**Why**:
- Prevents broken commits and build failures
- Standardizes quality gates across all developers
- Ensures documentation stays current
- Catches security issues before commit
- **Impact**: HIGH - Critical for code quality

---

### `/mcp-test` - MCP Server and Tool Testing
**Who**: Any Claude instance  
**When**: After MCP changes, debugging connectivity issues  
**What**:
- Test MCP server health and connectivity
- Validate all 4 hockey coaching tools functionality
- Test agent-to-MCP integration
- Verify ChromaDB connectivity and data access
- Generate MCP tool usage report

**Why**:
- Validates MCP infrastructure integrity
- Catches integration issues early
- Provides diagnostic information for debugging
- **Impact**: MEDIUM - Important for MCP development

---

### `/web-validate` - Full Web Integration Testing
**Who**: Any Claude instance  
**When**: After UI changes, before production deployment  
**What**:
- Test complete web application functionality
- Validate chat interface and agent responses  
- Check responsive behavior (desktop, mobile)
- Test all API endpoints and integration points
- Generate screenshots for visual validation
- Verify browser compatibility

**Why**:
- Ensures web application quality and functionality
- Catches UI/UX issues before user exposure
- Validates complete user journey end-to-end
- **Impact**: MEDIUM - Important for user experience

---

### `/trace-check` - OpenAI Tracing Functionality Verification
**Who**: Any Claude instance  
**When**: After agent changes, debugging performance issues  
**What**:
- Verify OpenAI tracing integration working
- Generate sample traces and validate dashboard access
- Check trace metadata and grouping functionality
- Test performance monitoring and token usage tracking
- Validate trace URLs and accessibility

**Why**:
- Ensures observability and debugging capabilities
- Validates performance monitoring infrastructure
- Confirms trace data quality and accessibility
- **Impact**: LOW - Useful for debugging and monitoring

---

## 🚀 PHASE 1 COMMANDS (Critical Automation - Implementing Now)

### `/multi-claude-setup` - Multi-Claude Infrastructure Setup  
**Who**: Planning Claude  
**When**: At start of each new batch of parallel tasks  
**What**:
- Create Git worktrees for task batch with proper branch naming
- Initialize all coordination scratchpad files
- Update shared status dashboard with new task assignments
- Verify all coordination files are properly configured
- Run health checks on core services before Worker Claude launch

**Why**:
- Eliminates 15+ manual commands per batch
- Ensures consistent worktree and communication setup
- Prevents coordination file setup errors
- Validates environment before Worker Claude launch
- **Impact**: HIGH - Essential for multi-Claude workflow

---

### `/worker-ready-check` - Worker Claude Environment Validation
**Who**: Worker Claude instances  
**When**: Upon assignment to worktree, before beginning exploration  
**What**:
- Verify worktree setup and correct branch checkout
- Validate Python environment (spacy_env) activation
- Test service connectivity (MCP server, web app, ChromaDB)
- Acknowledge task assignment in coordination scratchpad
- Run initial system health checks
- Update coordination files with "READY" status

**Why**:
- Prevents Worker Claude startup failures
- Standardizes environment validation across all workers
- Provides automatic task acknowledgment
- Enables immediate issue detection and resolution
- **Impact**: HIGH - Critical for reliable parallel development

---

### `/integration-ready` - Pre-Integration Quality Gates
**Who**: Worker Claude instances  
**When**: After Build phase, before requesting integration  
**What**:
- Execute complete quality check suite (lint, type-check, build, tests)
- Run service health validation on all components
- Perform git operations (add, commit, rebase main, push branch)
- Update integration queue with standardized completion format
- Generate comprehensive integration summary and notes

**Why**:
- Ensures consistent quality standards across all tasks
- Eliminates integration failures and merge conflicts
- Standardizes submission format for Planning Claude
- Reduces Planning Claude review and integration time
- **Impact**: HIGH - Essential for reliable integration process

---

## 🔧 PHASE 2 COMMANDS (Workflow Optimization - Next Priority)

### `/checkpoint-report` - Standardized Progress Updates
**Who**: Worker Claude instances  
**When**: At Draft+Questions and Testing Ready checkpoints  
**What**:
- Generate standardized progress report with consistent formatting
- Update individual scratchpad with current phase status and completion percentage
- Format Draft+Questions presentation in standard template
- Automatically update shared status dashboard
- Calculate and report completion metrics

**Why**:
- Ensures consistent reporting format across all Worker Claudes
- Provides automatic status dashboard updates
- Reduces communication overhead and improves visibility
- Enables better progress tracking and coordination
- **Impact**: MEDIUM - Improves communication consistency

---

### `/task-handoff` - Planning Claude Integration Process
**Who**: Planning Claude  
**When**: Processing completed tasks from integration queue  
**What**:
- Review and validate integration queue submissions
- Confirm all quality gates completed successfully
- Execute git merge operations in proper dependency order
- Run comprehensive integration tests
- Update all coordination files with integration status
- Archive completed task scratchpads and clean up worktrees

**Why**:
- Ensures consistent integration process across all tasks
- Reduces integration errors and dependency conflicts
- Provides automatic cleanup and maintenance
- Improves dependency management and sequencing
- **Impact**: MEDIUM - Streamlines Planning Claude operations

---

### `/hockey-system-test` - Full System Validation
**Who**: Any Claude instance  
**When**: After integrations, before declaring batch complete  
**What**:
- Start all core services using unified startup process
- Execute comprehensive system test suite
- Test all service endpoints and integration points
- Validate agent HTTP server and MCP connectivity
- Run CLI agent tests and generate system health report

**Why**:
- Validates complete system integrity after changes
- Catches integration issues early in development cycle
- Provides standardized testing approach across all instances
- Builds confidence in system state and functionality
- **Impact**: MEDIUM - Important for system reliability

---

## 📋 PHASE 3 COMMANDS (Future Backlog - Nice to Have)

### `/scratchpad-sync` - Communication File Management
**Who**: All Claude instances  
**When**: Periodic maintenance, end of development batches  
**What**:
- Archive completed task scratchpads to organized folders
- Clean up stale communication files and temporary data
- Update coordination file permissions and access
- Synchronize timestamps across coordination files
- Generate communication health report

**Why**:
- Maintains clean and organized coordination workspace
- Prevents coordination file clutter and confusion
- Ensures proper file permissions for multi-Claude access
- **Impact**: LOW - Quality of life improvement

---

### `/batch-status` - Multi-Claude Development Dashboard
**Who**: Planning Claude  
**When**: Daily status checks, batch progress reviews  
**What**:
- Parse and analyze all Worker Claude scratchpad files
- Generate unified status report with progress metrics
- Identify blocked tasks and dependency issues
- Calculate batch completion percentage and timeline estimates
- Generate executive summary for human review

**Why**:
- Provides comprehensive visibility into multi-Claude development
- Enables proactive identification of issues and bottlenecks
- Supports better resource allocation and planning decisions
- **Impact**: LOW - Enhanced visibility and reporting

---

### `/code-review-assist` - Automated Code Review Support
**Who**: Planning Claude, Worker Claude instances  
**When**: Before integration, during peer review processes  
**What**:
- Analyze code changes against project conventions and patterns
- Check for security issues, performance concerns, and best practices
- Generate code review checklist based on file types and changes
- Identify potential integration conflicts with other active tasks
- Provide automated code quality scoring and recommendations

**Why**:
- Improves code quality through consistent review standards
- Catches issues before human review, saving time
- Ensures adherence to project conventions and patterns
- **Impact**: LOW - Code quality improvement

---

### `/deployment-prep` - Production Deployment Preparation
**Who**: Planning Claude  
**When**: Before production deployments  
**What**:
- Run comprehensive pre-deployment testing suite
- Validate environment configuration for production
- Generate deployment checklist and rollback procedures
- Test Docker container builds and deployment scripts
- Verify production service connectivity and health

**Why**:
- Reduces production deployment failures and issues
- Ensures consistent deployment process and quality
- Provides confidence in production readiness
- **Impact**: LOW - Production deployment support

---

## 📊 Implementation Roadmap

### Immediate Priority (Phase 1)
**Timeline**: Before launching Worker Claude instances
**Commands**: `/multi-claude-setup`, `/worker-ready-check`, `/integration-ready`
**Expected Impact**: 
- 80% reduction in setup failures
- 30 minutes saved per development batch
- Consistent quality gates across all tasks

### Next Phase (Phase 2)  
**Timeline**: After successful multi-Claude workflow validation
**Commands**: `/checkpoint-report`, `/task-handoff`, `/hockey-system-test`
**Expected Impact**:
- 60% improvement in communication consistency
- 15 minutes saved per task completion
- Better system reliability and confidence

### Future Enhancement (Phase 3)
**Timeline**: Based on workflow optimization needs
**Commands**: `/scratchpad-sync`, `/batch-status`, `/code-review-assist`, `/deployment-prep`
**Expected Impact**:
- Enhanced workflow visibility and reporting
- Improved code quality and deployment reliability
- Quality of life improvements for development process

---

## 🎯 Success Metrics

**Automation Coverage**: 
- Phase 1: 70% of critical manual tasks automated
- Phase 2: 85% of routine tasks automated  
- Phase 3: 95% of repetitive tasks automated

**Time Savings**:
- Phase 1: 30+ minutes per development batch
- Phase 2: 45+ minutes per development batch
- Phase 3: 60+ minutes per development batch

**Error Rate Reduction**:
- Setup failures: 80% reduction
- Integration conflicts: 70% reduction  
- Quality gate failures: 60% reduction

**Developer Experience**:
- Consistent workflows across all Claude instances
- Reduced cognitive load and manual task overhead
- Improved focus on high-value development activities

---

*This manifest is maintained by the Planning Claude and updated as new commands are implemented and workflows evolve.*