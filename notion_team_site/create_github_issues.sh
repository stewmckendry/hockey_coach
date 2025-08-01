#!/bin/bash

# Script to create GitHub issues for U10 Hockey Team Notion Site Development
# Run from the notion_team_site directory

echo "Creating GitHub issues for U10 Hockey Team Notion Site..."

# Issue #1: Initialize Team Notion Workspace
gh issue create \
  --title "Initialize Team Notion Workspace" \
  --body-file issues/issue_001_initialize_workspace.md \
  --label "enhancement,notion,setup" \
  --milestone "Phase 1: Foundation"

# Issue #2: Create Team Information Section  
gh issue create \
  --title "Create Team Information Section" \
  --body-file issues/issue_002_team_information.md \
  --label "enhancement,notion,content" \
  --milestone "Phase 1: Foundation"

# Issue #3: TeamSnap Calendar Integration
gh issue create \
  --title "TeamSnap Calendar Integration" \
  --body-file issues/issue_003_teamsnap_integration.md \
  --label "enhancement,integration,notion" \
  --milestone "Phase 1: Foundation"

# Issue #4: Build Skills Library
gh issue create \
  --title "Build Skills Library (15-20 pages)" \
  --body-file issues/issue_004_skills_library.md \
  --label "enhancement,content,notion" \
  --milestone "Phase 2: Education Content"

# Issue #5: Develop Position Guides
gh issue create \
  --title "Develop Position Guides (3 guides)" \
  --body-file issues/issue_005_position_guides.md \
  --label "enhancement,content,notion" \
  --milestone "Phase 2: Education Content"

# Issue #6: Design Team Systems Pages
gh issue create \
  --title "Design Team Systems Pages (5-6 systems)" \
  --body-file issues/issue_006_team_systems.md \
  --label "enhancement,content,notion" \
  --milestone "Phase 2: Education Content"

# Issue #7: Create Practice Plan Slash Command
gh issue create \
  --title "Create Practice Plan Slash Command" \
  --body-file issues/issue_007_practice_plan_command.md \
  --label "enhancement,feature,automation" \
  --milestone "Phase 3: Interactive Features"

# Issue #8: Implement Hockey IQ Chatbot
gh issue create \
  --title "Implement Hockey IQ Chatbot" \
  --body-file issues/issue_008_hockey_iq_chatbot.md \
  --label "enhancement,feature,interactive" \
  --milestone "Phase 3: Interactive Features"

echo "All issues created successfully!"
echo "View issues at: https://github.com/stewmckendry/hockey_coach/issues"