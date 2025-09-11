#!/usr/bin/env python3
"""
Off-Ice Workout Enrichment Script

This script loads raw off-ice workout data, enriches them using OpenAI's API,
and saves the enhanced data with additional metadata for coaching purposes.
"""

import asyncio
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

from openai import AsyncOpenAI

# Configuration
BATCH_SIZE = 3  # Number of workouts to process per API call (conservative for off-ice content)
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Setup paths
SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR.parent / "raw" / "dryland"
PROCESSED_DIR = SCRIPT_DIR.parent / "processed" / "dryland"
PROMPTS_DIR = SCRIPT_DIR.parent / "prompts"

class OffIceEnricher:
    def __init__(self, model: str = "gpt-4o", dry_run: bool = False, preview_count: int = 3):
        self.client = AsyncOpenAI()
        self.model = model
        self.dry_run = dry_run
        self.preview_count = preview_count
        self.prompt = self._load_prompt()
        
    def _load_prompt(self) -> str:
        """Load the off-ice enrichment prompt."""
        prompt_file = PROMPTS_DIR / "off_ice_enrichment.txt"
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    def load_raw_workouts(self, input_file: Optional[Path] = None) -> List[Dict]:
        """Load raw off-ice workout JSON file."""
        if input_file is None:
            input_file = RAW_DIR / "off_ice_raw.json"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                workouts = json.load(f)
            print(f"📂 Loaded {len(workouts)} raw off-ice workouts from {input_file}")
            return workouts
        except FileNotFoundError:
            raise FileNotFoundError(f"Raw workouts file not found: {input_file}")
    
    async def enrich_workout_batch(self, workouts: List[Dict]) -> List[Optional[Dict]]:
        """Enrich a batch of workouts using OpenAI API."""
        
        # Prepare batch prompt
        batch_content = "Process these off-ice workouts:\n\n"
        for i, workout in enumerate(workouts):
            batch_content += f"WORKOUT {i+1}:\n"
            batch_content += f"Title: {workout.get('title', '')}\n"
            batch_content += f"Category: {workout.get('category', '')}\n"
            batch_content += f"Description: {workout.get('description', '')}\n"
            
            # Safely handle goals field
            goals = workout.get('goals', [])
            if isinstance(goals, list):
                goals_str = '; '.join(str(goal) for goal in goals)
            else:
                goals_str = str(goals) if goals else ''
            batch_content += f"Goals: {goals_str}\n\n"
        
        batch_content += "Return a JSON array with one object per workout in the same order. Use the enrichment format specified in the prompt."
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": batch_content}
                ],
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            enriched_batch = json.loads(response_text)
            
            # Ensure we have a list
            if not isinstance(enriched_batch, list):
                enriched_batch = [enriched_batch]
            
            # Pad with None if we got fewer results than expected
            while len(enriched_batch) < len(workouts):
                enriched_batch.append(None)
            
            # Add original metadata to enriched workouts
            results = []
            for i, (original, enriched) in enumerate(zip(workouts, enriched_batch)):
                if enriched and enriched.get('specific_workout', False):
                    # Merge original metadata with enriched data
                    enriched_workout = {
                        **enriched,
                        'source_page': original.get('source_page'),
                        'source': original.get('source')
                    }
                    # Remove the specific_workout flag from final output
                    enriched_workout.pop('specific_workout', None)
                    results.append(enriched_workout)
                else:
                    results.append(None)  # Workout was filtered out
            
            return results
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error in batch: {e}")
            print(f"Response was: {response_text[:500]}...")
            return [None] * len(workouts)
        except Exception as e:
            print(f"❌ API error in batch: {e}")
            return [None] * len(workouts)
    
    async def process_workouts(self, workouts: List[Dict]) -> Dict[str, Any]:
        """Process all workouts with enrichment."""
        
        if self.dry_run:
            print(f"🔍 DRY RUN: Would process {len(workouts)} workouts")
            
            # Show preview of workouts
            print(f"\n📋 Preview of first {self.preview_count} workouts:")
            for i, workout in enumerate(workouts[:self.preview_count]):
                print(f"\n{i+1}. {workout.get('title', 'No title')}")
                print(f"   Category: {workout.get('category', 'No category')}")
                print(f"   Description: {workout.get('description', 'No description')[:100]}...")
            
            return {
                "enriched_workouts": [],
                "skipped_workouts": [],
                "category_counts": {},
                "processing_stats": {
                    "total_processed": len(workouts),
                    "enriched_count": 0,
                    "skipped_count": 0,
                    "processing_time": 0
                }
            }
        
        print(f"🚀 Enriching {len(workouts)} off-ice workouts...")
        start_time = time.time()
        
        enriched_workouts = []
        skipped_workouts = []
        category_counts = {}
        
        # Process in batches
        semaphore = asyncio.Semaphore(3)  # Limit concurrent API calls
        
        async def process_batch_with_semaphore(batch, batch_num):
            async with semaphore:
                print(f"🔄 Processing batch {batch_num+1} ({len(batch)} workouts)...")
                return await self.enrich_workout_batch(batch)
        
        # Create batches
        batches = [workouts[i:i + BATCH_SIZE] for i in range(0, len(workouts), BATCH_SIZE)]
        
        # Process all batches
        batch_tasks = [
            process_batch_with_semaphore(batch, i) 
            for i, batch in enumerate(batches)
        ]
        
        batch_results = await asyncio.gather(*batch_tasks)
        
        # Collect results
        for batch_idx, (batch, batch_result) in enumerate(zip(batches, batch_results)):
            for workout_idx, (original_workout, enriched_workout) in enumerate(zip(batch, batch_result)):
                overall_idx = batch_idx * BATCH_SIZE + workout_idx
                
                if enriched_workout is not None:
                    # Count by category
                    category = enriched_workout.get('category', 'unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
                    enriched_workouts.append(enriched_workout)
                    print(f"✅ Enriched workout {overall_idx+1}: {enriched_workout.get('title', 'No title')}")
                else:
                    skipped_workouts.append({
                        'title': original_workout.get('title', 'No title'),
                        'category': original_workout.get('category', 'No category'),
                        'reason': 'Generic/non-specific workout filtered out by LLM'
                    })
                    print(f"⏭️  Skipped workout {overall_idx+1}: {original_workout.get('title', 'No title')} (generic)")
        
        processing_time = time.time() - start_time
        
        return {
            "enriched_workouts": enriched_workouts,
            "skipped_workouts": skipped_workouts,
            "category_counts": category_counts,
            "processing_stats": {
                "total_processed": len(workouts),
                "enriched_count": len(enriched_workouts),
                "skipped_count": len(skipped_workouts),
                "processing_time": processing_time
            }
        }
    
    def save_enriched_workouts(self, enriched_workouts: List[Dict]) -> str:
        """Save enriched workouts to timestamped JSON file."""
        
        if self.dry_run:
            print("🔍 DRY RUN: Would save enriched workouts")
            return "dry-run-output"
        
        # Ensure processed directory exists
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = PROCESSED_DIR / f"off_ice_enriched_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_workouts, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(enriched_workouts)} enriched workouts to: {output_file}")
        return str(output_file)

