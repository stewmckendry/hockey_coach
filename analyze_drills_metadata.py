import json
import sys
from collections import defaultdict

def analyze_drill_metadata(file_path):
    """Analyze metadata fields in drills.json and count empty vs completed fields."""
    
    # Load the JSON data
    with open(file_path, 'r', encoding='utf-8') as f:
        drills = json.load(f)
    
    # Initialize counters for each field
    field_stats = defaultdict(lambda: {'empty': 0, 'completed': 0, 'total': 0})
    
    def is_empty_value(value):
        """Check if a value is considered empty."""
        if value is None:
            return True
        if isinstance(value, str) and (value.strip() == "" or value.strip().lower() == "unknown"):
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        return False
    
    # Analyze each drill
    for drill in drills:
        for field, value in drill.items():
            field_stats[field]['total'] += 1
            
            if is_empty_value(value):
                field_stats[field]['empty'] += 1
            else:
                field_stats[field]['completed'] += 1
    
    # Print results
    total_drills = len(drills)
    print(f"Analysis of {total_drills:,} drills from {file_path}")
    print("=" * 80)
    print(f"{'Field Name':<20} {'Empty':<8} {'Completed':<10} {'Total':<8} {'% Complete':<12}")
    print("-" * 80)
    
    # Sort fields by completion percentage (lowest first)
    sorted_fields = sorted(field_stats.items(), 
                          key=lambda x: (x[1]['completed'] / x[1]['total']) * 100)
    
    for field, stats in sorted_fields:
        empty = stats['empty']
        completed = stats['completed']
        total = stats['total']
        pct_complete = (completed / total) * 100 if total > 0 else 0
        
        print(f"{field:<20} {empty:<8,} {completed:<10,} {total:<8,} {pct_complete:<12.1f}%")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    total_fields = len(field_stats)
    fields_with_data = sum(1 for stats in field_stats.values() if stats['completed'] > 0)
    fields_mostly_empty = sum(1 for stats in field_stats.values() 
                             if (stats['completed'] / stats['total']) * 100 < 10)
    fields_mostly_complete = sum(1 for stats in field_stats.values() 
                                if (stats['completed'] / stats['total']) * 100 > 90)
    
    print(f"Total metadata fields: {total_fields}")
    print(f"Fields with any data: {fields_with_data}")
    print(f"Fields mostly empty (<10% complete): {fields_mostly_empty}")
    print(f"Fields mostly complete (>90% complete): {fields_mostly_complete}")
    
    # Most problematic fields (least complete)
    print(f"\nMOST PROBLEMATIC FIELDS (lowest completion rates):")
    print("-" * 50)
    for field, stats in sorted_fields[:5]:
        pct_complete = (stats['completed'] / stats['total']) * 100
        print(f"{field}: {pct_complete:.1f}% complete ({stats['completed']:,}/{stats['total']:,})")
    
    # Best fields (most complete)
    print(f"\nBEST FIELDS (highest completion rates):")
    print("-" * 50)
    for field, stats in sorted_fields[-5:]:
        pct_complete = (stats['completed'] / stats['total']) * 100
        print(f"{field}: {pct_complete:.1f}% complete ({stats['completed']:,}/{stats['total']:,})")

if __name__ == "__main__":
    file_path = "/Users/liammckendry/thunder_playbook/chroma_load/processed/drills.json"
    analyze_drill_metadata(file_path)
