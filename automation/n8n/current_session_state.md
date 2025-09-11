# Current Session State - n8n Workflow Issue

## Active Work
- **Workflow ID**: NLSGnPWngNkvkxqs
- **Issue**: Evaluation trigger node error "Can not get sheet 'undefined'"

## Problem Analysis
The evaluation trigger expects different parameter structure than what we provided.
Based on n8n docs, it needs:
- Document selection method (list/url/id)
- Sheet selection method (list/url/id/name)

## Next Steps to Fix
1. Export working evaluation trigger from n8n UI
2. Compare parameter structure
3. Update workflow JSON to match
4. Re-import with correct structure

## Google Sheets Info
- **Document ID**: 1xbgdJvP0TBeiInOS85ot0afIZRUp1t1jgbTy1NKhGLA
- **Test Cases Sheet**: Where drill descriptions are read
- **Results Sheet**: Where evaluation results are written  
- **Specs Sheet**: Where generated/expected specs are written

## Commands for Next Session
```bash
# If restarting session
cd /Users/liammckendry/thunder_playbook_worktrees/issue-109/n8n

# Check current workflow
cat workflows/drill_evaluation_clean.json

# Re-import if needed
source /Users/liammckendry/spacy_env/bin/activate
python test_workflow_with_auth.py
```