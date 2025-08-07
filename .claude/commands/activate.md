# /activate

## Purpose
Set up persistent virtual environment activation for all subsequent bash commands in Claude Code session.

## Arguments
None

## Implementation

The challenge: Each bash command in Claude Code runs in a separate shell session, so `source activate` doesn't persist.

**Solution**: Always prefix Python commands with the full virtual environment path, and provide helper instructions.

```bash
#!/bin/bash

echo "🐍 Setting up spacy_env virtual environment for Claude Code..."

# Check if virtual environment exists
if [ ! -f "/Users/liammckendry/spacy_env/bin/activate" ]; then
    echo "❌ ERROR: Virtual environment not found at /Users/liammckendry/spacy_env/"
    echo "Please check that the path is correct."
    exit 1
fi

# Test virtual environment
echo "📋 Testing virtual environment..."
/Users/liammckendry/spacy_env/bin/python --version
echo "📍 Virtual environment location: /Users/liammckendry/spacy_env/"
echo "🐍 Python executable: /Users/liammckendry/spacy_env/bin/python"

# Check for key packages
echo ""
echo "📋 Checking key dependencies..."
/Users/liammckendry/spacy_env/bin/python -c "
import sys
packages = ['fastmcp', 'openai', 'chromadb', 'numpy', 'spacy']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}: Available')
    except ImportError:
        print(f'❌ {pkg}: Not found')
"

echo ""
echo "✅ Virtual environment verified!"
echo ""
echo "📝 IMPORTANT: For subsequent bash commands in this Claude Code session:"
echo "   Use: /Users/liammckendry/spacy_env/bin/python instead of just 'python'"
echo "   Use: /Users/liammckendry/spacy_env/bin/pip instead of just 'pip'"
echo ""
echo "💡 Better solution: Use the compound activation pattern:"
echo "   source /Users/liammckendry/spacy_env/bin/activate && python your_script.py"
echo ""
echo "🔧 Best practice examples:"
echo "   source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp.py"
echo "   source /Users/liammckendry/spacy_env/bin/activate && python -m pytest tests/"
echo "   source /Users/liammckendry/spacy_env/bin/activate && pip install package_name"
```

## Usage Examples

```bash
# Check virtual environment and get usage instructions
/activate

# Then use these patterns for subsequent commands:

# Method 1: Compound activation (recommended)
source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp.py
source /Users/liammckendry/spacy_env/bin/activate && python -m pytest tests/
source /Users/liammckendry/spacy_env/bin/activate && pip install new_package

# Method 2: Direct path (alternative)
/Users/liammckendry/spacy_env/bin/python servers/hockey_mcp.py
/Users/liammckendry/spacy_env/bin/python -m pytest tests/
/Users/liammckendry/spacy_env/bin/pip install new_package
```

## Expected Output

```
🐍 Setting up spacy_env virtual environment for Claude Code...
📋 Testing virtual environment...
Python 3.x.x
📍 Virtual environment location: /Users/liammckendry/spacy_env/
🐍 Python executable: /Users/liammekendry/spacy_env/bin/python

📋 Checking key dependencies...
✅ fastmcp: Available
✅ openai: Available
✅ chromadb: Available
✅ numpy: Available
✅ spacy: Available

✅ Virtual environment verified!

📝 IMPORTANT: For subsequent bash commands in this Claude Code session:
   Use: /Users/liammckendry/spacy_env/bin/python instead of just 'python'
   Use: /Users/liammckendry/spacy_env/bin/pip instead of just 'pip'

💡 Better solution: Use the compound activation pattern:
   source /Users/liammckendry/spacy_env/bin/activate && python your_script.py

🔧 Best practice examples:
   source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp.py
   source /Users/liammckendry/spacy_env/bin/activate && python -m pytest tests/
   source /Users/liammckendry/spacy_env/bin/activate && pip install package_name
```

## Notes

- **Key Insight**: Claude Code bash commands run in separate shell sessions, so `source activate` doesn't persist
- **Solution**: Use compound commands with `&&` to activate and run in the same shell session
- **Alternative**: Use full paths to the virtual environment Python/pip executables
- The compound activation pattern is recommended because it's more readable and handles complex commands better
- This command now serves as a verification tool and provides the correct usage patterns

## Related Commands

- `/hockey-setup` - Complete development environment setup (includes this activation)
- `/commit-prep` - Pre-commit checks (requires activated environment)
- `/mcp-test` - MCP server testing (requires activated environment)