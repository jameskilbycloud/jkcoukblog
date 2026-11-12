# SEO code review: jkcoukblog (2026-10-20)

Read-only code review. Nothing was fixed, committed, pushed or deployed. This file is the only change.

**How this was checked**
- Code read at `origin/main` = `70716dcf8a` (local `main` is 17 commits behind; all `file:line` references below are at `origin/main`).
- Files: `config.py`, `fix_seo_issues.py`, `validate_seo.py`, `breadcrumb_navigation.py`, `wp_content_discovery.py`, `page_seo_meta.py`, `content_schema_rewriter.py`, `site_artifacts_builder.py` (sitemap/robots/lastmod), `generate_og_images.py`, the SEO calls in `wp_to_static_generator.py:process_html` and `html_transformer.py:_apply_seo_fixes`.
- Grounded against `docs/seo/seo-recommendations-2026-10-19.md` (B1–B11), `docs/seo/seo-gsc-insights-2026-10-19.md` and the SEO fix backlog (2026-08-31, since deleted). Those findings are not re-derived here; this report gives their **code cause** plus new defects.
- Behaviour checked three ways: a JSON-LD scan of all `public/**/index.html` at `origin/main`; small probes that call the real functions on crafted input (results quoted below); `pytest tests/test_fix_seo_issues.py tests/test_config.py` → **30 passed**.

## Summary

| # | Pri | Finding | Known? |
|---|---|---|---|
| 1 | **P0** | `/evs/` is noindexed by config **and** skipped by the validator, so no check can catch it | B1 (cause + new: validator blind) |
| 2 | **P0** | Author links never repaired: `_link_author_to_person` only fills a missing `@id`, and `'James'` in `PERSON_CANONICAL_NAMES` makes the pipeline enrich the 404 Person | B3 (cause) |
| 3 | **P1** | Article dates come from a frozen Rank Math saved schema; the pipeline only fills gaps and the sitemap prefers the same frozen value | B2 (cause) |
| 4 | **P1** | `ensure_image_alt_text` overwrites decorative `alt=""`, turns `data:` URIs into alt text, and a unit test locks the behaviour in | B7 (cause + new) |
| 5 | **P1** | The OG card generator only triggers on the ChatGPT fallback image, never on small featured images | B4 (cause) |
| 6 | **P1** | `add_site_schema` misses list-typed `["Person","Organization"]` and appends a second `#organization` node on every page | B10 (cause) |
| 7 | **P1** | Validator blind spots and threshold drift: Article checks run on `/YYYY/MM/` posts only; title/description limits disagree in three places, none of them in `config.py` | New |
| 8 | **P1** | Two noindex sources disagree: `page_seo_meta` hard-codes tag-only noindex and says categories "should be indexed" | New |
| 9 | P2 | `_fix_jsonld_object` prefixes the domain onto any JSON-LD string that starts with `/` (FAQ text, articleBody), and skips strings inside lists | New |
| 10 | P2 | `fix_jsonld_absolute_ids` turns `//host` into `https://jameskilby.co.uk//host` and ignores `#fragment` ids; 21 pages share `@id:"#rank-math-toc"` | New |
| 11 | P2 | Silent failure paths: `SEOFixer.process_file` swallows all exceptions; post discovery stops on any non-200 | New |
| 12 | P2 | `HTMLTransformer._apply_seo_fixes` is a hand-copied mirror of `SEOFixer.process_file` | New (maintainability) |
| 13 | P2 | Smaller defects (sitemap noindex sniff, canonical ordering, breadcrumb names, hard-coded sitemap page list, and more) | New |

---

## P0

