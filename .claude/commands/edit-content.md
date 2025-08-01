---
description: "Edit draft content pages by applying user feedback and UX Guidelines improvements to create polished final versions"
argument-hint: "<draft-page-url> <user-feedback>"
allowed-tools: ["mcp__notion-remote__search", "mcp__notion-remote__fetch", "mcp__notion-remote__create-pages", "mcp__notion-remote__update-page", "mcp__notion-remote__update-database", "Read", "TodoWrite"]
---

# Edit Content Command

Transforms draft coaching content into polished, publication-ready pages by applying user-provided feedback and UX Guidelines improvements to ensure age-appropriate, high-quality coaching materials.

## User Feedback Integration

The primary purpose of this command is to incorporate specific user feedback into the draft content. User feedback takes priority and guides all editing decisions.

### Types of User Feedback
- **Content corrections**: "Add more detail about defensive positioning"
- **Safety concerns**: "Emphasize helmet requirements in the safety section"
- **Clarity improvements**: "Simplify the passing drill instructions for beginners"
- **Missing elements**: "Include a warm-up section before the main drills"
- **Team-specific needs**: "Adapt for half-ice practice format"
- **Visual requests**: "Add more diagram descriptions for the breakout play"
- **Progression adjustments**: "Make the advanced variations more challenging"

## Editing Workflow

### Step 1: Parse Feedback and Analyze Draft
- Extract draft page URL and user feedback from arguments
- Parse user feedback to identify specific edit requirements
- Fetch the draft page content and metadata
- Create a checklist of requested changes
- Identify age group and team context

**Error Handling:**
```
If draft page not found:
  "Draft page not found at provided URL.
   
   Please verify the URL or search Content Library for drafts:
   - Page Type: 'Draft'
   - Topic: '[inferred topic]'"

If arguments missing:
  "Missing required arguments.
   
   Usage: /edit-content <draft-page-url> <user-feedback>
   
   Example: /edit-content https://notion.so/draft-url 'Add warm-up section and simplify drill 2'"

If draft fetch fails:
  "Unable to access draft page.
   Error: [specific error]
   
   Please verify:
   - URL is correct
   - Page is a draft (not final/published)
   - You have access permissions"
```

**Version Management:**
```
Before editing:
  1. Always fetch latest draft version with mcp__notion-remote__fetch
  2. Check last_edited timestamp
  3. If recently modified:
     "Draft was recently updated.
      Last modified: [timestamp]
      
      Proceeding with latest version."
  4. Store original draft content for comparison
```

### Step 2: Prioritized Edit Planning
**Edit Priority Order:**
1. **User-requested changes** (highest priority)
2. **Safety enhancements** (if mentioned in feedback)
3. **Clarity improvements** (based on feedback)
4. **UX Guidelines compliance** (supporting edits)
5. **General polish** (final touches)

### Step 3: Apply User Feedback
**Feedback Implementation Process:**
```
For each piece of user feedback:
1. Locate relevant section in draft
2. Implement requested change
3. Ensure change maintains age-appropriateness
4. Verify safety considerations
5. Document what was changed
```

### Step 4: UX Guidelines Enhancement
After implementing user feedback, apply UX improvements:

**Age-Appropriate Adjustments:**
- Verify visual-text ratios still meet standards
- Ensure terminology remains age-appropriate
- Check attention span considerations
- Validate safety prominence
- Maintain engagement elements

### Step 5: Create Final Version
**Final Page Structure:**
```
# [Topic] for [Age Group]

[Content with all user feedback incorporated]
[UX Guidelines improvements applied]
[Safety considerations verified]
[Age-appropriate presentation confirmed]

## What's Changed
[Summary of edits made based on user feedback]
- [Specific change 1]
- [Specific change 2]
- [Enhancement 3]

---
*Edited from draft: [Draft page link]*
*Version: Final*
*User feedback applied: "[Feedback summary]"*
```

## Feedback-Driven Enhancements

### Content Modifications
**Based on user feedback, may include:**
- Adding new sections or drills
- Removing unnecessary complexity
- Enhancing specific explanations
- Adjusting difficulty levels
- Incorporating team-specific adaptations
- Strengthening safety protocols
- Improving visual descriptions

### Structural Changes
**If requested by user:**
- Reordering sections for better flow
- Combining or splitting activities
- Adding transition elements
- Creating new subsections
- Adjusting time allocations
- Modifying progression sequences

### Team-Specific Adaptations
**When feedback mentions team needs:**
- Equipment availability adjustments
- Ice time format modifications
- Player count considerations
- Skill level adaptations
- Coaching philosophy alignment
- Practice duration optimization

## Implementation Process

### Phase 1: Feedback Analysis
1. Parse user feedback into actionable items
2. Categorize feedback by type and priority
3. Fetch draft page and analyze current content
4. Create detailed editing plan
5. Set up TodoWrite for tracking changes

### Phase 2: User Feedback Implementation
6. Apply each feedback item systematically
7. Ensure changes maintain content coherence
8. Verify age-appropriateness after each change
9. Document all modifications made
10. Cross-check against original feedback

