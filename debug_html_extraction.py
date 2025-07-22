#!/usr/bin/env python3
"""
Debug version of HTML Skills Extraction Script
"""

import asyncio
import json
import time
from pathlib import Path
import os
from dotenv import load_dotenv

from bs4 import BeautifulSoup
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

def test_html_extraction():
    """Test HTML content extraction from a single file."""
    html_file = Path("chroma_load/raw/ltad/html/Stick Checking Fundamentals.html")
    
    print(f"Testing HTML extraction from: {html_file}")
    print("=" * 50)
    
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
            
            print(f"Extracted content ({len(content)} chars):")
            print("-" * 30)
            print(content[:1000])
            print("-" * 30)
            if len(content) > 1000:
                print(f"[... {len(content) - 1000} more characters]")
            
            return content
        else:
            print("No body element found!")
            return ""
            
    except Exception as e:
        print(f"Error extracting content: {e}")
        return ""

async def test_openai_extraction():
    """Test OpenAI skill extraction."""
    print("\n" + "=" * 50)
    print("Testing OpenAI extraction...")
    
    # Get content
    content = test_html_extraction()
    if not content:
        print("No content to process!")
        return
    
    # Load prompt
    prompt_file = Path("chroma_load/prompts/html_checking_extraction.txt")
    with open(prompt_file, 'r') as f:
        prompt = f.read()
    
    # Replace filename placeholder
    prompt = prompt.replace("[filename]", "Stick Checking Fundamentals.html")
    
    print(f"\nSending {len(content)} characters to OpenAI...")
    
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Extract checking skills from this HTML content:\n\n{content}"}
            ],
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        print(f"\nOpenAI Response ({len(result)} chars):")
        print("-" * 30)
        print(result)
        
        # Parse JSON
        skills_data = json.loads(result)
        print(f"\nParsed JSON structure: {type(skills_data)}")
        print(f"Keys: {list(skills_data.keys()) if isinstance(skills_data, dict) else 'Not a dict'}")
        
        # Handle both array and object responses
        if isinstance(skills_data, dict):
            if 'skills' in skills_data:
                skills = skills_data['skills']
            elif 'data' in skills_data:
                skills = skills_data['data']
            else:
                skills = []
        elif isinstance(skills_data, list):
            skills = skills_data
        else:
            skills = []
        
        print(f"\nExtracted {len(skills)} skills:")
        for i, skill in enumerate(skills, 1):
            if isinstance(skill, dict):
                print(f"{i}. {skill.get('skill_name', 'Unknown')} - {skill.get('skill_category', 'Unknown')}")
                print(f"   Description: {skill.get('raw_description', '')[:100]}...")
            else:
                print(f"{i}. Invalid skill format: {type(skill)}")
        
        return skills
        
    except Exception as e:
        print(f"Error with OpenAI extraction: {e}")
        return []

async def main():
    """Run debug tests."""
    print("HTML Skills Extraction Debug")
    print("=" * 50)
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Test extraction
    skills = await test_openai_extraction()
    
    print(f"\n" + "=" * 50)
    print(f"Debug Summary: Extracted {len(skills)} skills from test file")

if __name__ == "__main__":
    asyncio.run(main())
