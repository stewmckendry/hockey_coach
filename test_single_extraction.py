#!/usr/bin/env python3
"""
Test single file extraction to debug the save issue
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

async def test_single_file_extraction():
    """Test extraction on a single file and save to see what happens."""
    
    # Setup
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    html_file = Path("chroma_load/raw/ltad/html/Stick Checking Fundamentals.html")
    output_file = Path("test_extraction_output.json")
    prompt_file = Path("chroma_load/prompts/html_checking_extraction.txt")
    
    print(f"Testing single file extraction: {html_file.name}")
    
    # Extract HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    
    # Extract text from body
    body = soup.find('body')
    main_content = (
        body.find('main') or 
        body.find('div', class_='container') or
        body.find('div', class_='content') or
        body
    )
    
    # Get text and clean it up
    text = main_content.get_text(separator='\n', strip=True)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    content = '\n'.join(lines)
    
    # Limit content size for API efficiency
    if len(content) > 4000:
        content = content[:4000] + "\n[Content truncated for processing...]"
    
    print(f"Extracted {len(content)} characters of content")
    
    # Load prompt
    with open(prompt_file, 'r') as f:
        prompt = f.read()
    
    # Replace filename placeholder
    prompt = prompt.replace("[filename]", html_file.name)
    
    # Extract skills using OpenAI
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Extract checking skills from this HTML content:\n\n{content}"}
        ],
        response_format={"type": "json_object"}
    )
    
    result = response.choices[0].message.content
    skills_data = json.loads(result)
    
    print(f"OpenAI returned: {skills_data}")
    
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
    
    print(f"Parsed {len(skills)} skills")
    
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
            print(f"  Valid skill: {skill['skill_name']}")
        else:
            print(f"  Invalid skill: {skill}")
    
    print(f"Final valid skills: {len(valid_skills)}")
    
    # Test loading existing skills
    ltad_file = Path("chroma_load/raw/ltad/ltad_raw_skill_rows.json")
    print(f"\nLoading existing skills from {ltad_file}")
    
    with open(ltad_file, 'r', encoding='utf-8') as f:
        existing_skills = json.load(f)
    
    print(f"Loaded {len(existing_skills)} existing skills")
    
    # Combine
    all_skills = existing_skills + valid_skills
    print(f"Combined total: {len(all_skills)} skills")
    
    # Save test output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_skills, f, indent=2, ensure_ascii=False)
    
    print(f"Saved test output to {output_file}")
    
    # Check if checking skills are in the test file
    checking_count = sum(1 for skill in all_skills if skill.get('skill_category') == 'Checking')
    print(f"Checking skills in output: {checking_count}")
    
    return valid_skills

if __name__ == "__main__":
    asyncio.run(test_single_file_extraction())
