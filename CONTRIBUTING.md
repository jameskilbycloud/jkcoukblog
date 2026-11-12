# Contributing

## Branch Strategy

`main` holds code. The built site lives on the `site` branch — a single commit containing `public/`, force-pushed by `deploy-static-site.yml` on every deploy — and Cloudflare Pages deploys from `site`. `public/` is gitignored on `main`; WordPress is the source of truth for content. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#the-site-branch).

The pipeline still commits small build caches (`chore(build): …`) and Lighthouse scores (`chore(lighthouse): …`) to `main`.

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
| `scripts/assets/` | Site assets shipped at build time (fonts, `js/` with search.js + vendored fuse/splide) |
| `tests/` | pytest unit tests (`make test`; ruff config in `ruff.toml`) |
| `public/` | Build output — gitignored; published to the `site` branch (`make fetch-site` to inspect the live build) |
| `docs/` | Project documentation |
| `workers/` | Cloudflare Workers (search API, Slack notifier) |

## Root-Level Working Artifacts

Some files at the repo root are data, not documentation — know their lifecycle
before deleting or editing them:

| File | Lifecycle |
|------|-----------|
| `typo-patches.json` | **Consumed by CI** (`apply-typo-patches.yml` pushes fixes to WordPress). Entries are removed once applied. |
| `alt-patches.json` | **Consumed by CI** (`apply-alt-patches.yml`). Same lifecycle as typo patches. |
| `typo-patches.md`, `typo-patches-pending.md` | Human-readable companions to the JSON — keep in sync when editing patches by hand. |
| `docs/archive/site-audit-*.md` | Point-in-time audit reports (moved out of the repo root). Reference material only. |

Content fixes belong in WordPress (the source of truth) when possible — the
patch files exist for batch corrections applied via the REST API.
