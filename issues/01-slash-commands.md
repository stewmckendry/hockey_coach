# Issue 1: Claude Code Slash Commands System

## Overview
Create reusable Claude Code slash commands for streamlined hockey team content creation workflows. These commands will integrate with existing MCP servers (Notion, Exa, YouTube) to provide one-command solutions for common content tasks.

## Objectives
- Eliminate repetitive prompt patterns in content creation workflows
- Standardize content generation processes across team contexts
- Integrate multiple MCP servers seamlessly within single commands
- Provide guided workflows for complex multi-step processes

## Slash Commands to Implement

### `/setup-team`
**Purpose**: Initialize complete team context and Notion workspace setup

**Workflow**:
1. Prompt for team details (name, age group, skill level, philosophy, goals)
2. Create team context page in Notion with structured template
3. Set up content management database with appropriate properties
4. Create initial page templates customized for age group
5. Configure access permissions and sharing settings

**Example Usage**:
```bash
/setup-team
# Guided prompts:
# - Team name: Thunder U10 Sharks
# - Age group: U10 (9-10 years)
# - Skill level: Intermediate
# - Coaching philosophy: Skill development focused, fun-first approach
# - Season goals: Improve skating, basic passing, teamwork
```

**Expected Output**:
- Notion team context page with all details
- Content database ready for use
- Age-appropriate templates installed
- Public workspace URL for team access

### `/new-page <section> <type> [title]`
**Purpose**: Create structured Notion pages with appropriate templates

**Parameters**:
- `section`: fundamentals | systems | practice-plans | team-guide
- `type`: drill | concept | plan | guide | rules
- `title`: Optional custom title

**Workflow**:
1. Validate section and type combination
2. Load appropriate template for team's age group
3. Create Notion page with structured template
4. Add to content management database
5. Return page URL for editing

**Example Usage**:
```bash
/new-page fundamentals drill "Basic Skating Stops"
/new-page systems powerplay "2-1-2 Powerplay Setup"
/new-page practice-plans weekly "Week 3 - Passing Focus"
```

### `/draft-content <topic> [age-group]`
**Purpose**: Research and generate comprehensive content drafts using multiple sources

**Workflow**:
1. Search Thunder Playbook ChromaDB collections for relevant content
2. Use Exa web search for latest training methodologies
3. Search YouTube for appropriate instructional videos
4. Generate structured content combining all sources
5. Create Notion page with draft content
6. Apply UX guidelines for specified age group

**Example Usage**:
```bash
/draft-content "wrist shot technique" U10
/draft-content "forechecking systems" U12
/draft-content "skating stride development"  # Uses team's default age group
```

**Research Sources**:
- Thunder Playbook local data (ChromaDB collections)
- Exa web search for current best practices
- YouTube video search for visual demonstrations
- USA Hockey guidelines integration

### `/edit-content <page-url> "<feedback>"`
**Purpose**: Apply feedback and improvements to existing Notion content

**Workflow**:
1. Fetch existing Notion page content
2. Parse current structure and content
3. Apply requested changes maintaining template structure
4. Research additional sources if needed for improvements
5. Update Notion page with tracked changes
6. Maintain version history in content database

**Example Usage**:
```bash
/edit-content "https://thunder-u10.notion.site/skating-stops" "Add more beginner-friendly language and include safety tips"
/edit-content "https://thunder-u10.notion.site/powerplay" "Include diagram showing player positions and add common mistakes section"
```

### `/publish-page <page-url>`
**Purpose**: Optimize and publish Notion pages for team access

**Workflow**:
1. Load Notion page and validate content quality
2. Apply publishing checklist (UX guidelines compliance)
3. Optimize for mobile viewing and accessibility
4. Make page public with appropriate settings
5. Generate shareable URLs for different audiences
6. Update content tracking database with metrics

**Example Usage**:
```bash
/publish-page "https://notion.so/thunder-u10/skating-fundamentals"
# Output: 
# ✅ Published: https://thunder-u10.notion.site/skating-fundamentals
# 📱 Mobile optimized
# 🔗 Shareable links:
#   - Players: https://thunder-u10.notion.site/skating-fundamentals?view=player
#   - Parents: https://thunder-u10.notion.site/skating-fundamentals?view=parent
#   - Coaches: https://thunder-u10.notion.site/skating-fundamentals?view=coach
```