### Phase 3: UX Guidelines Compliance
11. Review visual-text ratios
12. Verify terminology appropriateness
13. Check safety visibility
14. Ensure positive tone
15. Validate attention span considerations

### Phase 4: Final Creation and Documentation
16. Create new page with all edits applied
17. Remove "Draft" suffix from title
18. Add change summary section
19. Link to original draft
20. Update Content Library database entry:
    - Search for draft page entry
    - Create new entry for final page with Page Type: "Final"
    - Link to draft version and original research
    - Add user feedback summary in Change Notes
    - Set UX Guidelines Compliant: True

**Final Page Creation Error Handling:**
```
If final page creation fails:
  "Error creating final version.
   Error: [specific error]
   
   Edited content prepared. Options:
   1. Retry page creation
   2. Update draft page instead
   3. Save content locally"

If Content Library update fails:
  "Final page created but not tracked in Content Library.
   
   Final page URL: [final-page-url]
   Draft page URL: [draft-page-url]
   
   Manual tracking recommended."

If duplicate final exists:
  "A final version already exists for this content:
   '[Existing title]' created on [date]
   
   Options:
   1. Create new version (v2)
   2. Update existing final
   3. View existing final"
```

**Version Control Best Practices:**
```
When creating final version:
  1. Always create new page (don't overwrite draft)
  2. Preserve draft for version history
  3. Link final → draft → research chain
  4. Include edit timestamp
  5. Document all changes made
  6. Store user feedback in metadata
```

### Phase 5: Quality Verification
21. Confirm all user feedback addressed
22. Verify UX Guidelines compliance
23. Check content accuracy and safety
24. Validate age-appropriate presentation
25. Mark as ready for publishing

## Change Documentation

### Edit Summary Format
```
## Changes Made in This Version

### User-Requested Changes:
✓ [Feedback item 1]: [How it was addressed]
✓ [Feedback item 2]: [Implementation details]
✓ [Feedback item 3]: [Specific modifications]

### Additional Improvements:
- Enhanced safety visibility in [section]
- Clarified instructions for [activity]
- Added visual descriptions for [concept]
- Improved age-appropriate language throughout

### UX Guidelines Compliance:
- Visual ratio: [Percentage] (meets [age group] standard)
- Terminology: Tier [X] vocabulary applied
- Safety: Prominently featured in [X] sections
- Engagement: Added [specific elements]
```

## Error Handling

### Unclear Feedback
```
"User feedback needs clarification:
 '[Ambiguous feedback]'
 
 Could mean:
 1. [Interpretation 1]
 2. [Interpretation 2]
 
 Proceeding with most likely interpretation.
 Please review changes carefully."
```

### Conflicting Requirements
```
"User feedback conflicts with age-group standards:
 Requested: '[Specific request]'
 Concern: [Age-appropriateness issue]
 
 Applying modified version that maintains safety
 and age-appropriate presentation."
```

### Safety Override
```
"User feedback may compromise safety:
 Requested: '[Specific request]'
 Safety concern: [Specific issue]
 
 Implementing alternative that maintains safety standards.
 Safety cannot be compromised in youth coaching content."
```

### Team Context Issues
```
If team context unavailable:
  "Unable to retrieve team context.
   
   Applying general [age-group] standards.
   Team-specific elements may need manual adjustment."
```

## Success Criteria

- ✅ All user feedback items addressed and implemented
- ✅ Changes documented clearly in final version
- ✅ UX Guidelines compliance maintained
- ✅ Age-appropriate presentation preserved
- ✅ Safety considerations enhanced where needed
- ✅ Final page created with professional polish
- ✅ Content Library updated with version tracking
- ✅ Clear audit trail from draft to final
- ✅ Ready for publishing workflow

## Workflow Integration

**Research → Draft → Edit → Publish Flow:**
```
1. /research-hockey "breakout plays" U10
   → Creates research page

2. /draft-content [research-url] "Lightning"
   → Creates: "Breakout Plays for U10 - Draft"

3. /edit-content [draft-url] "Add more beginner options and emphasize 
   the importance of head-up skating. Also need clearer diagrams for 
   the 2-1-2 formation. Make it work for half-ice practice too."
   → Creates: "Breakout Plays for U10"
   → Implements all requested changes
   → Documents modifications

4. /publish-page [final-url]
   → Makes content publicly available
```

## Example Usage

```bash
# Edit with specific content feedback
/edit-content https://notion.so/draft-url "Add warm-up section and make drill 2 easier for beginners"

# Edit with safety concerns
/edit-content [draft-url] "Emphasize proper checking technique and add more safety warnings"

# Edit with team-specific needs
/edit-content [draft-url] "Adapt all drills for 12 players and half-ice format"

# Edit with multiple improvements
/edit-content [draft-url] "Simplify language for younger players, add more fun elements, and include a cool-down section"

# Edit with visual enhancement request
/edit-content [draft-url] "Need better descriptions of player positioning and movement patterns"
```

The edit-content command transforms drafts into polished final versions by prioritizing user feedback while ensuring UX Guidelines compliance and maintaining age-appropriate, safe coaching content.