def print_summary(results: Dict[str, Any], output_file: str, processing_time: float):
    """Print comprehensive processing summary."""
    stats = results["processing_stats"]
    
    print(f"\n📋 OFF-ICE WORKOUT ENRICHMENT SUMMARY")
    print("=" * 60)
    print(f"Total workouts processed: {stats['total_processed']}")
    print(f"Workouts enriched: {stats['enriched_count']}")
    print(f"Workouts skipped: {stats['skipped_count']}")
    print(f"Processing time: {stats['processing_time']:.1f} seconds")
    print(f"Output file: {output_file}")
    
    # Category breakdown
    if results["category_counts"]:
        print(f"\n📊 Enriched workouts by category:")
        for category, count in sorted(results["category_counts"].items()):
            print(f"  {category}: {count}")
    
    # Skipped workouts
    if results["skipped_workouts"]:
        print(f"\n⏭️  Skipped workouts ({len(results['skipped_workouts'])}):")
        for skipped in results["skipped_workouts"][:10]:  # Show first 10
            print(f"  • {skipped['title']} ({skipped['category']}) - {skipped['reason']}")
        
        if len(results["skipped_workouts"]) > 10:
            print(f"  ... and {len(results['skipped_workouts']) - 10} more")

async def main():
    parser = argparse.ArgumentParser(description="Enrich off-ice workout data with OpenAI")
    parser.add_argument(
        "--input",
        type=Path,
        help="Input raw off-ice JSON file (default: raw/dryland/off_ice_raw.json)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview workouts without enriching"
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=3,
        help="Number of workouts to preview in dry run (default: 3)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit processing to first N workouts (for testing)"
    )
    
    args = parser.parse_args()
    
    print("🏒 Off-Ice Workout Enrichment Script")
    print("=" * 50)
    print(f"Model: {args.model}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL ENRICHMENT'}")
    
    enricher = OffIceEnricher(
        model=args.model,
        dry_run=args.dry_run,
        preview_count=args.preview
    )
    
    try:
        # Load raw workouts
        workouts = enricher.load_raw_workouts(args.input)
        
        if args.limit:
            workouts = workouts[:args.limit]
            print(f"🔢 Limited to first {args.limit} workouts for testing")
        
        # Process workouts
        start_time = time.time()
        results = await enricher.process_workouts(workouts)
        processing_time = time.time() - start_time
        
        # Save results
        output_file = enricher.save_enriched_workouts(results["enriched_workouts"])
        
        # Print summary
        print_summary(results, output_file, processing_time)
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to enrich all workouts")
        else:
            print(f"\n✅ ENRICHMENT COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
