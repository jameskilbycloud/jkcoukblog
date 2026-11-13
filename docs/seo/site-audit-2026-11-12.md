# Site + SEO audit: jameskilby.co.uk (2026-11-12)

Read-only audit. Nothing was changed in WordPress, the worker or the build. It follows on from
`seo-recommendations-2026-10-19.md` and the 2026-10-29 GSC pull, and only re-lists items from those
reports that are still open.

**How this was checked**
- **Google Search Console API** (`sc-domain:jameskilby.co.uk`, service account in `~/.config/gsc/sa.json`):
  URL Inspection of all 82 sitemap URLs, Sitemaps API, and Search Analytics (28 d / 90 d / 16-month daily, by page, query, query×page, device and country).
- **Live crawl** of all 82 sitemap URLs plus 250 internal URLs found in their links. Checked: status, redirects, canonical, robots, title/description, H1, JSON-LD, OG/Twitter, alt text, word count, headers.
- 338 outbound links checked. Redirects, 404 handling, `robots.txt`, `pages.dev` and `/api/` checked with curl.
- Performance: the CI Lighthouse run from today (`data/lighthouse-latest.json`) and a page-weight check of the subresources. The PageSpeed Insights API quota was exhausted, and CrUX has no field data for the origin because traffic is too low.

## Headline

The technical base is still very good: 82/82 sitemap URLs return 200 with a self-canonical, one H1, valid JSON-LD and `en-GB`. Rich results pass, there are 0 canonical mismatches, and the sitemap shows 0 errors. HSTS, CSP, 301s, real 404s and the `pages.dev` noindex all work.

**The problem is demand, not technical health.** Search traffic has been falling steadily for four months while average position stayed flat:

| Period | Clicks | Impressions | CTR | Avg pos |
|---|---|---|---|---|
| Jul 2026 (peak clicks) | 333 | 25,307 | 1.3% | 9.8 |
| May 2026 (peak impressions) | 247 | 32,686 | 0.8% | 9.7 |
| Oct 2026 | 154 | 11,259 | 1.4% | 9.5 |
| Last 28 d (to 11-09) | 138 | 9,824 | 1.4% | 9.7 |
| Previous 28 d | 169 | 13,665 | 1.2% | 8.6 |

Weekly impressions went from about 6,200 in June to about 2,100 in early November. No site change in git history lines up with the start of the decline. Two things do:

1. **No new posts since 20 June 2026.** That is the latest RSS `pubDate`. The site's impressions have always come from new posts, which pick up long-tail queries for a few months and then fade.
2. **Long-tail erosion on the biggest pages.** Positions held or improved, but Google stopped showing those pages for many queries:

| Page | Impr/day May–Jul → Sep–Nov | Position |
|---|---|---|
| `/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/` | 194 → 27 | 7.7 → 4.8 |
| `/2022/01/cloudflare-workers-limits-of-the-free-tier/` | 114 → 21 | 10.6 → 7.8 |
| `/2025/09/managing-my-homelab-with-semaphoreui/` | 126 → 61 | 8.6 → 8.0 |
| `/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/` | 47 → 9 | 10.4 → 10.6 |

The only pages that grew are the UDM Beast post (+39/day), `/vmc/`, Packer and `/lab/`.

The fixes are therefore mostly about **content**: publish again, refresh the decaying winners, consolidate or prune thin posts, and turn high-impression, zero-click pages into clicks.

## Index coverage (GSC URL Inspection, 82 sitemap URLs)

| State | 10-29 | 11-12 |
|---|---|---|
| Submitted and indexed | 68 | 68 |
| Crawled – currently not indexed | 10 | 9 |
| Discovered – currently not indexed | 1 | 2 |
| URL is unknown to Google | 2 | 2 |
| Excluded by noindex | – | 1 (`/evs/`, stale) |

- **Dropped out since 10-29:** `aws-for-beginners1` (267 words), `aws-status-page-monitoring-included` (171 w), `veeamon2020` (327 w).
- **Came in:** `and-now-for-something-completely-different`, `vmc-host-errors`, `lab-update-part-1-compute`.
- **Thin content is the cause, not linking.** 10 of the 13 non-indexed posts are under 350 words. Their internal inlinks are normal (2–12; the median indexable post has 10).
- **Exceptions worth acting on:**
  - `/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/` has 1,524 words but is not indexed. It is being cannibalised (see S3).
  - `/2025/12/time-in-a-vmc-environment/` has 699 words and 11 inlinks, but Google doesn't know the URL. Request indexing.
