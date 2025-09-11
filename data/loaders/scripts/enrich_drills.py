#!/usr/bin/env python3
"""
Hockey Drill Enrichment Script

This script loads raw drill data from JSON files, enriches them using OpenAI's API,
and saves the enhanced data with additional metadata for coaching purposes.
"""

import asyncio
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys

from openai import AsyncOpenAI

# Configuration
BATCH_SIZE = 5  # Number of drills to process per API call
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Setup paths
SCRIPT_DIR = Path(__file__).parent
RAW_DRILLS_DIR = SCRIPT_DIR.parent / "raw" / "drills"
PROCESSED_DIR = SCRIPT_DIR.parent / "processed"
PROMPTS_DIR = SCRIPT_DIR.parent / "prompts"

class DrillEnricher:
    def __init__(self, model: str = "gpt-4o", dry_run: bool = False, preview_count: int = 3):
        self.client = AsyncOpenAI()
        self.model = model
        self.dry_run = dry_run
        self.preview_count = preview_count
        self.prompt = self._load_prompt()
        
    def _load_prompt(self) -> str:
        """Load the drill enrichment prompt."""
        prompt_file = PROMPTS_DIR / "drill_enrichment.txt"
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    def load_raw_drills(self) -> Dict[str, List[Dict]]:
        """Load all raw drill JSON files."""
        drill_files = {
            "source1": RAW_DRILLS_DIR / "source1_drills_raw.json",
            "source2": RAW_DRILLS_DIR / "source2_drills_raw.json", 
            "source3": RAW_DRILLS_DIR / "source3_drills_raw.json"
        }
        
        all_drills = {}
        for source_name, file_path in drill_files.items():
            if file_path.exists():
                print(f"📂 Loading {file_path}...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    drills = json.load(f)
                    all_drills[source_name] = drills
                    print(f"   Loaded {len(drills)} drills from {source_name}")
            else:
                print(f"⚠️  File not found: {file_path}")
                
        return all_drills
    
    def prepare_drill_for_enrichment(self, drill: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Prepare a drill record with source-specific field mapping."""
        
        # Extract common fields across sources
        title = drill.get("title", "")
        
        # Handle URL field variations
        url = drill.get("url") or drill.get("video_url", "")
        
        # Extract existing instructions/setup/description
        raw_instructions = ""
        if "instructions" in drill:
            raw_instructions = drill["instructions"]
        elif "setup" in drill and isinstance(drill["setup"], list):
            raw_instructions = "; ".join(drill["setup"])
        elif "description" in drill:
            raw_instructions = drill["description"]
            
        # Extract existing teaching points/coaching points
        raw_teaching_points = ""
        if "teaching_points" in drill:
            if isinstance(drill["teaching_points"], list):
                raw_teaching_points = "; ".join(drill["teaching_points"])
            else:
                raw_teaching_points = drill["teaching_points"]
        elif "coaching_points" in drill and isinstance(drill["coaching_points"], list):
            raw_teaching_points = "; ".join(drill["coaching_points"])
            
        # Extract existing summary
        raw_summary = drill.get("summary", "")
        
        return {
            "title": title,
            "url": url,
            "raw_instructions": raw_instructions,
            "raw_teaching_points": raw_teaching_points,
            "raw_summary": raw_summary,
            "source": source,
            "original_data": drill  # Keep original for reference
        }
    
    async def enrich_drill_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich a batch of drills using OpenAI API."""
        
        # Prepare drill data for the prompt
        drill_texts = []
        for i, drill in enumerate(batch):
            drill_text = f"""
DRILL {i+1}:
Title: {drill['title']}
Existing Instructions: {drill['raw_instructions']}
Existing Teaching Points: {drill['raw_teaching_points']}
Existing Summary: {drill['raw_summary']}
"""
            drill_texts.append(drill_text.strip())
        
        batch_text = "\n\n" + "="*50 + "\n\n".join(drill_texts)
        
        full_prompt = f"""{self.prompt}

Here are {len(batch)} hockey drills to analyze and enrich:

{batch_text}

Please provide a JSON response with an array of {len(batch)} objects, each containing the enriched metadata for the corresponding drill in the same order."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional hockey coach and drill expert."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            enriched_data = json.loads(content)
            
            if not isinstance(enriched_data, list) or len(enriched_data) != len(batch):
                raise ValueError(f"Expected list of {len(batch)} items, got {type(enriched_data)} with {len(enriched_data) if isinstance(enriched_data, list) else 'unknown'} items")
            
            # Combine enriched data with original drill info
            enriched_drills = []
            for original_drill, enriched_meta in zip(batch, enriched_data):
                enriched_drill = {
                    "title": original_drill["title"],  # Hard-coded from source
                    "url": original_drill["url"],      # Hard-coded from source  
                    "source": original_drill["source"], # Hard-coded from source
                    "summary": enriched_meta.get("summary", ""),
                    "instructions": enriched_meta.get("instructions", ""),
                    "teaching_points": enriched_meta.get("teaching_points", []),
                    "equipment": enriched_meta.get("equipment", []),
                    "complexity": enriched_meta.get("complexity", 3),
                    "skills": enriched_meta.get("skills", []),
                    "sub_skills": enriched_meta.get("sub_skills", []),
                    "positions": enriched_meta.get("positions", []),
                    "original_data": original_drill["original_data"]
                }
                enriched_drills.append(enriched_drill)
                
            return enriched_drills
            
        except Exception as e:
            print(f"❌ Error enriching batch: {str(e)}")
            # Return original drills with minimal enrichment on error
            return [{
                "title": drill["title"],
                "url": drill["url"], 
                "source": drill["source"],
                "summary": drill["raw_summary"] or "Summary not available",
                "instructions": drill["raw_instructions"] or "Instructions not available", 
                "teaching_points": drill["raw_teaching_points"].split("; ") if drill["raw_teaching_points"] else [],
                "equipment": [],
                "complexity": 3,
                "skills": [],
                "sub_skills": [],
                "positions": [],
                "original_data": drill["original_data"],
                "enrichment_error": str(e)
            } for drill in batch]
    
    async def process_drills(self, all_drills: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Process all drills with enrichment."""
        all_enriched = []
        total_drills = sum(len(drills) for drills in all_drills.values())
        processed_count = 0
        
        print(f"\n🚀 Processing {total_drills} total drills...")
        if self.dry_run:
            print(f"🔍 DRY RUN MODE: Processing first {self.preview_count} drills from each source")
            
        start_time = time.time()
        
        for source_name, drills in all_drills.items():
            print(f"\n📚 Processing {source_name} ({len(drills)} drills)...")
            
            # Limit drills for dry run
            if self.dry_run:
                drills = drills[:self.preview_count]
                print(f"   Limited to {len(drills)} drills for preview")
            
            # Prepare drills for enrichment
            prepared_drills = [
                self.prepare_drill_for_enrichment(drill, source_name) 
                for drill in drills
            ]
            
            # Create all batches first
            batches = []
            for i in range(0, len(prepared_drills), BATCH_SIZE):
                batch = prepared_drills[i:i + BATCH_SIZE]
                batch_num = i // BATCH_SIZE + 1
                total_batches = (len(prepared_drills) + BATCH_SIZE - 1) // BATCH_SIZE
                batches.append((batch, batch_num, total_batches))
            
            # Process batches asynchronously
            if self.dry_run:
                # In dry run, process one batch to show sample
                for batch, batch_num, total_batches in batches[:1]:
                    print(f"   🎨 Processing batch {batch_num}/{total_batches} ({len(batch)} drills)...")
                    print(f"      📝 Sample drill: {batch[0]['title']}")
                    enriched_batch = await self.enrich_drill_batch(batch)
                    
                    # Print enriched sample
                    if enriched_batch:
                        sample = enriched_batch[0]
                        print(f"      ✅ Enriched sample:")
                        print(f"         Summary: {sample['summary'][:100]}...")
                        print(f"         Instructions: {sample['instructions'][:300]}...")
                        print(f"         Teaching Points: {sample['teaching_points'][:100]}...")
                        print(f"         Complexity: {sample['complexity']}")
                        print(f"         Skills: {sample['skills']}")
                        print(f"         Sub-Skills: {sample['sub_skills']}")
                        print(f"         Positions: {sample['positions']}")
                    
                    all_enriched.extend(enriched_batch)
                    processed_count += len(batch)
            else:
                # Process all batches for this source asynchronously
                print(f"   🎨 Processing {len(batches)} batches asynchronously...")
                
                # Create tasks for async processing
                tasks = []
                for batch, batch_num, total_batches in batches:
                    task = self.enrich_drill_batch(batch)
                    tasks.append(task)
                
                # Execute all batches for this source in parallel
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(batch_results):
                    batch, batch_num, total_batches = batches[i]
                    
                    if isinstance(result, Exception):
                        print(f"   ❌ Batch {batch_num} failed: {result}")
                        # Create fallback entries
                        fallback_batch = [{
                            "title": drill["title"],
                            "url": drill["url"], 
                            "source": drill["source"],
                            "summary": drill["raw_summary"] or "Summary not available",
                            "instructions": drill["raw_instructions"] or "Instructions not available", 
                            "teaching_points": drill["raw_teaching_points"].split("; ") if drill["raw_teaching_points"] else [],
                            "equipment": [],
                            "complexity": 3,
                            "skills": [],
                            "sub_skills": [],
                            "positions": [],
                            "original_data": drill["original_data"],
                            "enrichment_error": str(result)
                        } for drill in batch]
                        all_enriched.extend(fallback_batch)
                    else:
                        print(f"   ✅ Batch {batch_num}/{total_batches} completed ({len(result)} drills)")
                        all_enriched.extend(result)
                    
                    processed_count += len(batch)
                    
                # Progress update for this source
                progress = (processed_count / total_drills) * 100
                print(f"   📊 Source progress: {len(prepared_drills)} drills completed")
                print(f"   📊 Overall progress: {processed_count}/{total_drills} ({progress:.1f}%)")
                
                # Rate limiting delay between sources
                await asyncio.sleep(2)
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Processing completed in {elapsed_time:.1f} seconds")
        print(f"📊 Processed {len(all_enriched)} drills total")
        
        return all_enriched
    
    def save_enriched_drills(self, enriched_drills: List[Dict[str, Any]]) -> str:
        """Save enriched drills to timestamped file."""
        if self.dry_run:
            print(f"\n🔍 DRY RUN: Would save {len(enriched_drills)} enriched drills")
            return "dry-run-output"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = PROCESSED_DIR / f"enriched_drills_{timestamp}.json"
        
        # Ensure processed directory exists
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_drills, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Saved enriched drills to: {output_file}")
        return str(output_file)

async def main():
    parser = argparse.ArgumentParser(description="Enrich hockey drill data using OpenAI API")
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process and print first k drills from each file for verification"
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=3,
        help="Number of drills to process from each source in dry-run mode (default: 3)"
    )
    
    args = parser.parse_args()
    
    print("🏒 Hockey Drill Enrichment Script")
    print("=" * 50)
    print(f"Model: {args.model}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL PROCESSING'}")
    if args.dry_run:
        print(f"Preview count: {args.preview_count} drills per source")
    
    enricher = DrillEnricher(
        model=args.model,
        dry_run=args.dry_run,
        preview_count=args.preview_count
    )
    
    try:
        # Load raw drills
        all_drills = enricher.load_raw_drills()
        
        if not all_drills:
            print("❌ No drill files found!")
            return
            
        # Process drills
        enriched_drills = await enricher.process_drills(all_drills)
        
        # Save results
        output_file = enricher.save_enriched_drills(enriched_drills)
        
        # Print summary
        total_records = len(enriched_drills)
        print(f"\n📋 SUMMARY")
        print(f"Records enriched: {total_records}")
        print(f"Output location: {output_file}")
        print(f"Model used: {args.model}")
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to process all drills")
        else:
            print(f"\n✅ ENRICHMENT COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
