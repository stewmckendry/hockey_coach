---
description: "Publish final content pages by validating quality, updating metadata, and providing sharing instructions"
argument-hint: "<final-page-url> [sharing-scope] [announcement-message]"
allowed-tools: ["mcp__notion-remote__search", "mcp__notion-remote__fetch", "mcp__notion-remote__update-page", "mcp__notion-remote__update-database", "Read", "TodoWrite"]
---

# Publish Page Command

Validates final coaching content, updates page metadata to indicate published status, and provides clear instructions for manual sharing configuration in Notion.

## Sharing Scope Options

Optional sharing scope parameter (for documentation and instructions):
- **`team`** (default) - Share with team members only
- **`organization`** - Share within league/organization
- **`public`** - Make publicly accessible to all
- **`unlisted`** - Accessible via link only

**Note**: Actual sharing must be configured manually in Notion due to API limitations. This command will provide step-by-step instructions.

## Publishing Workflow

### Step 1: Content Validation
- Parse final page URL from arguments
- Verify page type is "Final" (not Draft or Research)
- Fetch page content and metadata
- Run quality assurance checks
- Verify team context if applicable

**Error Handling:**
```
If page not found:
  "Page not found at provided URL.
   
   Please verify the URL or search Content Library for final pages:
   - Page Type: 'Final'
   - Status: Ready for publishing"

If not final version:
  "This page appears to be a [Page Type] page, not a final version.
   
   Publishing workflow requires:
   1. Research page → /research-hockey
   2. Draft page → /draft-content
   3. Final page → /edit-content
   4. Publishing → /publish-page (current step)
   
   Please complete editing first with /edit-content"

If already published:
  "This page is already published.
   Last published: [date]
   
   Would you like to:
   1. Update publication metadata
   2. Generate new sharing instructions
   3. Cancel"
```

**Version Management:**
```
Before publishing:
  1. Always fetch latest version with mcp__notion-remote__fetch
  2. Verify no recent edits since final version created
  3. If modified after finalization:
     "Page has been modified since final version created.
      Last edit: [timestamp]
      
      Recommend running /edit-content again to ensure quality."
```

### Step 2: Pre-Publication Checklist
**Quality Validation:**
```
Content Completeness:
□ All sections have substantial content
□ No placeholder text remaining
□ Visual descriptions included
□ Safety sections complete
□ Resources properly linked

Technical Accuracy:
□ Hockey terminology correct
□ Drill instructions clear
□ Safety guidance accurate
□ Progressions logical
□ Age-appropriate content

UX Compliance:
□ Visual ratio appropriate
□ Language tier correct
□ Positive tone throughout
□ Engagement elements present
□ Attention span considered

Legal/Ethical:
□ No copyrighted material
□ Safety warnings adequate
□ Age-appropriate only
□ No personal information
□ Team privacy respected
```

### Step 3: Update Page Metadata
**Using mcp__notion-remote__update-page:**
Add publication information to the page:
```
## 📢 Publication Status
- **Status**: Published ✅
- **Published Date**: [Current date]
- **Intended Sharing**: [Sharing scope]
- **Version**: 1.0
- **Quality Validated**: Yes

## 📤 Sharing Configuration Required
This page is ready for sharing. Please follow the manual steps below
to configure sharing in Notion.
```

### Step 4: Update Content Library Database
**Using mcp__notion-remote__update-database:**
Update the Content Library entry:
- Page Type: "Published"
- Sharing Scope: [Selected scope]
- Publication Date: [Timestamp]
- Version Number: 1.0
- Quality Validated: ✓
- Published Status: True

**Database Update Error Handling:**
```
If Content Library entry not found:
  "Warning: No Content Library entry found for this page.
   
   Page will be marked as published but not tracked.
   Consider manually adding to Content Library."

If database update fails:
  "Unable to update Content Library.
   Error: [specific error]
   
   Page metadata has been updated.
   Manual Content Library update recommended."

If version conflict:
  "Multiple versions found in Content Library:
   - Draft version: [date]
   - Final version: [date]
   
   Updating most recent entry to Published status."
```

### Step 5: Generate Sharing Instructions
**Provide Clear Manual Steps:**
Based on sharing scope, generate specific instructions:

**For Team Sharing:**
```
## 🔒 Team Sharing Instructions

1. Click "Share" button in top-right of this page
2. Ensure your team workspace is selected
3. Set permissions to "Can view"
4. Enable "Allow comments" for feedback
5. Click "Copy link" to share with team

✅ Your team can now access this resource!
```

**For Organization Sharing:**
```
## 🏢 Organization Sharing Instructions

1. Click "Share" button in top-right of this page
2. Add your organization workspace
3. Set permissions to "Can view"
4. Enable "Allow duplicate as template"
5. Click "Copy link" for organization newsletter

Consider adding to organization's coaching library.
```