- **`/evs/`** is indexable on the live site now (B1 from October is done), but Google last crawled it on 2026-06-20. Request indexing.

## SEO findings, prioritised

### S1 · High · Publish again, and refresh the decaying winners (WordPress)
- Nothing new for about 5 months. Even 1–2 posts a month in the topics that already earn impressions (UniFi/networking, homelab automation with Ansible/Semaphore/Packer, self-hosted AI, VMC) would restore the pattern the site had in spring.
- Refresh with a visible "Updated Nov 2026" and real new content, not just a date bump:
  - **Self-hosted AI stack (Part 1):** current model and tool versions. It lost about 85% of its impressions.
  - **Cloudflare Workers free tier (2022, 344 w):** people are searching `cloudflare workers free tier limits 2026` and `workers kv limits`. Rewrite it around the current limits, with a table.
  - **SemaphoreUI:** add an explicit "Docker Compose" section and heading (`semaphore docker compose` 62 impressions, `semaphoreui docker` 58).

### S2 · High · About page / brand query (WordPress, open since June)
`james kilby` gets about 140 impressions in 90 days at **position 9.2 with 1 click**. For a person's own name that is poor. The About page title is still `about me` (8 chars), the H1 is `About Me`, and the description is 167 chars with US spelling.
- Rank Math title: `About James Kilby — Cloud & VMware Solution Architect`
- H1: `About James Kilby`
- Description ≤155 chars, "specialising"
- Also change the WP display name `James` → `James Kilby`. It still shows as `twitter:data1` "Written by: James" on 75 pages.

### S3 · High · Consolidate the three "WordPress → static on Cloudflare Pages" posts
| Post | Words | 90-day impr | Pos | GSC state |
|---|---|---|---|---|
| `/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/` | – | 1,123 | 14.2 | indexed |
| `/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/` | – | 734 | 28.9 | indexed |
| `/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/` | 1,524 | – | – | **crawled, not indexed** |

They compete for the same intent, and Google picked the weakest ones. Merge the best of the older two into the 2025 post (or a refreshed 2026 version). Then 301 the old URLs to it, using a worker redirect like the existing typo-slug block, and delete or unpublish them in WP.

### S4 · High · Prune or merge thin posts that aren't indexed
For each one choose **expand**, **merge**, or **unpublish + 301/410**. Keeping them as they are adds index bloat that Google has already declined.
- Merge candidates: `lab-update-part-3-network` (176 w) and `lab-update-part-5-desired-workloads` (215 w) into one "Lab update 2022" post. The same goes for `lab-storage` (2018, 269 w) and `lab-storage-2`.
- Low value, so unpublish/redirect: `aws-status-page-monitoring-included` (171 w), `my-first-pull` (285 w), `veeamon2020` (327 w), `aws-for-beginners1` (267 w).
- Expand: `analytics-in-a-privacy-focused-world` (Plausible and CF Analytics are both live on this site, so there is a real story), `runecast-remediation-scripts`, `apple-content-caching`, `homelab-bad-days-almost`.

### S5 · High · `/vmc/` hub: 1,742 impressions, 0 clicks, position 22
Queries: `vmc on aws` (321, pos 26.5), `vmware cloud on aws documentation` (162, pos 23), `vmc aws`, `vmc on aws sizer`, `vmc on aws faq`, `vmc on aws i3en`, `release notes`. The page is 466 words, mostly links. Turn it into a real hub:
- A short "what VMC on AWS is in 2026" intro
- An FAQ section with real answers (host types i3en/i4i/i7i, sizing, licensing after Broadcom)
- Links to your own VMC posts grouped by task
- An "updated" date

Use the same pattern for `/evs/` once it is indexed. Its title is 67 chars, its description 197 chars, and the H1 doesn't match the title (October A3).

