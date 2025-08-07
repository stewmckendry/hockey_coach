# /activate

## Purpose
Activate the spacy_env virtual environment located at `/Users/liammckendry/spacy_env/` and verify it's working correctly.

## Arguments
None

## Implementation

```bash
#!/bin/bash

echo "🐍 Activating spacy_env virtual environment..."

# Check if virtual environment exists
if [ ! -f "/Users/liammckendry/spacy_env/bin/activate" ]; then
    echo "❌ ERROR: Virtual environment not found at /Users/liammckendry/spacy_env/"
    echo "Please check that the path is correct."
    exit 1
fi

# Activate the virtual environment
source /Users/liammckendry/spacy_env/bin/activate

# Verify activation
if [ "$VIRTUAL_ENV" = "/Users/liammckendry/spacy_env" ]; then
    echo "✅ Virtual environment activated successfully!"
    echo "📍 Active environment: $VIRTUAL_ENV"
    echo "🐍 Python path: $(which python)"
    echo "📦 Python version: $(python --version)"
    
    # Check for key packages
    echo ""
    echo "📋 Checking key dependencies..."
    python -c "
import sys
packages = ['fastmcp', 'openai', 'chromadb', 'numpy', 'spacy']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}: Available')
    except ImportError:
        print(f'❌ {pkg}: Not found')
"
else
    echo "❌ ERROR: Virtual environment activation failed"
    echo "Current VIRTUAL_ENV: $VIRTUAL_ENV"
    exit 1
fi
```

## Usage Examples

```bash
# Activate virtual environment
/activate
```

## Expected Output

```
🐍 Activating spacy_env virtual environment...
✅ Virtual environment activated successfully!
📍 Active environment: /Users/liammckendry/spacy_env
🐍 Python path: /Users/liammckendry/spacy_env/bin/python
📦 Python version: Python 3.x.x

📋 Checking key dependencies...
✅ fastmcp: Available
✅ openai: Available
✅ chromadb: Available
✅ numpy: Available
✅ spacy: Available
```

## Notes

- This command addresses the common issue where Claude Code struggles with Python commands because the virtual environment isn't activated
- The virtual environment is located at `/Users/liammckendry/spacy_env/` (parent directory of the project)
- After running this command, all subsequent Python commands in the session will use the activated environment
- The command includes verification steps to ensure activation was successful
- Key package availability is checked to confirm the environment is properly set up

## Related Commands

- `/hockey-setup` - Complete development environment setup (includes this activation)
- `/commit-prep` - Pre-commit checks (requires activated environment)
- `/mcp-test` - MCP server testing (requires activated environment)