# Scripts Directory

This directory contains organized utility scripts for the Thunder Playbook project.

## Structure

- **data_processing/**: Scripts for analyzing and processing hockey data
  - `analyze_drills_metadata.py`: Analyzes drill metadata from ChromaDB collections
  - `debug_html_extraction.py`: Debug tools for HTML content extraction
  - `validate_skills_coverage.py`: Validates skills coverage against Hockey Canada curriculum
  - `skills_coverage_report.txt`: Generated coverage analysis report

- **deployment/**: Scripts for deploying and setting up the project
  - `deploy-production.sh`: Production deployment script
  - `setup-development.sh`: Development environment setup

- **testing/**: Performance and testing scripts
  - `test_performance.py`: Performance benchmarking
  - `test_telemetry.py`: Telemetry system testing

- **telemetry/**: Telemetry and monitoring scripts
  - `telemetry_hook.py`: Main telemetry hook
  - `telemetry_hook_debug.py`: Debug version of telemetry hook
  - `telemetry_raw_debug.py`: Raw telemetry debugging
  - `telemetry_viewer.py`: Telemetry data viewer
  - `telemetry_wrapper.sh`: Shell wrapper for telemetry

- **utilities/**: General utility scripts
  - `notification_helper.sh`: System notification helpers
  - `simple_notify.sh`: Simple notification script

## Other Script Directories

- `/chroma_load/scripts/`: ChromaDB data loading and enrichment scripts
- `/image_gen/scripts/`: Image generation scripts for hockey diagrams
- `/n8n/scripts/`: n8n workflow API testing scripts
- `/web_app/scripts/`: Next.js web application utility scripts