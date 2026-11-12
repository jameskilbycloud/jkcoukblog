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
make deploy-local    # serve ./static-output on :8080
make fetch-site      # extract the live build (site branch) into ./public

make test-csp        # CSP must allow Utterances, Plausible, Credly — fails build if not
make spell-check     # AI spell check of the last 3 posts (SPELL_POSTS=n; needs WP_AUTH_TOKEN + OLLAMA_API_CREDENTIALS)
```

`STATIC_DIR` defaults to `./static-output` and `OUTPUT_DIR` defaults to `STATIC_DIR`, so `make build` generates, optimises and validates the same directory. `public/` is gitignored — CI only moves `static-output` there at publish time. To work against the live build instead: `make fetch-site`, then pass `OUTPUT_DIR=./public`.

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

### The pipeline (see `.github/workflows/deploy-static-site.yml`; stage-by-stage table in `docs/DEPLOYMENT.md`)

The order matters and each stage assumes the previous one ran. If you modify a step, understand what consumes its output:

0. **Restore** — `public/` is extracted from the `site` branch (`PREV_SITE_SHA`); the incremental build cache and raw pre-transform HTML snapshot come from the Actions cache.
1. **Pre-flight** — CSP validation (`test_csp.py`) **fails the build** if the CSP would block Utterances, Plausible, or Credly badges. The CSP lives in the repo-root `_headers` file (the build stamps the same line into `_worker.js` for Worker-built responses) — run `make test-csp` before changing it; `_redirects` size check; WordPress source health.
2. **Generate** (`wp_to_static_generator.py` → `./static-output`) — seeded from the restored `public/`, then only posts modified since the last build are re-fetched (`modified_after`). `incremental_builder.py` uses BLAKE2b hashes to skip unchanged content.
3. **Markdown export + API** — `markdown_exporter.py` and `markdown_api.py` produce `/markdown/` and `/api/` paths the worker knows how to serve; then `llms.txt`.
4. **Image optimisation** (`optimize_images.py`) — AVIF + WebP (4 parallel workers), cached in `.image_optimization_cache/optimization_cache.json`; derivatives from the previous build are reused.
5. **CSS** — `optimize_css.py` removes unused selectors, then a minify pass.
6. **HTML, single pass** (`html_transformer.py`) — one parse per file running the passes from `fix_seo_issues.py` (title length, meta description scoped to `<article>`/`<main>`, H1 dedup), `convert_images_to_picture.py` (`<img>` → `<picture>`), `enhance_html_performance.py` (LCP `fetchpriority`, lazy loading, preconnect), `extract_critical_css.py` (critical CSS for the still-async sheets: rules whose selectors match an element in the first screen — body start to ~100 elements into `<main>`, footer excluded — inlined as one `<style data-critical-for>` right before each sheet's `<link>` so cascade order matches the final page; 16 KB cap; runs after small WP sheets are inlined in full) and `minify_html.py`. Then internal links for orphan posts, standalone pages, soft-404 artefacts + Worker stamp, OG images, font subset, JS minify.
7. **Compression** (`brotli_compress.py`) — pre-encodes `.br` (quality 11) and `.gz` (level 9) at build time. Only writes if reduction ≥ 5%. Runtime CPU cost is zero because Cloudflare serves the precompressed files.
8. **Final validation** (`validate_html.py`, `validate_deployment.py`, `validate_seo.py`) — Brotli integrity, AVIF/WebP presence, picture structure, sitemap not shrunk vs the previous build.
9. **Commit + push** — build caches to main; `public/` as a fresh parentless commit force-pushed (with lease) to `site`, which triggers the Cloudflare Pages deploy.
10. **Post-deploy** — search index uploaded to Workers KV (`SEARCH_INDEX` namespace), selective KV cache purge for changed HTML pages, edge cache purge, IndexNow submission, Slack notify.

If you're touching anything in stages 4–7, run `make optimize OUTPUT_DIR=./static-output` after a `make generate` to verify locally.

### Key cross-cutting pieces

- **`scripts/config.py`** — single source of truth for URLs/domains. Never hardcode `jameskilby.co.uk`, `wordpress.jameskilby.cloud`, `jkcoukblog.pages.dev`, `ollama.jameskilby.cloud`, or `plausible.jameskilby.cloud` anywhere else. Edit `Config` and import from it.
- **`_worker.template.js`** — the Advanced Mode Worker. Gets copied to `public/_worker.js` during deploy. Owns: KV HTML cache (smart TTL — 5 min homepage, 15 min recent posts, 1 hr older; **absolute expiry**, view-count updates do not reset the clock), `/markdown/` and `/api/` routing, security headers, view tracking, selective purge.
- **KV namespaces** — `HTML_CACHE` and `SEARCH_INDEX`. Bindings are configured in the Cloudflare Pages dashboard (Settings → Functions → KV namespace bindings) — `wrangler.toml` only documents the IDs for ad-hoc `wrangler kv:*` commands. The Advanced Mode Worker reads them via `env.HTML_CACHE` / `env.SEARCH_INDEX` at runtime.
- **No Pages Functions, no standalone route Worker.** The repo previously had a Pages Function middleware (`functions/_middleware.js`) and a separate route-bound Worker (`workers/html-cache-kv.js`); both were dead code shadowed by the Advanced Mode Worker and have been removed. Don't reintroduce them — Cloudflare Pages ignores `functions/` whenever `public/_worker.js` exists, and there's no `wrangler deploy` step in CI for a route-bound worker. Some unrelated workers (search API, Slack notifier) still live in `workers/`.
- **`_headers`** — static Cloudflare Pages header rules, copied into the build by `site_artifacts_builder.py`, and the **source of truth for the CSP**. Pages doesn't apply `_headers` to Responses the Worker builds itself, so the Worker re-applies the security headers and gets the CSP line stamped in at build time.
- **`incremental_builder.py`** — BLAKE2b content hashing that drives the "skip unchanged" behaviour across the pipeline. Cache invalidation bugs almost always trace back here, to `.image_optimization_cache/`, or to the seed restored from the `site` branch. `force-full-deploy.yml` (also every Sunday) clears the incremental caches when a template change needs to reach every post.

### Cloudflare topology

```
Reader → jameskilby.co.uk → CF Pages (site branch: public/) ← Advanced Mode Worker (_worker.js)
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

`docs/README.md` is the documentation hub; deeper references live in `docs/DEPLOYMENT.md`, `docs/OPTIMIZATION.md`, `docs/IMAGE_OPTIMIZATION.md`, `docs/SEO.md`, `docs/PAGES_KV_SETUP.md`. Read these before making non-trivial changes to the corresponding subsystem.
