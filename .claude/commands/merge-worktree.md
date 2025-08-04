---
description: "Review PR, merge changes, remove worktree, and close GitHub issue"
argument-hint: "<github-issue-url> <pr-url>"
allowed-tools: ["Bash", "WebFetch", "TodoWrite"]
---

# Merge Worktree and Complete Issue

You are tasked with completing the git worktree workflow by reviewing the PR, merging changes, cleaning up the worktree, and closing the GitHub issue. This is the final phase of the issue implementation workflow.

## 📋 WORKFLOW STEPS

### Phase 1: Parse Arguments and Fetch Details
1. **Extract Arguments**: 
   - GitHub issue URL (required)
   - Pull Request URL (required)
2. **Parse Components**: Extract owner, repo, issue number, and PR number
3. **Fetch PR Details**: Use gh CLI to get PR status and review state

### Phase 2: Validate PR State
1. **Check PR Status**:
   ```bash
   gh pr view {pr-url} --json state,reviews,checks,mergeable
   ```

2. **Validate Ready to Merge**:
   - PR is open (not already merged)
   - All checks passing
   - Has required approvals
   - No merge conflicts

3. **Review Summary**:
   ```bash
   gh pr checks {pr-url}
   gh pr review {pr-url}
   ```

### Phase 3: Handle Merge Conflicts (if any)
1. **Detect Conflicts**:
   ```bash
   # Navigate to worktree
   cd ../thunder_playbook_worktrees/issue-{number}
   
   # Update from main
   git fetch origin main
   git rebase origin/main
   ```

2. **Resolve Conflicts** (if present):
   - Guide user through conflict resolution
   - Ensure clean rebase
   - Force push if needed:
   ```bash
   git push --force-with-lease origin {branch-name}
   ```

3. **Wait for Checks**: Ensure all CI checks pass after conflict resolution

### Phase 4: Merge Pull Request
1. **Perform Merge**:
   ```bash
   # Squash and merge (preferred for feature branches)
   gh pr merge {pr-url} --squash --delete-branch
   
   # Or regular merge if preferred
   # gh pr merge {pr-url} --merge --delete-branch
   ```

2. **Confirm Merge**: Capture merge confirmation and commit SHA

### Phase 5: Clean Up Worktree
1. **Return to Main Repository**:
   ```bash
   cd {main-repo-path}
   ```

2. **Remove Worktree**:
   ```bash
   git worktree remove ../thunder_playbook_worktrees/issue-{number}
   ```

3. **Prune Worktree List**:
   ```bash
   git worktree prune
   ```

4. **Clean Up Local Branch** (if it exists):
   ```bash
   git branch -d {branch-name} 2>/dev/null || true
   ```

### Phase 6: Update and Close GitHub Issue
1. **Add Completion Comment**:
   ```bash
   gh issue comment {issue-number} \
     --body "✅ Issue completed and merged!
   
   **Merged PR**: {pr-url}
   **Merge Commit**: {merge-sha}
   
   ## Summary:
   {brief summary of what was implemented}
   
   The implementation has been successfully merged into main."
   ```

2. **Close Issue**:
   ```bash
   gh issue close {issue-number}
   ```

### Phase 7: Post-Merge Tasks
1. **Update Local Main**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Provide Completion Summary**:
   ```
   ✅ Issue Complete!
   
   📍 Issue: #{number} - {title} [CLOSED]
   🔗 Merged PR: {pr-url}
   📝 Merge Commit: {merge-sha}
   🧹 Worktree: Removed
   
   Summary:
   - PR successfully merged to main
   - Remote branch deleted
   - Local worktree cleaned up
   - GitHub issue closed
   
   Your local main branch has been updated with the changes.
   ```

## 🚨 ERROR HANDLING

Handle these scenarios:
- **PR Not Found**: Verify PR URL and accessibility
- **PR Not Approved**: List missing approvals and reviewers
- **Checks Failing**: Show which checks are failing
- **Merge Conflicts**: Guide through resolution process
- **Already Merged**: Detect and handle already-merged PRs
- **Worktree Issues**: Handle missing or locked worktrees
- **Permission Errors**: Handle cases where user can't merge

## 📊 Success Criteria
✅ PR reviews and checks validated
✅ Any conflicts resolved cleanly
✅ PR merged successfully
✅ Remote branch deleted
✅ Local worktree removed
✅ GitHub issue closed with summary
✅ Local main branch updated

## 🔧 Merge Options
The command supports different merge strategies:
- **Squash** (default): Combines all commits into one
- **Merge**: Preserves all commit history
- **Rebase**: Rebase and merge (if enabled in repo)

## ⚠️ Safety Checks
- Confirms PR is approved before merging
- Ensures all CI checks pass
- Validates no merge conflicts exist
- Preserves work if merge fails

---

**Now begin by parsing arguments and checking PR status:**

Arguments: `$ARGUMENTS`