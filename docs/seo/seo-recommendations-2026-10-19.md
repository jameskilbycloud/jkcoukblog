# SEO recommendations: jameskilby.co.uk (2026-10-19)

Read-only review. Nothing was changed, committed or deployed.

**How this was checked**
- Code: `scripts/config.py`, `fix_seo_issues.py`, `content_schema_rewriter.py`, `site_artifacts_builder.py` read at `origin/main` (local `main` is 15 commits behind; PRs #212–#214 are included).
- Live `<head>` of 8 pages fetched with curl on 2026-10-19 ~13:50 UTC: home, `/2026/04/automated-vcf-9-offline-depot/`, `/category/homelab/`, `/tag/homelab/`, `/page/2/`, About, `/evs/`, plus `sitemap.xml` and `robots.txt`.
- Site-wide scan of all 264 HTML pages in `public/` at `origin/main` (81 indexable, 183 noindex).
- Reconciled with `docs/seo-fix-backlog.md` (2026-08-31, local only), `docs/archive/site-audit-2026-06-01-v2.md` and `docs/seo/link-audit-2026-10-19.md`.

## Summary

The technical SEO base is strong. Every indexable page has a unique title and meta description, a self canonical, full Open Graph and Twitter tags, exactly one H1, a BreadcrumbList, and Person/Organization/WebSite structured data with `sameAs`. The sitemap has lastmod and image entries and 0 broken URLs. Images are AVIF/WebP with width/height and lazy loading.

What is left is mostly **content quality in WordPress** (alt text, the About page title, short or thin posts) plus a few **generator bugs**:
- `/evs/` is wrongly noindexed. The config comment calls it a "raw event log", but it is the AWS EVS resources hub.
- Article dates have no timezone and disagree with each other.
- 8 pages point their author at a second "James" Person whose URL is a 404.
- 46 of 81 social images are smaller than 1200 px wide.

## Bucket A: fix in WordPress (source content)

| # | Pri | Issue | Why it matters | Where in WP | Effort |
|---|---|---|---|---|---|
| A1 | **High** | About page `<title>` and og:title are `about me` (8 chars, lowercase). Still open since the June audit. Its meta description is 167 chars and uses US "specializing". | The About page is the main "who is the author" (E-E-A-T, expertise and trust) page and the target of the Person entity. A weak title wastes the obvious "James Kilby" query. | Page 3037 → Rank Math → SEO title, e.g. `About James Kilby — Cloud & VMware Solution Architect`. Set description to ≤155 chars. Set featured image alt (now `About Me`). | 10 min |
| A2 | **High** | 84 of 181 in-article images have filename or generic alt text, e.g. `Screenshot 2022 10 05 at 12.56.21 1`, `IMG 8711`, or `<post title> Screenshot` repeated 2–3× per post. Worst posts: starlink, portainer, self-hosting-ai-stack, how-i-moved-…-cloudflare-pages, new-nodes, intel-optane, zen-internet. | Google Images and accessibility. Repeated identical alts add nothing. Alt text is the main relevance signal for screenshots in a technical blog. | Media Library → Alt Text per image (or in each post's image block). Start with the ~20 posts in the scan list (full list: re-run the scan in the appendix). | 2–4 h total, can be done in batches |
| A3 | **Med** | `/evs/` content: title 67 chars, description 197 chars, H1 (`… – Links & Resources`) differs from title (`… – Resources & Documentation`). Only matters once B1 makes the page indexable. | Truncated in results. Title/H1 mismatch weakens the topic signal. | `/evs/` page → Rank Math title ≤60 chars, description ≤155 chars, align H1. | 10 min |
| A4 | **Med** | WP author display name is `James`. It surfaces as `twitter:data1 "Written by: James"` on every post and as the Article author name on 8 pages. | Author-name consistency (`James Kilby`) helps Google tie posts to the author entity. | Users → Profile → "Display name publicly as" → `James Kilby`. Fixes it at the source for every page. | 2 min |
| A5 | **Med** | 10 indexable titles over 60 chars (was 5 in the August backlog; the threshold is now 60): zen-internet (76), vsphere-power-management (74), self-hosted-ai-stack (68), octopus-agile (65), zfs-on-vmware (64), packer-vsphere (64), web-development-improvements (63), nutanix-lcm (63), cloudflare 2018 (61), automating-ai-homelab (61). | Truncated in search results, so lower click-through. The generator already drops the brand suffix, so what is left is the post title itself. | Rank Math SEO title per post (leave the visible H1 alone). | 30 min |
| A6 | **Med** | 6 indexable pages have no featured image: lab-update-part-3-network, lab-update-part-5-desired-workloads, homelab-software, money-saving-uk-version, lab-storage (2018), media. Their TechArticle has no `image` (backlog P0-2, still open). | `image` is recommended for Article rich results. Shares fall back to the logo. | Set a featured image on each. B5 covers the generator fallback. | 20 min |
| A7 | **Med** | 13 meta descriptions under 110 chars (starlink 89, 100gb-s 82, vcm-specialist-hci 78, forcing-an-upgrade-to-vsphere-8 89, new-laptop 92, intel-optane 95, …). Backlog said 17, so it is improving. | Click-through only. Google often rewrites short descriptions. | Rank Math description per post, aim for 120–155 chars. | 30 min |
| A8 | **Med** | Thin content: about 37 posts are under 400 words of body text, e.g. nutanix-command-reference-guide 166, aws-status-page 171, vsan-cluster-shutdown 175, lab-update-part-3 176, ubuntu-disk-expansion 185. | Thin pages are the usual cause of "Crawled – currently not indexed". GSC data (C1) would confirm which ones Google actually drops. | Per post: expand the high-value ones; merge series such as `lab-update-part-1…5` into one updated guide with a 301 redirect (redirect goes in the worker); leave dated diary posts alone. Decide after GSC data. | Ongoing |
| A9 | Low | Internal links that hit a redirect (link audit §4.5): `/about-me/`, `/nutanix-command-reference-guide/`, `/stats`, `/changelog`. Plus 8 plain `http://` outbound links. | Wastes a little link equity and crawl. | Edit the hrefs in those posts. | 15 min |
| A10 | Low | `/vmc/` hub: thin intro (386 words), stray `.htmlv` link, empty "Table of Contents" heading (June audit). `/homelab-software/` has US "Optimize" and generic `→` anchor text. | Hub pages are the natural topic-cluster landing pages. | Page edits in WP. | 30 min |
| A11 | Low | Category descriptions are empty. The generator fills a template ("Browse all Homelab articles…"). | Only matters if categories become indexable (B6). A real 100–200-word intro then becomes the hub content. | Posts → Categories → Description, for Homelab, VMware, AI, AWS. | 1 h |

## Bucket B: add or change in deployment (generator, config, CI)

| # | Pri | Issue | Why it matters | File / change | Effort |
|---|---|---|---|---|---|
| B1 | **High** | `/evs/` is `noindex,follow` and left out of the sitemap because `config.py` `NOINDEX_PATH_PATTERNS` has `r'^/evs/?$'  # raw event log`. The live page is actually the **Amazon Elastic VMware Service resources hub** (Article schema, 2025-06 publish), the twin of `/vmc/`, which is indexed. The comment is factually wrong. | A topical page that should rank for "AWS EVS" is hidden from Google. This is a pure mistake, not a choice. | `scripts/config.py`: remove the `/evs/` entry. The sitemap and the meta tag both read this list. Then run a deploy (full rebuild not needed; it is a post-process step, but confirm it reaches `/evs/`). Ask James to confirm (C3). | 15 min + deploy |
| B2 | **Med** | Article dates: on 72 of 81 pages the TechArticle `datePublished`/`dateModified` (and `article:published_time`) have **no timezone** (`2026-04-10T11:36:03`). The same page's WebPage node has `+00:00`, and TechArticle `dateModified` (2026-04-16) disagrees with WebPage `dateModified` and `og:updated_time` (2026-07-11). The sitemap `<lastmod>` follows the first value. | Google advises a timezone on Article dates. Conflicting modified dates make Google trust lastmod and freshness signals less. 56 of 81 sitemap lastmods sit on the same day (2026-04-16), which already looks like a bulk edit. | `fix_seo_issues.py:fix_techarticle_dedupe_and_dates`: normalise every Article/WebPage date and the `article:*_time` meta to ISO-8601 with an offset (WP REST `date_gmt`/`modified_gmt` + `Z`), and use one modified value for TechArticle, WebPage, og:updated_time and `site_artifacts_builder._extract_modified_date`. Add a `validate_seo.py` check. | 2–3 h |
| B3 | **Med** | 8 indexable pages (homelab-software, lab, vmc, About, packer-vsphere-golden-images, ubiquiti-udm-beast, nutanix-lcm, media) have Article `author` = `{"@id":"…/author/admin/","name":"James"}` plus a separate Person node with a Gravatar. `/author/admin/` returns **404**. All other pages link to `#person`. | Splits the author into two entities, one of them pointing at a dead URL. That undoes the E-E-A-T `sameAs` work in `config.py`. | `fix_seo_issues.py:fix_person_name` / `_link_author_to_person`: rewrite the `/author/admin/` Person to `{"@id":"https://jameskilby.co.uk/#person"}` and drop the duplicate node. A4 fixes the name at the source but not the @id. | 1–2 h |
| B4 | **Med** | 46 of 81 indexable pages have an og:image under 1200 px wide (e.g. the VCF depot post is 588×501). The generator already makes 1200×630 cards for archives and home (`/wp-content/uploads/og/*.png`). | `summary_large_image` and Google Discover (`max-image-preview:large` is already set) want images at least 1200 px wide. Small images get cropped or shown as small cards, so lower share click-through. | Extend the OG-card generator to posts whose featured image is under 1200 px wide. Keep the featured image as the JSON-LD `image`; put the card in og:/twitter:image. | 3–4 h |
| B5 | **Med** | 6 Article nodes have no `image` (list in A6). Backlog P0-2, still open. | Rich-results "recommended field" warning. | In `content_schema_rewriter.py` or `fix_techarticle_dedupe_and_dates`: fall back to the page og:image (or `Config.DEFAULT_OG_IMAGE_PATH`) when `image` is missing. | 1 h |
| B6 | **Med** (strategy) | All category archives are noindex (`NOINDEX_PATH_PATTERNS ^/category/.+`). This **supersedes backlog P0-1** ("categories absent from sitemap"): it was a deliberate choice, not a bug. | Honest view: as thin excerpt lists, noindex is right. But the 3–4 big categories (Homelab 27 posts, VMware, AI, AWS) are the natural topic-cluster hubs. With a real intro (A11) and pagination now generated (#212), indexing them can help rankings for broad queries. | `config.py`: narrow the pattern to exempt chosen slugs, e.g. `^/category/(?!homelab/|vmware/).+`. Leave tags, pagination (`/category/x/page/N/`) and the rest noindex. Do only together with A11. | 30 min + A11 |
| B7 | **Med** | `ensure_image_alt_text` fills a missing alt with a title-cased filename (`Screenshot 2022 11 21 at 17.36.13`, `IMG 8711`). | That hides the gap from `validate_seo` and gives search engines junk text. An empty `alt=""` is better than a fake one. | `fix_seo_issues.py:ensure_image_alt_text`: for camera/screenshot/hash filenames, emit `alt=""` and log the URL. Add a `validate_seo` warning listing images without real alt text, so A2 has a running to-do list. | 1 h |
| B8 | Low | Duplicate titles: 28 category/tag pairs share `"<X> Archives - James Kilby"`. `/page/2…7/` titles are the 150-char site description, with **no H1**. Tag pages use the first post's excerpt as their meta description. `og:type` is `article` on archives. | All are noindex, so search impact is small (cosmetic, and for social shares). | `fix_seo_issues.py`: template `Category: X – James Kilby` / `Tag: X – James Kilby`; `Posts – page N – James Kilby` for pagination plus a visually-hidden H1; set tag description from the template; `og:type=website` on archives. | 1–2 h |
| B9 | Low | `/about-james-kilby-solution-architect/` is typed `WebPage` + `Article` (headline `about me`). | `ProfilePage` with `mainEntity: #person` is the type Google documents for profile pages. It strengthens the author entity. | `content_schema_rewriter.py`: for the About path, set `@type: ProfilePage`, `mainEntity: {"@id": "#person"}`, and drop the Article node. | 1 h |
| B10 | Low | Merged `["Person","Organization"]` node with `@id #person` plus a separate `#organization` Organization node on every page (backlog P2). | Valid, but ambiguous for entity reconciliation. A personal blog is normally Person-only, with publisher = Person. | `fix_organization_sameas` / `content_schema_rewriter`: split into a clean Person node; publisher → `#person`. | 1–2 h |
| B11 | Low | No `<link rel="alternate" type="text/markdown">` or `hreflang`. | hreflang is **not needed** (single-language en-GB site, set correctly in `og:locale` and `<html lang>`). A markdown alternate is optional, for AI crawlers that already use `/llms.txt`. | Skip hreflang. Optionally add the markdown alternate link in the generator. | 30 min |

**Considered and not recommended**
- *WebSite SearchAction*: deliberately omitted (`content_schema_rewriter.py` ~L714), search is client-side only, and Google retired the sitelinks search box in Nov 2024.
- *`<changefreq>`/`<priority>` tuning*: Google ignores both.
- *News sitemap*: the site is not a news publisher.
- *More Core Web Vitals work*: LCP preload, `fetchpriority`, critical CSS, AVIF/WebP, width/height and precompression are all already in place (Lighthouse SEO 100, Perf 95–96 in recent commits).

## Needs James / external

| # | Item | Why it needs James |
|---|---|---|
| C1 | **Google Search Console access** (card HAG-1 / old `seo-2`, still blocked: `~/.config/gsc/sa.json` absent). `scripts/fetch_gsc.py` is merged and ready. | Only GSC shows which pages Google actually indexes or drops ("Crawled – currently not indexed") and real queries. It would turn A5, A7 and A8 from guesswork into a ranked list. It also confirms whether `jkcoukblog.pages.dev` is still separately indexed (the worker noindexes it). |
| C2 | After deploys of B1–B3: re-submit `sitemap.xml` and request indexing of `/evs/` and the About page in GSC. | Manual GSC action. |
| C3 | Confirm `/evs/` should be indexable (B1) and whether `/vmc-analyzer/` should stay `noindex, nofollow` (it is a working tool page that could attract "VMC sizing/analyzer" searches; `nofollow` also stops link discovery from it). | Product decision. |
| C4 | Choose which categories, if any, become indexable hubs (B6 + A11). | Content strategy. |
| C5 | Backlinks and authority (backlog P2): vExpert/VMUG profiles, community posts linking to the flagship guides. | Off-site, ongoing. |

## Already done (reconciled; do not redo)

| Item | Source | State now (verified) |
|---|---|---|
| Canonicals, OG and Twitter tags on every page | backlog #1–3 | 81/81 indexable pages; self canonicals all return 200 |
| Duplicate titles and descriptions among indexable pages | — | 0 duplicates in the 81 indexable pages |
| Single H1 | June audit | 81/81 have exactly one H1 |
| Sitemap image 404s | backlog #13 | 0 of 177 image entries fail |
| Orphan posts / internal linking | seo-4 | 13/13 linked; `related_posts.py` in pipeline |
| Taxonomy pagination 404s and `/tag/` breadcrumb 404 | link audit §2 → PR #212 | merged and deployed |
| `rel=pingback` / `rel=shortlink` (`/?p=ID` served the homepage) | link audit §4 → PR #213 | merged; full rebuild 5b71a685f2, 0 files carry them |
| Credly embed on the About page (youracclaim → credly) | link audit §5.1 | fixed in WP 2026-10-19 |
| LinkedIn profile URL unified | PR #214 | merged; `config.py` `SOCIAL_PROFILES` |
| Person E-E-A-T (`sameAs`, `knowsAbout`, `award`, `jobTitle`), topic `about`/`mentions` entities | `config.py` | live on all pages |
| BreadcrumbList on all non-home pages; dedupe and positions fixed | `fix_seo_issues.py` | 80/80 |
| robots.txt (feeds and `/api/` disallowed, sitemap declared), pages.dev noindex, `/llms.txt` | — | live |
| Homepage title and H1 locked to `Config.HOMEPAGE_TITLE` | — | live, 58 chars |
| Thin archives and utility pages noindexed + removed from sitemap | `NOINDEX_PATH_PATTERNS` | live (but see B1 for `/evs/`) |
| Backlog P0-1 "categories missing from sitemap" | backlog | **superseded**: categories are deliberately noindex (see B6) |

## Appendix: re-running the checks

The site-wide numbers above come from a BeautifulSoup scan of `public/**/index.html` at `origin/main` (skipping `/markdown`, `/api`, `/wp-content`). It counts indexable pages (no `noindex`), title and description lengths, H1 count, JSON-LD types, Article date offsets, Article `image`/`author`, filename-style alt text, `og:image:width`, and body word count. `scripts/validate_seo.py` covers most of this; B2 and B7 suggest adding the date-offset and alt-quality checks to it so these regressions fail the build.

---
*Generated by the seo-review temp agent. Read-only: no content, scripts, config or deployment were changed.*
