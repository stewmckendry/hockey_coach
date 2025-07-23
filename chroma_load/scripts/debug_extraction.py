#!/usr/bin/env python3
"""
Test script to debug tactics extraction for specific files
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import AsyncOpenAI

load_dotenv()

async def test_single_file(filename):
    """Test extraction on a single file to debug the issue."""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    html_file = project_root / "chroma_load/raw/tactics/html" / filename
    prompt_file = project_root / "chroma_load/prompts/tactics_extraction.txt"
    
    # Extract content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    
    # Extract text from body
    body = soup.find('body')
    if body:
        text = body.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        content = '\n'.join(lines)
        
        if len(content) > 12000:
            content = content[:12000] + "\n[Content truncated for processing...]"
    else:
        content = soup.get_text(separator='\n', strip=True)[:12000]
    
    print(f"Extracted content from {filename}:")
    print("-" * 50)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("-" * 50)
    
    # Load prompt
    with open(prompt_file, 'r') as f:
        prompt = f.read()
    
    prompt = prompt.replace("[filename]", filename)
    
    # Call OpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Extract hockey tactics from this content:\n\n{content}"}
            ],
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        print(f"\nOpenAI Response for {filename}:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        tactics_data = json.loads(result)
        print(f"\nParsed JSON structure:")
        print(type(tactics_data))
        print(tactics_data.keys() if isinstance(tactics_data, dict) else f"List length: {len(tactics_data)}")
        
        # Handle response format (updated logic)
        if isinstance(tactics_data, dict):
            # Check if it's a single tactic object (has title and raw_content)
            if 'title' in tactics_data and 'raw_content' in tactics_data:
                tactics = [tactics_data]  # Wrap single tactic in a list
            # Check if it's a container with tactics array
            elif 'tactics' in tactics_data:
                tactics = tactics_data['tactics']
            elif 'data' in tactics_data:
                tactics = tactics_data['data']
            else:
                tactics = []
        elif isinstance(tactics_data, list):
            tactics = tactics_data
        else:
            tactics = []
        
        print(f"\nExtracted {len(tactics)} tactics")
        for i, tactic in enumerate(tactics, 1):
            print(f"{i}. {tactic.get('title', 'No title')}")
            
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Test multiple files that failed extraction."""
    test_files = [
        "1-2-2_forecheck.html",
        "neutral_zone_trap.html", 
        "power_play_diamond.html"
    ]
    
    for filename in test_files:
        print(f"\n{'='*60}")
        print(f"TESTING: {filename}")
        print(f"{'='*60}")
        await test_single_file(filename)
        
if __name__ == "__main__":
    asyncio.run(main())