### `/research-hockey <query> [focus]`
**Purpose**: Comprehensive hockey research combining multiple sources

**Parameters**:
- `query`: Research topic or question
- `focus`: Optional focus area (drills | tactics | development | equipment)

**Workflow**:
1. Search Thunder Playbook ChromaDB for existing knowledge
2. Exa web search for latest research and methodologies
3. YouTube search for instructional content
4. Compile structured research report
5. Provide source citations and recommendations

**Example Usage**:
```bash
/research-hockey "improving backward skating" drills
/research-hockey "youth hockey nutrition guidelines"
/research-hockey "goalie development U10"
```

## Technical Implementation

### Command Storage Structure
```
~/.claude/commands/hockey/
├── setup-team.py
├── new-page.py
├── draft-content.py
├── edit-content.py
├── publish-page.py
└── research-hockey.py
```

### MCP Server Integration
Commands will integrate with:
- **Notion MCP**: Page creation, editing, publishing
- **Exa MCP**: Web research and content discovery
- **YouTube MCP**: Video search and transcript extraction
- **Hockey MCP**: Local Thunder Playbook data access

### Command Configuration
```json
{
  "hockeyCommands": {
    "defaultAgeGroup": "U10",
    "notionWorkspace": "thunder-u10",
    "contentDatabase": "database-id-here",
    "teamContextPage": "page-id-here",
    "uxGuidelinesUrl": "https://notion.so/ux-guidelines",
    "publishingSettings": {
      "autoOptimize": true,
      "generateShareableLinks": true,
      "trackMetrics": true
    }
  }
}
```

## Acceptance Criteria

### Command Functionality
- [ ] All 6 slash commands execute successfully
- [ ] Commands integrate with existing MCP servers
- [ ] Error handling and validation for all inputs
- [ ] Progress feedback during multi-step operations
- [ ] Help documentation accessible via `/help hockey`

### Content Quality
- [ ] Generated content follows UX guidelines automatically
- [ ] Age-appropriate language and complexity
- [ ] Proper source citation and attribution
- [ ] Mobile-optimized formatting in Notion

### Integration Testing
- [ ] Commands work with existing Thunder Playbook data
- [ ] Notion pages created with proper templates
- [ ] YouTube videos embedded correctly
- [ ] Exa research integrated seamlessly

### User Experience
- [ ] Commands complete in <30 seconds for simple operations
- [ ] Clear progress indicators for longer operations
- [ ] Intuitive parameter validation and error messages
- [ ] Consistent output formatting across commands

## Testing Scenarios

### Basic Workflow Test
1. Run `/setup-team` for new team
2. Create content with `/new-page fundamentals drill`
3. Generate content draft with `/draft-content "skating stops"`
4. Edit content with feedback using `/edit-content`
5. Publish final content with `/publish-page`

### Integration Test
- Verify all MCP servers respond correctly
- Test command chaining (setup → create → draft → publish)
- Validate Notion database updates
- Confirm public URLs are accessible

### Error Handling Test
- Invalid parameters for each command
- MCP server unavailable scenarios
- Notion API rate limiting
- Network connectivity issues

## Documentation Requirements

### Command Reference
- Detailed parameter documentation
- Usage examples for each command
- Error message reference
- Troubleshooting guide

### Integration Guide
- MCP server setup instructions
- Configuration file templates
- Team onboarding workflow
- Best practices for content creation

## Timeline Estimate
**Total**: 2-3 hours
- Command implementation: 1.5 hours
- MCP integration: 45 minutes
- Testing and validation: 30 minutes

## Dependencies
- Existing MCP servers (Notion, Exa, YouTube)
- Thunder Playbook ChromaDB collections
- UX guidelines from Issue #2
- Notion templates from Issue #3

## Success Metrics
- Commands reduce content creation time by 70%
- 100% of generated content passes UX guidelines
- Team setup time reduced to <30 minutes
- User adoption rate >90% for primary workflows