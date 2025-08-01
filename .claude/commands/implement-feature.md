---
description: "Implement a feature from a GitHub issue URL with comprehensive planning and validation"
argument-hint: "<primary-issue-url> [related-issue-url-1] [related-issue-url-2] ..."
allowed-tools: ["Read", "Write", "Edit", "MultiEdit", "Bash", "Glob", "Grep", "WebFetch", "TodoWrite", "Task"]
---

# Feature Implementation from GitHub Issue

You are tasked with implementing a feature based on a GitHub issue. Follow this comprehensive workflow to ensure high-quality, well-tested, and properly documented implementation.

**Note**: Not all steps may be applicable depending on the scope and nature of the issue. Apply these steps as relevant to the specific feature being implemented.

## 📋 CRITICAL WORKFLOW STEPS

### Phase 1: Deep Analysis and Planning
**🧠 THINK ULTRA HARD about implementation approach:**

1. **Parse Arguments**: Extract primary issue URL and related issue URLs from: `$ARGUMENTS`
2. **Fetch and Analyze Primary Issue**: Use WebFetch to retrieve the main GitHub issue
3. **Fetch Related Issues**: Use WebFetch to retrieve all related GitHub issues for additional context
4. **Analyze Issue Comments**: Review all comments on the primary issue for:
   - Implementation updates and progress
   - Clarifications or requirement changes
   - Technical decisions made during discussion
   - Dependencies or blockers identified
   - Completed work that impacts implementation approach
5. **Cross-Reference Analysis**: Identify dependencies, conflicts, or complementary requirements across all issues
6. **Understand Requirements**: Parse issue descriptions, acceptance criteria, comments, and any linked discussions
7. **Architecture Planning**: Consider how this feature fits into the existing codebase structure
8. **Risk Assessment**: Identify potential challenges, breaking changes, and edge cases
9. **Create Comprehensive Todo List**: Use TodoWrite to break down EVERY step needed (as applicable):
   - Code changes required
   - Tests to write/update
   - Documentation to create/update
   - Dependencies to install
   - Configuration changes
   - Database migrations (if needed)
   - Performance considerations
   - Security implications

### Phase 2: User Validation (MANDATORY PAUSE)
**⏸️ PAUSE and validate assumptions with the user:**

Before implementing anything, present your analysis and ask:
- "Does this implementation approach align with your expectations?"
- "Are there any constraints or preferences I should consider?"
- "Have I missed any requirements or edge cases?"
- "Should I proceed with this plan, or would you like modifications?"

**Wait for explicit user approval before proceeding.**

### Phase 3: Implementation
**📝 Follow existing codebase patterns:**

1. **Explore Codebase**: Use Read, Glob, and Grep to understand:
   - Existing similar features
   - Code style and patterns
   - Directory structure
   - Testing approaches
   - Documentation standards

2. **Implement Incrementally**:
   - Start with core functionality
   - Follow established naming conventions
   - Use existing utilities and patterns
   - Maintain consistency with existing code style
   - Update TodoWrite progress as you complete each step

3. **Security First** (if applicable):
   - Never expose secrets or sensitive data
   - Follow security best practices
   - Validate all inputs
   - Handle errors gracefully

### Phase 4: Testing (NON-NEGOTIABLE - if tests exist in project)
**🧪 Comprehensive testing as applicable:**

1. **Write Tests** (if project has testing infrastructure):
   - Unit tests for individual functions
   - Integration tests for feature workflows
   - End-to-end tests for user journeys
   - Edge case testing
   - Error handling validation
2. **Run Existing Tests**: Ensure no regressions (if test suite exists)
3. **Check for Test Coverage**: Aim for comprehensive coverage of new code
4. **Manual Testing**: Test the feature in realistic scenarios

### Phase 5: Documentation (as applicable)
**📚 Update relevant documentation:**

1. **Code Documentation** (if complex logic):
   - Clear comments for complex logic
   - Function/class docstrings
   - API documentation (if applicable)

2. **User Documentation** (if user-facing changes):
   - README updates (if feature affects setup/usage)
   - User guide updates
   - API documentation
   - Migration guides (if breaking changes)

3. **Developer Documentation** (if significant architectural changes):
   - Architecture decision records
   - Development setup changes
   - Troubleshooting guides

### Phase 6: CLAUDE.md Updates (if applicable)
**📝 Update CLAUDE.md when relevant:**

Consider updating CLAUDE.md if your implementation:
- Adds new build/test commands
- Changes development workflow
- Introduces new dependencies
- Modifies project structure
- Adds new conventions or patterns
- Creates new utility functions
- Changes environment setup requirements

### Phase 7: Final Quality Check
**✅ Pre-completion checklist (apply as relevant):**

- [ ] All todo items completed and marked as done
- [ ] Code follows existing patterns and conventions
- [ ] All tests pass (run linting and type checking if available)
- [ ] Documentation is comprehensive and accurate
- [ ] No secrets or sensitive data exposed
- [ ] Error handling is robust
- [ ] Performance impact considered
- [ ] Security implications addressed
- [ ] CLAUDE.md updated if needed

## 🚨 IMPORTANT REMINDERS

- **Scope Awareness**: Not every step applies to every issue - use judgment based on the feature's complexity and scope
- **Don't Rush**: Take time to understand the full scope before coding
- **Ask Questions**: Better to over-communicate than make assumptions
- **Follow Patterns**: Consistency with existing code is crucial
- **Test Appropriately**: Test according to project standards and feature complexity
- **Document Sensibly**: Focus on documentation that adds value
- **Security Matters**: Always consider security implications when applicable
- **Performance Counts**: Consider the impact of your changes

## 📊 Success Criteria
Your implementation is complete when:
1. ✅ Feature works as specified in the GitHub issue
2. ✅ All relevant tests pass (including existing tests)
3. ✅ Code follows project conventions
4. ✅ Appropriate documentation is updated
5. ✅ No security vulnerabilities introduced (if applicable)
6. ✅ Performance impact is acceptable
7. ✅ User has validated the approach and result

Remember: **Quality over speed**. Apply these steps thoughtfully based on the specific requirements and scope of the issue.

---

**Now begin with parsing arguments and fetching all GitHub issues:**

**Primary Issue URL**: (first argument from `$ARGUMENTS`)
**Related Issue URLs**: (any additional arguments from `$ARGUMENTS`)

Start by fetching and analyzing the primary issue, then review all related issues to understand the complete context and requirements.