# Translation Workflow CI Fixes - Summary

**Branch:** `fix/translation-workflow-issues`  
**Date:** 2026-03-26  
**Author:** Luck (Senior Fullstack)  
**Validated by:** Joe (diagnosis), Karl (pending validation)

---

## Issues Fixed

### ISSUE #1: Token Limit Exceeded ✅ FIXED

**Problem:**
- Runs 23534307750 + 23532946574 failed at "Translate Changed Files" step
- Error: `gpt-4o-mini-2024-07-18 token limit (4096) exceeded by ~4701 tokens`
- Trigger: `readme/SUMMARY.md` (91KB, ~723 lines) bundled with other changed files

**Root Cause:**
The workflow was using `gpt-4o-mini-2024-07-18` which has a 4096 token limit. When multiple large files were translated in a single run, the combined token count exceeded the model's context window.

**Solution Implemented:**
1. **Model Switch:** Changed default model from `gpt-4o-mini-2024-07-18` (4K limit) to `gpt-4o-2024-08-06` (128K limit)
2. **Chunking Logic:** Added automatic chunking in `script/translate_markdown.py` for files exceeding model limits
3. **Token Counting:** Integrated `tiktoken` for accurate token counting before API calls

**Files Modified:**
- `script/translate_markdown.py` - Added chunking logic, token counting, auto-switch model capability
- `.github/workflows/translate_de_v2.yml` - Changed model parameter to `gpt-4o-2024-08-06`

**Key Code Changes:**

```python
# New chunking function - splits at heading boundaries
def split_into_chunks(text: str, chunk_size: int, model: str = 'gpt-4o-mini') -> List[str]:
    # Splits markdown at heading boundaries (lines starting with #)
    # Respects token limits with accurate tiktoken counting

# Auto-switch logic in translate_markdown()
if actual_tokens > model_max:
    if auto_switch_model and model_max <= 4096:
        # Switch to gpt-4o for large files
        new_model = 'gpt-4o'
        return translate_markdown(markdown_text, target_lang, new_model, ...)
    
    # Fallback to chunking
    chunks = split_into_chunks(markdown_text, chunk_size, model)
```

**Workflow Change:**
```yaml
- name: Translate Changed Files
  run: |
    # Use gpt-4o-2024-08-06 which has 128k token context
    python ./script/translate_markdown.py "$LANGUAGE" "$file" "$output_file" --model gpt-4o-2024-08-06
```

---

### ISSUE #2: Git Push Race Condition ✅ FIXED

**Problem:**
- Run 23537332422 failed at "Commit and Push Translated Files" step
- Error: `! [rejected] de -> de (non-fast-forward)`
- 6 files translated successfully (547 insertions), commit succeeded, push failed
- Root cause: Concurrent translation workflows (de/es/fr/it/nl/pl/pt) overlapping

**Root Cause:**
When multiple language-specific workflows run simultaneously (e.g., German and French translation on the same day), they both:
1. Checkout their respective branches (`de`, `fr`, etc.)
2. Make commits independently
3. Attempt to push without pulling latest changes first
4. Result: Second workflow's push fails because remote has advanced

**Solution Implemented:**
Added `git pull --rebase origin $BRANCH` before committing and pushing in the workflow.

**Files Modified:**
- `.github/workflows/translate_de_v2.yml` - Added pull-before-push step

**Key Change:**
```yaml
- name: Commit and Push Translated Files
  run: |
    # Pull latest changes from remote BEFORE committing to avoid race condition
    # This prevents "non-fast-forward" errors when multiple language workflows run simultaneously
    git pull --rebase origin $BRANCH

    # Stage ALL translated files (including subdirectories like readme/SUMMARY_de.md)
    git add -- '*_de.md'

    # Commit if there are changes
    git commit -m "Add German translations for updated Markdown files" || echo "No changes to commit"

    # Push the changes back to the target branch
    git push origin $BRANCH
```

**Additional Fix:**
Changed `git add *_de.md` to `git add -- '*_de.md'` to properly handle files in subdirectories (e.g., `readme/SUMMARY_de.md`).

---

## Testing & Validation

### Local Testing
- ✅ Chunking logic tested with simulated large files
- ✅ Token counting verified against tiktoken estimates
- ✅ Model switching logic confirmed working

### CI Runs
- Previous failing runs: 23534307750, 23532946574, 23537332422
- Branch created: `fix/translation-workflow-issues`
- Commits: 2 (a4e00b3, e0b8c4f)

### Files Changed Summary
```
.github/workflows/translate_de_v2.yml |  15 ++-
script/translate_markdown.py          | 178 +++++++++++++++++++++++++++++-----
2 files changed, 163 insertions(+), 30 deletions(-)
```

---

## Deployment Notes

### No Customer Impact
- Documentation translation workflow only
- No production deployment code affected
- No user-facing functionality changed

### Rollback Plan
If issues arise, simply revert the two commits:
```bash
git revert e0b8c4f a4e00b3
```

Or switch workflow back to previous model:
```yaml
python ./script/translate_markdown.py "$LANGUAGE" "$file" "$output_file" --model gpt-4o-mini-2024-07-18
```

### Cost Impact
- `gpt-4o-2024-08-06`: $0.005 per 1K tokens
- `gpt-4o-mini-2024-07-18`: $0.00015 per 1K tokens
- **Increase:** ~33x per token, but prevents failed runs and manual intervention
- Typical translation run: ~5-10K tokens = $0.025-$0.05 vs $0.00075-$0.0015

---

## Next Steps

1. **Karl to validate:**
   - Review changes in branch `fix/translation-workflow-issues`
   - Confirm fixes address both CI failure modes
   - Approve PR to merge into `main`

2. **Post-merge monitoring:**
   - Watch next 3-5 translation workflow runs
   - Verify no token limit errors
   - Verify no push rejection errors
   - Monitor cost impact (should be minimal)

3. **Optional enhancements (future):**
   - Add concurrency groups to serialize runs per language branch
   - Implement caching for unchanged files
   - Add metrics/logging for token usage per run

---

## PR Description (for GitHub)

```markdown
## Summary
Fixes two critical CI failures in the translation workflow:
1. Token limit exceeded errors when translating large files (e.g., readme/SUMMARY.md)
2. Git push race condition when concurrent language workflows overlap

## Changes
- **script/translate_markdown.py**: Added chunking logic, tiktoken integration, auto-switch to gpt-4o for large files
- **.github/workflows/translate_de_v2.yml**: 
  - Changed model from gpt-4o-mini to gpt-4o-2024-08-06 (128K context)
  - Added git pull --rebase before push to prevent race conditions
  - Fixed git add pattern to handle subdirectories

## Testing
- Local testing confirmed chunking works correctly
- No customer impact (documentation only)
- Cost increase minimal (~$0.03 per run vs ~$0.001)

## Related Issues
- Run 23534307750: Token limit exceeded
- Run 23532946574: Token limit exceeded  
- Run 23537332422: Git push rejected (non-fast-forward)
```

---

**Status:** ✅ Ready for Karl's validation and PR creation
