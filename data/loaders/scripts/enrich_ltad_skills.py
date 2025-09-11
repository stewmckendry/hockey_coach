#!/usr/bin/env python3
"""
Hockey LTAD Skill Enrichment Script

This script loads raw LTAD skill data from JSON files, enriches them using OpenAI's API,
and saves the enhanced data with additional metadata for coaching purposes.
"""

import asyncio
import argparse
import json
import os
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys

from openai import AsyncOpenAI

# Configuration
BATCH_SIZE = 10  # Number of skills to process per API call
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Setup paths
SCRIPT_DIR = Path(__file__).parent
RAW_LTAD_DIR = SCRIPT_DIR.parent / "raw" / "ltad"
PROCESSED_DIR = SCRIPT_DIR.parent / "processed"
PROMPTS_DIR = SCRIPT_DIR.parent / "prompts"

class SkillEnricher:
    def __init__(self, model: str = "gpt-4o", dry_run: bool = False, preview_count: int = 5):
        self.client = AsyncOpenAI()
        self.model = model
        self.dry_run = dry_run
        self.preview_count = preview_count
        self.prompt = self._load_prompt()
        self.skipped_skills = []
        
    def _load_prompt(self) -> str:
        """Load the LTAD skill enrichment prompt."""
        prompt_file = PROMPTS_DIR / "ltad_skill_enrichment.txt"
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    def load_raw_skills(self) -> List[Dict[str, Any]]:
        """Load raw LTAD skill data from JSON file."""
        skill_file = RAW_LTAD_DIR / "ltad_raw_skill_rows.json"
        
        if skill_file.exists():
            print(f"📂 Loading {skill_file}...")
            with open(skill_file, 'r', encoding='utf-8') as f:
                skills = json.load(f)
                print(f"   Loaded {len(skills)} skills from LTAD data")
                return skills
        else:
            raise FileNotFoundError(f"LTAD skill file not found: {skill_file}")
    
    def derive_age_group(self, source: str, skill_category: str = "") -> str:
        """Derive age group from source field using specified rules."""
        source_lower = source.lower()
        
        # Rule 1: Look for U followed by number
        u_match = re.search(r'u(\d+)', source_lower)
        if u_match:
            return f"U{u_match.group(1)}"
        
        # Rule 2: Check for defence/defense
        if 'defence' in source_lower or 'defense' in source_lower:
            return "All Ages - Defence"
        
        # Rule 3: Check for goaltending
        if 'goaltending' in source_lower:
            return "All Ages - Goalies"
        
        # Rule 4: Check for checking skills
        if skill_category.lower() == 'checking':
            # Special case: Body Checking Drills.html is for U15
            if source.lower() == 'body checking drills.html':
                return "U15"
            else:
                return "All Ages - Checking"
        
        # Default
        return "All Ages"
    
    def prepare_skill_for_enrichment(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a skill record for enrichment."""
        
        # Derive age group from source and skill category
        age_group = self.derive_age_group(
            skill.get("source", ""), 
            skill.get("skill_category", "")
        )
        
        return {
            "skill_name": skill.get("skill_name", ""),
            "skill_category": skill.get("skill_category", ""),
            "raw_description": skill.get("raw_description", ""),
            "source": skill.get("source", ""),
            "age_group": age_group,
            "page_number": skill.get("page_number"),
            "section_title": skill.get("section_title", ""),
            "original_data": skill  # Keep original for reference
        }
    
    async def enrich_skill_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich a batch of skills using OpenAI API."""
        
        # Prepare skill data for the prompt
        skill_texts = []
        for i, skill in enumerate(batch):
            skill_text = f"""
SKILL {i+1}:
Skill Name: {skill['skill_name']}
Category: {skill['skill_category']}
Description: {skill['raw_description']}
Source: {skill['source']}
Section: {skill['section_title']}
"""
            skill_texts.append(skill_text.strip())
        
        batch_text = "\n\n" + "="*50 + "\n\n".join(skill_texts)
        
        full_prompt = f"""{self.prompt}

Here are {len(batch)} hockey skills to analyze and enrich:

{batch_text}

Please provide a JSON response with an array of {len(batch)} objects, each containing either the enriched metadata for specific skills or exclusion information for generic categories, in the same order as provided."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional hockey coach and LTAD expert."},
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
            
            # Process enriched data and separate included vs excluded skills
            enriched_skills = []
            for original_skill, enriched_meta in zip(batch, enriched_data):
                
                # Check if skill was excluded
                if enriched_meta.get("action") == "exclude":
                    self.skipped_skills.append({
                        "skill_name": enriched_meta.get("skill_name", original_skill["skill_name"]),
                        "reason": enriched_meta.get("skip_reason", "Generic category")
                    })
                    continue
                    
                # Create enriched skill record
                enriched_skill = {
                    "skill_name": original_skill["skill_name"],  # Hard-coded from source
                    "skill_category": original_skill["skill_category"], # Hard-coded from source
                    "age_group": original_skill["age_group"], # Derived from source
                    "source": original_skill["source"], # Hard-coded from source
                    "summary": enriched_meta.get("summary", ""),
                    "instructions": enriched_meta.get("instructions", ""),
                    "teaching_points": enriched_meta.get("teaching_points", []),
                    "equipment": enriched_meta.get("equipment", []),
                    "complexity": enriched_meta.get("complexity", 3),
                    "positions": enriched_meta.get("positions", []),
                    "original_data": original_skill["original_data"]
                }
                enriched_skills.append(enriched_skill)
                
            return enriched_skills
            
        except Exception as e:
            print(f"❌ Error enriching batch: {str(e)}")
            # Return original skills with minimal enrichment on error
            fallback_skills = []
            for skill in batch:
                # Only include if it looks like a specific skill (basic heuristic)
                skill_name = skill["skill_name"].lower()
                if not any(generic in skill_name for generic in [
                    "basic", "fundamental", "development", "program", "introduction", 
                    "understanding", "enhanced", "skills", "try", "objectives"
                ]):
                    fallback_skills.append({
                        "skill_name": skill["skill_name"],
                        "skill_category": skill["skill_category"], 
                        "age_group": skill["age_group"],
                        "source": skill["source"],
                        "summary": skill["raw_description"] or "Summary not available",
                        "instructions": "Instructions not available due to processing error", 
                        "teaching_points": [],
                        "equipment": [],
                        "complexity": 3,
                        "positions": [],
                        "original_data": skill["original_data"],
                        "enrichment_error": str(e)
                    })
                else:
                    self.skipped_skills.append({
                        "skill_name": skill["skill_name"],
                        "reason": f"Generic category (fallback) - {str(e)}"
                    })
            return fallback_skills
    
    async def process_skills(self, all_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process all skills with enrichment."""
        total_skills = len(all_skills)
        processed_count = 0
        
        print(f"\n🚀 Processing {total_skills} total skills...")
        if self.dry_run:
            print(f"🔍 DRY RUN MODE: Processing first {self.preview_count} skills for verification")
            all_skills = all_skills[:self.preview_count]
            
        start_time = time.time()
        
        # Prepare skills for enrichment
        prepared_skills = [
            self.prepare_skill_for_enrichment(skill) 
            for skill in all_skills
        ]
        
        # Create all batches first
        batches = []
        for i in range(0, len(prepared_skills), BATCH_SIZE):
            batch = prepared_skills[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (len(prepared_skills) + BATCH_SIZE - 1) // BATCH_SIZE
            batches.append((batch, batch_num, total_batches))
        
        all_enriched = []
        
        # Process batches
        if self.dry_run:
            # In dry run, process one batch to show sample
            for batch, batch_num, total_batches in batches[:1]:
                print(f"   🎨 Processing batch {batch_num}/{total_batches} ({len(batch)} skills)...")
                print(f"      📝 Sample skill: {batch[0]['skill_name']}")
                print(f"      📝 Age group derived: {batch[0]['age_group']}")
                enriched_batch = await self.enrich_skill_batch(batch)
                
                # Print enriched sample
                if enriched_batch:
                    sample = enriched_batch[0]
                    print(f"      ✅ Enriched sample:")
                    print(f"         Summary: {sample['summary'][:100]}...")
                    print(f"         Instructions: {sample['instructions'][:200]}...")
                    print(f"         Teaching Points: {sample['teaching_points']}")
                    print(f"         Equipment: {sample['equipment']}")
                    print(f"         Complexity: {sample['complexity']}")
                    print(f"         Age Group: {sample['age_group']}")
                    print(f"         Positions: {sample['positions']}")
                
                all_enriched.extend(enriched_batch)
                processed_count += len(batch)
        else:
            # Process all batches asynchronously
            print(f"   🎨 Processing {len(batches)} batches asynchronously...")
            
            # Create tasks for async processing
            tasks = []
            for batch, batch_num, total_batches in batches:
                task = self.enrich_skill_batch(batch)
                tasks.append(task)
            
            # Execute all batches in parallel
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(batch_results):
                batch, batch_num, total_batches = batches[i]
                
                if isinstance(result, Exception):
                    print(f"   ❌ Batch {batch_num} failed: {result}")
                    # Create fallback entries for specific skills only
                    fallback_batch = []
                    for skill in batch:
                        skill_name = skill["skill_name"].lower()
                        if not any(generic in skill_name for generic in [
                            "basic", "fundamental", "development", "program", "introduction", 
                            "understanding", "enhanced", "skills", "try", "objectives"
                        ]):
                            fallback_batch.append({
                                "skill_name": skill["skill_name"],
                                "skill_category": skill["skill_category"], 
                                "age_group": skill["age_group"],
                                "source": skill["source"],
                                "summary": skill["raw_description"] or "Summary not available",
                                "instructions": "Instructions not available due to processing error", 
                                "teaching_points": [],
                                "equipment": [],
                                "complexity": 3,
                                "positions": [],
                                "original_data": skill["original_data"],
                                "enrichment_error": str(result)
                            })
                        else:
                            self.skipped_skills.append({
                                "skill_name": skill["skill_name"],
                                "reason": f"Generic category (fallback) - {str(result)}"
                            })
                    all_enriched.extend(fallback_batch)
                else:
                    print(f"   ✅ Batch {batch_num}/{total_batches} completed ({len(result)} skills enriched)")
                    all_enriched.extend(result)
                
                processed_count += len(batch)
                
                # Progress update
                progress = (processed_count / len(prepared_skills)) * 100
                print(f"   📊 Progress: {processed_count}/{len(prepared_skills)} ({progress:.1f}%)")
                
                # Rate limiting delay between batches
                await asyncio.sleep(1)
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Processing completed in {elapsed_time:.1f} seconds")
        print(f"📊 Processed {len(all_enriched)} skills successfully")
        print(f"📊 Skipped {len(self.skipped_skills)} generic categories")
        
        return all_enriched
    
    def save_enriched_skills(self, enriched_skills: List[Dict[str, Any]]) -> str:
        """Save enriched skills to timestamped file."""
        if self.dry_run:
            print(f"\n🔍 DRY RUN: Would save {len(enriched_skills)} enriched skills")
            return "dry-run-output"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = PROCESSED_DIR / f"enriched_ltad_skills_{timestamp}.json"
        
        # Ensure processed directory exists
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_skills, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Saved enriched skills to: {output_file}")
        return str(output_file)

async def main():
    parser = argparse.ArgumentParser(description="Enrich hockey LTAD skill data using OpenAI API")
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process and print first k skills for verification"
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=5,
        help="Number of skills to process in dry-run mode (default: 5)"
    )
    
    args = parser.parse_args()
    
    print("🏒 Hockey LTAD Skill Enrichment Script")
    print("=" * 50)
    print(f"Model: {args.model}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL PROCESSING'}")
    if args.dry_run:
        print(f"Preview count: {args.preview_count} skills")
    
    enricher = SkillEnricher(
        model=args.model,
        dry_run=args.dry_run,
        preview_count=args.preview_count
    )
    
    try:
        # Load raw skills
        all_skills = enricher.load_raw_skills()
        
        if not all_skills:
            print("❌ No skill data found!")
            return
            
        # Process skills
        enriched_skills = await enricher.process_skills(all_skills)
        
        # Save results
        output_file = enricher.save_enriched_skills(enriched_skills)
        
        # Print summary
        total_enriched = len(enriched_skills)
        total_skipped = len(enricher.skipped_skills)
        
        print(f"\n📋 SUMMARY")
        print(f"Skills enriched: {total_enriched}")
        print(f"Generic categories skipped: {total_skipped}")
        print(f"Output location: {output_file}")
        print(f"Model used: {args.model}")
        
        if enricher.skipped_skills:
            print(f"\n📝 SKIPPED SKILLS:")
            for skip in enricher.skipped_skills[:10]:  # Show first 10
                print(f"   • {skip['skill_name']} - {skip['reason']}")
            if len(enricher.skipped_skills) > 10:
                print(f"   ... and {len(enricher.skipped_skills) - 10} more")
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - Run without --dry-run to process all skills")
        else:
            print(f"\n✅ ENRICHMENT COMPLETE")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
