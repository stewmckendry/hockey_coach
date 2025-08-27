# Issue #3: TeamSnap Calendar Integration

## Overview
Create a calendar integration between TeamSnap (current team scheduling tool) and the Notion team site to provide parents and players with easy access to practice and game schedules.

## Objectives
- Research TeamSnap integration options
- Design calendar display in Notion
- Create sync mechanism or manual update process
- Ensure mobile-friendly calendar view
- Provide clear schedule information

## Research Phase

### 1. TeamSnap API Investigation
Use Exa and Ref-Tools to research:
- TeamSnap API availability and access
- Export options (iCal, CSV, RSS)
- Authentication requirements
- Rate limits and restrictions

### 2. Integration Approaches
Evaluate options:
- **Option A**: Direct API integration (if available)
- **Option B**: iCal feed embedding
- **Option C**: Manual CSV export/import workflow
- **Option D**: Zapier or similar automation tool

## Implementation Options

### Automated Sync (Preferred)
```python
# Pseudo-code for automated sync
1. Connect to TeamSnap API/feed
2. Fetch schedule data
3. Transform to Notion format
4. Update Notion calendar database
5. Run on schedule (daily/hourly)
```

### Manual Process (Fallback)
1. Export schedule from TeamSnap
2. Format data for Notion import
3. Create update procedure document
4. Train team manager on process

## Notion Calendar Design

### Calendar Database Schema
- Event Type (Practice/Game/Tournament)
- Date & Time
- Location/Rink
- Home/Away (for games)
- Opponent (for games)
- Special Instructions
- Uniform (home/away jerseys)

### Display Views
1. **Monthly Calendar View**: Visual calendar grid
2. **List View**: Upcoming events list
3. **Game Schedule**: Games only filter
4. **Practice Schedule**: Practices only filter

## Tools to Use
- **Exa MCP**: Research TeamSnap API documentation
- **Ref-Tools MCP**: Find integration guides
- **Notion MCP**: Create calendar database and views
- **Claude LLM**: Design sync logic and procedures

## Visual Requirements
- Color coding for event types
- Clear time and location display
- Mobile-responsive design
- Export/subscribe options for parents

## File Locations
- Integration scripts: `docs/notion/integrations/`
- Documentation: `docs/notion/docs/`
- Store in Notion under Team Information section

## Success Criteria
- [ ] TeamSnap integration method chosen
- [ ] Calendar database created in Notion
- [ ] Sync process documented
- [ ] Mobile view optimized
- [ ] Parents can easily access schedule
- [ ] Update process sustainable

## Technical Considerations
- API key security (if using API)
- Update frequency requirements
- Handling schedule changes
- Notification system for changes
- Backup/manual override process

## Notes
- Prioritize ease of maintenance
- Consider parent tech comfort level
- Provide multiple access methods
- Include instructions for calendar apps
- Plan for mid-season schedule changes