### S6 · Medium · CTR on pages already ranking
| Page | Query (90 d) | Impr | Pos | Clicks | Suggestion |
|---|---|---|---|---|---|
| UDM Beast | `udm beast` / `udm-beast` / `unifi udm beast` | 618 / 145 / 48 | ~9.3 | 0 | The intent is a review. Title: `UniFi UDM Beast Review: Real-World iperf, WAN & BGP Tests`. Change the H1 from `Unleashing the UDM Beast` to include "UDM Beast review". |
| Wrangler/brew | `brew wrangler`, `wrangler brew` | 191 | ~7.3 | 0 | The description is a truncated excerpt ("…and have never"). Write one that answers the question directly. |
| UniFi Option 43 | `unifi dhcp option 43` etc. | ~830 | ~5 | 13 | A CTR of about 1.6% at position 5 is low. Shorten the H1 (82 chars) and put the answer (the hex format) in the first 2 lines. |
| vGPU P4 | `nvidia grid tesla`, `tesla p4 gpu` | 291 / 72 | 18–20 | 0 | Add a P4 spec/compatibility section with "Tesla P4" and "GRID" in a heading. |
| Cloudflare 2018 | `is cloudflare cdn free` | 56 | 9.0 | 0 | 348 words from 2018. Refresh it, or fold it into the Workers free-tier rewrite. |

### S7 · Medium · 21 meta descriptions are excerpts cut off mid-sentence (WordPress)
These pages have no Rank Math description, so the 155-char excerpt ends mid-thought ("…uploading th", "…for myself and"). Write real descriptions:

`money-saving-uk-version`, `nutanix-ce`, `2018/03/cloudflare`, `and-now-for-something-completely-different`, `whats-in-my-backpack`, `aws-solution-architect-associate`, `cloudflare-workers-limits-of-the-free-tier`, `wrangler-and-node-versions`, `homelab-bad-days-almost`, `homelab-storage-refresh-part-1`, `how-to-take-a-wordpress-site…`, `analytics-in-a-privacy-focused-world`, `truenas-scale-useful-commands`, `vsan-esa-and-the-improvements-it-brings-to-vmc`, `self-hosting-ai-stack-using-vsphere…`, `zfs-on-vmware`, `warp-the-intelligent-terminal`, `octopus-agile-battery-solar-calculator`, `my-self-hosted-ai-stack-infrastructure-deep-dive-part-2`, `new-vmc-host-i7i-metal-24xl`, `/lab/`.

*Optional generator guard:* make `validate_seo.py` warn when an indexable page's description doesn't end in terminal punctuation.

### S8 · Low · Smaller content items (WordPress; mostly carried over from October)
- **Titles over 60 chars (9):** vsphere-power-management (74), zen-internet (76), self-hosted-ai-stack (68), octopus-agile (65), zfs-on-vmware (64), packer-vsphere (64), nutanix-lcm (63), web-development-improvements (63), automating-ai-homelab (61).
- **Alt text:** 70 images on 26 posts still have filename or "Screenshot …" alts. Worst: home-office-setup (7), vgpu-setup (6), new-nodes (6), apple-content-caching (5), zen-internet (5), starlink (4).
- **No featured image (6):** money-saving-uk-version, lab-storage, lab-update-part-3-network, lab-update-part-5, homelab-software, media.
- **Internal links to fix in post bodies:**
  - `/changelog` returns 404 (from `web-development-improvements`).
  - `/about-me/` redirects (from `monitoring-vmc-part-1`).
  - `/nutanix-command-reference-guide/` redirects (from `nutanix-life-cycle-manager`).
  - `/stats` → `/stats/`.
- **Dead outbound links (16):**
  - `ent.box.com/s/u4wiwh2…`
  - `github.com/johanbook/airtrail`
  - `gtmetrix.com/reports/…` (410)
  - `jameskilbynet.github.io/AgileBatteryPredicter/example_report.html`
  - `knowledge.broadcom.com/…legacyId=77167`
  - `vracdba.com/publications-2/`
  - `nutanix.com/products/cloud-infrastructure`
  - the VMware advanced-deploy exam guide PDF
  - `vmware.com/docs/…license-portability…`
  - `vmware.com/education-services/certification/vmware-ms-hci.html`
  - `vmware.com/uk/products/nsx.html`
  - `xtravirt.com/cloudinsiders`
  - `zen.co.uk/blog/…plexus…`
  - `deepstack.cc` (domain gone)
  - `robware.net/rvtools/` (TLS error)
  - homelab-internal `langfuse.jameskilby.cloud` and `uk-bhr-p-vc-1.jameskilby.cloud` URLs published in posts. Remove those, or make them non-links.

### Not a problem (checked)
- **`#fragment` URLs in GSC** (e.g. `…/semaphoreui/#docker-configuration`): these are Google's jump-to-section links built from your headings. That's a good sign.
- **FAQPage on one page:** valid. Google only shows FAQ rich results for authority sites, so it is harmless.
- **`?p=123` returns 200:** it canonicalises to `/`.

## Technical / performance findings

