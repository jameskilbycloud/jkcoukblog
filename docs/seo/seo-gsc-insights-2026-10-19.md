# Google Search Console insights — 2026-10-19

Read-only pull. Nothing in the repo was changed, committed or deployed apart from this file and the two JSON snapshots.

**Source**
- Property: `sc-domain:jameskilby.co.uk` (Domain property). The Search Console service account has Full access on it. It has **no** access to the URL-prefix property `https://jameskilby.co.uk/`, which is the `fetch_gsc.py` default, so that call returns 403. Always pass `--site sc-domain:jameskilby.co.uk`.
- Search Analytics: 2026-09-18 → 2026-10-16 (28 days; Google's data lags about 3 days).
- Raw data (local only, gitignored): `docs/seo/gsc/gsc-report-2026-10-19.json` (analytics + sitemaps) and `docs/seo/gsc/gsc-inspect-sample-2026-10-19.json` (URL Inspection on 25 URLs).
- Word counts: body text of each sitemap page in local `public/` (local `main`, may lag `origin/main` slightly).

## Summary

- **164 clicks, 13,244 impressions** in 28 days, across 69 real pages (96 rows, of which 27 are `#fragment` deep links).
- **Ranking is not the problem. Click-through rate (CTR) is.** 65 of 96 page rows sit at average position 5–10, yet the top 5 pages by impressions all have CTR of 0.8–2.0%. For position 5–8, about 3–6% is typical. Better titles and meta descriptions on about 10 pages are the cheapest win.
- **Index coverage:** 19 of 25 sampled URLs are indexed. 5 are "Crawled – currently not indexed" and 1 is unknown to Google. All 6 are old, short posts.
- **16 of 81 sitemap pages got zero impressions.** 11 of them are thin posts (under 400 words).
- The branded query `james kilby` averages **position 9.4** (106 impressions, 1 click). That confirms seo-recommendations **A1** (About page title `about me`) and **B3** (split author entity) are worth doing.

## 1. Index coverage

**Sitemap** (`/sitemap.xml`): 81 web URLs + 177 images submitted. 0 errors, 0 warnings. Last downloaded by Google 2026-10-16. The API reports `indexed: 0` for both. That field has been deprecated by Google and is always 0, so it says nothing about real indexing.

**URL Inspection sample** (first 25 URLs in sitemap order, which skews to older posts; no quota hit):

| Coverage state | Count |
|---|---|
| Submitted and indexed | 19 |
| Crawled – currently not indexed | 5 |
| URL is unknown to Google | 1 |

No canonical mismatches: Google's chosen canonical matched the page's own canonical on every inspected URL. Robots and fetch status were fine on all crawled URLs.

| URL not indexed | State | Words | Last crawl |
|---|---|---|---|
| `/2017/05/money-saving-uk-version/` | Crawled, not indexed | ≥400 | 2026-07-24 |
| `/2018/01/lab-storage/` | Crawled, not indexed | 269 | 2026-10-13 |
| `/2018/10/and-now-for-something-completely-different/` | Crawled, not indexed | 315 | 2026-08-22 |
| `/2020/09/vmc-host-errors/` | Crawled, not indexed | 301 | 2026-08-31 |
| `/2020/12/my-first-pull/` | Crawled, not indexed | 285 | 2026-09-09 |
| `/2021/02/apple-content-caching/` | Unknown to Google | 367 | never |

Reading: 5 of the 6 are under 400 words, which supports seo-recommendations **A8** ("thin pages cause Crawled – currently not indexed"). The sample is 25 of 81, so do not scale it up to a site-wide rate. Older posts are over-represented. A later run could inspect the remaining 56 in batches of 25 (`--limit` takes the first N URLs, so the script would need an offset option first).

## 2. Top pages (by clicks)

| Clicks | Impr. | CTR | Pos. | Page |
|---|---|---|---|---|
| 23 | 1,494 | 1.5% | 7.7 | `/2025/09/managing-my-homelab-with-semaphoreui/` |
| 23 | 1,391 | 1.7% | 7.6 | `/2026/06/ubiquiti-udm-beast/` |
| 22 | 1,113 | 2.0% | 6.4 | `/2024/06/unifi-dhcp-option-43/` |
| 13 | 766 | 1.7% | 4.8 | `/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/` |
| 11 | 218 | 5.1% | 6.9 | `/2026/03/octopus-agile-battery-solar-calculator/` |
| 11 | 140 | 7.9% | 6.3 | `/2024/01/multihost-holodeck-vcf/` |
| 10 | 511 | 2.0% | 7.5 | `/2026/04/packer-vsphere-golden-images/` |
| 7 | 595 | 1.2% | 8.6 | `/2023/10/vgpu-setup-in-my-homelab/` |
| 6 | 726 | 0.8% | 4.2 | `/2025/12/ubuntu-disk-expansion-steps/` |
| 6 | 129 | 4.7% | 5.0 | `/2024/12/zfs-on-vmware/` |
| 4 | 187 | 2.1% | 13.8 | `/lab/` |

## 3. Top queries

Only 12 of the 164 clicks have a query attached. Google hides rare queries for privacy, so this list is thin by nature.

| Clicks | Impr. | Pos. | Query |
|---|---|---|---|
| 0 | 158 | 2.1 | a LinkedIn people search for a named individual (not relevant; ignore) |
| 2 | 108 | 5.7 | unifi dhcp option 43 |
| 1 | 106 | 9.4 | **james kilby** (branded, should be position 1) |
| 0 | 32 | 7.6 | brew wrangler |
| 1 | 22 | 6.5 | comfyui vs ollama |
| 1 | 16 | 8.8 | semaphoreui docker |
| 0 | 16 | 6.3 | cdn cloudflare |
| 0 | 15 | 31.9 | aws monitoring tools |
| 2 | 10 | 10.7 | dream machine beast review |
| 1 | 9 | 3.9 | esxi zfs |

## 4. CTR and position opportunities

**A. High impressions, low CTR, already on page 1.** Rewrite the Rank Math SEO title and description in WordPress. Lead with the searcher's problem, not the story.

| Impr. | CTR | Pos. | Page | Note |
|---|---|---|---|---|
| 1,494 | 1.5% | 7.7 | semaphoreui | Biggest page. Queries: "semaphoreui docker", "ansible semaphore docker". Put "Ansible Semaphore UI with Docker" in the title. |
| 1,391 | 1.7% | 7.6 | ubiquiti-udm-beast | "dream machine beast review" gets 20% CTR when shown. Use "UniFi Dream Machine Beast review" wording. |
| 1,113 | 2.0% | 6.4 | unifi-dhcp-option-43 | Ranks 5.7 for its exact query. Thin (378 words). A short how-to step list could lift it into the top 3. |
| 766 | 1.7% | **4.8** | self-hosted-ai-stack | Title 68 chars (A5): truncated. |
| 726 | **0.8%** | **4.2** | ubuntu-disk-expansion-steps | Position 4 with under 1% CTR: the snippet is the problem. Thin (185 words). |
| 597 | **0.0%** | 7.7 | cloudflare-workers-limits-of-the-free-tier | 0 clicks. 2022 post on a fast-moving topic; title likely reads as stale. Thin (301 words). |
| 595 | 1.2% | 8.6 | vgpu-setup-in-my-homelab | |
| 511 | 2.0% | 7.5 | packer-vsphere-golden-images | Title 64 chars (A5). |
| 486 | 0.2% | 8.8 | `/2018/03/cloudflare/` | 2018, thin (348 words). Competes with the 2022 Cloudflare Pages post. Consider merging. |
| 353 | 0.6% | 7.1 | zen-internet-city-fibre | Title 76 chars, the longest on the site (A5). |
| 315 | 0.3% | 9.8 | how-i-moved-my-wordpress-site-to-cloudflare-pages | |
| 296 | 0.0% | 7.3 | pocket-to-hoarder | |
| 190 | 0.0% | 7.7 | home-network-upgrade | |
| 179 | 0.0% | 9.0 | wrangler-and-node-versions | "brew wrangler" query at 7.6. Thin (206 words). |
| 163 | 0.0% | 7.7 | vsan-cluster-shutdown | Thin (175 words). |

**B. Position 10–25, close to page 1.** These need content, not just snippet work.

| Impr. | Pos. | Page |
|---|---|---|
| 315 | 17.7 | `/vmc/` hub (A10: thin intro, empty ToC heading) |
| 223 | 22.8 | `/2019/12/monitoring-vmc-part-1/` |
| 187 | 13.8 | `/lab/` |
| 178 | 15.9 | `/2022/10/starlink/` |
| 135 | 13.2 | automating-the-deployment-of-my-ai-homelab |

**C. Branded.** `james kilby` at position 9.4 should be position 1. Fix A1 (About page title) and B3 (author entity pointing at a 404) first.

## 5. Thin posts (under 400 words) vs GSC traffic

39 sitemap pages are under 400 words by this count. Seo-recommendations said "about 37"; the difference is the homepage (76 words) and `/media/`. Decision guide: **expand** the ones with real impressions, **merge or leave** the ones with none.

**Expand: thin but getting real impressions**

| Words | Clicks | Impr. | Pos. | Page |
|---|---|---|---|---|
| 378 | 22 | 1,113 | 6.4 | `/2024/06/unifi-dhcp-option-43/` (3rd-biggest page) |
| 185 | 6 | 726 | 4.2 | `/2025/12/ubuntu-disk-expansion-steps/` |
| 301 | 0 | 597 | 7.7 | `/2022/01/cloudflare-workers-limits-of-the-free-tier/` |
| 348 | 1 | 486 | 8.8 | `/2018/03/cloudflare/` |
| 393 | 2 | 353 | 7.1 | `/2023/11/configuring-a-zen-internet-…-3rd-party-router/` |
| 367 | 1 | 219 | 9.1 | `/2022/12/100gb-s-in-my-homelab-sort-of/` |
| 206 | 0 | 179 | 9.0 | `/2022/01/wrangler-and-node-versions/` |
| 175 | 0 | 163 | 7.7 | `/2025/12/vsan-cluster-shutdown/` |
| 258 | 2 | 137 | 8.6 | `/about-james-kilby-solution-architect/` (also A1) |
| 166 | 2 | 86 | 6.7 | `/2018/06/nutanix-command-reference-guide/` |
| 207 | 0 | 70 | 7.2 | `/2023/11/truenas-scale-useful-commands/` |
| 294 | 0 | 64 | 11.4 | `/2019/02/lab-storage-2/` |

**Low traffic (under 50 impressions): leave or fold into a related post.** new-laptop, vmware-certified-master-specialist-hci-2020, advanced-deploy-vsphere-7 (3V0-22.21), lab-update-part-5, nutanix-ce, aws-for-beginners1, lab-storage (2018, not indexed), whats-in-my-backpack, nutanix-ncp, vmc-host-errors (not indexed), forcing-an-upgrade-to-vsphere-8, veeamon2020, `/media/`, holodeck-cpu-fixes, vmc-host-deepdive.

**Zero impressions in 28 days (thin):** aws-status-page-monitoring-included, lab-update-part-3-network, aws-solution-architect-associate, going-out-with-a-bang, web-development, my-first-pull (not indexed), lab-update-part-1-compute, and-now-for-something-completely-different (not indexed), runecast-remediation-scripts, analytics-in-a-privacy-focused-world, apple-content-caching (unknown to Google). These are the best candidates for the A8 "merge series / leave diary posts" decision. `lab-update-part-1/3/5` together get 4 impressions, which supports merging them into one updated guide with a 301 redirect.

**Zero impressions, not thin:** money-saving-uk-version (not indexed), nutanix-life-cycle-manager, homelab-bad-days-almost, how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare, time-in-a-vmc-environment. The 2025 blog-deploy post getting nothing is surprising and worth an individual URL Inspection.

## 6. Small oddities

- `/evs/` shows 1 impression even though it is noindexed (seo-recommendations B1). It is not ranking, so B1 still stands.
- Four junk URLs got 1 impression each: `/ubuntu-expansion-steps/`, `/co.uk/expand-ubuntu-disk-space-with-lvm-pvresize-step-by-step/`, `/data-on-vmware/` and `/evs/`. The `/co.uk/…` path suggests a bad internal or external link somewhere. Check that these return 301 or 404, not 200.
- 27 page rows are `#fragment` URLs (Google sitelinks jumping to headings). That is a good sign: the H2/H3 anchors are working.

## How to re-run

```bash
python3 -m venv venv && ./venv/bin/pip install google-api-python-client google-auth requests
./venv/bin/python scripts/fetch_gsc.py --skip-inspection --site sc-domain:jameskilby.co.uk --out docs/seo/gsc/gsc-report-YYYY-MM-DD.json
./venv/bin/python scripts/fetch_gsc.py --limit 25 --site sc-domain:jameskilby.co.uk --out docs/seo/gsc/gsc-inspect-sample-YYYY-MM-DD.json
```

The service-account key is at `~/.config/gsc/sa.json`. Inside the Claude Code sandbox, pip and the Google APIs fail with a TLS certificate error (`OSStatus -26276`) caused by the network proxy, so both have to run outside it.
