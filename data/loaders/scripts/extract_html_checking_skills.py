#!/usr/bin/env python3
"""
HTML Skills Extraction Script

This script extracts hockey checking skills from HTML files and appends them to the LTAD skills database.
It processes HTML files in parallel using async/await for improved performance.
"""

import asyncio
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

from bs4 import BeautifulSoup
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

class HTMLSkillExtractor:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Get the script directory and construct paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        
        self.html_dir = project_root / "chroma_load/raw/ltad/html"
        self.output_file = project_root / "chroma_load/raw/ltad/ltad_raw_skill_rows.json"
        self.prompt_file = project_root / "chroma_load/prompts/html_checking_extraction.txt"
        
    def extract_html_content(self, html_file: Path) -> str:
        """Extract meaningful content from HTML file using BeautifulSoup."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Extract text from body or main content areas
            body = soup.find('body')
            if body:
                # Look for main content containers
                main_content = (
                    body.find('main') or 
                    body.find('div', class_='container') or
                    body.find('div', class_='content') or
                    body
                )
                
                # Get text and clean it up
                text = main_content.get_text(separator='\n', strip=True)
                
                # Clean up excessive whitespace
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                content = '\n'.join(lines)
                
                # Increase content size limit for better extraction (roughly 8000 chars)
                if len(content) > 8000:
                    content = content[:8000] + "\n[Content truncated for processing...]"
                
                return content
            else:
                return soup.get_text(separator='\n', strip=True)[:4000]
                
        except Exception as e:
            print(f"Error extracting content from {html_file}: {e}")
            return ""
    
    async def extract_skills_from_content(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Use OpenAI API to extract skills from HTML content."""
        try:
            # Load prompt
            with open(self.prompt_file, 'r') as f:
                prompt = f.read()
            
            # Replace filename placeholder in prompt
            prompt = prompt.replace("[filename]", filename)
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Extract checking skills from this HTML content:\n\n{content}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            skills_data = json.loads(result)
            
            # Handle both array and object responses
            if isinstance(skills_data, dict):
                if 'skills' in skills_data:
                    return skills_data['skills']
                elif 'data' in skills_data:
                    return skills_data['data']
                else:
                    return []
            elif isinstance(skills_data, list):
                return skills_data
            else:
                return []
                
        except Exception as e:
            print(f"Error extracting skills from {filename}: {e}")
            return []
    
    async def process_html_file(self, html_file: Path) -> List[Dict[str, Any]]:
        """Process a single HTML file and extract skills."""
        print(f"Processing: {html_file.name}")
        
        # Extract HTML content
        content = self.extract_html_content(html_file)
        if not content:
            print(f"  No content extracted from {html_file.name}")
            return []
        
        # Extract skills using OpenAI
        skills = await self.extract_skills_from_content(content, html_file.name)
        
        # Validate and clean skills
        valid_skills = []
        for skill in skills:
            if (isinstance(skill, dict) and 
                skill.get('skill_name', '').strip() and
                skill.get('skill_category', '').strip() and 
                skill.get('raw_description', '').strip()):
                
                # Ensure required fields
                skill['skill_category'] = 'Checking'
                skill['source'] = html_file.name
                skill['page_number'] = 'N/A'
                skill['section_title'] = 'N/A'
                
                valid_skills.append(skill)
        
        print(f"  Extracted {len(valid_skills)} skills from {html_file.name}")
        return valid_skills
    
    def load_existing_skills(self) -> List[Dict[str, Any]]:
        """Load existing skills from the output file."""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading existing skills: {e}")
                return []
        return []
    
    def save_skills(self, all_skills: List[Dict[str, Any]]):
        """Save all skills to the output file."""
        if self.dry_run:
            print(f"DRY RUN: Would save {len(all_skills)} total skills to {self.output_file}")
            return
        
        try:
            # Create backup
            if self.output_file.exists():
                backup_file = self.output_file.with_suffix('.backup.json')
                import shutil
                shutil.copy2(self.output_file, backup_file)
                print(f"Created backup: {backup_file}")
            
            # Save updated skills with explicit encoding
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(all_skills, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(all_skills)} total skills to {self.output_file}")
            
        except Exception as e:
            print(f"Error saving skills: {e}")
            # Restore from backup if available
            backup_file = self.output_file.with_suffix('.backup.json')
            if backup_file.exists():
                import shutil
                shutil.copy2(backup_file, self.output_file)
                print(f"Restored from backup due to error")
            raise
    
    async def run(self):
        """Main execution function."""
        start_time = time.time()
        
        # Find all HTML files
        html_files = list(self.html_dir.glob("*.html"))
        if not html_files:
            print(f"No HTML files found in {self.html_dir}")
            return
        
        print(f"Found {len(html_files)} HTML files to process")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE PROCESSING'}")
        print("-" * 50)
        
        # Load existing skills
        existing_skills = self.load_existing_skills()
        print(f"Loaded {len(existing_skills)} existing skills")
        
        # Process HTML files in parallel (with limited concurrency)
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
        
        async def process_with_semaphore(html_file):
            async with semaphore:
                return await self.process_html_file(html_file)
        
        # Process all files
        tasks = [process_with_semaphore(html_file) for html_file in html_files]
        results = await asyncio.gather(*tasks)
        
        # Combine all extracted skills
        new_skills = []
        for skills_list in results:
            new_skills.extend(skills_list)
        
        # Combine with existing skills
        all_skills = existing_skills + new_skills
        
        # Remove duplicates based on skill_name and source
        seen = set()
        deduplicated_skills = []
        for skill in all_skills:
            key = (skill.get('skill_name', ''), skill.get('source', ''))
            if key not in seen:
                seen.add(key)
                deduplicated_skills.append(skill)
        
        removed_duplicates = len(all_skills) - len(deduplicated_skills)
        if removed_duplicates > 0:
            print(f"Removed {removed_duplicates} duplicate skills")
        
        # Save results
        self.save_skills(deduplicated_skills)
        
        # Print summary
        end_time = time.time()
        processing_time = end_time - start_time
        
        print("\n" + "=" * 50)
        print("PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Files processed: {len(html_files)}")
        print(f"New skills extracted: {len(new_skills)}")
        print(f"Total skills in database: {len(deduplicated_skills)}")
        print(f"Processing time: {processing_time:.1f} seconds")
        print(f"Output file: {self.output_file}")
        
        if self.dry_run:
            print("\nDRY RUN - No files were modified")
            # Show sample of extracted skills
            if new_skills:
                print(f"\nSample extracted skills:")
                for i, skill in enumerate(new_skills[:3], 1):
                    print(f"{i}. {skill.get('skill_name', 'Unknown')} ({skill.get('source', 'Unknown')})")

def main():
    parser = argparse.ArgumentParser(description="Extract hockey checking skills from HTML files")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Preview output without modifying files"
    )
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Run the extractor
    extractor = HTMLSkillExtractor(dry_run=args.dry_run)
    asyncio.run(extractor.run())

if __name__ == "__main__":
    main()
