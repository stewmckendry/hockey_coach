---
description: "Close a GitHub issue with delivery summary and implementation details"
argument-hint: "[github-issue-url]"
allowed-tools: ["Read", "Write", "Edit", "MultiEdit", "Bash", "Glob", "Grep", "WebFetch", "TodoWrite", "Task"]
---

# Close GitHub Issue with Delivery Summary

You are tasked with closing a GitHub issue by creating a comprehensive delivery summary and posting it as a comment before closing the issue.

## 📋 WORKFLOW STEPS

### Phase 1: Issue Identification and Context Gathering
**🔍 Determine the GitHub issue to close:**

1. **Check for Provided URL**: If `$ARGUMENTS` contains a GitHub issue URL, use that as the target issue
2. **Session Context Analysis**: If no URL provided, analyze the current conversation to identify:
   - Any GitHub issue URLs mentioned in the session
   - Issues that were being worked on during this session
   - The primary issue that was implemented or resolved
3. **Confirm Target Issue**: Present the identified issue URL to the user for confirmation
4. **Fetch Issue Details**: Use WebFetch to retrieve the current issue details and requirements

### Phase 2: Implementation Analysis and Documentation
**📝 Analyze what was delivered in this session:**

1. **Session Review**: Review the conversation history to identify:
   - All code changes made during the session
   - Files that were created, modified, or deleted
   - Tests that were written or updated
   - Documentation that was added or changed
   - Any configuration or setup changes
   - Dependencies that were added or updated

2. **Deliverable Categorization**: Organize the work into clear categories:
   - **Core Implementation**: Main feature/fix code changes
   - **Testing**: Unit tests, integration tests, test data
   - **Documentation**: README updates, inline comments, guides
   - **Configuration**: Config files, environment setup, dependencies
   - **Refactoring**: Code improvements, cleanup, optimization
   - **Bug Fixes**: Issues resolved during implementation

3. **Impact Assessment**: Document:
   - What functionality was added or changed
   - What problems were solved
   - Any breaking changes introduced
   - Performance or security improvements
   - User-facing changes

### Phase 3: Delivery Summary Creation
**📋 Create comprehensive markdown delivery report:**

Create a markdown file named `delivery-summary-issue-[issue-number].md` with the following structure:

```markdown
# Delivery Summary - Issue #[issue-number]

**Issue**: [Issue Title]
**URL**: [GitHub Issue URL]
**Completed**: [Current Date/Time]
**Session Duration**: [Estimated based on conversation]

## 🎯 Requirements Fulfilled

[List each requirement from the original issue and how it was addressed]

## 📦 Deliverables

### Core Implementation
- [List all main code files and changes]
- [Include brief description of each change]

### Testing
- [List test files and test cases added]
- [Note test coverage improvements]

### Documentation  
- [List documentation updates]
- [Note any README or guide changes]

### Configuration & Setup
- [List config changes, dependencies, etc.]

## 🔧 Technical Details

### Files Modified
```
[List all files that were changed with brief descriptions]
```

### New Dependencies
- [List any new packages or libraries added]

### Breaking Changes
- [List any breaking changes, or "None" if no breaking changes]

## ✅ Quality Assurance

### Testing Status
- [ ] Unit tests written/updated
- [ ] Integration tests written/updated  
- [ ] Manual testing completed
- [ ] Existing tests still pass

### Code Quality
- [ ] Follows project coding standards
- [ ] Code reviewed and optimized
- [ ] No security vulnerabilities introduced
- [ ] Performance impact assessed

### Documentation
- [ ] Code properly commented
- [ ] README updated if needed
- [ ] API documentation updated if applicable
- [ ] CLAUDE.md updated if applicable

## 🚀 Next Steps & Recommendations

[Any suggestions for follow-up work, monitoring, or improvements]

## 📊 Session Statistics

- **Files Modified**: [Number]
- **Lines Added**: [Estimate based on changes]
- **Tests Added**: [Number]  
- **Documentation Updates**: [Number]

---

*This summary was generated automatically by Claude Code upon issue completion.*
```

### Phase 4: GitHub Integration
**🔗 Post summary and close issue:**

1. **Present Summary**: Show the user the complete delivery summary for review
2. **User Approval**: Ask for user confirmation:
   - "Does this delivery summary accurately reflect what was accomplished?"
   - "Should I post this summary as a comment and close the issue?"
   - "Any additions or modifications needed?"

3. **GitHub Actions** (Note: Claude Code cannot directly interact with GitHub API, so provide instructions):
   - **For User to Execute**: Provide the exact steps for the user to:
     - Copy the delivery summary
     - Post it as a comment on the GitHub issue
     - Close the issue
   - **Alternative**: If the user has GitHub CLI configured, provide the exact `gh` commands to:
     - Add the comment: `gh issue comment [issue-number] --body-file delivery-summary-issue-[issue-number].md`
     - Close the issue: `gh issue close [issue-number] --comment "Implementation completed. See delivery summary above."`

### Phase 5: Cleanup and Archival
**🗂️ Organize delivery documentation:**

1. **Save Delivery Summary**: Store the markdown file in an appropriate location:
   - `docs/delivery-summaries/` (if exists)
   - `issues/completed/` (if exists)  
   - Project root with clear naming

2. **Update Project Records**: If the project maintains:
   - A changelog, suggest adding an entry
   - Issue tracking documentation, note the completion
   - Release notes, mention the feature/fix

## 🚨 IMPORTANT NOTES

- **Session Context Awareness**: This command works best when used in the same session where implementation occurred
- **Accuracy First**: Ensure the delivery summary accurately reflects what was actually completed
- **User Confirmation**: Always get user approval before any GitHub actions
- **GitHub Limitations**: Claude Code cannot directly modify GitHub issues - provide clear instructions for user actions
- **Documentation Quality**: The delivery summary should be professional and comprehensive enough to serve as project documentation

## 📊 Success Criteria

Your task is complete when:
1. ✅ GitHub issue is correctly identified (from args or session context)
2. ✅ Comprehensive delivery summary is created
3. ✅ All work from the session is accurately documented
4. ✅ User has approved the summary
5. ✅ Clear instructions provided for GitHub actions
6. ✅ Delivery summary file is saved in appropriate location

---

**Begin by identifying the GitHub issue to close:**

**Arguments provided**: `$ARGUMENTS`

If no arguments provided, analyze the current session to identify the GitHub issue that was worked on and should be closed.