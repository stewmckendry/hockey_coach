#!/usr/bin/env python3
"""
Hockey Tactics Enrichment Script

This script loads raw tactics data, enriches it using OpenAI's API,
and saves the enhanced data with detailed coaching metadata.
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
BATCH_SIZE = 3  # Number of tactics to process per API call
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Setup paths
SCRIPT_DIR = Path(__file__).parent
RAW_TACTICS_DIR = SCRIPT_DIR.parent / "raw" / "tactics"
PROCESSED_DIR = SCRIPT_DIR.parent / "processed" / "tactics"
PROMPTS_DIR = SCRIPT_DIR.parent / "prompts"

class TacticsEnricher:
    def __init__(self, model: str = "gpt-4o", dry_run: bool = False, preview_count: int = 5):
        self.client = AsyncOpenAI()
        self.model = model
        self.dry_run = dry_run
        self.preview_count = preview_count
        self.prompt = self._load_prompt()
        self.skipped_tactics = []
        
    def _load_prompt(self) -> str:
        """Load the tactics enrichment prompt."""
        prompt_file = PROMPTS_DIR / "tactics_enrichment.txt"
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    def load_raw_tactics(self, input_file: Path = None) -> List[Dict[str, Any]]:
        """Load raw tactics from JSON file."""
        if input_file is None:
            tactics_file = RAW_TACTICS_DIR / "tactics_raw_rows.json"
        else:
            tactics_file = input_file
            
        if tactics_file.exists():
            try:
                with open(tactics_file, 'r', encoding='utf-8') as f:
                    tactics = json.load(f)
                print(f"📂 Loaded {len(tactics)} raw tactics from {tactics_file}")
                return tactics
            except Exception as e:
                print(f"❌ Error loading tactics: {e}")
                return []
        else:
            raise FileNotFoundError(f"Tactics file not found: {tactics_file}")
    
    def prepare_tactic_for_enrichment(self, tactic: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a tactic record for enrichment."""
        return {
            "title": tactic.get("title", ""),
            "raw_content": tactic.get("raw_content", ""),
            "source": tactic.get("source", ""),
            "original_data": tactic  # Keep original for reference
        }
    
    async def enrich_tactic_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich a batch of tactics using OpenAI API."""
        
        # Prepare tactic data for the prompt
        tactic_texts = []
        for i, tactic in enumerate(batch):
            tactic_text = f"""
TACTIC {i+1}:
Title: {tactic['title']}
Raw Content: {tactic['raw_content']}
Source: {tactic['source']}
"""
            tactic_texts.append(tactic_text.strip())
        
        batch_text = "\n\n" + "="*50 + "\n\n".join(tactic_texts)
        
        full_prompt = f"""{self.prompt}

Here are {len(batch)} hockey tactics to analyze and enrich:

{batch_text}

