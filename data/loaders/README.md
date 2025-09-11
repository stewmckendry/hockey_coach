# Hockey Drill Enrichment System

This system enriches raw hockey drill data with detailed metadata using OpenAI's API.

## Files Created/Updated:

### 1. Drill Enrichment Script
**File:** `chroma_load/scripts/enrich_drills.py`

Loads raw drill JSON files, enriches them with OpenAI, and saves timestamped results.

**Usage:**
```bash
# Full processing with default model (gpt-4o)
python chroma_load/scripts/enrich_drills.py

# Dry run to preview first 3 drills from each source
python chroma_load/scripts/enrich_drills.py --dry-run

# Custom model and preview count
python chroma_load/scripts/enrich_drills.py --model gpt-4o-mini --dry-run --preview-count 5

# Full run with different model
python chroma_load/scripts/enrich_drills.py --model gpt-4o-mini
```

### 2. Enrichment Prompt
**File:** `chroma_load/prompts/drill_enrichment.txt`

Professional coaching prompt that guides the LLM to generate:
- Detailed step-by-step instructions
- Coaching summaries and teaching points
- Equipment lists and complexity ratings
- Skill development focus areas

### 3. Updated Indexing Script
**File:** `chroma_load/scripts/index_drills_chroma.py`

Enhanced with CLI options to handle enriched drill files.

**Usage:**
```bash
# Index most recent enriched drills (auto-detects latest file)
python chroma_load/scripts/index_drills_chroma.py

# Clear existing drill documents first
python chroma_load/scripts/index_drills_chroma.py --clear-drills

# Index specific file
python chroma_load/scripts/index_drills_chroma.py --input-file chroma_load/processed/enriched_drills_20250722_143052.json
```

## Workflow:

1. **Enrich Raw Drills:**
   ```bash
   # Test with dry run first
   python chroma_load/scripts/enrich_drills.py --dry-run
   
   # Run full enrichment
   python chroma_load/scripts/enrich_drills.py
   ```

2. **Index Enriched Drills:**
   ```bash
   # Clear old drills and index new ones
   python chroma_load/scripts/index_drills_chroma.py --clear-drills
   ```

## Output Structure:

Enriched drill files are saved as `chroma_load/processed/enriched_drills_YYYYMMDD_HHMMSS.json`

Each drill contains:
- `title` (from source)
- `url` (from source)  
- `source` (from source)
- `summary` (LLM generated)
- `instructions` (LLM generated with numbered steps)
- `teaching_points` (LLM generated coaching cues)
- `equipment` (LLM generated equipment list)
- `complexity` (LLM generated 1-5 scale)
- `skills` (LLM generated skill list)
- `original_data` (preserved source data)

## Configuration:

- **Batch Size:** 5 drills per API call (configurable in script)
- **Models:** Supports any OpenAI chat model
- **Rate Limiting:** 1 second delay between batches
- **Error Handling:** Graceful fallback on API errors
