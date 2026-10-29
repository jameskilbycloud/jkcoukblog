# Link and health audit: jameskilby.co.uk (2026-10-19)

Read-only audit of the live site. Nothing was fixed, edited or deployed. "Live" is the authority for every status code below; repo paths are given only to show where a fix would go.

**Method.** A small crawler (Python standard library, 4 concurrent workers) started at `https://jameskilby.co.uk/` plus every `<loc>` in `/sitemap.xml`, followed every internal `<a href>`, and recorded the status of every `href`/`src`/`srcset`, `<link>` (stylesheet, preload, icon, next, pingback, shortlink, alternate) and `og:image` it found. Internal URLs were fetched with GET and redirects followed by hand so chains are visible. External URLs got one HEAD request each (redirects followed); no retries except a GET when HEAD itself was refused. Page budget was 3,000; the crawl finished at 266 pages, so the budget was not reached. Crawl run 2026-10-19 ~11:10 UTC, about 165 s.

## 1. Summary

| Measure | Count |
|---|---|
| HTML pages crawled | 266 (257 × 200, 9 × 404) |
| Internal asset/link URLs checked (images, CSS, JS, feeds, etc.) | 2,990 |
| External URLs checked | 345 |
| Link references (edges) recorded | 32,014 |
| **Broken internal URLs** | **12** distinct (9 pages, 2 images, 1 `xmlrpc.php` header link) |
| **Broken external URLs** | **17** (11 × 404, 1 × 410, 2 malformed hrefs, 1 dead host, 2 TLS/certificate failures) |
| External URLs blocked/unverifiable (403 / LinkedIn 999 / TLS error) | 13 |
| Other issues | 8 (see section 4) |
| Sitemap URLs that fail | 0 of 81 pages, 0 of 177 image entries |
| Mixed content (`http://` sub-resources on https pages) | 0 |
| Redirect chains (2+ hops) or loops | 0 |
| Pages missing `<title>` | 0 |
| Broken / mismatched canonicals | 0 |

## 2. Broken internal links

| Source page | Broken target | Status |
|---|---|---|
| https://jameskilby.co.uk/tag/*/ (all 130 tag pages, e.g. /tag/homelab/, /tag/ai/) | https://jameskilby.co.uk/tag/ (breadcrumb "Tags") | 404 |
| https://jameskilby.co.uk/category/homelab/ (`<a>` and `<link rel="next">`) | https://jameskilby.co.uk/category/homelab/page/2/ | 404 |
| https://jameskilby.co.uk/category/homelab/ | https://jameskilby.co.uk/category/homelab/page/3/ | 404 |
| https://jameskilby.co.uk/category/vmware/ (`<a>` and `<link rel="next">`) | https://jameskilby.co.uk/category/vmware/page/2/ | 404 |
| https://jameskilby.co.uk/category/vmware/ | https://jameskilby.co.uk/category/vmware/page/3/ | 404 |
| https://jameskilby.co.uk/tag/homelab/ (`<a>` and `<link rel="next">`) | https://jameskilby.co.uk/tag/homelab/page/2/ | 404 |
| https://jameskilby.co.uk/tag/homelab/ | https://jameskilby.co.uk/tag/homelab/page/3/ | 404 |
| https://jameskilby.co.uk/tag/vmware/ (`<a>` and `<link rel="next">`) | https://jameskilby.co.uk/tag/vmware/page/2/ | 404 |
| https://jameskilby.co.uk/2018/04/nutanix-life-cycle-manager/ (`<img>`) | https://jameskilby.co.uk/wp-content/uploads/2018/03/Screen-Shot-2018-02-14-at-22.25.32-300x160.png | 404 |
| https://jameskilby.co.uk/2018/04/nutanix-life-cycle-manager/ (`<img>`) | https://jameskilby.co.uk/wp-content/uploads/2018/03/Screen-Shot-2018-03-10-at-20.41.50-300x156.png | 404 |
| 9 pages via `<link rel="pingback">`, incl. /2018/04/nutanix-life-cycle-manager/, /2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/, /2026/03/octopus-agile-battery-solar-calculator/, /2026/04/automated-vcf-9-offline-depot/, /2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/, /2026/04/new-vmc-host-i7i-metal-24xl/ | https://jameskilby.co.uk/xmlrpc.php | 404 |
| /2019/12/monitoring-vmc-part-1/, /2023/05/runecast-remediation-scripts/, /2025/09/managing-my-homelab-with-semaphoreui/, /2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/, /2026/04/vsphere-power-management-driven-by-ansible/ | https://jameskilby.co.uk/cdn-cgi/l/email-protection#… | 404 without JavaScript |

