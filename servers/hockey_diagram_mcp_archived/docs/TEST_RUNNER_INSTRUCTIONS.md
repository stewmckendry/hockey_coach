# Test Runner Instructions for Hockey Diagram MCP Server

## Quick Start

The test scripts are already set up and ready to use. Here's how to run them:

### Method 1: Direct Python Execution (Recommended)

```bash
# Navigate to the hockey diagram directory
cd /Users/liammckendry/thunder_playbook/servers/hockey_diagram_mcp

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run a single test (test numbers 0-32)
python test_single_diagram.py "$OPENAI_API_KEY" 0
```

### Method 2: Using Shell Scripts

If the shell scripts have execution issues, make them executable first:

```bash
# Make scripts executable
chmod +x run_single_test.sh
chmod +x run_quick_test.sh
chmod +x run_integration_test.sh

# Then run
./run_single_test.sh "your-api-key-here" 0
```

### Method 3: Virtual Environment Activation (If Direct Python Fails)

```bash
# Navigate to parent directory and activate virtual environment
cd /Users/liammckendry
source spacy_env/bin/activate
cd thunder_playbook/servers/hockey_diagram_mcp

# Run test
python test_single_diagram.py "your-api-key-here" 0
```

## Available Test Scripts

### 1. Single Diagram Test (`test_single_diagram.py`)
Tests one diagram at a time with detailed output showing:
- Stage 1: Parser output (players, movements, zones)
- Stage 2: Diagram generation result
- QA Analysis: Automatic quality checks

**Usage**: `python test_single_diagram.py [API_KEY] [test_number]`

**Test Numbers**:
- 0-4: View tests (full, offensive, defensive, neutral)
- 5-9: Formation tests (forechecks, penalty kills)
- 10-14: Drill tests (passing, rush, defensive)
- 15-19: Play tests (breakouts, cycles)
- 20-24: Special situations (6v5, 3v3, faceoffs)
- 25-32: Advanced formation tests (detailed tactical setups)

### 2. Quick Test (`quick_test_diagrams.py`)
Runs 4 basic tests quickly for validation:
- 2-1-2 forecheck
- Box penalty kill
- Power play umbrella
- Triangle passing drill

**Usage**: `python quick_test_diagrams.py [API_KEY]`

### 3. Integration Test (`test_integration_full.py`)
Comprehensive pytest suite (requires pytest installed):

**Usage**: `pytest test_integration_full.py -v`

## Recent Improvements Applied

The following fixes have already been implemented based on initial testing:

1. **Team Separation Logic**: Away team players are automatically offset to prevent overlap
2. **View Filtering**: Players outside view boundaries are removed
3. **Movement Validation**: Redundant movements (same start/end position) are filtered
4. **Zone Opacity**: Reduced to 0.2 for better visibility

## Common Issues and Solutions

### Issue: "No such file or directory"
**Solution**: Run from the correct directory
```bash
cd /Users/liammckendry/thunder_playbook/servers/hockey_diagram_mcp
```

### Issue: "ModuleNotFoundError"
**Solution**: The script already includes path fixes, but if needed:
```python
# These lines are already in test_single_diagram.py
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent))
```

### Issue: "OPENAI_API_KEY not set"
**Solution**: Provide API key as first argument:
```bash
python test_single_diagram.py "sk-proj-..." 0
```

## Expected Output Format

When running a test, you'll see:

```
Running test 1/33

============================================================
PROMPT: 5v5 neutral zone setup
VIEW: full
============================================================

📝 STAGE 1: Two-Stage Parser
----------------------------------------
Diagram Type: formation
Title: 5v5 Neutral Zone Setup
View: full

Players (10):
  1. C at (0.0, 0.0) - Team: home
  2. RW at (10.0, 20.0) - Team: home
  [... more players ...]

🎨 STAGE 2: Diagram Generation
----------------------------------------
✅ Success!
Diagram saved to: servers/hockey_diagram_mcp/generated_diagrams/hockey_diagram_[timestamp].png
Generation time: XX.XXs

🔍 QA ANALYSIS
----------------------------------------
✅ View correct: full
✅ All players in correct zone
✅ No movements expected or found
```

## Running Multiple Tests

To run a batch of tests sequentially:

```bash
# Run tests 0-4 (view tests)
for i in {0..4}; do
    python test_single_diagram.py "$OPENAI_API_KEY" $i
    sleep 2  # Pause between tests
done
```

## Generated Files

Diagrams are saved to:
`servers/hockey_diagram_mcp/generated_diagrams/hockey_diagram_[timestamp].png`

Test results and analysis (if using pipeline_detailed.py):
`servers/hockey_diagram_mcp/test_results/`

## Next Steps for Testing

1. Run tests 0-4 to validate view functionality
2. Run tests 5-9 to check formations
3. Run tests 10-14 to verify drills
4. Review generated images and provide feedback
5. Use Task agents to implement fixes based on findings

Good luck with testing! The system is ready to generate accurate hockey diagrams.