---
description: "Commit worktree changes, create PR, and update GitHub issue"
argument-hint: "<github-issue-url> [branch-name]"
allowed-tools: ["Bash", "WebFetch", "TodoWrite"]
---

# Commit Worktree and Create Pull Request

You are tasked with committing changes in a git worktree, creating a pull request, and updating the associated GitHub issue. This completes the implementation phase of the worktree workflow.

## 📋 WORKFLOW STEPS

### Phase 1: Parse Arguments and Validate State
1. **Extract Arguments**: 
   - GitHub issue URL from `$ARGUMENTS` (required)
   - Branch name (optional - can be derived from issue number)
2. **Validate URL Format**: Ensure valid GitHub issue URL
3. **Extract Components**: Parse owner, repo, and issue number
4. **Determine Branch**: Use provided branch name or default to `issue-{number}-*`

### Phase 2: Locate and Validate Worktree
1. **Find Worktree**:
   ```bash
   # Check standard location first
   cd ../thunder_playbook_worktrees/issue-{number}
   
   # Or find by branch if provided
   git worktree list | grep "{branch-name}"
   ```

2. **Validate State**:
   - Ensure we're in correct worktree
   - Check for uncommitted changes
   - Verify branch matches expected pattern

### Phase 3: Quality Checks (if applicable)
1. **Run Tests** (if test commands exist):
   ```bash
   # Python tests
   python -m pytest tests/ -v
   
   # Web app tests
   npm run lint
   npm run type-check
   npm run build
   ```

2. **Check for Issues**:
   - Stop if tests fail
   - Report any linting errors
   - Ensure build succeeds

### Phase 4: Commit Changes
1. **Stage All Changes**:
   ```bash
   git add -A
   ```

2. **Create Commit**:
   ```bash
   git commit -m "feat: Implement #{issue-number} - {issue-title}

   - {list key changes}
   - {mention any important decisions}
   
   Closes #{issue-number}"
   ```

3. **Push Branch**:
   ```bash
   git push -u origin {branch-name}
   ```

### Phase 5: Create Pull Request
1. **Create PR with gh CLI**:
   ```bash
   gh pr create \
     --title "feat: #{issue-number} - {issue-title}" \
     --body "## Summary
   
   Implements #{issue-number}: {brief description}
   
   ## Changes
   - {list of key changes}
   
   ## Testing
   - [ ] All tests pass
   - [ ] Manual testing completed
   - [ ] No console errors
   
   ## Screenshots (if UI changes)
   {attach any relevant screenshots}
   
   Closes #{issue-number}" \
     --base main
   ```

2. **Capture PR URL**: Store the created PR URL for reference

### Phase 6: Update GitHub Issue
1. **Add Implementation Comment**:
   ```bash
   gh issue comment {issue-number} \
     --body "🚀 Implementation complete!
   
   **Pull Request**: {pr-url}
   **Branch**: \`{branch-name}\`
   
   ## Summary of Changes:
   {brief summary of what was implemented}
   
   The PR is ready for review. Once approved and merged, this issue will be automatically closed."
   ```

### Phase 7: Clean Up and Provide Instructions
1. **Return to Main Directory**:
   ```bash
   cd {main-repo-path}
   ```

2. **Provide User Instructions**:
   ```
   ✅ PR Created Successfully!
   
   📍 Issue: #{number} - {title}
   🔗 Pull Request: {pr-url}
   🌿 Branch: {branch-name}
   
   Next Steps:
   1. Review PR at: {pr-url}
   2. Request reviews from team members
   3. Address any feedback
   4. Once approved, use /merge-worktree to complete
   
   The worktree remains active for addressing PR feedback.
   ```

## 🚨 ERROR HANDLING

Handle these scenarios:
- **No Worktree Found**: Provide clear error about missing worktree
- **Uncommitted Changes**: Offer to stash or commit changes
- **Tests Failing**: Stop and report which tests failed
- **Push Conflicts**: Guide through rebase if needed
- **PR Creation Failed**: Provide manual PR creation instructions
- **No gh CLI**: Provide git push instructions and PR creation URL

## 📊 Success Criteria
✅ All changes committed with descriptive message
✅ Branch pushed to remote
✅ Pull request created with proper description
✅ GitHub issue updated with PR link
✅ Clear next steps provided
✅ Worktree kept active for PR feedback

## 🔧 Advanced Options
- **Skip Tests**: Add `--skip-tests` flag if needed
- **Draft PR**: Add `--draft` flag for work in progress
- **Custom Base**: Specify different base branch if needed

---

**Now begin by parsing arguments and validating the worktree state:**

Arguments: `$ARGUMENTS`