Notes on the table:
- **Pagination.** Category and tag archives render "page 2 / page 3" links and `rel="next"`, but those pages are not in the build (`public/category/homelab/` and `public/tag/homelab/` hold only `index.html`). `scripts/wp_content_discovery.py` (~lines 130 and 240) discovers pagination for the homepage only (`/page/N/`), not for taxonomy archives. Affected archives: category/homelab, category/vmware, tag/homelab, tag/vmware.
- **`/tag/`.** `scripts/breadcrumb_navigation.py` (~line 74) builds a "Home > Tags > <tag>" trail whose middle link points at `/tag/`, but no tag index page exists (`public/tag/index.html` is absent).
- **Two screenshots.** The `-300x160` / `-300x156` thumbnail sizes are referenced in the post HTML but missing from `public/wp-content/uploads/2018/03/`. Most likely the thumbnails no longer exist in WordPress either; the fix belongs in the WordPress post (re-insert the image), not in `public/`.
- **`xmlrpc.php`.** `scripts/wordpress_cleanup.py` (~line 53) strips the `EditURI` RSD link to `xmlrpc.php` but not `<link rel="pingback">`, which survives on 9 pages.
- **`/cdn-cgi/l/email-protection`.** This is injected at the edge by Cloudflare Email Obfuscation (not present in `public/`). `email-decode.min.js` loads (200) and rewrites the links for JS users, so the 404 only hits no-JS visitors and crawlers. Low impact.

## 3. Broken external links (third-party sites)

These are other people's sites; status can change and some block automated requests. One HEAD request each, rechecked with curl where marked.

### Confirmed broken

| Source page | Broken target | Status |
|---|---|---|
| https://jameskilby.co.uk/2018/04/nutanix-life-cycle-manager/ | https://www.nutanix.com/products/cloud-infrastructure | 404 (curl confirmed) |
| https://jameskilby.co.uk/homelab-software/ | https://github.com/johanbook/airtrail | 404 (curl confirmed) |
| https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/ | https://ent.box.com/s/u4wiwh2mq8o05ct8e67ndapvxhudkhe2 | 404 |
| https://jameskilby.co.uk/2026/03/octopus-agile-battery-solar-calculator/ | https://jameskilbynet.github.io/AgileBatteryPredicter/example_report.html | 404 (James's own GitHub Pages) |
| https://jameskilby.co.uk/vmc/ | https://knowledge.broadcom.com/external/article?legacyId=77167 | 404 |
| https://jameskilby.co.uk/vmc/ | https://vracdba.com/publications-2/ | 404 |
| https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/ | https://www.vmware.com/content/dam/digitalmarketing/vmware/en/pdf/certification/vmware-advanced-deploy-exam-guide.pdf | 404 |
| https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/ | https://www.vmware.com/education-services/certification/vmware-ms-hci.html | 404 |
| https://jameskilby.co.uk/2018/10/and-now-for-something-completely-different/ | https://www.vmware.com/uk/products/nsx.html | 404 |
| https://jameskilby.co.uk/2018/10/and-now-for-something-completely-different/ | https://www.zen.co.uk/blog/posts/zen-blog/2018/02/09/how-plexus-came-about | 404 |
| https://jameskilby.co.uk/media/ | https://www.xtravirt.com/cloudinsiders | 404 |
| https://jameskilby.co.uk/2026/01/web-development-improvements/ | https://gtmetrix.com/reports/jameskilby.co.uk/ADjhUqtL/ | 410 (report expired) |
| https://jameskilby.co.uk/homelab-software/ | https://deepstack.cc/ | no connection (curl exit 56) — host appears dead |
| https://jameskilby.co.uk/about-james-kilby-solution-architect/ (`<script>` and `<link rel="preload">`) | https://cdn.youracclaim.com/assets/utilities/embed.js (`src="//cdn.youracclaim.com/…"`) | TLS failure: certificate expired (curl exit 60, verify result 10) |
| https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/ | `http://ansible/vGPU/install_nvidia_containertoolkit.yml` (2 links) | malformed href: a repo path written as a bare host; resolves nowhere |
| https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/ | `http://you can create one at: https://dash.cloudflare.com/profile/api-tokens` | malformed href: sentence text inside the link |
| https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/ | https://uk-bhr-p-vc-1.jameskilby.cloud:443/cls/vcsp/lib/165734dc-81a8-464a-bbe5-a99e4ae597da/lib.json | certificate verify failed; private lab vCenter, likely an example URL that should not be a live link |

