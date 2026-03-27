# PR Creation Instructions

**Note:** Automatic PR creation failed due to token permissions. Please create manually using the details below.

---

## PR Details

**Base Branch:** `upstream/main` (FELLOWPRO/DocBits_Documentation)  
**Head Branch:** `fix/translation-workflow-issues` (dajor/DocBits_Documentation)  
**Compare URL:** https://github.com/FELLOWPRO/DocBits_Documentation/compare/main...dajor:DocBits_Documentation:fix/translation-workflow-issues

---

## Title
```
Fix translation workflow CI failures (token limit + push race condition)
```

---

## Description
```markdown
## Summary

Fixes two critical CI failures in the FELLOWPRO/DocBits_Documentation translation workflow:

1. **Token limit exceeded** - Runs 23534307750 + 23532946574 failed when translating large files like `readme/SUMMARY.md`
2. **Git push race condition** - Run 23537332422 failed with `non-fast-forward` error when concurrent language workflows overlapped

## Changes

### script/translate_markdown.py
- Added `tiktoken` integration for accurate token counting
- Implemented `split_into_chunks()` function that splits markdown at heading boundaries
- Added auto-switch logic to use `gpt-4o` (128K context) for files exceeding 4K tokens
- Added `MODEL_TOKEN_LIMITS` dictionary for all supported models
- Changed default model from `gpt-3.5-turbo` to `gpt-4o-2024-08-06`

### .github/workflows/translate_de_v2.yml
- Changed translation model from `gpt-4o-mini-2024-07-18` to `gpt-4o-2024-08-06` (128K vs 4K context)
- Added `git pull --rebase origin $BRANCH` before commit/push to prevent race conditions
- Fixed `git add` pattern from `*_de.md` to `-- '*_de.md'` to handle subdirectories (e.g., `readme/SUMMARY_de.md`)

## Testing

- ✅ Chunking logic tested locally with large files
- ✅ Token counting verified against tiktoken estimates  
- ✅ Model switching confirmed working
- ✅ No customer impact (documentation translation only)

## Cost Impact

- `gpt-4o-2024-08-06`: $0.005 per 1K tokens
- `gpt-4o-mini-2024-07-18`: $0.00015 per 1K tokens
- Typical run: ~5-10K tokens = $0.025-$0.05 (vs $0.001 previously)
- **Justification:** Prevents failed runs and manual intervention

## Related CI Failures

- Run 23534307750: Token limit exceeded (~4701 tokens over limit)
- Run 23532946574: Token limit exceeded
- Run 23537332422: Git push rejected (non-fast-forward)

## Rollback Plan

If issues arise, revert commits `6dff69f`, `e0b8c4f`, `a4e00b3` or switch workflow model back to `gpt-4o-mini-2024-07-18`.

---

**Validated by:** Joe (diagnosis), Karl (pending)  
**Author:** Luck (Senior Fullstack)
```

---

## Manual Steps

1. Go to: https://github.com/FELLOWPRO/DocBits_Documentation/compare/main...dajor:DocBits_Documentation:fix/translation-workflow-issues

2. Click "Create pull request"

3. Paste title and description from above

4. Add reviewers: Karl, Joe

5. Submit PR

---

## Alternative: Using GitHub CLI with Proper Token

If you have a token with `repo` scope:

```bash
cd /Users/admin/.openclaw/workspace/DocBits_Documentation

# Create PR
gh pr create \
  --base main \
  --head dajor:fix/translation-workflow-issues \
  --title "Fix translation workflow CI failures (token limit + push race condition)" \
  --body-file TRANSLATION_CI_FIX_SUMMARY.md \
  --repo FELLOWPRO/DocBits_Documentation
```

---

## Files Changed in PR

```
.github/workflows/translate_de_v2.yml |  15 ++-
script/translate_markdown.py          | 178 +++++++++++++++++++++++++++++-----
TRANSLATION_CI_FIX_SUMMARY.md         | 199 ++++++++++++++++++++++++++++++++++
3 files changed, 378 insertions(+), 14 deletions(-)
```

---

**Status:** Branch pushed and ready for PR creation
