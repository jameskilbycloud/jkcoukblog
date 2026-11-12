# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A WordPress → static site automation pipeline. WordPress (private, behind Cloudflare Access at `wordpress.jameskilby.cloud`) is the **source of truth** for content. Python scripts pull posts via the REST API, transform them, optimise everything, and publish the resulting static site (`public/`) to the `site` branch. Cloudflare Pages auto-deploys from `site`.

The site at `jameskilby.co.uk` is fronted by an Advanced Mode Worker (`_worker.template.js` → copied to `public/_worker.js` at deploy) that adds a KV-backed HTML cache, view tracking, smart TTLs, and security headers.

## Branch model — important

`main` holds code only. **The built site lives on the `site` branch**: a single parentless commit containing `public/`, force-pushed by `deploy-static-site.yml` on every deploy. Cloudflare Pages' production branch is `site`. `public/` is gitignored on main — the pipeline extracts the published site from `site` at the start of each build (incremental seeding, AVIF/WebP reuse) and diffs against it to decide what to purge.

Implications:
- `site` has no history by design. Don't branch from it, merge it, or open PRs against it. To undo a bad deploy use `rollback-site.yml`, which rolls back via Cloudflare Pages' own deployment history.
- The pipeline still commits small build caches to main (`chore(build): update build caches - <date>`), and `quality-checks.yml` commits Lighthouse scores (`chore(lighthouse): …`). Those are expected.
- Never hand-edit files inside `public/` to "fix" content — content changes belong in WordPress, not in the build artifact. Script/template changes are the only thing humans edit.
- Code changes (scripts, workflows, worker template) should go through a feature branch + PR.

## Common commands

The `Makefile` is the primary entry point — run `make help` to see all targets. Key ones:

```bash
make install         # pip install -r requirements.txt
make install-dev     # also installs requirements-dev.txt

make build           # full pipeline: validate-source → generate → optimize → validate
make generate        # WP REST → static (writes to ./static-output by default)
make optimize        # images (AVIF/WebP) → CSS → HTML → brotli/gzip
make validate        # test-csp + validate-html + validate-deployment
make deploy-local    # serve ./public on :8080

make test-csp        # CSP must allow Utterances, Plausible, Credly — fails build if not
make spell-check     # AI spell checker (needs OLLAMA_API_CREDENTIALS)
```

`OUTPUT_DIR` defaults to `./public` and `STATIC_DIR` to `./static-output`. Override on the command line if needed (`make optimize OUTPUT_DIR=./static-output`).

`WP_AUTH_TOKEN` is **required** for any target that hits WordPress (`generate`, `validate-source`). Without it, generation will fail. The protected WP instance also requires running on a self-hosted runner with a Cloudflare Access service token — running `make generate` from a generic machine without that token will not work.

### Tests

Two layers:

1. **Unit tests** in `tests/` run with pytest (`make test` or `pytest tests/`). They cover the pure logic: incremental cache, critical-CSS truncation, typo-patch matching, the `wp_session` factory, and config invariants. Linting is `make lint` (`ruff check scripts/ tests/`, config in `ruff.toml` — critical rules only, tighten as files get touched). Both run in CI via `.github/workflows/python-checks.yml` on changes to `scripts/`/`tests/`.
2. **Pipeline test scripts** in `scripts/test_*.py` are single-purpose, run individually, and exit non-zero on failure:

```bash
python3 scripts/test_csp.py                                              # CSP validation
python3 scripts/test_live_site_formatting.py --url https://jkcoukblog.pages.dev   # live-site checks
```

### GitHub Actions

```bash
gh workflow run deploy-static-site.yml   # trigger main pipeline
gh run list --limit 10
gh run watch
gh run view <run-id> --log
gh run rerun <run-id> --failed
```

## Architecture

### The pipeline (28 steps, see `.github/workflows/deploy-static-site.yml`)

The order matters and each stage assumes the previous one ran. If you modify a step, understand what consumes its output:

