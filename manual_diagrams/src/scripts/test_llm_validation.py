#!/usr/bin/env python3
"""Test the enhanced LLM validation in validate_diagram_spec_full"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from servers.hockey_diagram_mcp_v2 import validate_diagram_spec_full
import json

def test_2v1_rush_validation():
    """Test validation of a 2v1 rush drill"""
    
    # Test case 1: Correct 2v1 rush
    print("\n" + "="*60)
    print("TEST 1: Correct 2v1 Rush Drill")
    print("="*60)
    
    correct_spec = {
        "rink": {"view": "full"},
        "players": [
            {"type": "forward", "position": "F1", "coordinates": {"x": 0, "y": 15}, "team": "home"},
            {"type": "forward", "position": "F2", "coordinates": {"x": 0, "y": -15}, "team": "home"},
            {"type": "defense", "position": "D1", "coordinates": {"x": 30, "y": 0}, "team": "away"}
        ],
        "movements": [
            {"type": "carry", "from_pos": {"x": 0, "y": 15}, "to_pos": {"x": 69, "y": 10}},
            {"type": "pass", "from_pos": {"x": 69, "y": 10}, "to_pos": {"x": 69, "y": -10}},
            {"type": "shot", "from_pos": {"x": 69, "y": -10}, "to_pos": {"x": 89, "y": 0}}
        ]
    }
    
    result = validate_diagram_spec_full(correct_spec, "2v1 rush drill with pass and shot")
    print(f"Valid: {result['valid']}")
    print(f"Hockey sense valid: {result['hockey_sense_valid']}")
    if result.get('llm_analysis'):
        print(f"LLM Analysis performed: {result['llm_analysis']['performed']}")
        print(f"LLM Match: {result['llm_analysis']['match']}")
        print(f"LLM Issues: {result['llm_analysis']['issues']}")
        print(f"LLM Warnings: {result['llm_analysis']['warnings']}")
    
    # Test case 2: Incorrect - only 1 forward for 2v1
    print("\n" + "="*60)
    print("TEST 2: Incorrect - Missing Forward for 2v1")
    print("="*60)
    
    incorrect_spec = {
        "rink": {"view": "full"},
        "players": [
            {"type": "forward", "position": "F1", "coordinates": {"x": 0, "y": 0}, "team": "home"},
            {"type": "defense", "position": "D1", "coordinates": {"x": 30, "y": 0}, "team": "away"}
        ],
        "movements": [
            {"type": "carry", "from_pos": {"x": 0, "y": 0}, "to_pos": {"x": 69, "y": 0}},
            {"type": "shot", "from_pos": {"x": 69, "y": 0}, "to_pos": {"x": 89, "y": 0}}
        ]
    }
    
    result = validate_diagram_spec_full(incorrect_spec, "2v1 rush drill with pass and shot")
    print(f"Valid: {result['valid']}")
    print(f"Hockey sense valid: {result['hockey_sense_valid']}")
    if result.get('llm_analysis'):
        print(f"LLM Analysis performed: {result['llm_analysis']['performed']}")
        print(f"LLM Match: {result['llm_analysis']['match']}")
        print(f"LLM Issues: {result['llm_analysis']['issues']}")
        print(f"LLM Warnings: {result['llm_analysis']['warnings']}")
    print(f"All Issues: {result['issues']}")
    
    # Test case 3: Missing movements
    print("\n" + "="*60)
    print("TEST 3: Missing Pass Movement")
    print("="*60)
    
    missing_movement_spec = {
        "rink": {"view": "full"},
        "players": [
            {"type": "forward", "position": "F1", "coordinates": {"x": 0, "y": 15}, "team": "home"},
            {"type": "forward", "position": "F2", "coordinates": {"x": 0, "y": -15}, "team": "home"},
            {"type": "defense", "position": "D1", "coordinates": {"x": 30, "y": 0}, "team": "away"}
        ],
        "movements": [
            {"type": "carry", "from_pos": {"x": 0, "y": 15}, "to_pos": {"x": 69, "y": 10}},
            # Missing pass movement
            {"type": "shot", "from_pos": {"x": 69, "y": 10}, "to_pos": {"x": 89, "y": 0}}
        ]
    }
    
    result = validate_diagram_spec_full(missing_movement_spec, "2v1 rush drill with pass and shot")
    print(f"Valid: {result['valid']}")
    print(f"Hockey sense valid: {result['hockey_sense_valid']}")
    if result.get('llm_analysis'):
        print(f"LLM Analysis performed: {result['llm_analysis']['performed']}")
        print(f"LLM Match: {result['llm_analysis']['match']}")
        print(f"LLM Issues: {result['llm_analysis']['issues']}")
        print(f"LLM Warnings: {result['llm_analysis']['warnings']}")
    
    # Test case 4: Power play setup validation
    print("\n" + "="*60)
    print("TEST 4: Power Play Setup")
    print("="*60)
    
    pp_spec = {
        "rink": {"view": "offensive"},
        "players": [
            {"type": "forward", "position": "F1", "coordinates": {"x": 79, "y": 0}, "team": "home"},  # Net front
            {"type": "forward", "position": "F2", "coordinates": {"x": 69, "y": 22.5}, "team": "home"},  # Left circle
            {"type": "forward", "position": "F3", "coordinates": {"x": 69, "y": -22.5}, "team": "home"}, # Right circle
            {"type": "defense", "position": "D1", "coordinates": {"x": 30, "y": 20}, "team": "home"},  # Left point
            {"type": "defense", "position": "D2", "coordinates": {"x": 30, "y": -20}, "team": "home"}  # Right point
        ],
        "movements": []
    }
    
    result = validate_diagram_spec_full(pp_spec, "5v4 power play umbrella formation")
    print(f"Valid: {result['valid']}")
    print(f"Hockey sense valid: {result['hockey_sense_valid']}")
    if result.get('llm_analysis'):
        print(f"LLM Analysis performed: {result['llm_analysis']['performed']}")
        print(f"LLM Match: {result['llm_analysis']['match']}")
        print(f"LLM Issues: {result['llm_analysis']['issues']}")
        print(f"LLM Warnings: {result['llm_analysis']['warnings']}")

if __name__ == "__main__":
    print("Testing Enhanced LLM Validation")
    print("================================")
    print("Note: Requires OPENAI_API_KEY to be set for LLM validation")
    
    test_2v1_rush_validation()
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)