| # | Pri | Finding | Fix |
|---|---|---|---|
| T1 | Med | **Splide is loaded twice on every post.** The Kadence theme's `kad-splide-js` + `kadence-slide-init-js` (async, also preloaded) and `inline_css_fixups.py` (L208–235) both add `/js/splide.min.js` (defer) plus their own inline init. That's about 33 KB of extra JS, 2 extra requests and 2 preloads, and the related-posts carousel probably gets initialised twice. | In `inline_css_fixups.py`, remove the theme's two `<script>` tags and their `<link rel=preload>`s when injecting the vendored copy (or keep the theme's and drop the injection). Then check that the related-posts carousel still works. The change lands in `public/`. |
| T2 | Med | **Homepage mobile LCP is 2.8 s in the lab** (Lighthouse P94, FCP 2.0 s, CLS 0). The "good" threshold is 2.5 s. The LCP image is preloaded with `fetchpriority=high`. Two fonts are preloaded ahead of it, and Space Grotesk 400 is **69 KB** (Anton is 12 KB). | Check that `subset_fonts.py` actually subsets Space Grotesk. 69 KB looks like the full latin file. Consider not preloading it, or using `font-display: optional` for the body face. |
| T3 | Low | **Cloudflare Email Obfuscation** (Scrape Shield) rewrites `mailto:` on 5 pages. It injects a render-blocking `/cdn-cgi/…/email-decode.min.js`, and crawlers see `/cdn-cgi/l/email-protection` links, which return 404. | Turn off Email Obfuscation in the CF dashboard, or remove the plain email addresses from those posts. |
| T4 | Low | `https://www.jameskilby.co.uk/nutanix-life-cycle-manager/` takes two 301 hops (www→apex, then flat slug→dated). GSC still sees 10 impressions on it. | Optional: make the www redirect resolve flat slugs in one hop. |
| T5 | Low | HEAD requests skip the worker (`request.method !== 'GET'` → `ASSETS.fetch`), so HEAD on `pages.dev` lacks `X-Robots-Tag`. GET is correct and `pages.dev/robots.txt` is `Disallow: /`. | No action needed. Noted so it isn't mistaken for a regression. |

**Verified OK:**
- http→https and www→apex 301
- No-trailing-slash → 308
- Unknown URLs return a real 404 with `noindex,follow`
- `/api/` sends `X-Robots-Tag: noindex`
- `pages.dev` sends `noindex, nofollow` and has a canonical to production
- Brotli served
- HSTS preload, CSP, nosniff, Referrer-Policy and Permissions-Policy present
- KV HTML cache HITs (`x-worker: advanced-worker-kv`)
- Median HTML response about 240 ms from the UK
- `llms.txt` / `robots.txt` / sitemap healthy
- 0 mixed content
- All `<img>` have alt attributes and dimensions

## Tooling notes
- `scripts/fetch_gsc.py` defaults to the **URL-prefix** property `https://jameskilby.co.uk/`, which returns **403**. The service account is granted on the **Domain** property. Run it with `--site sc-domain:jameskilby.co.uk`, or change `DEFAULT_SITE` to the `sc-domain:` form.
- The Google client libraries aren't in `requirements*.txt`. Add `google-api-python-client` and `google-auth` to `requirements-dev.txt`.
- The anonymous PageSpeed Insights quota is exhausted. Add a `key=` (the same GCP project as `CRUX_API_KEY` works) if you want PSI in the audit loop.

## Suggested order
1. **This week (WordPress, ~1 h):**
   - S2: About title, H1 and description, plus the display name.
   - S6: UDM Beast and Wrangler titles and descriptions.
   - GSC: request indexing for `/evs/`, `/2025/12/time-in-a-vmc-environment/` and the 2025/10 static-site post.
2. **Next (WordPress plus worker redirects):**
   - S3: consolidate the static-site posts.
   - S4: prune or merge the thin posts.
   - S7: write the 21 descriptions.
3. **Content plan:**
   - S1: refresh Workers free tier, AI stack and Semaphore.
   - S5: expand `/vmc/`.
   - Get back to a regular publishing cadence.
4. **Code PR (small):**
   - T1: remove the duplicate Splide.
   - T2: check font subsetting.
   - The `fetch_gsc.py` default property and the dev requirements.
5. **Re-measure:** rerun `fetch_gsc.py` about 4 weeks after the WordPress changes and compare against this report's 28-day baseline (138 clicks, 9,824 impressions, position 9.7).
