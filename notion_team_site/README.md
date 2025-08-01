# U10 Hockey Team Notion Site Development

This folder contains the implementation plan and GitHub issues for building a comprehensive Notion site for a U10 hockey team. The site will serve players, parents, and coaches with educational content, team information, and interactive features.

## Project Overview

The Notion site will provide:
- Team information and values
- Hockey education content (skills, positions, systems)
- Practice planning tools
- Interactive learning features
- Public access for all team stakeholders

## Site Architecture

```
Team Hub (Home Page)
├── 📋 Team Information
│   ├── Team Identity & Values
│   ├── Coaching Philosophy
│   ├── Team Expectations
│   ├── Roster & Contact Info
│   └── Team Calendar (TeamSnap Integration)
├── 🏒 Hockey Education Center
│   ├── Skills Library (15-20 pages)
│   ├── Position Guides (3 guides)
│   ├── Team Systems (5-6 systems)
│   └── Hockey IQ Chatbot
├── 📅 Practice Plans
│   ├── On-Ice Practice Library
│   ├── Dryland Training Plans
│   └── Skill Development Progressions
└── 🎯 Future Features (Backlog)
    ├── Parent Resources
    └── Player Development Tracking
```

## Implementation Issues

### Phase 1: Foundation Setup
1. **[Issue #1](issues/issue_001_initialize_workspace.md)**: Initialize Team Notion Workspace
2. **[Issue #2](issues/issue_002_team_information.md)**: Create Team Information Section  
3. **[Issue #3](issues/issue_003_teamsnap_integration.md)**: TeamSnap Calendar Integration

### Phase 2: Education Content Creation
4. **[Issue #4](issues/issue_004_skills_library.md)**: Build Skills Library (15-20 pages)
5. **[Issue #5](issues/issue_005_position_guides.md)**: Develop Position Guides (3 guides)
6. **[Issue #6](issues/issue_006_team_systems.md)**: Design Team Systems Pages (5-6 systems)

### Phase 3: Interactive Features
7. **[Issue #7](issues/issue_007_practice_plan_command.md)**: Create Practice Plan Slash Command
8. **[Issue #8](issues/issue_008_hockey_iq_chatbot.md)**: Implement Hockey IQ Chatbot

## Content Creation Workflow

For each content page, follow this workflow:

1. **Research**: `/research-hockey [topic] U10`
2. **Draft**: `/draft-content "[Title]" U10`
3. **Edit**: `/edit-content [page-url] "[feedback]"`
4. **Publish**: `/publish-page [page-url]`

## Available Tools & Integrations

### MCP Servers
- **Hockey MCP**: Custom coaching tools and knowledge base
- **Notion MCP**: Page creation and management
- **Exa MCP**: Web research for best practices
- **YouTube MCP**: Find instructional videos
- **StabilityAI MCP**: Generate tactical diagrams
- **Cloudinary MCP**: Host images with public URLs
- **Ref-Tools MCP**: Technical documentation

### Claude Code Features
- Native LLM for content generation
- Slash commands for workflow automation
- Multiple MCP server integrations
- Image generation and hosting
- Video search and embedding

## U10 Content Standards

All content must follow these guidelines:
- **Visual Ratio**: 70% images/video, 30% text
- **Reading Level**: Grade 3-4
- **Attention Span**: 10-15 minute modules
- **Language**: Clear, encouraging, simple
- **Focus**: Fundamentals, teamwork, fun

## Project Status

Track progress on the [Notion Development Plan page](https://www.notion.so/2420cdbf4977819ca24bf3f50cccf501).

## Getting Started

1. Review the UX Guidelines in the main project
2. Start with Issue #1 to initialize the workspace
3. Use provided slash commands for content creation
4. Follow the iterative workflow for each page
5. Ensure all content meets U10 standards

## File Structure

```
notion_team_site/
├── issues/          # GitHub issue descriptions
├── commands/        # Practice plan command implementation (future)
├── integrations/    # TeamSnap and other integrations (future)
└── README.md        # This file
```

## Contributing

Each issue can be assigned to different Claude Code instances for parallel development. Ensure:
- Follow the established workflows
- Apply UX guidelines consistently
- Test all content on mobile devices
- Use appropriate MCP tools
- Maintain positive, encouraging tone

## Resources

- [UX Guidelines](../UX_GUIDELINES.md)
- [Hockey MCP Documentation](../servers/hockey_mcp.py)
- [Slash Commands Issue #81](https://github.com/stewmckendry/hockey_coach/issues/81)
- [UX Guidelines Issue #82](https://github.com/stewmckendry/hockey_coach/issues/82)