### 1. `/evs/` noindex: wrong config, and the validator shares the same mistake
- **Where:** `scripts/config.py:176` `r'^/evs/?$'  # raw event log`; `scripts/validate_seo.py:68` `SKIP_PATH_PARTS = (... '/evs/',  # raw event log ...)`; `scripts/validate_seo.py:283-289` (noindex check runs only `if robots and is_post`); `scripts/fix_seo_issues.py:552` (docstring lists `/evs/` as a utility page).
- **What's wrong:** Four places carry the same wrong belief. Config noindexes `/evs/` and drops it from the sitemap. The validator also **skips the page completely**, and its `noindex-on-post` guard only covers `/YYYY/MM/slug/` paths. So nothing in the build can notice a content page being noindexed.
- **Failure:** The scan at `origin/main` shows `evs/index.html` has an `Article` JSON-LD node **and** `robots="noindex,follow"`. The AWS EVS hub is out of the index; GSC shows it getting 1 impression.
- **Fix:**
  1. Delete the `/evs/` entry in `config.py:176` and in `validate_seo.py:68`, and fix the docstring at `fix_seo_issues.py:552`.
  2. Add a validator rule that fails the build when any page carries an Article-family node **and** `noindex`, unless its path is on an explicit allowlist in `Config` (today only `/privacy-policy-2/` would be on it). That would have caught this bug.

### 2. Author entity split (`/author/admin/`): the code cause
- **Where:**
  - `scripts/fix_seo_issues.py:1168-1187` `_link_author_to_person`: `if isinstance(a, dict) and not a.get('@id')`.
  - `scripts/config.py:68` `PERSON_CANONICAL_NAMES = ('James Kilby', 'James')`.
  - `scripts/fix_seo_issues.py:1355-1363` `fix_person_enrichment.is_target_person`.
  - `scripts/validate_seo.py:143` (the dangling-author check fires only when the author dict is exactly `{"@id": …}`).
- **What's wrong:**
  - `fix_article_entity_links` resolves the right `#person` id, but `_link_author_to_person` only adds an `@id` when none is present. Rank Math's `{"@id": ".../author/admin/", "name": "James"}` already has one, so it is never rewritten.
  - Because `'James'` is a "canonical" name, `fix_person_enrichment` then gives the `/author/admin/` Person node the full `sameAs`, `jobTitle`, `knowsAbout` and `award`. The result is **two** Person entities with identical `sameAs`, and one of them has a URL that returns 404.
  - Probe on crafted input: after `fix_article_entity_links`, author is still `{'@id': 'https://jameskilby.co.uk/author/admin/', 'name': 'James'}`.
- **Failure:** 10 pages at `origin/main` (homelab-software, evs, privacy-policy-2, lab, vmc, about, ubiquiti-udm-beast, and others). The validator cannot see it: the author dict has 2 keys, the `@id` *is* defined in the graph, and most of these pages are not on post paths. This supports the branded query `james kilby` sitting at position 9.4.
- **Fix:**
  1. In `fix_article_entity_links`, treat any author whose `@id` matches `/author/` (or whose name is in `PERSON_CANONICAL_NAMES`) as the site owner. Replace it with `{"@id": TARGET_DOMAIN + "/#person"}` and drop the now-orphaned `/author/…` Person node from `@graph`.
  2. Keep `'James'` in `PERSON_CANONICAL_NAMES` for *matching*, but only enrich the node whose `@id` ends in `/#person`.
  3. In `validate_seo`, run `_validate_article_jsonld` on every page with an Article node (not only posts), and fail when `author.@id != TARGET_DOMAIN + '/#person'`.
  4. Optional: also normalise `twitter:data1` to `James Kilby` until the WordPress display name (A4) is changed.

## P1

### 3. Article dates: frozen saved-schema values are trusted, never reconciled
- **Where:**
  - `scripts/fix_seo_issues.py:1092-1102` (`fix_techarticle_dedupe_and_dates`, Step 2 only fills **missing** dates).
  - `scripts/site_artifacts_builder.py:431-435` (`_extract_modified_date` returns `article:modified_time` first).
  - `scripts/content_schema_rewriter.py:387-394` (copies the meta values as they are).
  - No pipeline script writes `article:*_time` (checked with grep).
- **What's wrong:**
  - Posts use a Rank Math **saved schema** (`@id …#schema-10682`, `#schema-10706`). Its dates are frozen at the time the schema was saved and have no offset: `2026-04-10T11:36:03`, `dateModified 2026-04-16T22:01:37`.
  - The `WebPage` node in the same `@graph` has the real values with an offset (`2026-07-11T13:21:15+00:00`), and so does `og:updated_time`.
  - `article:modified_time` repeats the frozen value. The sitemap takes it as source #1, so `<lastmod>` is stale.