### Blocked or unverifiable (not counted as broken)

403 from bot protection is common on these sites; check by hand before changing anything.

| Source page | Target | Result |
|---|---|---|
| / and many posts | https://www.linkedin.com/in/jameskilbynet/ | 999 (LinkedIn bot block) |
| many posts | https://www.linkedin.com/in/james-kilby/ | 999 — note two **different** LinkedIn profile URLs are in use |
| /about-james-kilby-solution-architect/ | http://www.trading212.com/invite/FMStpMpc | 403 |
| /2026/03/octopus-agile-battery-solar-calculator/ | http://claude.ai/ | 403 |
| /2023/05/homelab-storage-refresh-part-1/ | https://ark.intel.com/content/www/us/en/ark/products/97154/intel-optane-ssd-dc-p4800x-series-750gb-2-5in-pcie-x4-3d-xpoint.html | 403 |
| /homelab-software/ | https://docs.paperless-ngx.com/ | 403 |
| /2023/10/going-out-with-a-bang/ | https://rnli.org/ | 403 |
| /2021/01/my-home-office-setup-upgrades/ | https://www.dell.com/en-uk/shop/dell-ultrasharp-49-curved-monitor-u4919dw/apd/210-argk/monitors-monitor-accessories | 403 |
| /2026/04/new-vmc-host-i7i-metal-24xl/ | https://www.intel.com/content/dam/www/central-libraries/us/en/documents/white-paper-intel-tme.pdf | 403 |
| /2022/01/lab-update-part-1-compute/ | https://www.supermicro.com/products/system/2U/2027/SYS-2027TR-H71FRF.cfm | 403 |
| /2024/07/new-nodes/ | https://www.supermicro.com/en/products/system/mini-itx/sys-e200-8d.cfm | 403 |
| /vmc/ | https://www.penguinpunk.net/blog/ | 403 |
| /2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/ | https://www.robware.net/rvtools/ | TLS handshake error (curl exit 35); may be the audit network path |

## 4. Other issues

1. **Credly badge script on an expired-certificate host.** The About page loads `//cdn.youracclaim.com/assets/utilities/embed.js`; that certificate fails verification, so browsers will block the script and the badges will not render. Credly's current host is `cdn.credly.com` (already allowed in the CSP). `scripts/test_csp.py` and `scripts/test_live_site_formatting.py` still require `youracclaim.com` in the CSP.
2. **Taxonomy pagination missing** (section 2): 7 pagination URLs 404 and are advertised via `rel="next"`.
3. **`/tag/` breadcrumb target missing** (section 2): one broken link on each of 130 tag pages.
4. **WordPress shortlinks serve the homepage.** All 83 posts/pages carry `<link rel="shortlink" href="/?p=ID">`. On the static site the query string is ignored, so every `/?p=ID` returns 200 with the homepage (title "James Kilby — VMware, Homelab & Cloud Infrastructure Notes"), not the post. Not a 404, but a misleading link; `wordpress_cleanup.py` could strip it like the RSD link.
5. **Internal links that hit a redirect (1 hop each, no chains or loops):**
   - /2019/12/monitoring-vmc-part-1/ → `/about-me/` → 301 → `/about-james-kilby-solution-architect/`
   - /2018/04/nutanix-life-cycle-manager/ → `/nutanix-command-reference-guide/` → 301 → `/2018/06/nutanix-command-reference-guide/`
   - /2026/01/web-development-improvements/ → `/stats` → 308 → `/stats/`, and `/changelog` → 308 → `/changelog/`
