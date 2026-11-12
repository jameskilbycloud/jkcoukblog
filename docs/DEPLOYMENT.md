# Deployment

How the site gets from WordPress to `jameskilby.co.uk`: the build-and-deploy
workflow, where the built site lives, the Cloudflare Worker in front of it, and
how to roll back. The workflow file itself
(`.github/workflows/deploy-static-site.yml`) is the source of truth — every
step carries a comment explaining why it exists. The six longest step bodies
live in `scripts/ci/` (`generate_site.sh`, `optimize_images.sh`, `compress.sh`,
`prepare_output.sh`, `publish_site.sh`, `kv_purge.sh`); the workflow snapshots
that directory right after checkout and runs them from the snapshot.

## Table of Contents
- [Overview](#overview)
- [The site branch](#the-site-branch)
- [Build and deploy workflow](#build-and-deploy-workflow)
- [Caches between runs](#caches-between-runs)
- [Cloudflare Pages Advanced Mode Worker](#cloudflare-pages-advanced-mode-worker)
- [Rollback](#rollback)
- [Other deploy-related workflows](#other-deploy-related-workflows)
- [Secrets](#secrets)
- [Troubleshooting](#troubleshooting)

---

## Overview

```
WordPress (private)  ──REST──►  self-hosted runner  ──force-push──►  site branch  ──►  Cloudflare Pages  ──►  jameskilby.co.uk
wordpress.jameskilby.cloud      deploy-static-site.yml               (public/ only)     production branch     + Advanced Mode Worker
(behind Cloudflare Access)                                                              = site                + KV HTML cache
```

- **Triggers:** `repository_dispatch` (type `wordpress-update`, sent when a post
  is published) and manual `workflow_dispatch`.
- **Runner:** self-hosted — the WordPress instance is behind Cloudflare Access,
  which a GitHub-hosted runner can't reach.
- **Concurrency:** group `wordpress-static-site-deploy`,
  `cancel-in-progress: false` — a second trigger queues behind the running
  build rather than cancelling it.

```bash
gh workflow run deploy-static-site.yml
```

---

## The site branch

`main` holds code. The built site lives on the **`site` branch**: one
parentless commit containing `public/`, replaced on every deploy. Cloudflare
Pages' production branch is `site` and preview deployments are off, so pushes
to `main` and PR branches don't build anything on Cloudflare.

Why: committing `public/` to `main` on every deploy grew the repository to 2 GB
of build history. `main`'s history was rewritten to remove it in November 2026.

What this means in practice:

- `public/` is gitignored on `main`. To look at the live build locally, run
  `make fetch-site` (extracts `site` into `./public`).
- `site` has no history by design — don't branch from it, merge it, or open PRs
  against it. Use [rollback](#rollback) to go back to an earlier build.
- The push is a force-push with a lease pinned to the `site` commit the build
  started from. If anything else published in between, the build fails rather
  than overwrite it.

---

## Build and deploy workflow

Two jobs. `build-and-deploy` does everything below; `spell-check` runs **after**
it (`needs: build-and-deploy`, so it doesn't compete for the runner) and is
`continue-on-error` — it never affects the deploy.

| Stage | Steps | Blocking? |
|-------|-------|-----------|
| Set up | Validate secrets (only `WP_AUTH_TOKEN` is required) · checkout · **restore `public/` from the `site` branch** · restore the incremental build cache and raw HTML snapshot (Actions cache) · install `jq` + `bc` (apt only if missing) · install Python deps (skipped when `requirements.txt` is unchanged) | Yes |
| Pre-flight | CSP check (`test_csp.py` — Utterances, Plausible, Credly) · `_redirects` under the Pages free-plan limit · WordPress source health (`validate_wordpress_source.py`) | Yes |
| Generate | `wp_to_static_generator.py` into `./static-output`, seeded from the restored `public/` so only posts modified since the last build are re-fetched · save build cache + raw snapshot | Yes |
| Extras | Markdown export + `/api/` JSON · `llms.txt` · content quality report (`content_validator.py`) | Content report is non-blocking |
| Optimise | Images to AVIF/WebP (`optimize_images.py`, cached) · CSS unused-rule removal + minify · single-pass HTML transformer (`html_transformer.py`: SEO fixes, `<picture>`, perf hints, critical CSS, minify) · internal links for orphan posts · standalone pages (`copy_standalone_pages.py`) · soft-404 artefacts + Worker stamp · per-post OG images · Anton font subset · vendored-URL rewrite · JS minify · Brotli + Gzip | Images, soft-404/Worker stamp and vendored-URL rewrite block; the rest are non-blocking — a failed pass ships that file unoptimised and is listed by "Report non-blocking step failures" |
| Validate | Playwright UI smoke tests · `validate_html.py`, `validate_deployment.py`, `validate_seo.py` in parallel (sitemap compared with the previous build's) · SEO drift check | Validators yes; Playwright and drift are non-blocking |
| Publish | Move `static-output` → `public/`, write `security.txt`, convert to relative URLs · changelog + stats pages, recompress · **commit build caches to `main` (if changed) and force-push `public/` to `site`** | Yes, except changelog/stats |
| Post-deploy | Search index → Workers KV · wait for the Pages deployment of the pushed `site` commit, then purge the changed pages from the KV HTML cache (purge-all above 30 pages) · purge changed static assets from the CDN · IndexNow · report non-blocking failures · dispatch `quality-checks.yml` · Slack | Non-blocking |

Changed pages are found by diffing the new `site` commit against the one the
build started from, so an incremental build with one edited post purges only
the pages that actually changed.

---

## Caches between runs

| What | Where it persists | Notes |
|------|-------------------|-------|
| Previous build (`public/`) | `site` branch | Seed for incremental generation; source of reused AVIF/WebP; sitemap baseline |
| `.build-cache.json` | Actions cache `incremental-build-cache-<run>` | Which posts were built and when (`modified_after` for the next run) |
| `.raw-html-snapshot/` | Actions cache `raw-html-snapshot-<run>` | Pre-transform HTML/CSS, so the optimisation passes always start from the same input |
| `.image_optimization_cache/optimization_cache.json` | Git, on `main` | BLAKE2b hashes of optimised images |
| `.last_spell_check_timestamp` | Actions cache `spell-check-<sha>` (spell-check job) | Incremental spell checking; gitignored. If the cache has expired the spell check falls back to the last 3 posts |

The two Actions caches are restored by prefix, so the most recent one wins.
`force-full-deploy.yml` deletes them and triggers a deploy; the next run is a
full rebuild.

---

## Cloudflare Pages Advanced Mode Worker

**Source:** `_worker.template.js`. The build stamps it into `public/_worker.js`
("Generate soft-404 artefacts and stamp Advanced Mode Worker"). When
`_worker.js` exists, Pages runs it for every request.

| Feature | Detail |
|---------|--------|
| KV HTML cache | Rendered HTML in the `HTML_CACHE` namespace |
| Smart TTL | Homepage 5 min · posts from this or last month 15 min · everything else 1 h |
| Absolute expiry | Set on first write; view-count updates reuse it, so popular pages don't stay cached longer |
| Fallback | Uses the Cache API when KV isn't bound |
| Purge | `POST /.purge?path=<url>` or `POST /.purge?all=true` with `X-Purge-Token` |
| Admin endpoints | `/diagnostic`, `/trace?path=<url>`, `/test` — all require the purge token |
| Also | Security headers on Worker-built responses (the CSP line is stamped in from `_headers`, which Pages doesn't apply to those), view tracking, `/markdown/` + `/api/` routing, Plausible proxy, `/api/power` (homelab power widget) |

**Bindings and secrets** (set in the Pages dashboard, not `wrangler.toml` —
see [PAGES_KV_SETUP.md](PAGES_KV_SETUP.md)):

| Name | Kind | Purpose |
|------|------|---------|
| `HTML_CACHE` | KV | HTML cache; also holds the latest power reading |
| `SEARCH_INDEX` | KV | Search index, uploaded by CI |
| `PURGE_TOKEN` | Secret | Gates `/.purge` and the admin endpoints |
| `POWER_TOKEN` | Secret | Gates `POST /api/power` ([homelab-power-widget.md](homelab-power-widget.md)) |
| `VMC_CSP_API_TOKEN` | Secret | VMware CSP API token for the `/vmc-analyzer/` Sizer proxy (`/api/sizer/*`) |
| `CF_ACCESS_TEAM_DOMAIN` | Variable | Cloudflare Access team (`<team>` or `<team>.cloudflareaccess.com`) |
| `CF_ACCESS_AUD` | Variable | Audience (AUD) tag of the Access app protecting `/api/sizer` |
| `ASSETS` | Automatic | The static files of the deployment |

Pages only picks up new variables and secrets on the **next deployment**.

**Sizer proxy (`/api/sizer/*`).** The analyzer's "Validate with official
VMware Sizer" calls these Worker routes, which spend the owner's CSP
credential, so they are owner-only: a Cloudflare Access self-hosted app on
`jameskilby.co.uk/api/sizer` allows only the owner, and the Worker also
verifies the `Cf-Access-Jwt-Assertion` JWT (signature, issuer, AUD, expiry)
on every request. If any of the three settings above is missing, the routes
return 401 rather than run. `/api/sizer/signin` is the sign-in link: Access
prompts, then it redirects back to `/vmc-analyzer/#design`. Tests:
`node --test tests/worker/`.

```bash
curl -X POST "https://jameskilby.co.uk/.purge?path=/2026/01/my-post/" \
  -H "X-Purge-Token: $CACHE_PURGE_TOKEN"
```

---

## Rollback

`rollback-site.yml` (manual) uses Cloudflare Pages' own deployment history:
with no input it switches production to the successful deployment before the
live one; give it a `deployment_id` to pick a specific one. It then purges the
KV HTML cache.

The rollback lasts until the next deploy, which rebuilds from `main` — revert
the change that broke the site on `main` first.

---

## Other deploy-related workflows

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `force-full-deploy.yml` | Manual · Sundays 03:00 UTC | Deletes the incremental caches, then dispatches a deploy with `force_static_purge=true`. Manual runs can set `reencode_images=true` to re-encode every AVIF/WebP from source |
| `quality-checks.yml` | Dispatched after each deploy · daily 03:00 UTC · manual | Lighthouse + live-site formatting checks against production; records scores to `data/lighthouse-latest.json` on `main` |
| `wordpress-backup.yml` | 1st + 15th of the month · manual | WordPress backup |

---

## Secrets

| Secret | Required | Used for |
|--------|----------|----------|
| `WP_AUTH_TOKEN` | Yes | WordPress REST API |
| `CLOUDFLARE_API_TOKEN` | No | KV upload, deployment polling, CDN purge, rollback |
| `CLOUDFLARE_ACCOUNT_ID` | No | Pages and KV API calls |
| `CLOUDFLARE_ZONE_ID` | No | CDN static-asset purge |
| `KV_SEARCH_INDEX_ID` | No | Search index namespace |
| `CACHE_PURGE_TOKEN` | No | `/.purge` (must match the Worker's `PURGE_TOKEN`) |
| `SLACK_WEBHOOK_URL` | No | Notifications |
| `OLLAMA_API_CREDENTIALS` | No | Spell check (`user:password`) |
| `PLAUSIBLE_SHARE_LINK` | No | `/stats/` page |

Missing optional secrets skip the step that needs them; the build still deploys.

---

## Troubleshooting

**"site branch moved since this build started"** — something else published
while this build ran (a second runner, a manual push). Re-run the workflow; it
will seed from the newer `site` commit.

**Site shows old content after a deploy**
1. Check the "Purge changed HTML from KV cache" step: did it find the deployment
   for the pushed commit, and which paths did it purge?
2. Purge by hand: `curl -X POST "https://jameskilby.co.uk/.purge?path=/your-path/" -H "X-Purge-Token: $TOKEN"`
3. In the Pages dashboard, check the latest production deployment is for the
   `site` commit in the step summary.

**A change to a template or script didn't reach old posts** — incremental builds
skip unchanged posts. Run `force-full-deploy.yml` (or wait for Sunday's).

**Images not converting to AVIF** — check the "Optimize images" step log for the
file, and that the "Install dependencies" step's Pillow AVIF check passed. To
re-encode everything, run `force-full-deploy.yml` with `reencode_images=true`.

**WordPress source validation fails**
```bash
curl -H "Authorization: Basic $WP_AUTH_TOKEN" \
  "https://wordpress.jameskilby.cloud/wp-json/wp/v2/posts?per_page=1"
```

```bash
gh run list --workflow=deploy-static-site.yml
gh run view <run-id> --log
gh run rerun <run-id> --failed
```

---

## Related Documentation
- [Main README](../README.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
- [PAGES_KV_SETUP.md](PAGES_KV_SETUP.md)
- [homelab-power-widget.md](homelab-power-widget.md)
