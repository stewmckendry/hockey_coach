#!/usr/bin/env python3
"""Test script to validate LTAD skill enrichment with specific technical skills."""

import asyncio
import json
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the enricher class
from chroma_load.scripts.enrich_ltad_skills import SkillEnricher

async def test_specific_skills():
    """Test enrichment with specific technical skills."""
    
    # Load skills and filter to specific technical ones
    raw_file = Path("chroma_load/raw/ltad/ltad_raw_skill_rows.json")
    with open(raw_file, 'r') as f:
        all_skills = json.load(f)
    
    # Find some specific technical skills to test
    specific_skills = []
    for skill in all_skills:
        skill_name = skill.get('skill_name', '').lower()
        if any(tech_skill in skill_name for tech_skill in [
            't-push', 'c-cut', 'shuffle', 'pivot', 'crossover', 'butterfly', 
            'wrist shot', 'backhand', 'forehand', 'stick handling'
        ]):
            specific_skills.append(skill)
            if len(specific_skills) >= 5:  # Test with 5 specific skills
                break
    
    print(f"🧪 Testing with {len(specific_skills)} specific technical skills:")
    for i, skill in enumerate(specific_skills):
        print(f"   {i+1}. {skill['skill_name']} ({skill['skill_category']})")
    
    if not specific_skills:
        print("❌ No specific technical skills found to test")
        return
    
    # Create enricher and test
    enricher = SkillEnricher(model="gpt-4o", dry_run=True)
    
    # Process the specific skills
    enriched = await enricher.process_skills(specific_skills)
    
    print(f"\n📊 Results:")
    print(f"   Enriched: {len(enriched)} skills")
    print(f"   Skipped: {len(enricher.skipped_skills)} skills")
    
    if enriched:
        print(f"\n✅ Sample enriched skill:")
        sample = enriched[0]
        print(f"   Name: {sample['skill_name']}")
        print(f"   Category: {sample['skill_category']}")
        print(f"   Age Group: {sample['age_group']}")
        print(f"   Complexity: {sample['complexity']}")
        print(f"   Summary: {sample['summary'][:100]}...")
        print(f"   Instructions: {sample['instructions'][:200]}...")
        print(f"   Teaching Points: {sample['teaching_points']}")
        print(f"   Equipment: {sample['equipment']}")

if __name__ == "__main__":
    asyncio.run(test_specific_skills())
