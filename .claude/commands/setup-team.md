---
description: "Interactive team setup with context gathering and Notion workspace population"
argument-hint: "<team-name> <age-group> [season]"
allowed-tools: ["mcp__notion-remote__search", "mcp__notion-remote__fetch", "mcp__notion-remote__create-pages", "mcp__notion-remote__update-page", "mcp__notion-remote__update-database", "Read", "TodoWrite"]
---

# Hockey Team Setup Command

Comprehensive team setup workflow that gathers team context through interactive questioning and populates the enhanced Team Information database in Notion for use by other slash commands.

## Team Context Gathering

### Step 1: Parse Arguments and Initialize
- Extract team name, age group, and optional season from arguments
- Search for existing team in Team Information database
- Create TodoWrite list for setup process tracking

**Error Handling:**
```
If Team Information database not found:
  "Unable to locate Team Information database.
   Please ensure Notion integration has access to:
   Database ID: edffa8546c574e98bfe2c58a030616aa
   
   Resolution: Check Notion integration permissions."

If search fails:
  "Error searching Team Information database.
   This may be due to connection issues or permissions.
   
   Continuing with new team setup process..."

If team name already exists:
  "Team '[team-name]' already exists.
   
   Would you like to:
   1. Update existing team information
   2. Create a new team with a different name
   
   Please specify your choice (1 or 2)."
```

### Step 2: Interactive Team Context Collection

**Essential Team Information (Database + Page):**
```
Core Identity (4 fields):
- Team Name: [From arguments or prompt]
- Age Group: [U8/U10/U12/U14/U16/U18]
- Season: [Fall/Winter/Spring/Summer] 
- Skill Level: [Beginner/Intermediate/Advanced/Mixed]

Coaching Team (3 fields):
- Head Coach: [Person field with bio on page]
- Assistant Coaches: [People field with bios on page]
- Coaching Philosophy: [Select + detailed narrative on page]
  Options: Development-Focused/Competitive/Fun-First/Skill-Building/Balanced

Practice Logistics (5 fields):
- Practice Schedule: [Combined days/times in rich text format]
- Practice Duration: [30/45/60/75/90 minutes]
- Home Rink: [Text with full details on page]
- Ice Time Type: [Full Ice/Half Ice/Cross Ice/Mixed]
- Player Count: [Typical attendance number]

Development Focus (3 fields):
- Season Focus Areas: [Multi-select key priorities]
  Options: Skating/Passing/Shooting/Systems/Conditioning/Fun
- Development Priorities: [Multi-select top 3]
  Options: Individual Skills/Team Play/Physical/Mental/Leadership
- Team Goals: [Rich text - brief in DB, detailed on page]

Resources & Constraints (4 fields):
- Available Equipment: [Multi-select standard items]
- Special Considerations: [Rich text for important notes]
- Parent Involvement: [High/Medium/Low]
- Communication Method: [Primary platform/tool]

Administrative (3 fields):
- Team Email: [Contact email]
- League/Organization: [Affiliation]
- Team Page Link: [URL to Team Profile page]
```

**Streamlined to 20 essential fields** that capture critical information while avoiding redundancy. Additional context and narrative details live on the Team Profile page where they can be richly expressed.

### Step 3: Notion Database and Team Page Creation

**Team Information Database Update:**
- Search Team Information database (ID: edffa8546c574e98bfe2c58a030616aa) for team
- If exists: Update existing record with all gathered information
- If new: Create new database entry with complete team profile
- Populate all 20 essential fields using interactive responses
- Validate all data against database schema requirements

**Team Profile Page Creation:**
- Create comprehensive Team Profile page as primary team hub
- Structure page with rich narrative content and visual elements
- Include all gathered context in engaging, readable format
- Link to Team Information database entry for structured data access
- Organize with clear sections for different stakeholder needs

