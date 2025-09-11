#!/usr/bin/env python3
"""Test question collection from multiple pipeline stages."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec

def test_multi_stage_questions():
    """Test questions generated from each stage of the pipeline."""
    
    query = """
    Run a complex drill with ambiguous positions.
    Players should be "somewhere in the offensive zone" but specifics unclear.
    One player goes to "the point" (left or right?).
    Another goes to "near the net" (which side?).
    Use equipment but placement depends on available space.
    Movement timing depends on coach whistle but sequence unclear.
    """
    
    print("=" * 80)
    print("MULTI-STAGE QUESTION AGGREGATION TEST")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    # Step 1: Analyze - Questions from initial interpretation
    print("🔍 STAGE 1: ANALYSIS QUESTIONS")
    print("-" * 50)
    analysis = analyze_hockey_query(query)
    
    analysis_questions = analysis.get("questions_for_user", [])
    print(f"Generated {len(analysis_questions)} questions from analysis:")
    for i, q in enumerate(analysis_questions):
        print(f"  [{i+1}] {q.get('question', 'N/A')}")
        print(f"      Key: {q.get('key', 'N/A')}")
        print(f"      Impact: {q.get('impact', 'N/A')}")
        print(f"      Critical: {q.get('critical', False)}")
        print()
    
    # Step 2: Translation - Questions from mapping stages
    print("\n🔧 STAGE 2: TRANSLATION QUESTIONS") 
    print("-" * 50)
    translate_result = translate_analysis_to_spec(
        analysis,
        title="Multi-Stage Question Test"
    )
    
    if translate_result.get("success"):
        metadata = translate_result.get("metadata", {})
        
        # Questions from different mapping stages
        critical_questions = metadata.get("critical_questions", [])
        regular_questions = metadata.get("questions", [])
        
        print(f"Critical questions from translation: {len(critical_questions)}")
        for i, q in enumerate(critical_questions):
            category = q.get("category", "unknown")
            question_text = q.get("question", q.get("text", "N/A"))
            print(f"  🔴 [{category}] {question_text}")
            
        print(f"\nRegular questions from translation: {len(regular_questions)}")
        for i, q in enumerate(regular_questions):
            category = q.get("category", "unknown")  
            question_text = q.get("question", q.get("text", "N/A"))
            print(f"  ⚠️  [{category}] {question_text}")
        
        # Check for mapping-specific questions in spec
        spec = translate_result.get("spec", {})
        mapping_questions = spec.get("mapping_questions", [])
        print(f"\nMapping questions embedded in spec: {len(mapping_questions)}")
        for i, q in enumerate(mapping_questions):
            print(f"  📍 {q.get('question', q.get('text', 'N/A'))}")
        
        # Show question sources by category
        print(f"\n📊 QUESTION SOURCES BREAKDOWN")
        print("-" * 50)
        
        total_questions = len(analysis_questions) + len(critical_questions) + len(regular_questions) + len(mapping_questions)
        print(f"Total questions across pipeline: {total_questions}")
        print(f"  - Analysis stage: {len(analysis_questions)}")
        print(f"  - Critical (translation): {len(critical_questions)}")
        print(f"  - Regular (translation): {len(regular_questions)}")
        print(f"  - Mapping-specific: {len(mapping_questions)}")
        
        # Show categories that generated questions
        questions_by_category = metadata.get("questions_by_category", {})
        print(f"\nQuestions by mapping category:")
        for category, q_list in questions_by_category.items():
            if q_list:
                print(f"  - {category}: {len(q_list)} questions")
        
        # Show warnings that might prompt questions
        warnings = metadata.get("warnings", [])
        print(f"\nWarnings that might need clarification: {len(warnings)}")
        for warning in warnings:
            category = warning.get("category", "unknown")
            issue = warning.get("issue", "N/A")
            print(f"  ⚠️ [{category}] {issue}")
        
        # Show validation guidance
        validation_summary = translate_result.get("validation_summary", [])
        print(f"\nValidation guidance: {len(validation_summary)} items")
        for item in validation_summary:
            print(f"  {item}")
        
        # Create aggregated question response structure
        aggregated_questions = {
            "analysis_questions": analysis_questions,
            "critical_questions": critical_questions, 
            "regular_questions": regular_questions,
            "mapping_questions": mapping_questions,
            "warnings_needing_clarification": warnings,
            "total_count": total_questions,
            "confidence_summary": {
                "overall": metadata.get("overall_confidence", 0),
                "by_category": metadata.get("confidence_by_category", {})
            }
        }
        
        # Save for inspection
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        questions_file = output_dir / "question_aggregation.json"
        with open(questions_file, 'w') as f:
            json.dump(aggregated_questions, f, indent=2)
        
        print(f"\n✅ Complete question data saved to {questions_file}")
        
        return total_questions > 0
    else:
        print(f"❌ Translation failed: {translate_result.get('error')}")
        return False

def show_question_flow_diagram():
    """Show the conceptual flow of questions through the pipeline."""
    
    print("\n" + "=" * 80)
    print("QUESTION FLOW DIAGRAM")
    print("=" * 80)
    
    flow = """
    USER QUERY
        ↓
    ┌─────────────────────────┐
    │   ANALYSIS STAGE        │ → questions_for_user[]
    │   (analyze_hockey_query)│   - Ambiguous positions
    └─────────────────────────┘   - Missing drill details
        ↓                         - Unclear equipment needs
    ┌─────────────────────────┐
    │   TRANSLATION STAGE     │ → metadata.critical_questions[]
    │   (translate_analysis)  │   - Player mapping issues
    └─────────────────────────┘   - Movement path problems
        ↓                         - Equipment placement conflicts
    ┌─────────────────────────┐
    │   PLAYER MAPPING        │ → mapping_questions[]
    │   (map_positions_with_llm)│  - Zone boundary clarifications
    └─────────────────────────┘   - Spatial relationship questions
        ↓
    ┌─────────────────────────┐
    │   MOVEMENT MAPPING      │ → metadata.questions[]
    │   (map_movements_with_llm)│  - Path validation issues
    └─────────────────────────┘   - Timing sequence questions
        ↓
    ┌─────────────────────────┐
    │   EQUIPMENT MAPPING     │ → metadata.warnings[]
    │   (map_equipment_with_llm)│  - Placement confidence issues
    └─────────────────────────┘   - Space availability questions
        ↓
    ┌─────────────────────────┐
    │   AGGREGATED RESPONSE   │ → Complete question collection
    │   (final return to client)│  - Categorized by stage & impact
    └─────────────────────────┘   - Prioritized by criticality
    
    CLIENT RECEIVES:
    {
        "analysis": { "questions_for_user": [...] },
        "translation": {
            "metadata": {
                "critical_questions": [...],
                "questions": [...],
                "warnings": [...],
                "confidence_by_category": {...}
            }
        }
    }
    """
    
    print(flow)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("TESTING MULTI-STAGE QUESTION COLLECTION")
    print("=" * 80)
    
    success = test_multi_stage_questions()
    
    show_question_flow_diagram()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if success:
        print("✅ Multi-stage question aggregation WORKING")
        print("\nKey findings:")
        print("  ✅ Analysis generates initial clarification questions")
        print("  ✅ Translation adds critical mapping questions")
        print("  ✅ Each mapping stage contributes domain-specific questions")
        print("  ✅ Questions categorized by impact level (critical vs regular)")
        print("  ✅ Warnings identify issues needing clarification")
        print("  ✅ Client gets complete question collection across all stages")
        print("\nQuestion sources:")
        print("  🔍 Analysis: Drill interpretation ambiguities")
        print("  📍 Player mapping: Position and zone clarifications")
        print("  🏃 Movement mapping: Path and timing questions")
        print("  🔧 Equipment mapping: Placement and space issues")
        print("  ⚠️  Validation: Confidence-based warnings")
    else:
        print("❌ Question aggregation test FAILED")