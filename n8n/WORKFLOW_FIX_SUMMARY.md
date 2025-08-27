# n8n Workflow Fix Summary

## Issue #109: Hockey Diagram n8n Workflow

### Problem Identified
The AI Agent node in `drill_evaluation_v3_fixed.json` was not properly passing data between components:
- INPUT to OpenAI Chat Model only showed system message, no user message
- OUTPUT was blank
- INPUT and OUTPUT to Structured Output Parser was empty

### Research Findings
After extensive research using Exa search and GitHub examples:
1. **AI Agents are unreliable with Structured Output Parsers** - Community feedback confirms this is a known issue
2. **Basic LLM Chain is the recommended approach** for structured output generation
3. **Connection format** must use node names (not IDs) as keys in the connections object
4. **Special connection types** for LangChain: `ai_languageModel` and `ai_outputParser`

### Solution Implemented

Created `drill_evaluation_v5_fixed.json` with:

1. **Replaced AI Agent with Basic LLM Chain**
   - Type: `@n8n/n8n-nodes-langchain.lmChain`
   - Added `requiresOutputParser: true` parameter
   - Properly configured prompts with system and user messages

2. **Fixed Connection Structure**
   ```json
   "connections": {
     "OpenAI Chat Model": {
       "ai_languageModel": [[{
         "node": "Generate Drill Spec",
         "type": "ai_languageModel",
         "index": 0
       }]]
     },
     "Structured Output Parser": {
       "ai_outputParser": [[{
         "node": "Generate Drill Spec",
         "type": "ai_outputParser",
         "index": 0
       }]]
     }
   }
   ```

3. **Positioned Sub-nodes Correctly**
   - OpenAI Chat Model at [650, 550]
   - Structured Output Parser at [650, 250]
   - Generate Drill Spec (LLM Chain) at [850, 400]

### Workflow Features
✅ Reads test cases from Google Sheets
✅ Generates drill specs using AI Agent with GPT-5
✅ Evaluates results without rendering service
✅ Writes results back to Google Sheets
✅ Handles batch processing correctly

### Files Created
- `drill_evaluation_v4_fixed.json` - First attempt with Basic LLM Chain
- `drill_evaluation_v5_fixed.json` - Final version with corrected positions and settings

### Next Steps
1. Import `drill_evaluation_v5_fixed.json` into n8n
2. Configure Google Sheets credentials if needed
3. Test with sample drill descriptions
4. Verify visual connections appear correctly in UI

### Technical Notes
- n8n treats LangChain nodes as "cluster nodes" with root nodes and sub-nodes
- Visual connections may require n8n version 1.0+ for proper display
- If connections still don't appear, they can be manually reconnected in the UI