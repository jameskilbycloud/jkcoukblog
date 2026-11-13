# TODO: jameskilby.co.uk

The single open-work list for the site. Last reviewed 2026-10-29.

- Tick items here as they ship, and link the PR.
- Evidence for the SEO items is in [`docs/seo/`](seo/). Item codes such as A1 or B3 refer to [`seo-recommendations-2026-10-19.md`](seo/seo-recommendations-2026-10-19.md); CR#n refers to [`seo-code-review-2026-10-20.md`](seo/seo-code-review-2026-10-20.md).
- Superseded reports are in [`docs/archive/`](archive/). Do not work from them.
- **Do not start another SEO audit until Phase 1 and 2 are done.** Three audits ran in October and nothing shipped between them.

## Where things stand (2026-10-29)

| Signal | Value | Target |
|---|---|---|
| Clicks / impressions, 28 days to 2026-10-26 | 145 / 11,088 (19 Oct: 164 / 13,244) | Up |
| `james kilby` search position | 9.3 | Top 3 |
| Sitemap pages not indexed by Google | 13 of 81 | Fewer |
| Cloudflare posts (4 posts, ~1,160 impressions) | 0 clicks | Above 0 |

Not indexed: lab-storage, and-now-for-something-completely-different, vmc-host-errors, my-first-pull, apple-content-caching, lab-update-part-1-compute, lab-update-part-3-network, web-development, homelab-bad-days-almost, runecast-remediation-scripts, analytics-in-a-privacy-focused-world, how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare, time-in-a-vmc-environment. Ten are under 400 words.

---

## SEO Phase 1: WordPress quick wins (James, about 1 hour)

- [ ] **About page (ID 3037):** set the Rank Math title to `About James Kilby – Cloud & VMware Solution Architect`. Keep the description to 155 characters or less, in UK spelling, and add alt text to the featured image. *(A1)*
- [ ] **Display name:** Users → Profile → `James Kilby`. This fixes `twitter:data1`, which currently shows "James". *(A4)*
- [ ] **Rewrite the title and description** on the high-impression pages that get few clicks. Lead with the searcher's problem; titles 60 characters or less, descriptions 120–155. *(GSC §4A, A5, A7)*
  - [ ] ubuntu-disk-expansion-steps (712 impressions, 0.8% click rate at position 4.5)
  - [ ] semaphoreui (1,200)
  - [ ] ubiquiti-udm-beast (1,146)
  - [ ] unifi-dhcp-option-43 (1,010)
  - [ ] self-hosted-ai-stack (604, title too long)
  - [ ] zen-internet (352, 76-character title)
- [ ] **`/evs/`:** title 60 characters or less, description 155 or less (now 197), and an H1 that matches the title. *(A3)*

## SEO Phase 2: generator fixes (code), PR [#220](https://github.com/jameskilbycloud/jkcoukblog/pull/220)

- [x] Merge #220 (merged and deployed 2026-10-31, verified live). It fixes:
  - `/evs/` noindex *(B1, CR#1)*
  - the author linked to the 404 `/author/admin/` *(B3, CR#2)*
  - Article dates with no timezone, and stale sitemap lastmod *(B2, CR#3)*
  - the duplicate `#organization` node *(B10, CR#6)*
  - validator blind spots *(CR#7)*
  - the duplicate noindex code *(CR#8)*
- [ ] After deploy, in Search Console: resubmit `sitemap.xml` and request indexing of `/evs/` and the About page.
- [x] Check `/evs/` is in `sitemap.xml` (it is, after the 2026-10-31 deploy).

## SEO Phase 3: content decisions (James)

- [ ] **Cloudflare posts:** merge into one main post (suggest the 2025 `how-i-deploy-my-blog…`, the newest and longest). 301-redirect `/2018/03/cloudflare/` and `how-i-moved…-cloudflare-pages` to it; redirects go in the worker. Refresh or merge `cloudflare-workers-limits-of-the-free-tier`.
- [ ] **Lab update series:** merge parts 1, 3 and 5 into one current guide, or fold them into `/lab/`, and 301 the parts. *(A8)*
- [ ] **Not-indexed posts:** decide expand, merge or leave for each one listed above. Diary posts are fine to leave. In URL Inspection, request indexing of `time-in-a-vmc-environment` and `web-development`.
- [ ] **Expand thin pages that get traffic:** unifi-dhcp-option-43 (378 words) and ubuntu-disk-expansion-steps (185 words). Add steps, commands and troubleshooting, aiming for over 600 words.
- [ ] **Alt text on screenshots**, worst first: starlink, portainer, self-hosting-ai-stack. *(A2)*
- [ ] Remaining WordPress items: short descriptions *(A7)*, featured images on 6 posts *(A6)*, internal links that hit a redirect *(A9)*, `/vmc/` and `/homelab-software/` copy *(A10)*.

## SEO Phase 4: second code PR (lower priority)

- [ ] Stop inventing alt text from filenames; leave `alt=""` and report missing alt. *(B7, CR#4)*
- [ ] 1200×630 share cards for posts whose featured image is under 1200 px wide (46 of 81). *(B4, CR#5)*
- [ ] Article `image` fallback for the 6 posts without one. *(B5)*
- [ ] About page as `ProfilePage` with `mainEntity: #person`. *(B9)*
- [ ] Archive titles and descriptions, `og:type` on archives. *(B8)*
- [ ] Code-review P2 items, when those files are next touched. *(CR#9–#13)*

## Later / strategy

- [ ] Index 2–3 big categories (Homelab, VMware, AI) as hubs, only after writing a real intro for each. *(B6, A11)*
- [ ] Backlinks: vExpert and VMUG profiles, and community posts linking to the flagship guides. *(C5)*
- [ ] Decide on AI crawler access in `robots.txt`. *(June audit M3)*
- [ ] Optional `humans.txt`. *(June audit L2)*

## Cloudflare dashboard (James)

- [ ] **Turn off Email Address Obfuscation** (jameskilby.co.uk → Security → Settings, or Scrape Shield). There are no contact addresses on the site; it only mangles code samples (`administrator@vsphere.local`, `slack-github-action@v1.23.0`, …) on 5 posts into `/cdn-cgi/l/email-protection` links that 404 for crawlers, and adds a render-blocking script. No rebuild needed. Verify: `curl -s https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/ | grep -c email-protection` → `0`. *(audit 2026-11-12, T3)*

## Typo patches

- [ ] **Reconcile `typo-patches.json` with the live site.** It still holds all 338 patches from 2026-06-01, but [`typo-patches-pending.md`](../typo-patches-pending.md) says 208 already landed. CONTRIBUTING says applied entries should be removed. Drop the applied ones, then work through the pending list (52 `NEVER_APPLIED` first).

## Docs

- [ ] Merge the three `STREAMDECK_*.md` files into one.

## Measure

Re-run about 4 weeks after the Phase 1 and 2 deploy (around 2026-12-01). Run it outside the Claude Code sandbox; the proxy breaks the Google API TLS connection.

```bash
python3 -m venv venv && ./venv/bin/pip install google-api-python-client google-auth requests
./venv/bin/python scripts/fetch_gsc.py --site sc-domain:jameskilby.co.uk --limit 100 --out docs/seo/gsc/gsc-full-YYYY-MM-DD.json
```

The raw JSON stays local (`docs/seo/gsc/` is gitignored because it holds real search queries). Update the "Where things stand" table above with the results.