**Team Profile Page Structure:**
```
# [Team Name] Team Profile

## Team Overview 🏒
[Engaging team introduction with identity and culture]

## Quick Facts
- Age Group: [U8/U10/U12/U14+] with visual badge
- Season: [Current season]
- Home Rink: [Facility details with directions/map link]
- Practice Schedule: [Visual schedule display]

## Our Coaching Team 👨‍🏫
### Head Coach: [Name]
[Photo placeholder, bio, coaching philosophy]

### Assistant Coaches
[Photos, bios, roles and specialties]

## Coaching Philosophy & Approach 🎯
[Detailed explanation of team's coaching philosophy]
[How it translates to practice and game situations]
[Parent/player expectations based on philosophy]

## Season Goals & Focus Areas 📈
### Primary Goals
[Detailed season objectives with context]

### Development Priorities
[Skill development focus with progression plans]

### Team Culture & Values
[What makes this team special]

## Practice Information 🏟️
### Schedule & Location
[Interactive practice calendar]
[Facility details and what to expect]

### Practice Structure
[Typical practice flow based on duration and philosophy]
[Equipment requirements and recommendations]

## Player Development Tracking 📊
[Overview of development approach]
[Link to individual player pages/tracking]

## Parent Resources 👨‍👩‍👧‍👦
### Communication
[Preferred communication methods]
[Team app/platform links]
[Contact information structure]

### Expectations & Involvement
[Parent involvement level and opportunities]
[Volunteer needs and sign-ups]

## Team Resources Hub 📚
### Content Library
[Links to team-specific practice plans]
[Drill collections tailored to team needs]
[Season planning documents]

### Quick Links
- 📋 Latest Practice Plan
- 📊 Player Development Sheets  
- 📅 Season Calendar
- 📧 Communication Center
- 🏒 Equipment & Gear Info

## Team Traditions & Culture 🌟
[Special team traditions]
[Team building activities]
[Celebration approaches]
[Photo gallery placeholder]

## Safety & Wellness 🏥
[Team safety protocols]
[Injury prevention focus]
[Mental wellness approach]
[Emergency contacts]

## Notes & Updates 📝
[Latest team news]
[Important announcements]
[Upcoming events]
```

### Step 4: Context Integration for Content Creation

**UX Guidelines Integration:**
```
Age Group: [Selected age group]
Visual Content Ratio: [U8: 80%, U10: 70%, U12: 60%, U14+: 50%]
Terminology Tier: [Tier 1: U8-U10, Tier 2: U10-U12, Tier 3: U12+]
Attention Span: [U8: 5-10min, U10: 10-15min, U12: 15-20min, U14+: 20-30min]
Reading Level: [Grade level equivalent for age group]
```

**Content Personalization Context:**
```
Skill Level + Age Group: [Precise content difficulty targeting]
Coaching Philosophy: [Influences instruction style and approach]
Season Focus Areas: [Guides content research priorities]
Available Equipment: [Drives drill selection and modifications]
Practice Duration: [Determines activity length and complexity]
Ice Time Type: [Affects drill setup and space usage]
Player Count: [Influences group sizes and organization]
```

## Implementation Steps

### Phase 1: Discovery and Preparation
1. Parse command arguments for team name, age group, season
2. Search Notion Team Information database for existing team
3. Create TodoWrite list with all setup phases
4. Read UX Guidelines for age-appropriate standards

### Phase 2: Interactive Data Gathering
5. Conduct comprehensive guided interview using enhanced schema
6. Collect all 22 database fields through structured questioning
7. Apply smart defaults based on age group and experience level
8. Validate responses and ask clarifying questions
9. Confirm all information with user before proceeding

### Phase 3: Notion Workspace Setup
10. **Always fetch latest version** before updates:
    - Use mcp__notion-remote__fetch if updating existing team
    - Get current database schema to ensure field compatibility
    - Check for concurrent modifications (last_edited timestamp)
11. Create or update Team Information database entry with 20 essential fields
12. Create comprehensive Team Profile page with rich narrative content
13. Link database entry and Team Profile page bidirectionally
14. Set up age-appropriate content organization on Team Profile page
15. Configure team-specific navigation and resource hub
16. Add visual elements, placeholders, and engaging formatting

**Version Management:**
```
Before any update:
  1. Fetch current team data: mcp__notion-remote__fetch
  2. Compare last_edited timestamp
  3. If recently modified:
     "Team information was recently updated by another user.
      Last modified: [timestamp]
      
      Would you like to:
      1. Review current information and merge changes
      2. Overwrite with new information
      3. Cancel and review manually"
  4. Proceed based on user choice
```