**For Public Sharing:**
```
## 🌐 Public Sharing Instructions

1. Click "Share" button in top-right of this page
2. Toggle "Share to web" to ON
3. Enable "Allow duplicate as template"
4. Enable "Search engine indexing" (optional)
5. Copy the public link

⚠️ Important: Review content one final time before making public
✅ Anyone with the link can now view this resource
```

**For Unlisted Sharing:**
```
## 🔗 Unlisted Sharing Instructions

1. Click "Share" button in top-right of this page
2. Toggle "Share to web" to ON
3. Disable "Search engine indexing"
4. Copy the link to share privately

Only people with the link can access this page.
```

### Step 6: Create Announcement Content
If announcement message provided, format it appropriately:

**Formatted Announcement:**
```
## 📣 Ready to Share!

Your announcement message:
"[User's announcement message]"

Suggested sharing text:
---
[Formatted announcement based on scope]
Page link: [Instructions to copy from Share menu]
---

Copy this text after configuring sharing!
```

## Implementation Process

### Phase 1: Validation and Fetching
1. Fetch final page and verify it's not a draft
2. Run through all quality checklists
3. Identify any blocking issues
4. Confirm page is ready for publication
5. Create TodoWrite tracking for process

### Phase 2: Metadata Updates
6. **Always fetch latest page version first**
7. Use `mcp__notion-remote__update-page` to add publication status
8. Add publication metadata section to page
9. Include version information
10. Add quality validation confirmation
11. Include sharing instructions section

**Page Update Error Handling:**
```
If update-page fails:
  "Unable to add publication metadata to page.
   Error: [specific error]
   
   Manual steps required:
   1. Add '📢 Publication Status' section
   2. Mark status as 'Published ✅'
   3. Add publication date
   4. Follow sharing instructions below"
```

### Phase 3: Database Updates
11. Fetch Content Library entry for the page
12. Use `mcp__notion-remote__update-database` to update status
13. Set Page Type to "Published"
14. Add publication timestamp
15. Record intended sharing scope

### Phase 4: Instructions Generation
16. Generate detailed sharing instructions based on scope
17. Add visual indicators (emojis) for clarity
18. Include step-by-step Notion UI guidance
19. Add warnings or considerations as needed
20. Format announcement if provided

### Phase 5: Final Summary
21. Provide clear success confirmation
22. Summarize what was updated
23. Highlight manual steps required
24. Include announcement text if applicable
25. Remind user to complete Notion sharing

## Error Handling

### Not Final Version
```
"This page appears to be a draft or research page.
 Page Type: [Current type]
 
 Please complete the editing process first:
 1. Use /edit-content to create final version
 2. Then use /publish-page on the final version"
```

### Quality Issues Found
```
"Quality check found issues:
 - [Issue 1]
 - [Issue 2]
 
 Please address these before publishing:
 1. Use /edit-content to fix issues
 2. Re-run /publish-page after corrections"
```

### API Limitations Notice
```
"✅ Page prepared for publishing!

⚠️ Note: Due to Notion API limitations, sharing settings 
must be configured manually. Detailed instructions have 
been added to the page.

Please open the page and follow the sharing instructions."
```

### Sharing Scope Issues
```
If invalid sharing scope:
  "Invalid sharing scope '[input]'.
   
   Valid options:
   - team (default): Team members only
   - organization: League/organization wide
   - public: Publicly accessible
   - unlisted: Link-only access
   
   Using default: team"
```

### Network/Connection Errors
```
If Notion connection fails:
  "Unable to connect to Notion.
   Error: [specific error]
   
   Please check:
   - Internet connection
   - Notion service status
   - API token validity
   
   Retry with /publish-page when resolved."
```

## Success Criteria

- ✅ Content quality validated against all checklists
- ✅ Age-appropriate and safe content confirmed
- ✅ Publication metadata added to page via update-page
- ✅ Content Library database updated with published status
- ✅ Clear manual sharing instructions provided
- ✅ Privacy and safety requirements verified
- ✅ Announcement formatted if requested
- ✅ User knows exactly what manual steps to take

## Final Output Format

```
✅ Publishing Complete!

Page: [Title]
Status: Published
Quality: Validated

📋 Completed Actions:
- Content quality validated
- Publication metadata added to page
- Content Library updated
- Sharing instructions added to page

⚠️ Required Manual Steps:
1. Open the page in Notion
2. Follow the [sharing scope] sharing instructions at the bottom
3. Configure sharing settings as directed
4. Copy announcement text if provided

🔗 Open page to complete sharing: [page URL]
```

## Example Usage

```bash
# Publish to team only (default)
/publish-page https://notion.so/final-page-url

# Publish to organization
/publish-page [final-url] organization

# Publish publicly with announcement
/publish-page [final-url] public "New U12 goalie training resource available!"

# Publish as unlisted (link-only access)
/publish-page [final-url] unlisted

# Team publish with announcement
/publish-page [final-url] team "New practice plan for Thursday available"
```

The publish-page command validates content quality, updates all metadata to indicate published status, and provides clear instructions for manual sharing configuration in Notion, working within API limitations while ensuring a smooth publishing workflow.