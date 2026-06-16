# SEO Action Plan — jameskilby.co.uk

Prioritised against the findings in `FULL-AUDIT-REPORT.md`. Effort is rough order-of-magnitude.

> **Status — last reviewed 2026-06-16.** Most of the original plan has shipped.
> Done: **C1, C2** (#60), **H1** (#61), **H2** (#62), **H4** (#63), **M2** (#64/#65),
> **M5** (#68/#69), **L1** (#91). In progress on `feat/seo-cwv-drift-entity`:
> **H3** (CrUX field metrics), **M4** (drift baseline), **M1 + L3** (entity enrichment).
> Genuinely still open: **M3** (formal AI-crawler decision — robots.txt already
> carries an explanatory comment), **L2** (humans.txt). Completed items are kept
> below for the audit trail, marked ✅.

---

## 🔴 Critical — fix within 1 week

### C1. Replace AI-generated OG title/description with SEO title/meta description ✅ (#60)
**Impact:** Fixes 44 OG-description mismatches (61% of posts) and 13 OG-title mismatches (18%) in one change.
**Effort:** ~1 hr.
**Where:** `scripts/html_transformer.py` (or `scripts/fix_seo_issues.py` if that path is still active). Find whatever step is generating the marketing-copy OG tags and either:
- Default `og:title` to `<title>` minus the `" - James Kilby"` suffix
- Default `og:description` to `meta[name=description]`

The custom copy isn't adding value over the SEO-tuned text — it's diluting it on the social-share surface.

**Verify:** After the next deploy, re-run the bulk meta sweep in this audit (the Python block in the audit conversation) — expect mismatch counts to drop to 0.

### C2. De-duplicate `BreadcrumbList` JSON-LD on post pages ✅ (#60)
**Impact:** Removes "Breadcrumbs item not specified" Search Console warnings; cleaner rich-result eligibility.
**Effort:** ~30 min.
**Where:** Two `<script type="application/ld+json">` blocks on `/2017/05/money-saving-uk-version/` both contain a `BreadcrumbList`. Check whether the duplicate originates from the WP plugin (Yoast/Rank Math) emitting one and the static-pipeline emitting another. Keep the pipeline's (it's the one inside the main `@graph`) and strip the standalone block.

**Verify:** Search Console → Enhancements → Breadcrumbs after re-deploy; should drop to 0 warnings on affected URLs.

---

## 🟠 High — fix within 1 month

### H1. Shorten `<title>` on long pages (drop brand suffix conditionally) ✅ (#61)
**Impact:** 32 / 72 posts (44%) currently truncate in mobile SERP. Better click-through on long-tail queries.
**Effort:** ~30 min.
**Where:** In whichever step appends `" - James Kilby"`, add: *if the body title is already > 55 chars, skip the suffix*. Single conditional.

**Verify:** Run the bulk title-length check again — expect title>70 count to drop from 32 to <5.

### H2. Generate `/llms.txt` (and optionally `/llms-full.txt`) ✅ (#62)
**Impact:** Steers LLM ingestion toward your curated content; declares AI citation preferences. Increases AI Search Readiness score from 50→75+.
**Effort:** ~2 hr — one new pipeline step modelled on `scripts/markdown_api.py`.
**Where:** New `scripts/generate_llms_txt.py`. Output should sit at `public/llms.txt` and contain:
- Site description (1 paragraph)
- "Allowed for citation" toggle
- Top 10–20 pages with one-line descriptions, linking to the `/markdown/` equivalents
- A pointer to `/llms-full.txt` if you build it

Reference: https://llmstxt.org/ for the format spec.

### H3. Wire authoritative CWV measurement ⏳ (this PR — `scripts/fetch_crux_metrics.py`)
**Impact:** Replaces the estimated 75/100 perf score with real CrUX field data. Lets you measure regressions per deploy.
**Effort:** ~1 hr (credential setup).
**Where:** ~~Configure `google_auth.py --setup` per the `claude-seo:seo-google` skill.~~ Implemented repo-native instead: `scripts/fetch_crux_metrics.py` queries the Chrome UX Report API directly for origin + key URLs and reports p75 LCP / INP / CLS. The CrUX API needs only an API key (no OAuth) — set `CRUX_API_KEY` (GitHub secret / env). GSC OAuth integration remains a possible follow-up.

**Verify:** `make crux` (or `python3 scripts/fetch_crux_metrics.py`) with `CRUX_API_KEY` set; perf section should show field metrics rather than the lab-estimate disclaimer.

### H4. Align `Person.sameAs` and `Organization.sameAs` ✅ (#63)
**Impact:** Stronger E-E-A-T author signal — Google and AI engines both consume `sameAs` for entity reconciliation. Currently `Person` has GitHub + X, `Organization` has GitHub + LinkedIn. Pick one canonical list (`github + x + linkedin`) and use it on both.
**Effort:** ~10 min.
**Where:** Wherever the JSON-LD graph is templated.

---

## 🟡 Medium — fix within ~1 quarter

### M1. Add explicit `article.author` link to `Person` `@id` on TechArticle nodes ⏳ (this PR — `fix_seo_issues.py:fix_article_entity_links`)
**Impact:** Tightens the article→author entity link for AI Overviews and Google's author-as-entity model.
**Effort:** ~30 min in the JSON-LD generator.

### M2. Re-evaluate post-page `cache-control: max-age=0` ✅ (#64/#65)
**Impact:** Currently posts have `cache-control: public, max-age=0, must-revalidate` — browsers won't soft-cache. The worker's KV layer compensates at the edge, but a `max-age=60` or `max-age=300` would help repeat visits without breaking the KV TTL logic (KV controls *origin freshness*; `max-age` controls *browser freshness*).
**Effort:** ~15 min in `_worker.template.js`.
**Caveat:** Verify this doesn't conflict with the "absolute expiry, view-count updates don't reset the clock" invariant called out in `CLAUDE.md`.

### M3. Make a deliberate decision on AI crawler access
**Impact:** Currently GPTBot / ClaudeBot / PerplexityBot are *implicitly* allowed. Either keep that and document why (it aligns with the `/markdown/` + `/api/` ingestion-friendly stance), or block specific bots in robots.txt and steer them via `/llms.txt` instead.
**Effort:** Decision + ~10 min edit.

### M4. Establish drift baseline now ⏳ (this PR — `scripts/drift_baseline.py`)
**Impact:** Lets future audits diff against today's state and catch silent regressions on every auto-deploy.
**Effort:** ~5 min.
**Where:** ~~claude-seo plugin script.~~ Implemented repo-native: `scripts/drift_baseline.py` snapshots key SEO signals (title, meta description, canonical, robots, JSON-LD @types, h1, og tags) from the built `public/` tree to a committed `docs/seo-audit-2026-06/seo-baseline.json`, with a `--check` mode that diffs the current build against it. Intended as a non-blocking warning step in the deploy workflow.
**When:** Snapshot taken from the corrected state (after C1/C2 et al. shipped).

### M5. Strengthen homepage `<h1>` ✅ (#68/#69)
**Impact:** Minor. `<h1>James Kilby</h1>` is thin for a content-heavy homepage. Consider `James Kilby — VMware, Homelab & Cloud Infrastructure Notes` (matching the `<title>`) or a topic-led variant.
**Effort:** ~10 min.

---

## 🔵 Low — backlog

### L1. Optional `HowTo` / `FAQPage` schema ✅ (FAQPage shipped in #91)
On step-by-step posts (VCF 9 offline depot, vSphere power-management, AI homelab automation), adding `HowTo` schema would improve AI extraction and citation citability — even though Google deprecated rich-result eligibility for most sites in mid-2023. `FAQPage` auto-injection shipped in #91; `HowTo` remains backlog.

### L2. Add `humans.txt`
Optional, no SEO impact, but free brand signal.

### L3. Article `mentions` / `about` enrichment ⏳ (this PR — `fix_seo_issues.py:fix_article_entity_links`)
Add specific entity refs (e.g., `https://www.wikidata.org/wiki/Q14958` for VMware) under `mentions` on the most-trafficked posts. Helps AI engines connect content to authoritative entities. Implemented as a `Config.TOPIC_ENTITIES` map matched against each post's section/keywords; emits `about` (primary topic) + `mentions` (matched topics) with `sameAs` to Wikipedia/Wikidata.

---

## Recommended sequence

1. ~~**Today–this week:** C1 + C2.~~ ✅ Shipped (#60).
2. ~~**Next week:** H1, H2, H4.~~ ✅ Shipped (#61, #62, #63).
3. **Now (this PR):** H3 (CrUX field metrics), M4 (drift baseline), M1 + L3 (entity enrichment).
4. **After this PR merges:** set `CRUX_API_KEY` as a GitHub secret, run `make crux` to confirm field data flows; take the first drift snapshot from the next clean build.
5. **Backlog:** M3 (formal AI-crawler decision), L2 (humans.txt), HowTo schema, optional GSC OAuth for query-level data.
6. **Quarterly:** Re-run the full audit and diff against the drift baseline.

---

## What's not in this plan

- **Hand-editing files in `public/`.** Per `CLAUDE.md`, `public/` is build output — all the above fixes go in the pipeline scripts and templates. The auto-deploy will regenerate `public/` correctly on next push.
- **Acting on the estimated CWV score (75).** Wait for real PSI / CrUX data before any perf-tuning work; the headers and pipeline look healthy and acting on the estimate would be guesswork.
