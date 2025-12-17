# Spell Check Tracking

## Overview
The spell checker now supports incremental checking - it only checks posts that have been modified since the last check, avoiding redundant checks of unchanged content.

## How It Works

### Timestamp Tracking
- A file `.last_spell_check_timestamp` stores the timestamp of the last spell check run
- This file is committed to the repository to persist across workflow runs
- The timestamp is in ISO 8601 format (e.g., `2024-12-08T10:30:00Z`)

### Deployment Workflow (`deploy-static-site.yml`)
The spell check in the deployment workflow automatically:
1. Reads the last check timestamp from `.last_spell_check_timestamp`
2. Only checks posts modified after that timestamp using the WordPress API `modified_after` parameter
3. If no timestamp file exists (first run), it falls back to checking the 3 most recent posts
4. After checking, it saves the current timestamp for the next run

### Manual Spell Check Workflow (`spell-check.yml`)
The manual spell check workflow now has two modes:

#### Mode 1: Check Recent Posts (default)
- Specify the number of posts to check (default: 5)
- Use this for comprehensive checks or when you want to review specific posts
```bash
# Check last 10 posts
post_count: 10
check_modified: false
```

#### Mode 2: Check Modified Posts
- Only checks posts modified since the last check
- Enable by setting `check_modified: true`
- Automatically updates the timestamp after successful check
```bash
# Only check modified posts
check_modified: true
```

## Benefits

1. **Efficiency**: Avoids re-checking unchanged posts, saving time and API calls
2. **Targeted**: Only reviews content that has actually changed
3. **Scalability**: As your blog grows, check times remain constant
4. **Flexible**: Can still manually check any number of recent posts when needed

## WordPress API Integration

The checker uses the WordPress REST API's `modified_after` parameter:
```python
params = {
    'per_page': count,
    'status': 'publish',
    'orderby': 'modified',
    'order': 'desc',
    'modified_after': '2024-12-08T10:30:00Z'  # ISO 8601 timestamp
}
```

This ensures only posts modified after the specified time are returned and checked.

## First Run Behavior

On the very first run (when no timestamp file exists):
- The deployment workflow checks the 3 most recent posts
- The manual workflow checks the configured number of posts (default: 5)
- A timestamp is created for subsequent incremental checks

## Resetting the Tracker

To force a full check of recent posts:
1. Delete the `.last_spell_check_timestamp` file
2. Commit and push the change
3. The next run will check recent posts and create a new timestamp
