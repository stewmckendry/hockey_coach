# Generated Outputs Directory

This directory contains dynamically generated files that are **excluded from version control**.

## Directory Structure

- `season_plans/` - Generated season plan documents with timestamps
- `practice_plans/` - Generated practice plan documents (if applicable)
- `diagrams/` - Generated hockey diagram images (if applicable)

## Important Notes

⚠️ **Files in this directory are automatically generated and should not be committed to git.**

- Generated files include timestamps in their names (e.g., `season_plan_20250726_174119.md`)
- These files are excluded via `.gitignore` patterns
- The directories are preserved with `.gitkeep` files for structure

## Purpose

This directory provides a consistent location for:
- Season planning agent outputs
- Practice plan generation results  
- Temporary diagram generation
- Any other dynamically created coaching resources

The structure helps keep generated content organized while ensuring it doesn't clutter the repository.