**Database Operation Error Handling:**
```
If create/update fails:
  "Unable to save team information to database.
   Error: [specific error message]
   
   Common causes:
   - Missing required fields
   - Invalid field values
   - Permission restrictions
   - Database schema changes
   
   Your information has been saved locally.
   Would you like to retry?"

If Team Profile page creation fails:
  "Database entry created successfully, but Team Profile page creation failed.
   
   Database entry ID: [id]
   Error: [specific error]
   
   You can manually create the Team Profile page and link it,
   or retry the page creation."
```

### Phase 4: Context Preservation and Integration
16. Verify database entry completeness and accuracy
17. Ensure Team Profile page captures full team narrative and culture
18. Test integration with UX Guidelines and content creation workflows
19. Provide comprehensive setup summary with page and database links
20. Give user clear next steps and personalized command recommendations

## Enhanced Data Collection Process

### Smart Questioning Flow
- **Adaptive Questions**: Questions adapt based on previous responses
- **Context-Aware Defaults**: Suggest appropriate defaults based on age group and experience
- **Progressive Disclosure**: Collect basic info first, then dive deeper
- **Validation Loops**: Confirm complex information before proceeding

### Example Question Sequences

**For New Coach (First Year Experience):**
- Focus on simple, supportive coaching philosophy options
- Recommend development-focused or fun-first approaches
- Provide examples of age-appropriate goals
- Suggest beginner-friendly equipment lists

**For Experienced Coach (10+ Years):**
- Allow more complex coaching philosophy discussions
- Assume knowledge of advanced concepts
- Enable detailed facility constraint descriptions
- Support sophisticated development priority combinations

## Error Handling

**Database Schema Validation:**
- Verify all select/multi-select values match available options
- Validate number fields (Practice Duration, Player Count) are reasonable
- Ensure required fields are populated
- Check email format for Team Email field

**User Experience:**
- Allow editing of responses throughout the process
- Provide clear progress indicators (Phase 1 of 4, etc.)
- Enable partial completion and resume capability
- Offer helpful examples and explanations for complex fields

**Integration Testing:**
- Verify database entry was created/updated successfully
- Test Team Homepage creation and customization
- Confirm all field relationships work properly
- Validate team context can be retrieved by other commands

## Success Criteria

- ✅ Team Information database entry with 20 essential fields populated
- ✅ Comprehensive Team Profile page created with rich narrative content
- ✅ Bidirectional linking between database entry and Team Profile page
- ✅ UX Guidelines integration configured precisely for age group + skill level
- ✅ Content creation context optimized for coaching philosophy and resources
- ✅ Team Profile page serves as engaging hub for all team content
- ✅ All database relationships and page links properly established
- ✅ User receives comprehensive summary with both database and page access
- ✅ Setup process completes in under 20 minutes with full context gathering
- ✅ Team context immediately available for both human reading and tool usage

## Integration with Other Commands

**Enhanced Context Usage:**
- `/draft-content`: Uses Season Focus Areas + Coaching Philosophy + Available Equipment + UX Guidelines
- `/new-page`: Applies team-specific templates with Skill Level + Development Priorities
- `/research-hockey`: Filters by Age Group + Skill Level + Season Focus Areas
- `/edit-content`: Maintains Coaching Philosophy + Communication Preference + Parent Involvement
- `/publish-page`: Includes team branding + Communication Preference + League context

**Smart Content Personalization:**
- Practice plans automatically sized for Practice Duration and Player Count
- Drill instructions adapted for Available Equipment and Ice Time Type
- Content complexity matches Skill Level + Age Group combination
- Communication style reflects Coaching Philosophy and Parent Involvement level

## Example Usage

```bash
# Basic setup for new team
/setup-team "Riverside Hawks" U10

# Returning team with season update
/setup-team "Thunder Wolves" U12 Winter

# Will guide through comprehensive context gathering:
# - 20 essential database fields collected interactively
# - Rich Team Profile page created with full narrative
# - Smart defaults based on age group and responses
# - Validation and confirmation throughout process
# - Complete team hub ready for content and collaboration
```

The enhanced command provides comprehensive team context gathering that enables highly personalized, contextually appropriate content creation across all other slash commands, ensuring every piece of content matches the team's specific situation, resources, goals, and coaching approach.