# ChromaDB Hockey Data Pipeline Index

## Overview
This directory contains a comprehensive data processing pipeline that enriches raw hockey data with AI-generated metadata and indexes it into ChromaDB for semantic search. The system handles 8 different hockey knowledge domains with 1000+ items total.

## Directory Structure

### 📁 Raw Data Sources (`raw/`)
Contains unprocessed hockey data from various sources:

- **`drills/`** - 3 JSON files with raw drill data from different sources
- **`ltad/`** - Long Term Athletic Development materials (PDFs, HTML files, skill data)
- **`tactics/`** - Hockey systems and tactics (HTML files, PDF faceoff positions)
- **`rules/`** - Conduct and fair play guidelines (HTML rulebook, PDFs)
- **`dryland/`** - Off-ice training manual and raw data
- **`nhl_interviews/`** - Professional insights from NHL players/coaches
- **`video/`** - Video content lists and URLs for instructional content

### 📁 Processing Scripts (`scripts/`)
AI-powered enrichment and indexing scripts:

#### Enrichment Scripts (OpenAI Integration)
- **`enrich_drills.py`** - Enriches drill data with detailed instructions, teaching points, equipment lists
- **`enrich_ltad_skills.py`** - Adds coaching summaries and complexity ratings to skill development
- **`enrich_tactics.py`** - Expands tactical systems with position-specific assignments
- **`enrich_off_ice.py`** - Enhances dryland training with structured metadata

#### Indexing Scripts (ChromaDB Integration)
- **`index_drills_chroma.py`** - Creates `drill-*` collections with semantic search
- **`index_ltad_chroma.py`** - Creates `ltad-*` collections for skill development
- **`index_tactics.py`** - Creates `tactics-*` collections for team systems
- **`index_conduct_chroma.py`** - Creates `conduct-*` collections for rules/ethics
- **`index_nhl_insights_chroma.py`** - Creates `insight-*` collections for expert knowledge
- **`index_office_manual_chroma.py`** - Creates `office-*` collections for off-ice training
- **`index_video_clips_chroma.py`** - Creates `video-*` collections for instructional content
- **`index_video_clips_dryland.py`** - Specialized dryland video indexing

#### Utility Scripts
- **`extract_html_checking_skills.py`** - Extracts checking skills from HTML sources
- **`extract_tactics.py`** - Extracts tactical systems from HTML content
- **`debug_extraction.py`** - Debug utility for data extraction issues

### 📁 AI Prompts (`prompts/`)
Specialized prompts for different enrichment types:

- **`drill_enrichment.txt`** - Professional coaching prompt for drill enhancement
- **`ltad_skill_enrichment.txt`** - Age-appropriate skill development guidance
- **`tactics_enrichment.txt`** - Team systems and positional assignments
- **`off_ice_enrichment.txt`** - Dryland training structure and progressions
- **`html_checking_extraction.txt`** - Body checking skill extraction prompts
- **`tactics_extraction.txt`** - Tactical system extraction from web content

### 📁 Processed Data (`processed/`)
AI-enriched data ready for indexing:

#### Drill Data
- **`drills/enriched_drills_20250722_200733.json`** - 500+ enriched drills with:
  - Detailed step-by-step instructions
  - Coaching teaching points
  - Equipment requirements
  - Complexity ratings (1-5)
  - Skill categorization

#### LTAD (Long Term Athletic Development)
- **`ltad/enriched_ltad_skills_20250722_195101.json`** - Age-specific skill development with:
  - Age group targeting
  - Skill complexity progressions
  - Equipment requirements
  - Position-specific adaptations

#### Tactical Systems
- **`tactics/tactics_enriched_20250722_211857.json`** - Team systems with:
  - Position-specific assignments (Center, Wingers, Defense, Goalie)
  - Strategic teaching points
  - System complexity ratings
  - Situation-specific applications

#### Off-Ice Training
- **`dryland/off_ice_enriched_20250722_221438.json`** - Structured dryland training with:
  - Exercise progressions
  - Equipment requirements
  - Age-appropriate modifications
  - Hockey-specific applications

#### Rules and Conduct
- **`rules/conduct_enriched.json`** - Fair play and conduct guidelines

#### Professional Insights
- **`nhl_interviews/mlhs_insights.json`** - Expert knowledge from NHL professionals