- **Failure:** Freshness signals disagree. Many posts' `<lastmod>` cluster on the date the schema was saved (seo-recs: 56/81 on 2026-04-16). Google may come to distrust the lastmod values.
- **Fix:**
  1. In `fix_techarticle_dedupe_and_dates`, *overwrite* every Article-family node's `datePublished`/`dateModified` from the same graph's `WebPage` node when one exists. Otherwise append `+00:00` to naive values; WP REST `date_gmt` is UTC.
  2. Rewrite `article:published_time`/`article:modified_time` to the same values.
  3. In `_extract_modified_date`, take the **latest** of `WebPage.dateModified`, `og:updated_time` and `article:modified_time`, not the first one found.
  4. Add a validator warning for Article dates without an offset, and for TechArticle vs WebPage `dateModified` mismatches.

### 4. `ensure_image_alt_text`: invented alt text, decorative images broken
- **Where:** `scripts/fix_seo_issues.py:733-758`; enshrined by `tests/test_fix_seo_issues.py:65-68` (`test_alt_derived_from_filename`) and `:75-78`; a sibling pattern at `scripts/site_artifacts_builder.py:257-259` (sitemap `<image:title>` falls back to the filename).
- **What's wrong:** `if not img.get('alt')` treats an intentional `alt=""` (decorative image) the same as a missing alt. `Path(src).stem` is used on any `src`.
  - Probe: `<img alt="" src=".../IMG_8711.jpg">` → `alt="Img 8711"`.
  - Probe: `<img src="data:image/gif;base64,R0lG">` → `alt="Gif;Base64,R0Lg"`.
- **Failure:** Junk alt text (84/181 in-article images, seo-recs A2). Screen readers announce decorative images. The real gap is hidden from any check, so A2 has no running to-do list.
- **Fix:**
  - Leave `alt=""` alone, and skip `data:` URIs.
  - When alt is missing, set `alt=""` and record `(page, src)` in a report file (or have `validate_seo` warn: `img-alt-missing`, `img-alt-filename` for `^(IMG|DSC|Screenshot)[\s_-]?\d` style values).
  - Update the two tests to assert the new behaviour.
  - Drop the filename fallback for `<image:title>`; Google deprecated `image:title`/`caption` in 2022 anyway.

### 5. og:image under 1200 px: the generator never looks at size
- **Where:** `scripts/generate_og_images.py:53-55` (`FALLBACK_URL_PATTERNS = ('ChatGPT-Image',)`), `:156` `_is_fallback`; `scripts/content_schema_rewriter.py:116-125` (the default og:image width/height is hard-coded to `1024`, not measured).
- **What's wrong:** Cards are made only when og:image is the ChatGPT fallback. A real but small featured image (VCF depot: 588×501) is never upgraded.
- **Failure:** 46/81 indexable pages ship sub-1200 px share images (seo-recs B4).
- **Fix:** In `_process_one`, also generate a card when `og:image:width < 1200`, or when it is missing and the file measures under 1200 (Pillow is already imported). Rewrite only the `og:`/`twitter:` tags and keep the featured image as the JSON-LD `image`. Read the real logo dimensions instead of `1024`.

### 6. Duplicate `#organization` node on every page
- **Where:** `scripts/content_schema_rewriter.py:689-690` `if item.get('@type') == 'Organization': has_org = True`.
- **What's wrong:** Rank Math's identity node is `"@type": ["Person","Organization"]`, a list, so the equality test is never true. `add_site_schema` then appends a separate `Organization` `#organization` node, and `fix_organization_sameas` gives both nodes the same `sameAs`.
- **Failure:** Seen on every page scanned: the `#person` [Person, Organization] node **plus** the `#organization` node. Two entities claim one identity (seo-recs B10).
- **Fix:** Test `'Organization' in (t if isinstance(t, list) else [t])`. Better, per B10: emit one clean `Person` node and point `WebSite.publisher` at `#person` (it already does on Rank Math pages).

