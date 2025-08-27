# Season Plans Directory

This directory contains hockey season planning resources and outputs.

## Structure

- **templates/**: Reusable season plan templates for different age groups
- **generated/**: AI-generated season plans from the planning agent
- **examples/**: Sample season plans for reference

## Usage

Season plans are generated using the season planning agent located at `servers/hockey_agents/season_planning_agent.py`. Generated plans are automatically saved to the `generated/` subdirectory with timestamps.

## Templates

Templates should follow the structure defined in `prompts/season_planning_instructions.md` and can be customized for specific age groups, skill levels, and team needs.