#### Video Content
- **`video/video_clips.json`** - Instructional video metadata
- **`video/video_clips_dryland.json`** - Dryland-specific video content
- **`video/video_clips_dryland_jj_sam.json`** - Specialized dryland instruction

### 📁 Indexed Data (`indexed/`)
Timestamped records of successful ChromaDB indexing:

- **`ltad_skills_indexed_20250722_200156.json`** - LTAD indexing log
- **`tactics_indexed_20250722_213244.json`** - Tactics indexing log

## Data Processing Pipeline

### 1. Raw Data Ingestion
- HTML scraping from hockey websites
- PDF extraction from coaching manuals  
- JSON compilation from multiple sources
- Video URL collection and metadata extraction

### 2. AI-Powered Enrichment
- OpenAI GPT-4 enhancement of raw data
- Professional coaching perspective integration
- Structured metadata generation
- Complexity and skill level assignment

### 3. ChromaDB Indexing
- Vector embedding generation for semantic search
- Metadata preservation for filtering
- Collection organization by domain
- Batch processing with error handling

### 4. Quality Assurance
- Automated validation of enriched content
- Token limit management (16,000 char max)
- Error handling and graceful fallbacks
- Timestamped processing logs

## ChromaDB Collections Created

| Collection Prefix | Content Type | Count | Features |
|------------------|--------------|-------|----------|
| `drill-*` | On-ice drills | 500+ | Instructions, equipment, complexity |
| `ltad-*` | Skill development | 200+ | Age groups, progressions, positions |
| `tactics-*` | Team systems | 50+ | Position assignments, situations |
| `conduct-*` | Rules/ethics | 30+ | Fair play, respect policies |
| `office-*` | Off-ice training | 100+ | Dryland exercises, progressions |
| `insight-*` | Expert knowledge | 50+ | NHL professional insights |
| `video-*` | Instructional content | 200+ | Video metadata, descriptions |

## Usage Examples

### Full Data Pipeline
```bash
# 1. Enrich raw data with AI
python chroma_load/scripts/enrich_drills.py
python chroma_load/scripts/enrich_ltad_skills.py
python chroma_load/scripts/enrich_tactics.py

# 2. Index enriched data into ChromaDB
python chroma_load/scripts/index_drills_chroma.py
python chroma_load/scripts/index_ltad_chroma.py
python chroma_load/scripts/index_tactics.py
```

### Incremental Updates
```bash
# Clear and re-index specific collection
python chroma_load/scripts/index_drills_chroma.py --clear-drills

# Preview enrichment before full run
python chroma_load/scripts/enrich_drills.py --dry-run --preview-count 3
```

## Key Features

### AI Enhancement
- **Professional Coaching Perspective**: All content enriched with coaching expertise
- **Structured Output**: Consistent JSON schema across all data types  
- **Complexity Assessment**: 1-5 scale difficulty ratings
- **Age-Appropriate Content**: LTAD principles integrated throughout

### Semantic Search Optimization
- **Rich Metadata**: Equipment, skills, positions, age groups
- **Full-Text Indexing**: Instructions, teaching points, summaries
- **Vector Embeddings**: OpenAI embeddings for semantic similarity
- **Batch Processing**: Efficient handling of large datasets

### Production Ready
- **Error Handling**: Graceful API failure recovery
- **Rate Limiting**: Prevents OpenAI API throttling
- **Timestamped Outputs**: Version control and audit trails
- **Configurable Parameters**: Model selection, batch sizes, preview modes

## Integration Points

This ChromaDB pipeline integrates with:
- **MCP Server** (`servers/hockey_mcp.py`) - Provides 4 main search tools
- **Web Application** (`web_app/`) - Frontend access to hockey knowledge
- **Direct API** (`servers/hockey_mcp_direct_api.py`) - HTTP wrapper for MCP tools
- **Season Planning Agent** - Advanced coaching workflow automation

## File Naming Conventions
- **Raw files**: `*_raw.json`, original HTML/PDF files
- **Enriched files**: `*_enriched_YYYYMMDD_HHMMSS.json`
- **Indexed files**: `*_indexed_YYYYMMDD_HHMMSS.json`
- **Collections**: `{domain}-{modifier}` (e.g., `drill-beginner`, `ltad-u12`)