### 7. Validator blind spots and threshold drift
- **Where:** `scripts/validate_seo.py:53-56`, `:61`, `:279-280`, `:283-289`; `scripts/fix_seo_issues.py:312`, `:651-653`; `scripts/config.py:43-47`.
- **What's wrong:**
  - All semantic checks (Article fields, canonical-self, h1, noindex, og tags, thin content) are gated on `POST_PATH_RE`. The hub pages (`/about…/`, `/lab/`, `/vmc/`, `/homelab-software/`, `/media/`, `/evs/`) are indexable Article pages but get no checks, and that is exactly where #1 and #2 live.
  - Thresholds disagree:

    | Threshold | Source | Value |
    |---|---|---|
    | Title max | validator `TITLE_MAX_LEN` | 65 |
    | Title max | fixer `_TITLE_SERP_MAX_CHARS` | 60 |
    | Title max | config comment | "50-60" |
    | Description min / max | validator | 50 / 200 |
    | Description min / max | fixer `fix_meta_description` | 120 / 160 |
    | Description target | the reports | 110–155 |

    None of these live in `config.py`, despite the brief saying config owns them.
  - There are no checks for date offsets, og:image width, or alt quality.
- **Failure:** Regressions in #1–#5 pass the build. A title of 61–65 characters is shortened by the fixer but not flagged by the validator, and the reverse can happen for other values.
- **Fix:**
  - Add `TITLE_MAX_CHARS`, `META_DESC_MIN_CHARS` and `META_DESC_MAX_CHARS` to `Config` and import them in both files.
  - Define "indexable content page" as *not noindex and has an Article/WebPage node* and run the post checks on that set.
  - Add the date, og:image and alt checks named in #3–#5 as warnings.
  - There are **no unit tests for `validate_seo.py`** at all; add a few fixtures.

### 8. Two noindex sources that contradict each other
- **Where:** `scripts/page_seo_meta.py:134-170` `add_noindex_to_thin_pages` (hard-coded `('/tag/',)`; docstring: "Category pages … should be indexed"); `scripts/config.py:171-179` (`^/category/.+` noindexed); `scripts/fix_seo_issues.py:543-594`.
- **What's wrong:** Noindex policy is written twice with different rules and different formats (`noindex, follow` vs `noindex,follow`), and one copy ignores `Config`. Someone acting on B6 (index chosen categories) by narrowing `NOINDEX_PATH_PATTERNS` would see it work for categories but not tags. Someone reading `page_seo_meta` would believe categories are already indexed.
- **Fix:** Delete `add_noindex_to_thin_pages` and its call at `wp_to_static_generator.py:298`. `fix_thin_archive_noindex` already covers `/tag/` from config.

## P2

### 9. `_fix_jsonld_object` corrupts text fields and misses list strings
- **Where:** `scripts/content_schema_rewriter.py:204-233`.
- **What's wrong:** Every string value starting with `/` is prefixed with the domain, whatever its key. Strings inside lists are never visited (only dict/list items are recursed).
  - Probe: FAQ `Answer.text` `"/etc/hosts must contain…"` → `"https://jameskilby.co.uk/etc/hosts must contain…"`.
  - Probe: `sameAs: ["https://wordpress.jameskilby.cloud/x"]` is left unchanged.
- **Failure:** Command paths at the start of FAQ answers or `articleBody` turn into fake URLs. WordPress-host URLs in any list survive; only Person and Organization `sameAs` are cleaned later.
- **Fix:** Restrict rewriting to URL keys (`@id`, `url`, `item`, `image`, `logo`, `contentUrl`, `thumbnailUrl`, `sameAs`), recurse into list strings for those keys, and keep the WP-host replace for any string.

### 10. JSON-LD id handling: `//host` and shared `#rank-math-toc`
- **Where:** `scripts/fix_seo_issues.py:778-782` `absolutify`.
- **What's wrong:**
  - `value.startswith('/')` also matches protocol-relative `//cdn…`. Probe: → `https://jameskilby.co.uk//cdn.example.com/x`.
  - Fragment-only ids are left relative. 21 posts at `origin/main` carry several `SiteNavigationElement` nodes that all share `"@id": "#rank-math-toc"`. JSON-LD processors merge nodes with the same id, so each page declares one node with up to 11 conflicting `name` values.
- **Fix:** Skip `//` values. Rewrite `#frag` ids to `<canonical>#frag-<n>`, or drop the TOC `SiteNavigationElement` nodes, which have no rich-result value.