1. **Generate** (`wp_to_static_generator.py`) — pulls posts via WP REST API. Incremental by default (uses `modified_after`); cached state lives in `.image_optimization_cache/` and the build cache. `incremental_builder.py` uses BLAKE2b hashes to skip unchanged content.
2. **Markdown export + API** — `markdown_exporter.py` and `markdown_api.py` produce `/markdown/` and `/api/` paths the worker knows how to serve.
3. **CSP validation** (`test_csp.py`) — **fails the build** if the configured CSP would block Utterances comments, Plausible, or Credly badges. If you change the CSP in `_worker.template.js`, run this locally first.
4. **Image optimisation** (`optimize_images.py` → `convert_images_to_picture.py`) — generates AVIF + WebP (4 parallel workers), then rewrites `<img>` into `<picture>` with sources + fallbacks. BLAKE2b cache means re-runs are cheap.
5. **CSS** — `optimize_css.py` removes unused selectors, `extract_critical_css.py` inlines above-fold CSS into `<head>`, then a minify pass.
6. **HTML** — `fix_seo_issues.py` (title length, meta description scoped to `<article>`/`<main>`, H1 dedup), `enhance_html_performance.py` (LCP `fetchpriority`, lazy loading, preconnect), `minify_html.py`.
7. **Compression** (`brotli_compress.py`) — pre-encodes `.br` (quality 11) and `.gz` (level 9) at build time. Only writes if reduction ≥ 5%. Runtime CPU cost is zero because Cloudflare serves the precompressed files.
8. **Final validation** (`validate_html.py`, `validate_deployment.py`) — checks Brotli integrity, AVIF/WebP presence, picture structure, etc.
9. **Commit + push** — build caches to main; `public/` as a fresh parentless commit force-pushed (with lease) to `site`, which triggers the Cloudflare Pages deploy.
10. **Post-deploy** — search index uploaded to Workers KV (`SEARCH_INDEX` namespace), selective KV cache purge for changed HTML pages, edge cache purge, IndexNow submission, Slack notify.

If you're touching anything in stages 4–7, run `make optimize OUTPUT_DIR=./static-output` after a `make generate` to verify locally.

### Key cross-cutting pieces

- **`scripts/config.py`** — single source of truth for URLs/domains. Never hardcode `jameskilby.co.uk`, `wordpress.jameskilby.cloud`, `jkcoukblog.pages.dev`, `ollama.jameskilby.cloud`, or `plausible.jameskilby.cloud` anywhere else. Edit `Config` and import from it.
- **`_worker.template.js`** — the Advanced Mode Worker. Gets copied to `public/_worker.js` during deploy. Owns: KV HTML cache (smart TTL — 5 min homepage, 15 min recent posts, 1 hr older; **absolute expiry**, view-count updates do not reset the clock), `/markdown/` and `/api/` routing, security headers, view tracking, selective purge.
- **KV namespaces** — `HTML_CACHE` and `SEARCH_INDEX`. Bindings are configured in the Cloudflare Pages dashboard (Settings → Functions → KV namespace bindings) — `wrangler.toml` only documents the IDs for ad-hoc `wrangler kv:*` commands. The Advanced Mode Worker reads them via `env.HTML_CACHE` / `env.SEARCH_INDEX` at runtime.
- **No Pages Functions, no standalone route Worker.** The repo previously had a Pages Function middleware (`functions/_middleware.js`) and a separate route-bound Worker (`workers/html-cache-kv.js`); both were dead code shadowed by the Advanced Mode Worker and have been removed. Don't reintroduce them — Cloudflare Pages ignores `functions/` whenever `public/_worker.js` exists, and there's no `wrangler deploy` step in CI for a route-bound worker. Some unrelated workers (search API, Slack notifier) still live in `workers/`; superseded versions live in `workers/archive/` and should not be edited.
- **`_headers`** — static Cloudflare Pages header rules.
- **`incremental_builder.py`** — BLAKE2b content hashing that drives the "skip unchanged" behaviour across the pipeline. Cache invalidation bugs almost always trace back here or to `.image_optimization_cache/`.

### Cloudflare topology

```
Reader → jameskilby.co.uk → CF Pages (public/) ← Advanced Mode Worker (_worker.js)
                                                  ↑ KV: HTML_CACHE, SEARCH_INDEX
Self-hosted runner → wordpress.jameskilby.cloud (CF Access protected) → REST API → generate
```

The self-hosted runner is required because the WordPress instance is behind Cloudflare Access — a generic GitHub-hosted runner cannot reach it.

## Conventions

- **Python 3.11+**, 4-space indent, snake_case file/function names. Each script in `scripts/` is single-purpose and runnable standalone (`python3 scripts/foo.py [args]`).
- **Commit prefixes** in use: `feat:`, `fix:`, `docs:`, `chore:`, `debug:`, `revert:` (emoji optional). Auto-pipeline commits on main use `chore(build): update build caches - <date>`.
- **Secrets** are environment variables / GitHub Secrets. The `.git-hooks/pre-commit` hook runs `gitleaks protect --staged` before every commit — enable it with `git config core.hooksPath .git-hooks`. Allowlist false positives in `.gitleaks.toml`, do not bypass with `--no-verify`.
- **If a PR changes anything that lands in `public/`**, call it out explicitly in the PR description — the deploy summary's diff stat is the only record of what the next build changed.

## Documentation

`docs/README.md` is the documentation hub; deeper references live in `docs/DEPLOYMENT.md`, `docs/OPTIMIZATION.md`, `docs/IMAGE_OPTIMIZATION.md`, `docs/SEO.md`, `docs/PAGES_KV_SETUP.md`, `docs/BUILD_AND_DEPLOY_DOCUMENTATION.md`. Read these before making non-trivial changes to the corresponding subsystem.
