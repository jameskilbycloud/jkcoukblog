# Contributing

## Branch Strategy

The `main` branch is the production branch. Cloudflare Pages auto-deploys from it.

The CI pipeline (`deploy-static-site.yml`) commits and pushes generated static files directly to `main`. This is by design — the WordPress content is the source of truth, and the static site in `public/` is a build artifact that gets committed.

For code changes to scripts, workflows, or the worker template, create a feature branch and open a PR.

## Local Development

### Prerequisites

- Python 3.11+
- Self-hosted GitHub runner (for Cloudflare Access authentication)
- `WP_AUTH_TOKEN` environment variable

### Setup

```bash
# Install core dependencies
make install

# Install all dependencies (including dev/CI tools)
make install-dev
```

### Common Tasks

```bash
# Full build pipeline
make build

# Generate static site only
make generate

# Run all validation checks
make validate

# Start local preview server
make deploy-local

# Run spell checker
make spell-check

# Show all available targets
make help
```

## Commit Conventions

Use these prefixes for commit messages:

| Prefix | Purpose |
|--------|---------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `chore:` | Maintenance, cleanup |
| `debug:` | Debugging changes |
| `revert:` | Revert previous commit |

Keep commits focused. Include what changed and how to verify.

## Configuration

All URLs and domains are centralised in `scripts/config.py`. Do not hardcode URLs in scripts.

Secrets are stored in GitHub Secrets (repository settings) and accessed via environment variables:

- `WP_AUTH_TOKEN` (required) — WordPress Basic Auth
- `SLACK_WEBHOOK_URL` (optional) — Slack notifications
- `CLOUDFLARE_API_TOKEN` (optional) — Cache purge
- `OLLAMA_API_CREDENTIALS` (optional) — AI spell check

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Python automation scripts |
| `public/` | Generated static site (deployed by Cloudflare Pages) |
| `docs/` | Project documentation |
| `workers/` | Cloudflare Workers (search API, Slack notifier) |
