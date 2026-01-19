# Spellcheck Workflow Consolidation

## Summary

The 5 separate spellcheck workflows have been consolidated into 2 workflows:

### New Structure

1. **spell-check-consolidated.yml** - Main unified workflow with 3 jobs:
   - `spell-check` - Performs spell checking (replaces spell-check.yml and spell-check-and-fix.yml)
   - `apply-corrections` - Applies approved corrections (replaces apply-spell-corrections-manual.yml)
   - `verify-corrections` - Verifies corrections were applied (replaces verify-spell-corrections.yml)

2. **spell-check-approval-handler.yml** - Unchanged, handles `/approve` and `/reject` comments on issues

### Old Workflows (Can be deleted)

- ❌ `spell-check.yml` - Merged into consolidated workflow
- ❌ `spell-check-and-fix.yml` - Merged into consolidated workflow
- ❌ `apply-spell-corrections-manual.yml` - Merged as a job
- ❌ `verify-spell-corrections.yml` - Merged as a job
- ✅ `spell-check-approval-handler.yml` - Keep as is

## How to Use

### Running Spell Check

The consolidated workflow has a `mode` parameter:

#### Report-Only Mode (default)
Just reports errors without creating corrections:
```yaml
workflow_dispatch:
  inputs:
    mode: report-only
    post_count: 5
```

#### Create-Corrections Mode
Creates corrections and opens an issue for approval:
```yaml
workflow_dispatch:
  inputs:
    mode: create-corrections
    post_count: 5
```

### Approval Process

1. Run workflow with `mode: create-corrections`
2. Review the generated issue
3. Comment `/approve` to apply corrections
4. The `spell-check-approval-handler` triggers `apply-corrections` job
5. Corrections are applied automatically

### Verification

To manually verify corrections were applied:
```bash
# Trigger via repository_dispatch
gh api repos/{owner}/{repo}/dispatches \
  -f event_type=verify-spell-corrections \
  -f client_payload[run_id]=<run_id>
```

## Migration Steps

1. Test the new consolidated workflow
2. Delete old workflows:
   ```bash
   rm .github/workflows/spell-check.yml
   rm .github/workflows/spell-check-and-fix.yml
   rm .github/workflows/apply-spell-corrections-manual.yml
   rm .github/workflows/verify-spell-corrections.yml
   ```
3. Rename consolidated workflow:
   ```bash
   mv .github/workflows/spell-check-consolidated.yml .github/workflows/spell-check.yml
   ```

## Benefits

- ✅ Single workflow to maintain
- ✅ Consistent behavior across all modes
- ✅ Reduced code duplication
- ✅ Easier to understand and modify
- ✅ All jobs in one place
