---
description: "Create a git worktree for a GitHub issue, create a branch, and add a comment linking the issue to the branch"
argument-hint: "<github-issue-url>"
allowed-tools: ["Bash", "WebFetch", "TodoWrite"]
---

# Git Worktree for GitHub Issue

You are tasked with setting up a git worktree for working on a GitHub issue. This workflow helps maintain clean branch separation and provides a dedicated workspace for each issue.

## 📋 WORKFLOW STEPS

### Phase 1: Parse and Validate Issue
1. **Extract Issue URL**: Parse the GitHub issue URL from `$ARGUMENTS`
2. **Validate URL Format**: Ensure it's a valid GitHub issue URL (format: `https://github.com/{owner}/{repo}/issues/{number}`)
3. **Extract Components**: Parse out owner, repo, and issue number from the URL

### Phase 2: Fetch Issue Details
1. **Use WebFetch**: Retrieve the GitHub issue to get:
   - Issue title
   - Issue number
   - Current status (ensure it's open)
   - Any existing branch references in comments

### Phase 3: Create Branch and Worktree
1. **Generate Branch Name**: Create a descriptive branch name following the pattern:
   - `issue-{number}-{sanitized-title}` (e.g., `issue-123-add-user-authentication`)
   - Sanitize title: lowercase, replace spaces with hyphens, remove special characters
   - Limit to reasonable length (max 50 chars after issue number)

2. **Check Existing Branches**: 
   ```bash
   git branch -a | grep -i "issue-{number}"
   ```
   If branch exists, ask user how to proceed

3. **Create New Branch**:
   ```bash
   git checkout -b issue-{number}-{sanitized-title}
   ```

4. **Create Worktree**:
   ```bash
   # Create worktree in a dedicated directory
   git worktree add ../thunder_playbook_worktrees/issue-{number} issue-{number}-{sanitized-title}
   ```

### Phase 4: Link Issue to Branch
1. **Create GitHub Comment**: Use gh CLI to add a comment to the issue:
   ```bash
   gh issue comment {issue-number} \
     --body "🌿 Created branch \`issue-{number}-{sanitized-title}\` and worktree for this issue.

   To work on this issue:
   \`\`\`bash
   cd ../thunder_playbook_worktrees/issue-{number}
   \`\`\`

   Branch: \`issue-{number}-{sanitized-title}\`
   Worktree: \`../thunder_playbook_worktrees/issue-{number}\`"
   ```

### Phase 5: Provide User Instructions
Print clear instructions for the user:

```
✅ Worktree Setup Complete!

📍 Issue: #{number} - {title}
🌿 Branch: issue-{number}-{sanitized-title}
📂 Worktree: ../thunder_playbook_worktrees/issue-{number}

To start working on this issue:
1. Open a new terminal/Claude session
2. Navigate to worktree:
   cd ../thunder_playbook_worktrees/issue-{number}

3. Work on the issue in the worktree
4. Commit changes as usual
5. When done, push the branch:
   git push -u origin issue-{number}-{sanitized-title}

To remove worktree when done:
   git worktree remove ../thunder_playbook_worktrees/issue-{number}

GitHub issue has been updated with branch information.
```

## 🚨 ERROR HANDLING

Handle these common scenarios:
- **Invalid URL**: Provide clear error message about expected format
- **Issue Not Found**: Check if issue exists and is accessible
- **Branch Already Exists**: Ask user if they want to use existing branch or create new one
- **Worktree Already Exists**: Inform user and provide options
- **No gh CLI**: Provide alternative using curl for API calls
- **Permission Issues**: Handle cases where user can't comment on issue

## 📊 Success Criteria
✅ Valid GitHub issue URL parsed
✅ Issue details fetched successfully
✅ Branch created with descriptive name
✅ Worktree created in organized location
✅ GitHub issue updated with branch reference
✅ Clear instructions provided to user

---

**Now begin by parsing the GitHub issue URL from arguments:**

Issue URL: `$ARGUMENTS`