6. **Duplicate titles (28 pairs + 1 group).** Each category and the tag of the same name share a title, e.g. "Homelab Archives - James Kilby" on both /category/homelab/ and /tag/homelab/ (28 pairs). Homepage pagination /page/2/ … /page/7/ all share one title (the full meta description, starting "James Kilby - James Kilby's technical blog covering VMware…"), which is also over-length. All of these pages are `noindex`, so search impact is small.
7. **`/evs/` is `noindex,follow`** and absent from the sitemap, unlike the other top-level content pages (/vmc/, /lab/, /media/). Flagging in case it is unintended.
8. **Plain `http://` outbound links** (not mixed content, just insecure links): /2023/04/intel-optane/ → http://www.virtualisedfruit.co.uk/; /2023/11/analytics-in-a-privacy-focused-world/ → http://blah.cloud/; /2024/09/can-you-really-squeeze-96tb-in-1u/ → http://qct.io/; /vmc/ → http://davidwzhang.com/; /evs/ → http://vcloudone.com/; About page → http://share.octopus.energy/pale-llama-822 (works via curl, 200) and http://www.trading212.com/invite/FMStpMpc; /2026/03/octopus-agile-battery-solar-calculator/ → http://claude.ai/.

Checked and clean: `robots.txt` present and valid (points to the sitemap); all 81 sitemap page URLs return 200 without redirect; all 177 sitemap image entries return 200; every indexable 200 page is in the sitemap (all non-sitemap pages are `noindex`); no mixed content; no redirect chains or loops; every crawled page has a `<title>` and a self-referencing canonical that returns 200; no soft-404s (assets returning HTML) detected.

## 5. Prioritised fix list

1. **Credly embed (About page).** Switch the embed script from `cdn.youracclaim.com` to `cdn.credly.com` in the WordPress page, then update `scripts/test_csp.py` / `scripts/test_live_site_formatting.py` expectations. Visible breakage on a key page.
2. **Taxonomy pagination.** Either generate `/category/<slug>/page/N/` and `/tag/<slug>/page/N/` in `scripts/wp_content_discovery.py` (as is done for `/page/N/`), or stop emitting the pagination links and `rel="next"`. 7 broken URLs, linked from 4 archive pages.
3. **`/tag/` breadcrumb.** In `scripts/breadcrumb_navigation.py`, render "Tags" as plain text (no link) or generate a tag index page. 130 broken links.
4. **Malformed links in /2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/** (fix in WordPress): the `http://ansible/vGPU/…` links (point at the GitHub file or make it code text) and the `http://you can create one at: …` link.
5. **Missing screenshots in /2018/04/nutanix-life-cycle-manager/** (fix in WordPress): re-insert the two images.
6. **Dead third-party links** (fix in WordPress, swap for current or archive.org URLs): the 11 × 404, the GTmetrix 410, deepstack.cc. Also James's own `AgileBatteryPredicter/example_report.html` (404) — fixable on his GitHub Pages side.
7. **Strip `<link rel="pingback">` and `<link rel="shortlink">`** in `scripts/wordpress_cleanup.py`, next to the existing `EditURI` removal.
8. **Point internal links at final URLs** (fix in WordPress): `/about-me/`, `/nutanix-command-reference-guide/`, `/stats`, `/changelog` (add trailing slash).
9. **Housekeeping:** unify the two LinkedIn profile URLs; distinct titles for category vs tag archives and homepage pagination; upgrade the `http://` outbound links to `https://` where the target supports it; confirm `/evs/` should be `noindex`; consider unlinking the private vCenter URL; manually spot-check the 403-blocked external links.

---
*Generated by the blog-audit temp agent. Read-only: no content, scripts, or deployment were changed.*
