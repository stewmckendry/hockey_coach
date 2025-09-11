#!/usr/bin/env python3
"""
Hockey Tactics Extraction Script

This script extracts hockey tactics from HTML and PDF files, using OpenAI API to identify
and structure tactical content into JSON records.
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

# Try to import PyPDF2, but handle gracefully if not available
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 not available - PDF processing will be skipped")

# Load environment variables
load_dotenv()

class TacticsExtractor:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Get the script directory and construct paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        
        self.html_dir = project_root / "chroma_load/raw/tactics/html"
        self.pdf_dir = project_root / "chroma_load/raw/tactics/pdf" 
        self.output_file = project_root / "chroma_load/raw/tactics/tactics_raw_rows.json"
        self.prompt_file = project_root / "chroma_load/prompts/tactics_extraction.txt"
        
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
                
                # Increase content size limit for tactics (roughly 12000 chars)
                if len(content) > 12000:
                    content = content[:12000] + "\n[Content truncated for processing...]"
                
                return content
            else:
                return soup.get_text(separator='\n', strip=True)[:12000]
                
        except Exception as e:
            print(f"Error extracting content from {html_file}: {e}")
            return ""
    
    def extract_pdf_content(self, pdf_file: Path) -> str:
        """Extract content from PDF file."""
        if not PDF_AVAILABLE:
            print(f"PyPDF2 not available, skipping PDF: {pdf_file}")
            return ""
            
        try:
            with open(pdf_file, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                # Clean up and limit content
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                content = '\n'.join(lines)
                
                if len(content) > 12000:
                    content = content[:12000] + "\n[Content truncated for processing...]"
                
                return content
                
        except Exception as e:
            print(f"Error extracting content from {pdf_file}: {e}")
            return ""
    
    async def extract_tactics_from_content(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Use OpenAI API to extract tactics from content."""
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
                    {"role": "user", "content": f"Extract hockey tactics from this content:\n\n{content}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            tactics_data = json.loads(result)
            
            # Handle different response formats
            if isinstance(tactics_data, dict):
                # Check if it's a single tactic object (has title and raw_content)
                if 'title' in tactics_data and 'raw_content' in tactics_data:
                    return [tactics_data]  # Wrap single tactic in a list
                # Check if it's a container with tactics array
                elif 'tactics' in tactics_data:
                    return tactics_data['tactics']
                elif 'data' in tactics_data:
                    return tactics_data['data']
                else:
                    return []
            elif isinstance(tactics_data, list):
                return tactics_data
            else:
                return []
                
        except Exception as e:
            print(f"Error extracting tactics from {filename}: {e}")
            return []
    
    async def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a single file and extract tactics."""
        print(f"Processing: {file_path.name}")
        
        # Extract content based on file type
        if file_path.suffix.lower() == '.html':
            content = self.extract_html_content(file_path)
        elif file_path.suffix.lower() == '.pdf':
            content = self.extract_pdf_content(file_path)
        else:
            print(f"  Unsupported file type: {file_path.suffix}")
            return []
        
        if not content:
            print(f"  No content extracted from {file_path.name}")
            return []
        
        # Extract tactics using OpenAI
        tactics = await self.extract_tactics_from_content(content, file_path.name)
        
        # Validate and clean tactics
        valid_tactics = []
        for tactic in tactics:
            if (isinstance(tactic, dict) and 
                tactic.get('title', '').strip() and
                tactic.get('raw_content', '').strip()):
                
                # Ensure required fields
                tactic['source'] = file_path.name
                
                valid_tactics.append(tactic)
        
        print(f"  Extracted {len(valid_tactics)} tactics from {file_path.name}")
        return valid_tactics
    
    def load_existing_tactics(self) -> List[Dict[str, Any]]:
        """Load existing tactics from the output file."""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading existing tactics: {e}")
                return []
        return []
    
    def save_tactics(self, all_tactics: List[Dict[str, Any]]):
        """Save all tactics to the output file."""
        if self.dry_run:
            print(f"DRY RUN: Would save {len(all_tactics)} total tactics to {self.output_file}")
            return
        
        try:
            # Create output directory if it doesn't exist
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            if self.output_file.exists():
                backup_file = self.output_file.with_suffix('.backup.json')
                import shutil
                shutil.copy2(self.output_file, backup_file)
                print(f"Created backup: {backup_file}")
            
            # Save updated tactics with explicit encoding
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(all_tactics, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(all_tactics)} total tactics to {self.output_file}")
            
        except Exception as e:
            print(f"Error saving tactics: {e}")
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
        
        # Find all HTML and PDF files
        html_files = list(self.html_dir.glob("*.html")) if self.html_dir.exists() else []
        pdf_files = list(self.pdf_dir.glob("*.pdf")) if self.pdf_dir.exists() else []
        all_files = html_files + pdf_files
        
        if not all_files:
            print(f"No HTML or PDF files found in:")
            print(f"  HTML: {self.html_dir}")
            print(f"  PDF: {self.pdf_dir}")
            return
        
        print(f"Found {len(all_files)} files to process ({len(html_files)} HTML, {len(pdf_files)} PDF)")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE PROCESSING'}")
        print("-" * 50)
        
        # Load existing tactics
        existing_tactics = self.load_existing_tactics()
        print(f"Loaded {len(existing_tactics)} existing tactics")
        
        # Process files in parallel (with limited concurrency)
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
        
        async def process_with_semaphore(file_path):
            async with semaphore:
                return await self.process_file(file_path)
        
        # Process all files
        tasks = [process_with_semaphore(file_path) for file_path in all_files]
        results = await asyncio.gather(*tasks)
        
        # Combine all extracted tactics
        new_tactics = []
        for tactics_list in results:
            new_tactics.extend(tactics_list)
        
        # Combine with existing tactics
        all_tactics = existing_tactics + new_tactics
        
        # Remove duplicates based on title and source
        seen = set()
        deduplicated_tactics = []
        for tactic in all_tactics:
            key = (tactic.get('title', ''), tactic.get('source', ''))
            if key not in seen:
                seen.add(key)
                deduplicated_tactics.append(tactic)
        
        removed_duplicates = len(all_tactics) - len(deduplicated_tactics)
        if removed_duplicates > 0:
            print(f"Removed {removed_duplicates} duplicate tactics")
        
        # Save results
        self.save_tactics(deduplicated_tactics)
        
        # Print summary
        end_time = time.time()
        processing_time = end_time - start_time
        
        print("\n" + "=" * 50)
        print("PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Files processed: {len(all_files)}")
        print(f"  HTML files: {len(html_files)}")
        print(f"  PDF files: {len(pdf_files)}")
        print(f"New tactics extracted: {len(new_tactics)}")
        print(f"Total tactics in database: {len(deduplicated_tactics)}")
        print(f"Processing time: {processing_time:.1f} seconds")
        print(f"Output file: {self.output_file}")
        
        if self.dry_run:
            print("\nDRY RUN - No files were modified")
            # Show sample of extracted tactics
            if new_tactics:
                print(f"\nSample extracted tactics:")
                for i, tactic in enumerate(new_tactics[:3], 1):
                    print(f"{i}. {tactic.get('title', 'Unknown')} ({tactic.get('source', 'Unknown')})")

def main():
    parser = argparse.ArgumentParser(description="Extract hockey tactics from HTML and PDF files")
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
    extractor = TacticsExtractor(dry_run=args.dry_run)
    asyncio.run(extractor.run())

if __name__ == "__main__":
    main()
