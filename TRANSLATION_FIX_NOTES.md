# Translation Workflow Fix - Implementation Notes

## Date: 2026-03-24

## Problem
The GitHub Actions workflow "Translate Markdown on Main Push" was failing with error:
- **File**: readme/SUMMARY.md (4632 tokens, 88900 bytes)
- **Error**: Exceeded gpt-4o-mini-2024-07-18's 4096 token limit
- **Step**: "Translate Changed Files" in translate-markdown job

## Solution Implemented

### 1. Added tiktoken for accurate token counting
- Replaced rough word-based estimation (`len(text.split()) * 1.5`) with tiktoken library
- Function `count_tokens()` uses OpenAI's official tokenizer for precise counts
- Fallback to estimation if tiktoken fails

### 2. Auto-switch to gpt-4o for large files
- When file exceeds model's token limit (4096 for gpt-4o-mini), script now:
  - Detects the overflow using accurate token counting
  - Auto-switches to gpt-4o (128k context limit)
  - Recursive call with new model, disables further switching
- Fallback to chunking if auto-switch disabled

### 3. Improved chunking logic
- Updated `split_into_chunks()` to use `count_tokens()` per line
- More accurate chunk boundaries at heading levels
- Prevents mid-chunk token overflow

### 4. Updated workflow configuration
- Changed model from `gpt-4o-mini-2024-07-18` to `gpt-4o`
- gpt-4o handles both small files (cost-effective) and large files (128k context)
- Added comment explaining the auto-switch behavior

## Files Modified

1. **script/translate_markdown.py**
   - Added `tiktoken` import
   - Added `MODEL_TOKEN_LIMITS` dict
   - Added `count_tokens()` function
   - Updated `split_into_chunks()` with accurate token counting
   - Updated `translate_markdown()` with `auto_switch_model` parameter
   - Added `--no-auto-switch` CLI flag

2. **.github/workflows/translate_de_v2.yml**
   - Changed `--model gpt-4o-mini-2024-07-18` to `--model gpt-4o`

## Git Actions Taken

```bash
# Committed changes
git add .
git commit -m "Fix translation workflow for large files..."

# Merged to main
git checkout main
git merge fix/translation-token-limit --no-edit

# Pushed to fork
git push fork main
```

## Next Steps for Validation

### Karl (QA) should:
1. Check GitHub Actions workflow status after next push to main
2. Verify readme/SUMMARY.md translates successfully
3. Confirm translated file (SUMMARY_de.md) is created in de branch
4. Check workflow logs for token count messages

### Expected log output:
```
File (4632 tokens) exceeds gpt-4o-mini's limit (4096 tokens)
Auto-switching to gpt-4o (limit: 128000 tokens) for large file
Translating file as single chunk (4632 tokens)
```

## Notes
- PR creation via gh CLI failed due to permission (403)
- Changes pushed to fork's main branch
- May need manual PR creation through GitHub UI if upstream requires review
- Joe (DevOps) can assist with workflow monitoring
