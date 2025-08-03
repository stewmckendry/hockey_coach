#!/usr/bin/env python3
"""
Validate skills coverage between Notion page and Hockey Canada enriched LTAD skills data.
Compares skills extracted and organized in Notion against the official Hockey Canada curriculum.
"""

import json
from typing import Dict, List, Set, Tuple
import re

def load_enriched_skills(file_path: str) -> List[Dict]:
    """Load the enriched LTAD skills from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def filter_relevant_skills(skills: List[Dict]) -> List[Dict]:
    """Filter skills for U11, All Ages - Defence, or All Ages - Goalies."""
    filtered = []
    for skill in skills:
        age_group = skill.get('age_group', '')
        # Check if the age group matches our targets
        if age_group in ['U11', 'All Ages - Defence', 'All Ages - Goalies']:
            filtered.append(skill)
    return filtered

def extract_notion_skills() -> Dict[str, Set[str]]:
    """Extract skills from our Notion page organization."""
    # Based on the content we just created, manually extract the skills
    notion_skills = {
        "Core Skating Skills": {
            "Basic stance", "Stationary balance", "Lateral movement", "Jumping", "Change of pace",
            "Inside edges", "Outside edges", "Weight transfer", "Edge transitions",
            "Forward start", "Backward start", "Two-foot stop", "One-foot stop", "T-stop",
            "Stride development", "Arm swing", "Speed generation", "Gliding",
            "C-cuts", "Backward stride", "Backward crossovers", "Backward stops", "Backward to forward pivot",
            "Tight turns", "Wide turns", "Forward crossovers", "Backward crossovers", "Mohawk turns"
        },
        "Puck Handling Skills": {
            "Forehand control", "Backhand control", "Toe drags", "Figure-8 patterns", "Wide dribbling",
            "Puck control while skating", "Wide carries", "Narrow carries", "Change of pace with puck",
            "Basic fakes", "Stick fakes", "Body dekes", "Combined moves"
        },
        "Passing Skills": {
            "Forehand pass", "Backhand pass", "Saucer pass", "One-touch pass",
            "Passing while skating", "Give-and-go", "Leading passes", "Board passes",
            "Cushioning", "Forehand reception", "Backhand reception", "Skate-to-stick", "In-motion receiving"
        },
        "Shooting Skills": {
            "Wrist shot", "Backhand shot", "Snap shot", "Slap shot",
            "Shooting in stride", "Quick release", "Shot selection", "Accuracy over power", "Screen shots"
        },
        "Defensive Skills": {
            "Defensive stance", "Stick positioning", "Gap control", "Angling", "Stick checking", "Body positioning",
            "Backchecking", "Zone coverage", "Communication", "Support"
        },
        "Defence Position Skills": {
            "Backward skating mastery", "Backward starts", "Backward stops", "Transitions", "Escape moves",
            "Toe turns/pivots", "Lateral skating", "D-to-D passes", "Outlet passes", "Skating the puck",
            "Rim/reverse", "Regroup support", "Gap control", "Transition timing", "Point shots",
            "One-timers", "Shot fakes", "Walking the line", "Net-front positioning", "Corner battles",
            "Clearing rebounds", "Shot blocking"
        },
        "Goaltender Skills": {
            "Basic stance", "Butterfly stance", "Recovery", "Flexibility",
            "Shuffles", "C-cuts", "T-push", "Pivots", "Slides",
            "Angles", "Squareness", "Depth", "Tracking the puck", "Post integration",
            "Stick saves", "Glove saves", "Blocker saves", "Body saves", "Breakaways",
            "Rebound control", "Freezing pucks", "Stickhandling", "Passing"
        },
        "Hockey IQ & Team Play": {
            "2-on-1 execution", "3-on-2 patterns", "Cycling", "Net-front presence", "Creating space",
            "Winger responsibilities", "Center responsibilities", "Defence partnerships", "Support positioning",
            "Power play basics", "Penalty kill basics", "Faceoff positioning", "Line changes",
            "Anticipation", "Decision making", "Communication", "Awareness", "Teamwork"
        }
    }
    return notion_skills

def normalize_skill_name(skill: str) -> str:
    """Normalize skill name for comparison."""
    # Convert to lowercase, remove special characters, standardize spacing
    normalized = skill.lower()
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def compare_skills(notion_skills: Dict[str, Set[str]], hockey_canada_skills: List[Dict]) -> Dict:
    """Compare Notion skills against Hockey Canada skills."""
    # Flatten Notion skills for easier comparison
    all_notion_skills = set()
    for category, skills in notion_skills.items():
        all_notion_skills.update(normalize_skill_name(s) for s in skills)
    
    # Extract Hockey Canada skill names and categories
    hc_skills_by_category = {}
    all_hc_skills = set()
    
    for skill in hockey_canada_skills:
        skill_name = skill.get('skill_name', '')
        category = skill.get('skill_category', 'Uncategorized')
        age_group = skill.get('age_group', '')
        
        normalized_name = normalize_skill_name(skill_name)
        all_hc_skills.add(normalized_name)
        
        if category not in hc_skills_by_category:
            hc_skills_by_category[category] = []
        hc_skills_by_category[category].append({
            'name': skill_name,
            'normalized': normalized_name,
            'age_group': age_group
        })
    
    # Calculate coverage
    covered_skills = all_notion_skills.intersection(all_hc_skills)
    missing_skills = all_hc_skills - all_notion_skills
    extra_skills = all_notion_skills - all_hc_skills
    
    coverage_percentage = len(covered_skills) / len(all_hc_skills) * 100 if all_hc_skills else 0
    
    return {
        'coverage_percentage': coverage_percentage,
        'total_hc_skills': len(all_hc_skills),
        'total_notion_skills': len(all_notion_skills),
        'covered_skills': len(covered_skills),
        'missing_skills': missing_skills,
        'extra_skills': extra_skills,
        'hc_skills_by_category': hc_skills_by_category,
        'notion_categories': list(notion_skills.keys())
    }

def generate_report(comparison: Dict) -> str:
    """Generate a detailed coverage report."""
    report = []
    report.append("=" * 80)
    report.append("SKILLS COVERAGE VALIDATION REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary statistics
    report.append("SUMMARY")
    report.append("-" * 40)
    report.append(f"Coverage Percentage: {comparison['coverage_percentage']:.1f}%")
    report.append(f"Total Hockey Canada Skills: {comparison['total_hc_skills']}")
    report.append(f"Total Notion Skills: {comparison['total_notion_skills']}")
    report.append(f"Covered Skills: {comparison['covered_skills']}")
    report.append(f"Missing from Notion: {len(comparison['missing_skills'])}")
    report.append(f"Extra in Notion: {len(comparison['extra_skills'])}")
    report.append("")
    
    # Missing skills by category
    if comparison['missing_skills']:
        report.append("MISSING SKILLS FROM HOCKEY CANADA CURRICULUM")
        report.append("-" * 40)
        
        # Organize missing skills by category
        missing_by_category = {}
        for category, skills in comparison['hc_skills_by_category'].items():
            missing_in_category = []
            for skill in skills:
                if skill['normalized'] in comparison['missing_skills']:
                    missing_in_category.append(f"{skill['name']} ({skill['age_group']})")
            if missing_in_category:
                missing_by_category[category] = missing_in_category
        
        for category, skills in missing_by_category.items():
            report.append(f"\n{category}:")
            for skill in skills:
                report.append(f"  - {skill}")
        report.append("")
    
    # Extra skills (not in Hockey Canada)
    if comparison['extra_skills']:
        report.append("ADDITIONAL SKILLS IN NOTION (Not in Hockey Canada dataset)")
        report.append("-" * 40)
        for skill in sorted(comparison['extra_skills']):
            report.append(f"  - {skill}")
        report.append("")
    
    # Category mapping
    report.append("CATEGORY ALIGNMENT")
    report.append("-" * 40)
    report.append("Hockey Canada Categories:")
    for category in sorted(comparison['hc_skills_by_category'].keys()):
        count = len(comparison['hc_skills_by_category'][category])
        report.append(f"  - {category}: {count} skills")
    report.append("\nNotion Categories:")
    for category in comparison['notion_categories']:
        report.append(f"  - {category}")
    
    return "\n".join(report)

def main():
    """Main execution function."""
    # Load Hockey Canada skills
    skills_file = "/Users/liammckendry/thunder_playbook/chroma_load/processed/ltad/enriched_ltad_skills_20250722_195101.json"
    
    print("Loading Hockey Canada enriched skills data...")
    all_skills = load_enriched_skills(skills_file)
    
    print("Filtering for U11, All Ages - Defence, and All Ages - Goalies...")
    relevant_skills = filter_relevant_skills(all_skills)
    print(f"Found {len(relevant_skills)} relevant skills")
    
    print("\nExtracting Notion skills organization...")
    notion_skills = extract_notion_skills()
    
    print("\nComparing skills coverage...")
    comparison = compare_skills(notion_skills, relevant_skills)
    
    # Generate and print report
    report = generate_report(comparison)
    print("\n" + report)
    
    # Save report to file
    report_file = "/Users/liammckendry/thunder_playbook/scripts/skills_coverage_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")
    
    # Return coverage percentage for decision making
    return comparison['coverage_percentage']

if __name__ == "__main__":
    coverage = main()
    if coverage < 80:
        print(f"\n⚠️  WARNING: Coverage is below 80% ({coverage:.1f}%). Consider adding missing skills.")
    else:
        print(f"\n✅ Good coverage: {coverage:.1f}%")