### 11. Silent-failure paths
- `scripts/fix_seo_issues.py:173-175`: `process_file` catches every exception, prints a warning and returns `False`. One bad page skips *all* SEO fixes and the build stays green (`main` always exits 0). Count the failures and exit non-zero if there are any.
- `scripts/wp_content_discovery.py:203-212`: the full-build post loop `break`s on **any** non-200, including a 5xx or 401 on page 1, then carries on with pages and taxonomies. A transient WordPress error can produce a build with few or no posts. `validate_seo` only errors on a completely empty sitemap. Raise on non-200 for page 1, and add a validator floor: the sitemap URL count must not fall more than about 10% below the previous build.

### 12. Hand-maintained mirror of the fix list
- **Where:** `scripts/html_transformer.py:325-384` vs `scripts/fix_seo_issues.py:89-163`; the docstring says "you MUST also add it here".
- **What's wrong:** Two copies of a 25-step ordered list. They match today; the next new fixer may land in one copy only. That is a drift bug waiting to happen, on the path that actually runs in CI.
- **Fix:** Add `SEOFixer.apply_all(soup, file_path) -> bool` and have both `process_file` and `_apply_seo_fixes` call it.

### 13. Smaller defects
- **Sitemap noindex sniff reads only the first 4 KB** (`site_artifacts_builder.py:539-550`). `fix_thin_archive_noindex` *appends* its robots meta at the end of `<head>` (`fix_seo_issues.py:590`). Config patterns cover this today, but a WordPress-set noindex placed after a large inline `<style>` would stay in the sitemap. Parse `<head>` instead.
- **Canonical derivation order** (`fix_seo_issues.py:114-118`, `:877-883`): `_derive_canonical_url` says og:url was "already absolutified by fix_og_absolute_urls earlier", but that fixer runs *after* `fix_canonical_url`. It is harmless today because a relative og:url falls through to the file path, but swap the order or fix the comment. `validate_seo` canonical-self also only checks posts.
- **Breadcrumb names from slugs** (`breadcrumb_navigation.py:66`, `:81`): `.title()` produces `Aws`, `Vmware`, `Ai` in the visible trail and in the standalone BreadcrumbList. Use the WordPress term name (the archive `<h1>` or the REST `name`). On `/category/x/page/N/` the category crumb is marked `aria-current="page"` even though it is not the current page.
- **Hard-coded sitemap page list** (`site_artifacts_builder.py:365-372`): image entries are emitted only for dated posts plus six named pages. `/evs/` (once indexable) and any new page get no image entries. Base it on "page is in the sitemap and has an `<article>`".
- **Tag descriptions = first post excerpt** (seo-recs B8): `page_seo_meta.py:35-43` keeps any existing description unless it contains both `James Kilby` and `technical blog`, so a Rank Math excerpt survives. Always apply the taxonomy template, or a WordPress term description when one is set.
- **`fix_meta_description`** (`fix_seo_issues.py:661-686`): on archives `soup.find('article')` is the first post card, so "expanded" descriptions come from another page. The concat path joins `desc + ' ' + p_text` with no sentence break. Skip archives.
- **`fix_pagination_meta_description`** (`page_seo_meta.py:129-130`) inserts a literal `...` mid-string, the anti-pattern the validator treats as broken. Use `SEOFixer._clean_truncate`.
- **`fix_blogposting_to_techarticle`** (`fix_seo_issues.py:934-935`) stamps `proficiencyLevel: Expert` on every post, diary posts included. It is a cosmetic claim; drop it or derive it from a category.
- **`ensure_homepage_h1`** (`page_seo_meta.py:207-208`) appends children while iterating `title_elem.children`, which skips every other child. It is a fallback path only; iterate over `list(title_elem.children)`.
- **Dead branch**: `_get_sitemap_priority` `'/category/'` → `0.5` (`site_artifacts_builder.py:526`) can never apply while categories are noindex.

---

## Suggested order of work
1. **#1 + #2 + #7** (one PR): config, fixer and validator changes, so the build fails if `/evs/` or the author split ever comes back.
2. **#3** (dates and lastmod) and **#6** (organization node): both are JSON-LD only and low risk.
3. **#4** (alt text) and **#5** (OG cards): both change files in `public/`, so call that out in the PR.
4. P2 items when the files are next touched.

---
*Jim (hive agent), card HAG-23. Read-only: no content, scripts, config or deployment changed.*
