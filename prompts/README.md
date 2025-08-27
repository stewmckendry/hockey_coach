# Prompts Directory Structure

This directory contains prompt engineering files organized by purpose and system component.

## Directory Organization

### `/prompts/` (Main Agent Prompts)
Core prompts for the main hockey coaching assistant:
- `completion_signals.md` - Recognition patterns for conversation completion
- `conversation_examples.md` - Example interactions and response patterns  
- `season_planning_instructions.md` - Detailed season planning guidance
- `tool_usage_guidelines.md` - Guidelines for MCP tool usage

### `/chroma_load/prompts/` (Data Processing Prompts)
Prompts used for enriching and processing hockey data:
- `drill_enrichment.txt` - Template for analyzing and enriching drill data
- `html_checking_extraction.txt` - HTML content extraction prompts
- `ltad_skill_enrichment.txt` - Long-term athlete development skill processing
- `off_ice_enrichment.txt` - Off-ice training data processing
- `tactics_enrichment.txt` - Tactical analysis and enrichment
- `tactics_extraction.txt` - Extracting tactical information from sources

### `/image_gen/prompts/` (Diagram Generation Prompts)
Specialized prompts for hockey diagram generation:
- `hockey_image_generator.txt` - Main hockey diagram generation prompt
- `hockey_image_reviewer.txt` - Quality review and feedback prompt
- `defensive_zone_coverage.txt` - Defensive zone specific diagrams
- `forechecking_pressure.txt` - Forechecking system diagrams
- `right_defenseman_coverage.txt` - Position-specific coverage diagrams
- `transition_paths.txt` - Transition play diagrams

### `/servers/hockey_prompts_mcp/prompts/` (MCP Server Templates)
Template prompts served via MCP for dynamic use:
- `drill_search.md` - Drill searching and recommendations
- `hockey_skills_list.md` - Skills categorization and listing
- `plan_next_practice.md` - Practice planning template
- `post_practice_review.md` - Post-practice analysis template
- `practice_template.md` - Comprehensive practice plan template

## Usage Guidelines

1. **Main Agent Prompts** - Used directly by the hockey coaching assistant
2. **Data Processing** - Used during data ingestion and ChromaDB population
3. **Image Generation** - Used by specialized diagram generation agents
4. **MCP Templates** - Dynamically served to agents via MCP protocol

## Best Practices

- Keep prompts focused on single responsibilities
- Use clear, actionable language
- Include examples where helpful
- Maintain consistency in formatting and structure
- Test prompts with real use cases before deployment