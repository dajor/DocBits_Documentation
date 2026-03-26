# CI Translation Fixes - Summary

## Issues Fixed

### Issue #1: Token Limit Exceeded
**Problem:** Workflow failing with error:
```
The input file is too large for the selected model (gpt-4o-mini-2024-07-18). 
Approximate tokens: 4701.0, Model limit: 4096
```

**Root Cause:** When `readme/SUMMARY.md` (723 lines) was bundled with other changed files, the combined token count exceeded gpt-4o-mini's 4096 token limit.

**Solution:** Modified `script/translate_markdown.py` to:
- Added `chunk_text()` function that splits large files at paragraph boundaries
- Added `estimate_tokens()` helper for token estimation
- Changed behavior from "fail on large files" to "automatically chunk and translate sequentially"
- Each chunk stays under 90% of the model's token limit to allow for prompt overhead

**Files Changed:** `script/translate_markdown.py`

---

### Issue #2: Git Push Race Condition
**Problem:** Workflow failing with error:
```
! [rejected] de -> de (non-fast-forward)
```

**Root Cause:** Multiple language translation workflows (de/es/fr/it/nl/pl/pt) run concurrently on main branch pushes. Each workflow:
1. Checks out its language branch
2. Translates files and commits
3. Pushes without pulling first

When two workflows overlap, the second one's push fails because the remote has advanced.

**Solution:** Modified `.github/workflows/translate_de_v2.yml` to:
- Added `git pull --rebase origin $BRANCH` before `git push origin $BRANCH`
- Changed concurrency group from `${{ github.ref }}` to `${{ github.workflow }}-${{ github.ref }}` to prevent workflow self-cancellation
- Set `cancel-in-progress: false` to let running workflows complete

**Files Changed:** `.github/workflows/translate_de_v2.yml`

---

## Testing Notes

### Local Testing
The chunking logic can be tested with:
```bash
export OPENAI_API_KEY=your_key
python script/translate_markdown.py German readme/SUMMARY.md output_de.md --model gpt-4o-mini-2024-07-18
```

### CI Testing
Push the `fix/translation-ci-issues` branch and create a PR to trigger the workflow.

---

## Recommendations for Other Languages

The same workflow fix should be applied to other language workflows:
- `translate_es.old` → needs migration to v2 format + pull-before-push
- `translate_fr.old` → needs migration to v2 format + pull-before-push
- `translate_it.old` → needs migration to v2 format + pull-before-push
- `translate_pl.old` → needs migration to v2 format + pull-before-push
- `translate_pt.old` → needs migration to v2 format + pull-before-push

The Python script fix (`translate_markdown.py`) is shared across all languages, so no additional changes needed there.

---

## Authors
- Diagnosis: Joe (DevOps)
- Implementation: Luck (Senior Fullstack)
- QA Validation: Karl (QA)