Please provide a JSON response with an array of {len(batch)} objects, each containing the enriched metadata for the corresponding tactic in the same order."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional hockey tactics expert and coaching instructor."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=6000
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
            
            # Combine enriched data with original tactic info
            enriched_tactics = []
            for original_tactic, enriched_meta in zip(batch, enriched_data):
                enriched_tactic = {
                    "tactic_name": enriched_meta.get("tactic_name", original_tactic["title"]),
                    "summary": enriched_meta.get("summary", ""),
                    "skills": enriched_meta.get("skills", []),
                    "instructions": enriched_meta.get("instructions", ""),
                    "centre_assignments": enriched_meta.get("centre_assignments", "N/A"),
                    "winger_assignments": enriched_meta.get("winger_assignments", "N/A"),
                    "defense_assignments": enriched_meta.get("defense_assignments", "N/A"),
                    "goalie_assignments": enriched_meta.get("goalie_assignments", "N/A"),
                    "teaching_points": enriched_meta.get("teaching_points", []),
                    "raw_content": original_tactic["raw_content"],
                    "source": original_tactic["source"],
                    "original_data": original_tactic["original_data"]
                }
                enriched_tactics.append(enriched_tactic)
                
            return enriched_tactics
            
        except Exception as e:
            print(f"❌ Error enriching batch: {str(e)}")
            # Return original tactics with minimal enrichment on error
            return [{
                "tactic_name": tactic["title"],
                "summary": "Summary not available due to enrichment error",
                "skills": [],
                "instructions": "Instructions not available due to enrichment error",
                "centre_assignments": "N/A",
                "winger_assignments": "N/A", 
                "defense_assignments": "N/A",
                "goalie_assignments": "N/A",
                "teaching_points": [],
                "raw_content": tactic["raw_content"],
                "source": tactic["source"],
                "original_data": tactic["original_data"],
                "enrichment_error": str(e)
            } for tactic in batch]
    
    async def process_tactics(self, tactics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process all tactics with enrichment."""
        
        print(f"\n🚀 Processing {len(tactics)} total tactics...")
        if self.dry_run:
            print(f"🔍 DRY RUN MODE: Processing first {self.preview_count} tactics")
            tactics = tactics[:self.preview_count]
            
        start_time = time.time()
        
        # Prepare tactics for enrichment
        prepared_tactics = [
            self.prepare_tactic_for_enrichment(tactic) 
            for tactic in tactics
        ]
        
        # Create all batches first
        batches = []
        for i in range(0, len(prepared_tactics), BATCH_SIZE):
            batch = prepared_tactics[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (len(prepared_tactics) + BATCH_SIZE - 1) // BATCH_SIZE
            batches.append((batch, batch_num, total_batches))
        
        all_enriched = []
        
        if self.dry_run:
            # In dry run, process one batch to show sample
            for batch, batch_num, total_batches in batches[:1]:
                print(f"🎨 Processing batch {batch_num}/{total_batches} ({len(batch)} tactics)...")
                print(f"   📝 Sample tactic: {batch[0]['title']}")
                enriched_batch = await self.enrich_tactic_batch(batch)
                
                # Print enriched sample
                if enriched_batch:
                    sample = enriched_batch[0]
                    print(f"   ✅ Enriched sample:")
                    print(f"      Summary: {sample['summary'][:100]}...")
                    print(f"      Skills: {sample['skills']}")
                    print(f"      Centre: {sample['centre_assignments']}")
                    print(f"      Wingers: {sample['winger_assignments']}")
                    print(f"      Defense: {sample['defense_assignments']}")
                    print(f"      Goalie: {sample['goalie_assignments']}")
                    print(f"      Teaching Points: {sample['teaching_points']}")
                
                all_enriched.extend(enriched_batch)
        else:
            # Process all batches asynchronously
            print(f"🎨 Processing {len(batches)} batches asynchronously...")
            
            # Create tasks for async processing
            tasks = []
            for batch, batch_num, total_batches in batches:
                task = self.enrich_tactic_batch(batch)
                tasks.append(task)
            
            # Execute all batches in parallel
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(batch_results):
                batch, batch_num, total_batches = batches[i]
                
                if isinstance(result, Exception):
                    print(f"❌ Batch {batch_num} failed: {result}")
                    # Create fallback entries
                    fallback_batch = [{
                        "tactic_name": tactic["title"],
                        "summary": "Summary not available due to enrichment error",
                        "skills": [],
                        "instructions": "Instructions not available due to enrichment error",
                        "centre_assignments": "N/A",
                        "winger_assignments": "N/A",
                        "defense_assignments": "N/A", 
                        "goalie_assignments": "N/A",
                        "teaching_points": [],
                        "raw_content": tactic["raw_content"],
                        "source": tactic["source"],
                        "original_data": tactic["original_data"],
                        "enrichment_error": str(result)
                    } for tactic in batch]
                    all_enriched.extend(fallback_batch)
                else:
                    print(f"✅ Batch {batch_num}/{total_batches} completed ({len(result)} tactics)")
                    all_enriched.extend(result)
                
                # Progress update
                progress = (len(all_enriched) / len(prepared_tactics)) * 100
                print(f"📊 Overall progress: {len(all_enriched)}/{len(prepared_tactics)} ({progress:.1f}%)")
                
                # Rate limiting delay between batches
                if i < len(batch_results) - 1:  # Don't delay after last batch
                    await asyncio.sleep(1)
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Processing completed in {elapsed_time:.1f} seconds")
        print(f"📊 Processed {len(all_enriched)} tactics total")
        
        return all_enriched
    
    def analyze_enrichment_quality(self, enriched_tactics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the quality of enrichment results."""
        if not enriched_tactics:
            return {}
        
        # Count non-empty fields
        field_completeness = {}
        required_fields = ['summary', 'skills', 'instructions', 'teaching_points']
        assignment_fields = ['centre_assignments', 'winger_assignments', 'defense_assignments', 'goalie_assignments']
        
        for field in required_fields + assignment_fields:
            non_empty = 0
            for tactic in enriched_tactics:
                value = tactic.get(field, "")
                if field in assignment_fields:
                    # For assignment fields, "N/A" is considered complete
                    if value and value != "":
                        non_empty += 1
                else:
                    # For other fields, check if actually has content
                    if value and (isinstance(value, str) and value.strip()) or (isinstance(value, list) and value):
                        non_empty += 1
            
            percentage = (non_empty / len(enriched_tactics)) * 100
            field_completeness[field] = {
                'count': non_empty,
                'percentage': percentage
            }
        
        # Count skills distribution
        skills_distribution = {}
        for tactic in enriched_tactics:
            for skill in tactic.get('skills', []):
                skills_distribution[skill] = skills_distribution.get(skill, 0) + 1
        
        # Count errors
        error_count = sum(1 for tactic in enriched_tactics if 'enrichment_error' in tactic)
        
        return {
            'total_tactics': len(enriched_tactics),
            'field_completeness': field_completeness,
            'skills_distribution': dict(sorted(skills_distribution.items(), key=lambda x: x[1], reverse=True)),
            'enrichment_errors': error_count
        }
    
    def save_enriched_tactics(self, enriched_tactics: List[Dict[str, Any]]) -> str:
        """Save enriched tactics to timestamped file."""
        if self.dry_run:
            print(f"\n🔍 DRY RUN: Would save {len(enriched_tactics)} enriched tactics")
            return "dry-run-output"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = PROCESSED_DIR / f"tactics_enriched_{timestamp}.json"
        
        # Ensure processed directory exists
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_tactics, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Saved enriched tactics to: {output_file}")
        return str(output_file)

async def main():
    parser = argparse.ArgumentParser(description="Enrich hockey tactics data using OpenAI API")
    parser.add_argument(
        "--input",
        type=Path,
        help="Input file path (default: chroma_load/raw/tactics/tactics_raw_rows.json)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process and print first k tactics for verification"
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=5,
        help="Number of tactics to process in dry-run mode (default: 5)"
    )
    
    args = parser.parse_args()
    
    print("🏒 Hockey Tactics Enrichment Script")
    print("=" * 50)
    print(f"Model: {args.model}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL PROCESSING'}")
    if args.dry_run:
        print(f"Preview count: {args.preview_count} tactics")
    
    enricher = TacticsEnricher(
        model=args.model,
        dry_run=args.dry_run,
        preview_count=args.preview_count
    )
    
    try:
        # Load raw tactics
        raw_tactics = enricher.load_raw_tactics(args.input)
        
        if not raw_tactics:
            print("❌ No tactics found!")
            return
            
        # Process tactics
        enriched_tactics = await enricher.process_tactics(raw_tactics)
        
        # Analyze quality
        quality_analysis = enricher.analyze_enrichment_quality(enriched_tactics)
        
        # Save results
        output_file = enricher.save_enriched_tactics(enriched_tactics)
        
        # Print summary
        print(f"\n📋 ENRICHMENT SUMMARY")
        print("=" * 50)
        print(f"Records processed: {quality_analysis.get('total_tactics', 0)}")
        
        if 'field_completeness' in quality_analysis:
            print(f"\nField Completeness:")
            for field, stats in quality_analysis['field_completeness'].items():
                print(f"  {field}: {stats['count']}/{quality_analysis['total_tactics']} ({stats['percentage']:.1f}%)")
        
        if 'skills_distribution' in quality_analysis:
            print(f"\nSkills Distribution:")
            for skill, count in list(quality_analysis['skills_distribution'].items())[:10]:
                print(f"  {skill}: {count}")
        
        if quality_analysis.get('enrichment_errors', 0) > 0:
            print(f"\nEnrichment Errors: {quality_analysis['enrichment_errors']}")
        
        # Show sample records
        if enriched_tactics and not args.dry_run:
            print(f"\nSample Records:")
            for i, tactic in enumerate(enriched_tactics[:2], 1):
                print(f"\n{i}. {tactic['tactic_name']}")
                print(f"   Skills: {tactic['skills']}")
                print(f"   Summary: {tactic['summary'][:100]}...")
        
        print(f"\nOutput location: {output_file}")
        print(f"Model used: {args.model}")
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to process all tactics")
        else:
            print(f"\n✅ ENRICHMENT COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
