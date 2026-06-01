# Site Audit — jameskilby.co.uk

_Audit date: 2026-06-01. 78 pages reviewed (out of 78 in sitemap)._

## Summary

- 77 of 78 pages have findings; only the static landing pages with clean metadata escape unscathed.
- Across the site: ~280 typo/copy issues, ~190 cosmetic issues, and ~430 SEO issues flagged.
- Headline takeaways:
  - The pipeline is shipping most posts without meta description, canonical, or Open Graph tags — by far the dominant issue.
  - A large fraction of older posts are thin (<300 words), often with stale dates and dangling "I will follow up" promises that were never linked.
  - Image alt text is systemically weak: many posts have filename-derived alts (e.g. `Iu`, `Wa`, `Vmconaws.Png`) or empty alts on content images.
  - Several recurring copy patterns: stray possessive apostrophes on plurals (`SSD's`, `VM's`, `URL's`, `DAC's`), inconsistent product casing (`Macbook`, `Wordpress`, `vCentre`, `TrueNas`), and generic anchor text (`here`, `Repo`, `Check it out`).

## Systemic Issues

These appear on many pages and almost certainly trace back to the static generator or theme rather than per-post mistakes. Fixing them at the template level would eliminate the bulk of findings in this report.

- **Missing meta description on most posts** (~60+ pages). Pipeline is not emitting `<meta name="description">` for the majority of blog posts; only a handful of newer/static pages have one. Root cause is almost certainly the static generator's head template not pulling Yoast/RankMath description (or post excerpt) through. _Fix at `wp_to_static_generator.py` / template, not per-post._
- **Missing `rel="canonical"` on most posts** (~50+ pages). Same root cause — the head template is not emitting a self-referential canonical. High priority because category/tag/markdown variants of every post exist.
- **Missing Open Graph tag set on most posts** (~50+ pages). `og:title`, `og:description`, `og:image`, `og:type`, `og:url` all absent across the blog. Twitter Card tags also missing. Fix once in the head template.
- **Auto-generated image alt text is filename-derived** (~25+ pages). Patterns like `Iu`, `Wa`, `Iu 2`, `Vmconaws.Png`, `Brokenharddive 1200X630 1`, `Vsphere Overview 1024X530`, `Origionalpoweredbyvsan 550X324 1`. The optimisation pipeline (or WordPress media import) is falling back to filename when alt is empty. Either force empty alt for decorative images or surface a build-time warning when alt looks filename-shaped.
- **Bylines render two dates run together with no separator** (homepage and many posts). E.g. `By James April 15, 2026 May 31, 2026` or `October 16, 2018April 16, 2026`. Theme needs `Published:` / `Updated:` labels (or a separator) between the two dates.
- **"Read More …Continue" anchor text on every post card** (homepage). Two label strings appear concatenated without a separator on every card; SEO-weak as well as ugly.
- **`Updated` date bumped to 2026 on posts whose body is unchanged** (10+ older posts). Many 2017–2020 posts display `Updated: April/May 2026` despite no substantive edits, causing stale-content-as-fresh signals and reader confusion. Either suppress the modified date on cosmetic re-renders or only display it when the body actually changed.
- **Images missing intrinsic `width`/`height`** on featured images across many posts. Inconsistent with the optimisation pipeline's normal output — worth verifying `convert_images_to_picture.py` emits dimensions on the fallback `<img>` for hero images.
- **Heading hierarchy: theme chrome (`Post Tags:`, `Connect with me:`, `Related Posts`, `Post navigation`, `Similar Posts`) is emitted as `<h2>` inside `<article>`** on many posts. Flattens the article outline and dilutes topical heading signal. Demote to `<h3>` or move outside the article element.
- **Inconsistent product casing across the site**: `Wordpress` vs `WordPress`, `Macbook` vs `MacBook`, `vCentre` vs `vCenter`, `TrueNas`/`Truenas` vs `TrueNAS`, `Github` vs `GitHub`, `Netapp` vs `NetApp`, `Ipad` vs `iPad`. Worth a one-off find/replace pass in WordPress (or a lint rule in the build).
- **Duplicate social links in footer** (`LinkedIn` + `Linkedin`, `GitHub` + `Github`, `Twitter` + `X` both pointing at the same x.com URL) — appears on at least the `/lab/` page and likely site-wide.

## Static / Landing Pages

### /
**Title:** James Kilby — VMware, Homelab & Cloud Infrastructure Notes
**One-liner:** Homepage renders cleanly with strong topical content, but is missing meta description, canonical, and Open Graph tags, and has a duplicated H1.
- typo: "How to safety shutdown a vSAN Environment" → "How to safely shut down a vSAN environment" _(context: vSAN Cluster Shutdown excerpt)_
- typo: excerpt for 'New VMware Cloud on AWS Host: i7i.metal-24xl' ends mid-phrase at "the new i7i (i7i." → sentence should complete, e.g. "…the new i7i (i7i.metal-24xl)."
- cosmetic [high]: Duplicate H1 — two `<h1>James Kilby</h1>` elements (masthead + hero).
- cosmetic [medium]: Post-card excerpt for `i7i.metal-24xl` is truncated mid-sentence. _(card on homepage)_
- cosmetic [medium]: Every card shows two raw dates with no separator/label. _(byline on every post card)_
- cosmetic [medium]: Several content images lack `width`/`height` (offlinedepot.png, VMConAWS.png.webp, Octopus-Energy-logo.jpg, UbuntuExpand.png). _(post-card thumbnails)_
- cosmetic [medium]: `Read More <Title>Continue` concatenation on every card. _(every post card)_
- cosmetic [low]: `VMConAWS.png.webp` has a double extension suggesting a malformed filename through the pipeline. _(i7i.metal-24xl card image)_
- cosmetic [low]: Hero stats block reads `deploys.month............0` on a page that has clearly been updated today.
- seo [high]: Meta description missing. → Add a 140–158 char description summarising the blog and core topics.
- seo [high]: `rel=canonical` missing. → Emit `<link rel="canonical" href="https://jameskilby.co.uk/">`.
- seo [high]: All Open Graph tags missing. → Add og:title, og:description, og:image (1200×630), og:type=website, og:url plus twitter:card.
- seo [high]: Two `<h1>` elements. → Demote the masthead site-title to `<p class="site-title">` and keep one hero H1.
- seo [medium]: Heading hierarchy shallow — H2 used for a decorative tagline and for card titles. → Make tagline a `<p>`; use H2 only for true sections; card titles as H3.
- seo [medium]: Card "Read More …Continue" anchor text is non-descriptive. → Hide for SEO/a11y or anchor on the post title.
- seo [medium]: Byline exposes two dates with no schema. → Wrap in `<time datetime="…">` with `itemprop=datePublished/dateModified`.
- seo [low]: `<title>` omits "blog"/"vExpert". → Optional rewrite: "James Kilby Blog — VMware vExpert, Homelab & Cloud Notes".
- seo [low]: Some image alts duplicate the card title verbatim (offlinedepot.png, VMConAWS.png.webp). → Shorten to descriptive alts.

### /about-me/
**Title:** about me
**One-liner:** Page is reachable with clean structure and valid metadata, but the `<title>` is weak ("about me" lowercase) and one body sentence has broken grammar.
- typo: "I have been a vExpert for the last 12 years and previously and has been honoured to be awarded Veeam Vanguard status for four years." → "I have been a vExpert for the last 12 years and was previously honoured to be awarded Veeam Vanguard status for four years." _(stray 'and', subject/verb mismatch)_
- seo [high]: `<title>` is "about me" — 8 chars, lowercase, no brand. → Rewrite to e.g. "About James Kilby — Solution Architect & vExpert".
- seo [medium]: `<title>` and `og:title` disagree (`og:title` = "About Me: Tech Enthusiast & Photographer"). → Align them.
- seo [medium]: No internal links to actual blog posts; only category landings. → Add 2–4 contextual links to flagship posts.
- seo [medium]: Affiliate links — no visible evidence of `rel="sponsored nofollow noopener"`. → Verify and apply to monetised links (Nutmeg, Trading212, Krisp, Octopus, Zen, Wise).
- seo [low]: Thin content (~235 words). → Expand with specialisms, talks, contact intent.
- seo [low]: Heading hierarchy flat — no H3s under "Affiliate Links" or "Certifications Awarded". → Add H3 groupings as those sections grow.
- seo [low]: Five `<title>` elements in document (one real plus inline SVG `<title>`s). → Confirm the document-level `<title>` parses correctly; no action unless SERP snippet shows the wrong text.

### /lab/
**Title:** Homelab - Hardware - James Kilby
**One-liner:** Solid content page with a clear hardware inventory, but lacks meta description, canonical, and Open Graph tags, plus a few typography/heading-hierarchy issues.
- typo: "GPU/ Management Cluster" → "GPU / Management Cluster" _(H3 spacing)_
- typo: "TrueNAS scale" → "TrueNAS Scale" _(product name)_
- typo: "( 21.8TiB Usable)" → "(21.8TiB Usable)" _(stray space after `(`)_
- typo: "lab (running multiple functions for over 6 years) It currently" → add full stop before "It currently"
- typo: "GPU is an essential in at least one node." → "GPU is essential in at least one node."
- typo: "Noise isn't really a factor due to location" → add terminal full stop _(bullet punctuation inconsistency)_
- typo: "Heat Output isn't a huge factor" → "Heat output isn't a huge factor." _(case + missing full stop)_
- typo: "giving me a usable 66.3 TB This is presented" → add full stop after "TB"
- cosmetic [high]: Storage summary table malformed — rows have mismatched column counts. _(after "Secondary Storage" section)_
- cosmetic [medium]: Duplicate social links in footer (LinkedIn/Linkedin, GitHub/Github, Twitter/X same URL).
- cosmetic [medium]: Image alt text is filename-derived ("Vsphere Overview 1024X530", "Housenetworkoverview 1024X634").
- cosmetic [low]: Inconsistent unit notation — body mixes `TiB` and `TB`.
- cosmetic [low]: Stray/inconsistent spacing in headings (`GPU/ Management Cluster`, `( 21.8TiB Usable)`).
- seo [high]: Meta description missing. → Add a 140–155 char description naming the key tech (vSphere, Nutanix, A10 GPU, TrueNAS, 25 GbE).
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing. → Use a hardware photo or vSphere overview diagram for og:image.
- seo [medium]: Title (30 chars) underused. → Lengthen to surface key technologies.
- seo [medium]: Heading hierarchy skips — "Primary Storage" and "Secondary Storage" are H2 but should be H3 under "Storage"; "Overview" sits before any H2-level grouping.
- seo [medium]: Filename-derived image alts hurt image SEO. → Rewrite to describe the content.
- seo [low]: Only one internal blog link in main content. → Add contextual links to A10 upgrade post, TrueNAS RAIDZ2 post, AI inference posts.
- seo [low]: No machine-readable `dateModified`. → Add Article/TechArticle JSON-LD.
- seo [low]: Anchor text "More details are here" is generic, and the link target may be missing/broken. → Replace with descriptive anchor.

### /media/
**Title:** Media - James Kilby
**One-liner:** Clean prose with no typos, but the title is too short and several social/meta tags misrepresent the page as a single podcast rather than a media-appearances hub.
- cosmetic [low]: Heading hierarchy skip — H1 → H3 with no H2 in between.
- seo [medium]: Title is 19 chars. → Lengthen, e.g. "Media: Podcasts, Talks & Conference Appearances - James Kilby".
- seo [medium]: Meta description is the author bio, not page-specific. → Rewrite to describe podcast/VMUG content.
- seo [medium]: `og:title` and `twitter:title` say "Xtravirt CloudInsiders Podcast Awaits You" — misrepresents the page. → Set to "Media – Podcasts, Talks & VMUG Sessions by James Kilby".
- seo [low]: Heading hierarchy skip — promote H3s to H2.
- seo [low]: Thin content (~398 words). → Add per-appearance intros with key takeaways.
- seo [low]: No internal links to actual blog posts. → Link from each section to relevant articles.

### /vmc/
**Title:** VMware Cloud on AWS (VMC) – Links & Resources - James Kilby
**One-liner:** Useful curated link hub with solid heading structure, but missing meta description, canonical, and Open Graph tags, plus a duplicate H1/H2 title and a malformed external URL.
- typo: "Pre Req's" → "Prerequisites"
- cosmetic [medium]: Duplicate page title — H1 immediately followed by an H2 of identical text, then a third repeat in the opening paragraph.
- cosmetic [low]: "Connect with me" links appear as bare label text with no visible URLs in the extracted content.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: "My VMware Cloud on AWS Blog Posts" and "Official Blogs I contributed to" entries appear as plain text — internal links may be missing. → Verify and link them.
- seo [medium]: Duplicate H1-equivalent at top of page. → Remove the duplicate H2 and the third repetition.
- seo [medium]: Generic anchor text on many outbound links (FAQ, Sizing, Configuration, Max, Privacy, etc.). → Prefix with the product/topic.
- seo [medium]: "Useful Blogs" section lists 13 author names as plain text. → Link them or remove.
- seo [medium]: Thin-content risk: 311 words of prose. → Add intro sentences under each H2.
- seo [medium]: "Updated: May 29, 2026" shown but no machine-readable date metadata. → Add Article JSON-LD.
- seo [low]: Title leans on the parenthetical "(VMC)" rather than searchable terms.

### /homelab-software/
**Title:** Homelab - Software - James Kilby
**One-liner:** Clean, well-structured pillar page with good UK English and no typos, but it is missing core SEO metadata and could use richer internal linking and visuals.
- cosmetic [low]: Published/Updated metadata line missing whitespace, producing `📅Published: November 11, 2023•Updated: April 02, 2026`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title uses a hyphen-only structure with weak keywords. → Rewrite to include Plex/Ollama/Grafana.
- seo [medium]: Only one internal blog link in main content. → Add internal links to write-up posts for each section (Plex, Immich, Home Assistant, Ollama/GPU, Traefik/Cloudflared).
- seo [low]: Generic anchor text on the two internal links ("Read my migration post →", "See related posts →").
- seo [low]: No images on the page — weakens engagement and provides nothing for og:image. → Add at least one hero image with descriptive alt text.

## Blog Posts

## 2026

### /2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/
**Title:** VMC Content Libraries: Faster Software Deployment in SDDC
**One-liner:** Solid tutorial content, but missing meta description, canonical, and Open Graph tags — plus a handful of small typos and one broken-sounding sentence in the Networking section.
- typo: "SDDC's" → "SDDCs"
- typo: "self contained" → "self-contained"
- typo: "IP's" → "IPs"
- typo: "vCentre's" → "vCentres" (and `vCentre` → `vCenter` throughout for VMware product consistency)
- typo: "Usually I don't utilise/DX for this" → "Usually I don't utilise DX for this"
- typo: "would be purely private IP" → add full stop
- typo: "Content Libary" → "Content Library" _(image alt)_
- cosmetic [medium]: Sentence "Usually I don't utilise/DX for this…would be purely private IP" reads as broken (missing word, no full stop). _(Networking section)_
- cosmetic [low]: Hero image has no `width`/`height` (unlike other body images). → CLS risk.
- cosmetic [low]: Hero alt "Firefly Gemini Flash" is the tool name, not a description.
- cosmetic [low]: Image filename/alt "ContentLibary" is misspelled.
- cosmetic [low]: Subscription URL exposes the internal vCenter hostname and library UUID verbatim. → Verify intentional.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Hero image missing dimensions — CLS impact.
- seo [medium]: Generic anchors "written" and "here" for external references. → Use descriptive anchor text.
- seo [low]: H1 vs `<title>` keyword mismatch (H1 omits "SDDC", title omits "on AWS"). → Align.
- seo [low]: Section ordering — "Prerequisites" H2 appears before any intro. → Move intro first.
- seo [low]: No inline internal links to `/vmc/` or related VMC posts.

### /2026/01/web-development-improvements/
**Title:** Blog Performance & SEO Improvements: Cloudflare, Privacy & More - James Kilby
**One-liner:** Solid, well-structured post let down by a recurring "Perfomance" misspelling baked into heading IDs/anchors/alt text, several small grammar slips, and a meta description that's a truncated paragraph copy.
- typo: "Perfomance" → "Performance" _(image alt and multiple heading IDs `#perfomance`, `#site-perfomance`, `#runner-perfomance`, `#perfomance-1`)_
- typo: "compression ratio's than gzip" → "compression ratios"
- typo: "excellent compression ratio's" → "compression ratios"
- typo: "just incase" → "just in case"
- typo: "reutilised" → "reused"
- typo: "less DNS lookups" → "fewer DNS lookups"
- typo: "Ie (Published" → "i.e. (Published"
- typo: "Github Action" → "GitHub Action" _(H3)_
- typo: "scans entire repository history" → "scans the entire repository history"
- typo: `"the backend" These help improve` → add full stop and capitalise "These".
- typo: "viewed to be loaded in the background." — awkward phrasing; rewrite for clarity.
- typo: "served directly from Cloudflare however the analytics run by plausible is on a separate domain plausible.jameskilby.cloud This resides" → split into sentences; capitalise Plausible; "analytics are".
- typo: "DNS prefetch for plausible.jameskilby.cloud and preconnect for plausible.jameskilby.cloud" — duplicated domain.
- typo: Incremental Build paragraph contains multiple run-on clauses. → Split with full stops.
- cosmetic [high]: TOC anchors broken/truncated to single letters (`#l`, `#r`, `#l-1`, `#hook`) — clicking does not scroll to the intended section.
- cosmetic [high]: Misspelling `Perfomance` is embedded in shareable fragment URLs.
- cosmetic [high]: `jameskilby.co.uk` link in the Lighthouse paragraph uses a bare host with no scheme — resolves to `/2026/01/web-development-improvements/jameskilby.co.uk` (broken).
- cosmetic [medium]: Image alt "Slack Lighthouse Perfomance" exposes the misspelling to screen readers.
- cosmetic [medium]: Visible link text `/change` points to `/changelog` — mismatched.
- cosmetic [medium]: Meta description is a verbatim truncated lede ending mid-sentence at "Privacy" with no full stop.
- cosmetic [low]: Inconsistent product casing — `Wordpress` (nav/tag) vs `WordPress` (body).
- cosmetic [low]: Inconsistent component naming — "GitHub runner", "deployment runner", "deployment wizard" all refer to the same thing.
- cosmetic [low]: Lead image (Website-Optimisations.png) missing `width`/`height`.
- seo [high]: Meta description is auto-truncated. → Hand-craft ~150 chars naming concrete wins (deploy time, Lighthouse, Brotli, AVIF, incremental builds).
- seo [high]: TOC anchors broken — internal jump-links fail (UX + crawler signal).
- seo [high]: `jameskilby.co.uk` anchor is a broken relative path.
- seo [medium]: Heading IDs contain `perfomance` typo. → Regenerate slugs and add 301 redirects.
- seo [low]: Title is 85 chars including suffix — likely truncated in SERPs.
- seo [low]: Generic anchors `report`, `public`, `change`.
- seo [low]: H3 "Github Action" — fix casing.

### /2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/
**Title:** Automating My AI Homelab: Ansible + NVIDIA Passthrough
**One-liner:** Solid long-form technical post, but missing meta description / canonical / Open Graph tags, has a broken "Install NVIDIA Container Toolkit" link, variable-name typos in a reference table, and a few small grammar slips.
- typo: "vCentre" → "vCenter"
- typo: "traefik_heakthcheck_timeout" → "traefik_healthcheck_timeout"
- typo: "traefik_heathcheck_start_period" → "traefik_healthcheck_start_period"
- typo: "A NVIDIA datacenter Graphics card" → "An NVIDIA datacenter graphics card"
- typo: `called "vGPU' set` → `called "vGPU", set` _(mismatched quote, missing comma)_
- typo: "multiple VM's" → "multiple VMs"
- typo: "a HTTPS service" → "an HTTPS service"
- typo: "take the output from this output" → "take the output from this command" _(duplicated word)_
- typo: "post deployment" → "post-deployment"
- typo: "AI Workloads" → "AI workloads" _(consistency)_
- cosmetic [high]: Broken link "Install NVIDIA Container Toolkit" points to `http://ansible/vGPU/install_nvidia_containertoolkit.yml`. _(relative path mangled to http URL)_
- cosmetic [high]: JSON snippet has a trailing comma after the last key — invalid JSON if pasted directly.
- cosmetic [medium]: Several content images missing alt text (lead VMware-NVIDIA logo, six related-posts thumbnails).
- cosmetic [low]: Dangling sentence "However, in a homelab environment a more straightforward Docker-based setup could be more appropriate…." _(four dots)_
- cosmetic [low]: Duplicated phrase "It has the added benefit … It has the added benefit" in Traefik intro.
- cosmetic [low]: Ansible "Show vGPU license info" code block cluttered with repeated `9:18:47 PM` timestamps.
- cosmetic [low]: Driver-version mismatch: prerequisites say `535.247.0` but commands/JSON use `535.247.01`/`535.247.02`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Broken internal link to NVIDIA Container Toolkit playbook. → Replace with the working GitHub URL used below.
- seo [medium]: Generic anchor text "here" for an important internal SemaphoreUI link.
- seo [low]: URL slug (`…-and-other-improvements`) is vague.
- seo [low]: Title (50 chars) doesn't include "vGPU".
- seo [low]: H1 vs title differ; H1 omits "Ansible" and "NVIDIA".
- seo [low]: Deep nesting H2>H3>H4>H5. → Flatten to H2>H3>H4.

### /2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/
**Title:** Self-Hosted AI Stack: Ollama, Open WebUI, n8n, ComfyUI & More (2026)
**One-liner:** Long, substantive technical post that is structurally sound but has several SEO gaps and a small architectural-layers count inconsistency in the body.
- typo: Intro says "seven architectural layers" but only five are documented and "langfuse" is listed as its own layer despite being a sub-section of Observability. → Rework so the count matches.
- typo: "a SMB-mounted volume" → "an SMB-mounted volume"
- cosmetic [medium]: Header link for the current post points to `undefined` instead of the canonical URL.
- cosmetic [low]: Featured image referenced twice with different alts and one without `width`/`height`.
- cosmetic [low]: TOC anchors with odd hyphen splits (`#comfy-ui`, `#n-8-n`, `#searx-ng`, `#open-web-ui`).
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title vs H1 mismatch — title markets a "(2026)" roundup while H1 says "Part 1: Architecture Overview".
- seo [medium]: H1 link href is `undefined`.
- seo [low]: Generic anchor "here" for "automating these prerequisites here".
- seo [low]: No inline link to the prior Infrastructure post when mentioned.
- seo [low]: VMUG anchor uses bare "VMUG" pointing at a youtu.be short URL.
- seo [low]: Title is 64 chars — slightly above ideal.
- seo [low]: SmarterRouter feature list could be H4 sub-headings.

### /2026/03/octopus-agile-battery-solar-calculator/
**Title:** Free Octopus Agile Battery & Solar Calculator: 5 Batteries Tested - James Kilby
**One-liner:** Well-written post with clean structure and good content, but missing meta description, canonical, and Open Graph tags, plus a few minor typos.
- typo: "Givenergy 13.5kWh" → "GivEnergy 13.5kWh" _(inconsistent brand casing)_
- typo: "the price of electric doubles" → "electricity"
- typo: "the price of batteries halve" → "halves" _(subject-verb agreement)_
- typo: "discharge≥20.0p" → "discharge ≥20.0p" _(missing space)_
- typo: "the 15yr return" → "15-year return"
- typo: "the benefits and the price of both solar and battery have changed" → "solar and batteries"
- cosmetic [low]: Featured image (Octopus Energy logo) missing `width`/`height`.
- cosmetic [low]: Dangling lead-in line under H2 "Code": "If you want to skip reading and jump straight to the code on Github".
- cosmetic [low]: Stray leading space inside `( I am £178 better off…)`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Generic anchor "here" for the most important outbound link (example report). → Replace with descriptive text.
- seo [medium]: No internal links to related posts in body.
- seo [low]: Title is 72 chars — likely truncated.
- seo [low]: Heading hierarchy: lone H4 "SEG – Smart Export Guarantee" between H3 and H2.
- seo [low]: Cryptic anchor IDs (`#c`, `#u`, `#c-1`).
- seo [low]: Image alts could be richer for image search.

### /2026/04/automated-vcf-9-offline-depot/
**Title:** Automated VCF 9 Offline Depot - James Kilby
**One-liner:** Solid technical article with clean structure and good internal linking; main weakness is missing meta description, canonical, and Open Graph tags, plus a couple of minor copy issues.
- typo: "go and look at the GitHub repo here" → also missing terminal full stop.
- typo: "execute the below" → "execute the command below" _(awkward noun use)_
- typo: "The script pulls and executes the below files." → "…the files listed below."
- typo: `https://traefik.domain.com` placeholder inconsistent with earlier `traefik.yourdomain.com`; `domain.com` is a real registered domain.
- cosmetic [high]: "See my blog here on how to expand the disk to its full size" — `here` has no href and no terminal full stop.
- cosmetic [low]: First bullet of "What it does" is a lead-in sentence rather than a list item.
- cosmetic [low]: Sentence "If you then access the nginx web server at your defined address i.e. https://vcf.jameskilby.cloud" has no terminal punctuation.
- cosmetic [low]: Featured image (offlinedepot.png) missing `width`/`height` (other content images have them).
- cosmetic [low]: Plausible analytics thumbnail missing dimensions.
- cosmetic [low]: "You will see something like this in the Traefik logs if you do" ends without a full stop before the code block.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Two external references use generic "here" anchor text (Broadcom TechDocs, GitHub repo).
- seo [medium]: H2 "Increase Disk Size" appears after an H3 inside Troubleshooting, breaking visual hierarchy.
- seo [medium]: Missing internal link for the disk-expansion blog reference.
- seo [low]: Title is 38 chars — could absorb a higher-intent keyword.

### /2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/
**Title:** My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2) - James Kilby
**One-liner:** Substantive 2k-word technical post with solid structure, but missing meta description, canonical, and Open Graph tags, plus a few sentence-level grammar slips and an inconsistency in the introduced data stores.
- typo: "allocated container resources as follows" → add colon before the table.
- typo: "the url can be adapted as needed. compose file uses the pattern" → "The URL…" and "The compose file…"
- typo: "you change one variable and every service picks it up" → comma splice; rewrite.
- typo: "is stored on a SMB share" → "an SMB share"
- typo: "a second container that runs alongside OpenWebUI sharing access to the same volumes" → add comma before "sharing".
- typo: "writes it out to the persistent smb share" → "SMB share"
- typo: "It also performs retention of the database only keeping the last 7 copies. This gives me the ability to restore" → add commas and colon.
- typo: "The internal network (Green Zone) is configured and a dedicated subnet" → "configured with a dedicated subnet"
- typo: "in the .env file GitHub repo URL (e.g. …)" → reads as run-on; rewrite.
- typo: "fast analytical queries—aggregations" → spaced em dash for consistency.
- typo: Intro lists "ChromaDB" but post documents Qdrant; also omits ClickHouse / MongoDB.
- cosmetic [medium]: Heading-level inconsistency — "N8N Backups" sits at H2 while sibling backup subsections (OpenWebUI/Qdrant/PostgreSQL) are H3.
- cosmetic [medium]: Tables rendered as pipe-delimited plain text rather than `<table>`.
- cosmetic [low]: Bullet lists rendered as plain paragraph lines (likely missing `<ul>`/`<li>`).
- cosmetic [low]: Featured image missing intrinsic dimensions in dump.
- cosmetic [low]: Mixed casing `OpenWebUI` vs `Open WebUI`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: H2 "N8N Backups" should be H3 under Backups.
- seo [medium]: Intro list wrong vector DB (ChromaDB) and omits ClickHouse/MongoDB. → Update to match body.
- seo [low]: Title is 71 chars — slightly above ideal.
- seo [low]: Body links mostly category pages; few inline contextual internal links.
- seo [low]: Featured image alt is 35+ words. → Shorten and move detail to `<figcaption>`.
- seo [low]: Byline "James" link points to homepage rather than `/about/`.

### /2026/04/new-vmc-host-i7i-metal-24xl/
**Title:** New VMware Cloud on AWS Host: i7i.metal-24xl - James Kilby
**One-liner:** Solid technical post with detailed specs and an FAQ, but missing meta description, canonical and Open Graph tags, has a non-descriptive featured-image alt, and contains a handful of minor copy and unit-formatting inconsistencies.
- typo: "2.5 Ghz" / "4.0 Ghz" → "GHz"
- typo: "Optimized" → "Optimised" _(UK English consistency)_
- typo: "No of Physical Cores" → "No. of Physical Cores"
- typo: "Network Adaptor" → "Network Adapter" _(industry standard)_
- typo: "instances website" → "instance's website" _(missing apostrophe)_
- typo: "ranging from bleeding edge performance for tier one applications." → sentence reads as a fragment; add hyphens for compound modifiers and complete the "ranging from X to Y" structure.
- cosmetic [medium]: Image alt "Vmconaws.Png" is auto-generated from the filename.
- cosmetic [medium]: Featured image missing `width`/`height` — CLS risk; inconsistent with the optimisation pipeline.
- cosmetic [low]: Comparison table renders as flat pipe-delimited text in plain output.
- cosmetic [low]: Footnote markers inconsistent (`*`, `^`, `**`) — referents not located in the table.
- cosmetic [low]: Closing line uses generic "here" anchor.
- cosmetic [low]: Heading style inconsistency — first H2 ends with `:`, others do not.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Generic "here" anchor on the only external announcement link.
- seo [medium]: Featured image alt is filename-derived.
- seo [medium]: No internal links to related VMC posts (e.g. vSAN ESA post). → Add contextual link.
- seo [low]: FAQ section not emitted as FAQPage JSON-LD.
- seo [low]: No `fetchpriority="high"` on the LCP image.

### /2026/04/vsphere-power-management-driven-by-ansible/
**Title:** Automate vSphere Power Management with Ansible: Easy Energy Savings [2026] - James Kilby
**One-liner:** Solid, in-depth technical post with clear structure, but missing meta description, canonical, and Open Graph tags, plus a handful of small grammar fixes.
- typo: "aggressively that govern frequency and voltage scaling. while preserving turbo boost" → "…to govern frequency and voltage scaling, while preserving…"
- typo: "With C-states enabled which govern idle sleep states" → add commas around the relative clause.
- typo: "As I have been using Ansible a lot lately therefore I decided" → "…lately, I decided"
- typo: "tedious and who wants to do that." → "tedious, and who wants to do that?"
- typo: "you get a repeatable, process" → drop the stray comma.
- typo: "This profile is typical especially the 1600-1900hrs peak." → add comma.
- typo: "I often will have 3 more additional vSphere servers on" → drop "more".
- typo: "you should see the task pop like" → sentence is truncated.
- typo: "I have previously talked about my supplier Octopus Energy and how they operate an innovative tariff called Agile." → set off "Octopus Energy" with commas.
- cosmetic [medium]: "you should see the task pop like" appears truncated — missing screenshot or completion.
- cosmetic [medium]: Stray full-stop creating a fragment: `…scaling. while preserving turbo boost…`.
- cosmetic [low]: Octopus carbon-intensity sentence dangles without a full stop before the image.
- cosmetic [low]: Featured image missing `width`/`height` (others have dimensions) — CLS risk.
- cosmetic [low]: Nav block shows "PreviousPrevious" — duplicated word from visually-hidden label leak.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title is 81 chars including suffix — over the 60-char ideal.
- seo [low]: Bracketed `[2026]` in title looks SEO-stuffy.
- seo [low]: H1 vs `<title>` keyphrase mismatch.
- seo [low]: Generic anchor "Repo" for the GitHub link.
- seo [low]: Single-word anchor "Agile" is ambiguous.
- seo [low]: Featured image lacks dimensions and caption.

## 2025

### /2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/
**Title:** How I Migrated from Pocket to Hoarder with AI Integration - James Kilby
**One-liner:** Solid article with clear structure and good word count, but missing meta description/canonical/Open Graph tags and a content image lacks alt text, plus a couple of minor grammar slips.
- typo: "saved URL's and tags" → "URLs"
- typo: "passes the URL's into a headless Chrome" → "URLs"
- typo: "connected it to my existing Ollama setup This means" → add full stop before "This".
- typo: "it generate similar tags" → "it generates"
- typo: "ranging from company takeovers. To sites being dead." → "…takeovers to sites being dead."
- typo: "The tags language must be in english." → "in English."
- cosmetic [medium]: First content image (Screenshot-2025-01-29-at-23.30.47.png) missing alt text.
- cosmetic [medium]: Run-on between sentences: `existing Ollama setup This means`.
- cosmetic [low]: Three screenshots share an identical generic alt.
- cosmetic [low]: Trailing four-dot ellipsis used twice.
- cosmetic [low]: Code block labelled "Hoarder" appears as a stray heading-like line.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title still says "Hoarder" — product renamed to Karakeep (noted in body). → Append "(now Karakeep)".
- seo [medium]: Vague anchor "setup" for the related AI stack post.
- seo [low]: Rename-announcement note sits as plain body text with no styling/link.
- seo [low]: "Finished Result" sits as H2 next to its H3 siblings — consider demoting to H3.

### /2025/04/warp-the-intelligent-terminal/
**Title:** Warp – The intelligent terminal - James Kilby
**One-liner:** Readable post with a working narrative, but missing essential SEO meta (description, canonical, Open Graph), a couple of grammar slips, and image alt-text problems.
- typo: "that is an acceptable risk" → "that are an acceptable risk" _(plural subject)_
- typo: "Sometimes you just need a helping hand" → add terminal full stop.
- typo: "Warps website" → "Warp's website"
- typo: "Where the beauty of warp kicked in and said" → sentence fragment; rewrite and capitalise "Warp".
- typo: "Once apt-get had been upgraded" → "Once apt-get had been run" _(apt-get itself wasn't upgraded)_
- typo: "sign up with my referral link here" → drop "here" and add full stop.
- cosmetic [medium]: Featured image alt "Wa" — truncated from "Warp".
- cosmetic [medium]: Two content screenshots have empty alt attributes.
- cosmetic [medium]: Narrative gap — Warp's actual message between paragraphs appears to be conveyed only via an unaltted screenshot.
- cosmetic [low]: Missing terminal punctuation on several sentences.
- cosmetic [low]: Informal `:p` emoticon in prose.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title is light on keywords. → "Warp Review: The AI Terminal That Tidied Up My Homelab".
- seo [medium]: Theme chrome (`Post Tags:`, `Connect with me:`, etc.) emitted as H2 — dilutes article outline.
- seo [medium]: Generic anchor "here" on the referral CTA.
- seo [medium]: No body internal links to author's own AI/homelab posts.
- seo [medium]: Truncated "Wa" alt on hero, empty alts on screenshots.
- seo [low]: Thin unique prose (much of the word count is verbatim apt-get output).

### /2025/05/vmc-quick-sizing-guide/
**Title:** VMware Cloud on AWS Storage Sizing Quick Reference Guide - James Kilby
**One-liner:** Clean, well-marked-up post but very thin (199 words), uses a generic "here" anchor for the key external link, and has a minor grammar/punctuation slip and an awkward double-header table row.
- typo: "(Ie valid for secondary clusters) It also" → "(i.e. valid for secondary clusters). It also"
- typo: "for up to date info" → "up-to-date info"
- cosmetic [medium]: Table has two header-like rows — `<thead>` plus a first `<tbody>` row that acts as a second header.
- cosmetic [low]: Trailing space inside `here ` link text and leading space at start of paragraph.
- cosmetic [low]: No inline image in body — wall of text + one table.
- seo [medium]: Thin content (199 words).
- seo [medium]: Generic anchor "here" on the most important outbound link (official VMware sizing tool).
- seo [medium]: Updated April 2026 but content still vSAN OSA only and missing newer hosts (i4i, i7i.metal-24xl). → Add an i7i row or note.
- seo [low]: Title is 70 chars including suffix.
- seo [low]: Meta description is the literal first sentence and doesn't sell value.
- seo [low]: OG image alt mismatches between this post and `/vmc/` — same image reused with different alts.
- seo [low]: No `<img>` in article body.
- seo [low]: No H2/H3 inside the body besides template H2s.

### /2025/08/vmc-host-deepdive/
**Title:** An in-depth look at VMware Cloud on AWS hosts - James Kilby
**One-liner:** Thin but functional comparison post; meta description has a missing article and the page would benefit from a proper table and stronger meta/keyword work.
- typo: "This is single page intended" → "This is a single page intended" _(also in meta description)_
- typo: "Network Adaptor" → "Network Adapter" _(networking context)_
- cosmetic [medium]: Featured image (`Picture-1-e1768509620339.png`) has no alt text.
- cosmetic [medium]: Comparison data rendered as prose ("I3.metal has 36…"), not as an HTML `<table>`.
- cosmetic [low]: Reading-time badge says "1 min read (219 words)" but body is ~419 words — counter is undercounting.
- cosmetic [low]: Hero image filename is the default WordPress export name.
- seo [high]: Meta description has the missing-article grammar bug and omits host-model keywords (i3, i3en, i4i).
- seo [high]: Updated date May 2026 but body still only covers i3/i3en/i4i — missing i7i.metal-24xl despite a newer post existing.
- seo [medium]: Title vs og:title inconsistency.
- seo [medium]: Thin content (~419 words).
- seo [medium]: No real `<table>` markup for a comparison page.
- seo [medium]: Featured image has empty alt.
- seo [medium]: Only one outbound contextual link; no in-body internal links to `/vmc/`, `/2020/07/i3en/`, or `/2025/05/vmc-quick-sizing-guide/`.
- seo [medium]: `og:image` is 816×205 — wrong aspect ratio for social cards (LinkedIn/X expect ~1200×630).
- seo [low]: Title (`<title>`) front-loads "VMC" rather than "VMware Cloud on AWS".
- seo [low]: Generic anchors throughout.
- seo [low]: No JSON-LD for Article/TechArticle.

### /2025/09/managing-my-homelab-with-semaphoreui/
**Title:** Managing My Homelab with SemaphoreUI (Ansible Web UI)
**One-liner:** Solid technical content with one H1, but missing meta description, canonical, and Open Graph; the page also has broken TOC anchors, an inconsistent step-numbering scheme, and several typos.
- typo: "Preps APT and stores GPG Keys" → "Prep APT and store GPG Keys" _(verb form)_
- typo: "repositroy" → "repository" _(anchor slug)_
- typo: "repositaries" → "repositories" _(anchor slug)_
- typo: "wishing Packer template building were supported natively…" — dangling participle; rewrite.
- typo: "Terraform and Ansible integration are significantly simplifying" → "integrations are" _(subject-verb agreement)_
- cosmetic [high]: TOC anchors broken/truncated to single letters (`#w`, `#p`, `#h`, `#i`, `#r`, `#w-1`, `#key-store-1`) — won't resolve on the page.
- cosmetic [medium]: TOC anchor slugs misspelled (`#repositaries`, `#step-1-is-to-connect-your-repositroy`).
- cosmetic [medium]: Step numbering inconsistency — H2s lack step numbers but body references "Step 1/2/3/4".
- cosmetic [medium]: Two H2s titled "Repositories" on the same page — anchor collision.
- cosmetic [low]: Content image has generic alt "Managing my Homelab with SemaphoreUI Screenshot".
- cosmetic [low]: Byline shows duplicated date stamps.
- cosmetic [low]: Heading skip — "Execution Output" rendered as bold body rather than a heading.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Generic "here" anchor used for two important outbound links.
- seo [medium]: No contextual internal links from body (only related-posts widget).
- seo [medium]: Broken TOC anchors hurt UX/crawlers.
- seo [low]: H1 vs title casing mismatch.
- seo [low]: Future-dated `Updated: May 26, 2026` plus links to 2026-02/2026-04 posts — verify intentional.

### /2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/
**Title:** How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare - James Kilby
**One-liner:** Solid technical post let down by a title/URL mismatch ("deploy" vs "upgraded"), missing meta description, missing canonical, and missing Open Graph tags — plus a handful of small grammar slips.
- typo: "Set's up the job on a runner" → "Sets up"
- typo: "Check's Out the repo" → "Checks out"
- typo: "Install any relevant dependencies" → "Installs"
- typo: "Test's the runner environment" → "Tests"
- typo: "Commit and Pushes the Static Site" → "Commits and pushes"
- typo: "Replaces all WordPress URL's as relative" → "URLs"
- typo: "for the GitHub-hosted runner" → reads as missing word/clause.
- typo: "so you can't instantly view your changes" → contradicts intended meaning; drop the "can't" → "can".
- typo: "I am using Ubuntu and therefore selected Linux" → add comma after "Architecture".
- typo: "Using Utterance for Comments" → "Utterances" _(product name plural)_
- typo: "Utterance is lightweight javascript code" → "Utterances is lightweight JavaScript code"
- cosmetic [medium]: Slack notification payload pasted as raw text rather than a screenshot or code block.
- cosmetic [low]: First content image (Github-Actions.webp) missing `width`/`height` while others have them.
- cosmetic [low]: Stray "Branch Alias URL:" with no value in the Slack paste — incomplete copy.
- cosmetic [low]: Numbered list under "Create a Slack Webhook URL" mixes prose with nested bullets.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing — particularly important because slug says "deploy" but title says "upgraded".
- seo [high]: Open Graph tags missing.
- seo [medium]: Title/slug mismatch — slug "deploy" vs title "upgraded".
- seo [medium]: Title is 91 chars — over the ~60 char ideal.
- seo [low]: Heading hierarchy: "GitHub Notifications" and "Cloudflare Notifications" sit as H4 under "Create a Slack Webhook URL" — should be H3.
- seo [low]: Bare URL anchor `/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/`.
- seo [low]: First image alt is just "Github Actions" — uninformative.
- seo [low]: Other image alts thin and use lowercase `Wordpress`.

## 2024

### /2024/01/holodeck-cpu-fixes/
**Title:** VMware Holodeck on Older CPUs: Fixing Compatibility Issues - James Kilby
**One-liner:** Functional and well-structured, but suffers from thin content, a weak meta description, and several plural-apostrophe errors plus a run-on sentence.
- typo: "Physical CPU's" → "Physical CPUs"
- typo: "my CPU's are not supported" → "my CPUs are not supported"
- typo: "vCLS VM's for DRS" → "vCLS VMs"
- typo: "Holodeck team please don't" → add comma.
- typo: "And last of all when the NSX edges attempt to power on they will fail" → add commas.
- typo: "Luckily a colleague of mine Tim Sommer has made all of the required changes to the VLCGUI.ps1 deployment script and that is available here" → commas around appositive, full stop at end.
- cosmetic [medium]: Featured image (40oOd8IipPvtrPJs-1198788743.jpg) has empty alt.
- cosmetic [low]: Code block flags `--ignoreprereqwarnings…` sit as a paragraph rather than a code block.
- cosmetic [low]: Solution paragraph ends without a full stop after "available here".
- seo [medium]: Title is 72 chars — likely truncated in SERPs.
- seo [high]: Meta description is just the disclaimer sentence (~111 chars) and doesn't include key terms (NSX Edge, VLCGUI, unsupported CPU).
- seo [medium]: Thin content (~268 words).
- seo [medium]: Generic "here" anchor for the most important outbound link.
- seo [low]: Generic anchor "previous post" for the related Multihost Holodeck post.
- seo [low]: No internal links inline within the body.
- seo [low]: OG/Twitter title mismatch with the on-page title.
- seo [low]: Disclaimer-as-first-content reduces snippet quality.

### /2024/01/multihost-holodeck-vcf/
**Title:** VMware Holodeck Multi-Host VCF: Lab Setup Guide
**One-liner:** Solid, useful homelab post but missing meta description, canonical and Open Graph tags, plus a handful of small punctuation/spelling tidies.
- typo: "Tanzu vRA" → "Tanzu, vRA"
- typo: "adaptors" → "adapters"
- typo: "IP's" → "IPs"
- typo: "CPU's" → "CPUs"
- typo: "Intel CPU's" → "Intel CPUs"
- typo: "preexisting" → "pre-existing"
- cosmetic [low]: First image (Holodeck-Overview.png) missing `width`/`height` — CLS risk.
- cosmetic [low]: Specifications appear as bullet points rather than a table; "4–3.5TB SSD Disks" lacks a space.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [low]: Title (47 chars) slightly under sweet spot.
- seo [low]: Inconsistent case between H1 title-case and several H2s in sentence case.

### /2024/06/unifi-dhcp-option-43/
**Title:** UniFi DHCP Option 43: Adopt Devices Across Subnets
**One-liner:** Short, technically clear post but missing meta description, canonical, and Open Graph tags, with a few minor grammar/punctuation issues in the body.
- typo: "I discounted SSH as who wants to manually log into things and make changes and I discounted DNS." → rewrite for clarity.
- typo: "That left me with DHCP option 43" → add full stop; capitalise "Option".
- typo: "It is made up of 2 parts" → add full stop; spell out numerals under ten.
- typo: "The first two parts 01:04 is fixed for UniFi." → "…parts, 01:04, are fixed…"
- typo: "I am hosting the controller on IP 192.168.20.2 The remaining part" → add full stop.
- typo: "A multitude of tools exist for converting IP to HEX one can be found here" → rewrite with punctuation.
- typo: "I can connect a factory fresh UniFi device to my network DHCP will hand out an IP" → split into sentences; hyphenate "factory-fresh".
- cosmetic [medium]: Featured image alt "Ubiquiti Networks Logo.Wine" includes a stray `.Wine` filename fragment.
- cosmetic [medium]: Inline "here" link target appears to be missing from the LINKS dump.
- cosmetic [low]: Featured image missing `width`/`height`.
- cosmetic [low]: Bullet list of values (Code/Name/Type/Value) renders as loose paragraphs rather than a structured config block.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: H1 is 90 chars and reads like a sentence; duplicates info from `<title>`. → Shorten.
- seo [low]: Generic anchor "here" on the IP-to-hex converter link.
- seo [low]: Thin content (~426 words).
- seo [low]: No internal links to other UniFi/networking posts.
- seo [low]: "recently" no longer accurate two years on.

### /2024/07/new-nodes/
**Title:** New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix - James Kilby
**One-liner:** Solid, content-rich homelab post, but missing meta description, canonical, and Open Graph tags, and contains several real grammar/typo issues plus a couple of factual/consistency mistakes (IP table) that hurt clarity.
- typo: "Supermicro e200's" → "Supermicro e200s"
- typo: "what I bought why and how" → add commas.
- typo: "SATADom's" → "SATADoms"
- typo: "SSD's" → "SSDs"
- typo: "had I chose to deploy" → "had I chosen to deploy"
- typo: "run it in a production" → "in production"
- typo: "CVM's" → "CVMs"
- typo: "Ip address's" → "IP addresses"
- typo: "IP address's in advance" → "IP addresses in advance"
- typo: "password's" → "passwords"
- typo: "The IPMI in the nodes were" → "…was" _(singular)_
- typo: "Cluster succeed in creating" → "A cluster that succeeded in being created"
- cosmetic [high]: IP-address table inconsistency — NODE C ESX MANAGEMENT is listed as `192.168.38.174`, duplicating NODE B's CVM IP; later cluster-create command uses `.175`.
- cosmetic [medium]: Featured image (IMG_6629-scaled.jpeg) has no alt text.
- cosmetic [medium]: Filename-only alts on multiple images (`IMG 6628 1`, `mimetype`, `Screenshot 2024 04 05 at 13.21.24`).
- cosmetic [low]: Three different images share the alt "New Nodes Screenshot".
- cosmetic [low]: Bill of Materials line "2TB Samsung EVO Consumer SATA SSD" annotated "Not included in total cost" but shows a 900.00 line total — misleading.
- cosmetic [low]: H3 "Distributed Switch" is a stub with one sentence.
- cosmetic [low]: Stray inline notes ("Successful Install", "Some of the configuration taking place") read as missing image captions.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title is 73 chars including suffix — over the 60-char limit.
- seo [medium]: Multiple weak/duplicated image alts.
- seo [low]: Generic anchors ("Paul", "changes").
- seo [low]: Related-posts widget links forward to future-dated 2026 posts — verify resolution.
- seo [low]: Promised follow-up (Prism Central / CVM RAM) is not linked.
- seo [low]: Updated 2026 date with no visible new content.

### /2024/09/can-you-really-squeeze-96tb-in-1u/
**Title:** Can you really squeeze 96TB in 1U ? - James Kilby
**One-liner:** Solid technical post with clear structure, but missing meta description, canonical and Open Graph tags, plus a couple of minor wording slips and an unaltted image.
- typo: "using second hard storage" → "second-hand storage"
- typo: "Memory: 256 DDR4" → "256GB DDR4" _(missing unit)_
- cosmetic [medium]: Content image `s-l1600-1` missing alt text.
- cosmetic [low]: Two images share generic alt "Can you really squeeze 96TB in 1U ? Screenshot".
- cosmetic [low]: H2 "Upgrades:" has a stray trailing colon.
- cosmetic [low]: Stray space inside `( Pink)`.
- cosmetic [low]: Performance section ends without terminal punctuation.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [low]: Title light on keywords (Quanta D51PH-1ULH, TrueNAS).
- seo [low]: Heading skip — "Table of Contents" inflates the outline.
- seo [low]: External Quanta link uses HTTP and a bare domain.
- seo [low]: Hero image lacks explicit dimensions.

### /2024/09/home-network-upgrade/
**Title:** Home Network Upgrade: 25Gb/s with MikroTik Switching
**One-liner:** Readable post with thin content and notable SEO gaps: meta description, canonical, and Open Graph tags all missing, and a promised "Part 2" follow-up appears overdue.
- typo: "webmanaged switch" → "web-managed switch"
- typo: "100GB/s switch" → "100Gb/s switch" _(bits vs bytes)_
- typo: "network adaptors" → "adapters" _(networking)_
- cosmetic [medium]: Switches Purchased table appears as pipe-delimited text in dump; verify it renders as an HTML table.
- cosmetic [low]: TOC heading exists but only one content H2.
- cosmetic [low]: Hero image alt "CRS-504" is terse; image missing `width`/`height` — CLS risk.
- cosmetic [low]: Inconsistent `Gb/s` vs `GB/s`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (~387 words).
- seo [medium]: Stale Part 2 promise.
- seo [low]: Heading hierarchy flat — no H3 subsections.
- seo [low]: Title omits "home network upgrade" keyphrase variants.
- seo [low]: Featured image alt is just the model name.
- seo [low]: Forward link to a 2026-04 post in a Sept 2024 article — verify intentional.

### /2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/
**Title:** Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU - James Kilby
**One-liner:** Solid technical content with a clear H1 and good internal linking, but the page is missing critical SEO meta tags (description, canonical, Open Graph) and has a few minor wording issues.
- typo: "running Ubuntu 24.04 VM" → drop duplicated "VM".
- typo: "how this much running chat queries may impact things" → drop "this".
- typo: "even if its not running any queries" → "it's"
- typo: "increases to around 24W this is probably due" → add punctuation between "24W" and "this".
- cosmetic [low]: Featured image (pexels-tara-winstead-8386440-scaled.jpg) has no alt text.
- cosmetic [low]: Multiple related-posts thumbnails have empty alts.
- cosmetic [low]: Four-dot ellipsis in body.
- cosmetic [low]: Code blocks render without language hints/copy buttons in plain text; verify in browser.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Generic/weak anchor text ("video", "guide", "Tim's"). → Use descriptive anchors.
- seo [medium]: Featured-image filename and alt are non-descriptive.
- seo [low]: Title is 67 chars including suffix.
- seo [low]: Heading hierarchy is uneven — three H3s under "Introduction" then no further H3s.
- seo [low]: No outbound links to Nvidia P4/Ubuntu/Nvidia Container Toolkit docs.
- seo [low]: Stale "early days" framing; add a 2025/2026 update.

### /2024/12/zfs-on-vmware/
**Title:** How to Run ZFS on VMware vSphere: Setup Guide and Best Practices - James Kilby
**One-liner:** Solid content with one duplicated phrase artifact and missing meta/OG/canonical SEO essentials.
- typo: "You also need to do is to to ensure" → "is to ensure"
- typo: "Sudo pool trim Pool-1" → "sudo zpool trim Pool-1" _(real command error)_
- typo: "the VMs's storage" → "the VM's storage"
- typo: "Before and after listed below command" → trailing stray word.
- typo: "You also need to do is to" → missing subject; rewrite as "What you also need to do is".
- cosmetic [high]: Duplicated phrase concatenated into a heading: "To confirm that To confirm that trim is working execute the below command command is working execute the below command command".
- cosmetic [medium]: TOC anchor leaks the duplicated phrase as a broken slug.
- cosmetic [medium]: TOC anchor labels are non-descriptive (`#w`, `#disk-i-ds`).
- cosmetic [medium]: Article ends abruptly mid-thought.
- cosmetic [low]: Featured image alt "Zfs" weak; no `width`/`height`.
- cosmetic [low]: Several content images missing dimensions.
- cosmetic [low]: Filename-derived image alts (`trimming 1`, `vm Before 2`, etc.).
- cosmetic [low]: Inconsistent ellipsis stylisation (`….` and `…..`).
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title is 79 chars including suffix.
- seo [medium]: Real command error in body (`Sudo pool trim Pool-1`).
- seo [medium]: Broken in-page anchor due to duplicated heading.
- seo [medium]: No internal links from body.
- seo [medium]: Article ends abruptly without conclusion.
- seo [low]: Flat heading hierarchy.
- seo [low]: Weak hero alt.

## 2023

### /2023/04/intel-optane/
**Title:** Using Intel Optane NVMe in a VMware Homelab: Setup & Results - James Kilby
**One-liner:** Short post with solid structure but missing meta description, canonical and Open Graph tags, plus a few grammar slips and weak image alt text.
- typo: "many many benefits" → drop duplicate.
- typo: "in particular some Optane drives" — phrase "in particular" used twice in one sentence; rewrite.
- typo: "Two that I have probably made the most use of is" → "are"
- typo: "I was lucky enough to get some together with Gareth Edwards we decided" → run-on; add punctuation.
- typo: "some back to back test" → "back-to-back tests"
- typo: "configure the Optane's as" → "Optanes"
- typo: "TrueNas Server" / "Truenas \"SAN\"" → "TrueNAS" _(consistency)_
- cosmetic [medium]: Both content images have weak filename-derived alts.
- cosmetic [low]: Content images missing `width`/`height`.
- cosmetic [medium]: Article ends abruptly with a specs table — promised "Results" missing.
- cosmetic [low]: Specifications appear as run-on text rather than a `<table>`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (~317 words); promised "Results" not delivered.
- seo [medium]: No H2/H3 inside article body.
- seo [medium]: Stale 2023 framing; no update note.
- seo [low]: Title is 70 chars including suffix.
- seo [low]: Light internal linking.

### /2023/05/homelab-storage-refresh-part-1/
**Title:** Homelab Storage Refresh (Part 1) - James Kilby
**One-liner:** Solid long-form post with strong internal links, but it has multiple grammar/wording issues and is missing core SEO metadata (meta description, canonical, Open Graph) plus has a heading-hierarchy issue.
- typo: "As my Z840 TrueNAS server has way more RAM and CPU capabilities." → sentence fragment; start with "My".
- typo: "This is a perfect drive for L2ARC as is a heavy read-focused NVMe" → "as it is"
- typo: "L2ARC stands for L2ARC Cache." → "Level 2 Adaptive Replacement Cache".
- typo: "ARC, or Adaptive Read Cache," → "Adaptive Replacement Cache"
- typo: "before it's committed this leads to higher performance" → add punctuation.
- typo: "I'm sure there optimisations I can make" → "there are optimisations"
- typo: "before I do that but until that's done." → rewrite.
- typo: "When running VMs sync write is basically essential." → add comma.
- typo: "So let's start with the definition: A synchronous write" → "a synchronous write"
- cosmetic [high]: Duplicated phrase artifact in body around the trim section.
- cosmetic [medium]: Disk architecture table rendered as pipe-delimited plain text.
- cosmetic [medium]: "L2ARC Configuration" and "ZIL Config" appear as bold body text rather than proper H3 headings.
- cosmetic [low]: Inconsistent casing TrueNAS/TrueNas/Truenas.
- cosmetic [low]: Filename-derived image alts (`IMG 0397`, `Screenshot 2023 05 19 at 10.54.27`).
- cosmetic [low]: VDEV roles list rendered as plain text not `<ul>`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title is 47 chars and omits TrueNAS/ZFS/Synology keywords.
- seo [medium]: Heading hierarchy skips ("L2ARC Configuration", "ZIL Config" not real headings).
- seo [medium]: Dangling Part 2 promise with no link.
- seo [low]: Duplicate "Homelab" anchor across related-posts block.
- seo [low]: Hero image lacks dimensions.
- seo [low]: External `rel` attribution unclear.

### /2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/
**Title:** WordPress Hosting with Cloudflare Pages - James Kilby
**One-liner:** Solid technical post but missing meta description, canonical, and Open Graph tags, with several grammar slips and image alt-text gaps.
- typo: "Cloudflare has been improving there capabilities" → "their"
- typo: "their worker's product" → "their Workers product"
- typo: "their datacenter's" → "datacentres"
- typo: "use relative URL's" → "URLs"
- typo: "navigate to the settings section ensure that" → add "and".
- typo: "( Or installed" → drop stray space and lowercase.
- typo: "following this link" → add full stop.
- typo: `production branch to be "Main" You can then` → add full stop.
- typo: "initialize the build environment clone the Git repository" → add comma.
- typo: "If you click the name of the project, In my case" → lowercase "in".
- typo: "In my case WordPress you can then scroll" → add comma after "WordPress".
- typo: "the domain is also managed by Cloudflare so this is a trivial step" → add full stop.
- cosmetic [high]: Multiple content images missing alt text.
- cosmetic [medium]: Several content images missing `width`/`height` — CLS risk.
- cosmetic [low]: Sentence ends with no terminator before next paragraph.
- cosmetic [low]: Run-on around `"Main" You can then leave`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Multiple content images lack alt attributes.
- seo [medium]: Title light on keywords. → "How to Host a WordPress Site as a Static Site on Cloudflare Pages".
- seo [medium]: Generic anchor "following this link".
- seo [medium]: Stale "2 years ago" with Updated 2026.
- seo [medium]: No inline internal link to the 2025 follow-up post.
- seo [low]: Heading hierarchy skip — "Cloudflare setup" H2 next to sibling H3s.

### /2023/05/runecast-remediation-scripts/
**Title:** Runecast Remediation Scripts: Auto-Fix VMware Storage Issues - James Kilby
**One-liner:** Useful short technical post, but it is missing meta description, canonical and Open Graph tags, has only a flat heading structure, and shows signs that intended inline screenshots are not rendering.
- typo: "data stores" → "datastores"
- typo: "Dropping this into a PowerCLI session we get…." → three dots.
- cosmetic [medium]: Body references screenshots ("It gave a great overview of what that issue means:", "If I drill into the specific issue…", "The below code is what Runecast generated for me.") but only one screenshot appears.
- cosmetic [low]: First image (Runecast Solutions Ltd logo) missing `width`/`height`.
- cosmetic [low]: Similar Posts image missing dimensions.
- cosmetic [low]: Unbalanced quote in code/output block.
- cosmetic [low]: Stray parenthesis spacing `( I have chosen not to enable SIOC on my ISO-NFS datastore)`.
- cosmetic [low]: Final sentence "What an amazing little feature" missing full stop.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Title is 72 chars — over ideal.
- seo [medium]: Heading hierarchy flat — no in-body H2/H3.
- seo [low]: Thin word count (~440) for an evergreen technical post.
- seo [low]: No outbound link to runecast.com.
- seo [low]: No inline internal links.
- seo [low]: Featured-image alt could be "Runecast Solutions logo".
- seo [low]: Second screenshot alt has apostrophe-S where plural intended.

### /2023/10/going-out-with-a-bang/
**Title:** VMware - Going out with a Bang! - James Kilby
**One-liner:** Thin, dated post (156 words) missing meta description, canonical, and Open Graph tags, with a redundant currency phrase and no internal links within the body copy.
- typo: "$1300 dollars" → "$1300" or "1300 dollars" _(redundant)_
- cosmetic [low]: Featured/inline image alt duplicates the post title rather than describing the image.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (~156 words).
- seo [medium]: No internal links from body copy.
- seo [medium]: Outdated content — Broadcom acquisition referenced as "pending" (now complete).
- seo [low]: Title duplicates brand suffix; could surface "VMware EPIC day" or "RNLI donation".
- seo [low]: Only one substantive H2 ("Related Posts").

### /2023/10/vgpu-setup-in-my-homelab/
**Title:** Nvidia Tesla P4 vGPU on VMware ESXi: Homelab Guide
**One-liner:** Solid technical content but missing meta description, canonical, and Open Graph tags; a few minor grammar/punctuation issues and two images without alt text.
- typo: "2xGb Nic's" → "2x Gb NICs"
- typo: "gFX cards" → "vGPU/graphics cards"
- typo: "isn't )" → `isn't).`
- typo: "as a Tdarr Node" → "Tdarr node."
- typo: "in windows" → "Windows"
- typo: "perform the install" → add full stop.
- typo: "list the capabilities of each profile I have copied" → split into two sentences.
- typo: "how are you going to use the card?" → "how you are going to use the card?"
- typo: "as well" → add full stop.
- cosmetic [medium]: Two content images missing alt text (IMG_1107 hero and Screenshot-2023-10-23-at-15.24.54).
- cosmetic [low]: Five screenshots share generic alt "Nvidia Tesla P4 Homelab Setup Screenshot".
- cosmetic [low]: vGPU profiles table renders as pipe-separated rows in plain text.
- cosmetic [low]: Card Stats data block appears as space-separated text rather than a structured table.
- cosmetic [low]: Stray whitespace `(even if it says it isn't )`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Empty alts on hero/PCI screenshot; five duplicate generic alts.
- seo [medium]: No internal links to related posts.
- seo [low]: Generic anchor "here" for Folding@home donor stats.
- seo [low]: Title (49 chars) could include "Setup" and ESXi version.
- seo [low]: 2023 framing without freshness note.

### /2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/
**Title:** (missing)
**One-liner:** Thin post (~134 words) with missing title/meta/canonical/OG tags and no alt text on related-post thumbnails; body is otherwise clean.
- typo: "VMware give me" → "gives"
- typo: "deal. I had some downtime" → comma instead of full stop.
- cosmetic [medium]: 7 related-post thumbnails have no alt text.
- cosmetic [low]: Inline body image `/wp-content/uploads/2023/11/image.png` has no alt text.
- seo [high]: `<title>` missing.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Thin content (~134 words).
- seo [medium]: No internal links inline.
- seo [medium]: "current pause in the Broadcom VMware takeover deal" — now stale.
- seo [medium]: Body never restates exam keyword (3V0-22.21N, VCAP-DCV Deploy) after H1.
- seo [low]: External "blueprint" link uses a single-word anchor.

### /2023/11/analytics-in-a-privacy-focused-world/
**Title:** (missing)
**One-liner:** Short but readable post; the WebFetch dump shows missing title/meta/canonical/OG tags and weak anchor text ("here"), plus thin content for SEO.
- typo: "approx 30 mins to setup" → "approximately 30 minutes to set up"
- typo: "self hosted version" → "self-hosted"
- cosmetic [low]: Generic link text "This can be seen here."
- seo [high]: `<title>` reported missing.
- seo [high]: Meta description reported missing.
- seo [high]: `rel=canonical` reported missing.
- seo [high]: Open Graph tags reported missing.
- seo [medium]: Thin content (~254 words).
- seo [medium]: Generic "here" anchor on the public-stats link.
- seo [medium]: No inline internal links.
- seo [low]: Heading "Update:" has trailing colon.
- seo [low]: Stale framing; no current update note.

### /2023/11/configuring-a-zen-internet-and-city-fibre-connection-with-a-3rd-party-router/
**Title:** Configuring a Zen Internet and City Fibre connection with a 3rd party router - James Kilby
**One-liner:** Page loads cleanly with full canonical and OG tags, but the title is too long, the meta description is a stale autogenerated first-sentence snippet, the body lacks internal headings and inbound links, and several screenshots share identical non-descriptive alt text.
- typo: "6 usable IP's" → "IPs"
- typo: "as /32's" → "/32s"
- cosmetic [medium]: Five screenshots share the identical alt "Configuring a Zen Internet and City Fibre connection with a 3rd party router Screenshot".
- cosmetic [low]: No internal subheadings — only template H2s.
- seo [high]: Meta description is just the first sentence of the post and doesn't describe the actual setup (CityFibre/Zen/WatchGuard VLAN 911 + /29). → Rewrite.
- seo [medium]: Title tag is 90 chars — likely truncated in SERPs.
- seo [medium]: Body lacks H2/H3 subheadings.
- seo [medium]: No internal links inline.
- seo [low]: Thin content for a technical how-to (316 words).
- seo [low]: "Back in July I bought a new house" is now ~3 years stale.
- seo [low]: "City Fibre" should be "CityFibre" (brand styling).

### /2023/11/truenas-scale-useful-commands/
**Title:** TrueNAS Scale CLI Reference: Storage & Kubernetes Commands - James Kilby
**One-liner:** Useful reference post that is functional but thin (221 words) and missing core SEO metadata — no meta description, no canonical, and no Open Graph tags.
- typo: "the GUI is very good occasionally I need to jump" → add comma.
- typo: "$Poolname" → "$PoolName" _(inconsistent with earlier `$PoolName`)_
- typo: "Get ZFS Compression ratio" → "Get ZFS compression ratio" _(case)_
- cosmetic [low]: Duplicate command listing — "Get ZFS Compression ratio" repeats "Get the compression ratio of each Pool".
- cosmetic [low]: TrueNAS logo image appears twice at different sizes.
- cosmetic [low]: Images lack explicit `width`/`height`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (221 words) despite "Updated April 2026" stamp.
- seo [medium]: Promise "I will update this page with anything else I find useful" is stale relative to content.
- seo [medium]: No inline internal links.
- seo [low]: Title is 67 chars.
- seo [low]: Section heading "Application" vague.
- seo [low]: Image alt "TrueNAS Logo" duplicated.

### /2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/
**Title:** vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24 - James Kilby
**One-liner:** Solid technical post with sound structure, but it is missing meta description, canonical and Open Graph tags, all eight content images lack alt text, and a couple of small wording errors.
- typo: "until now…. With" → three dots, full stop.
- typo: "to answer that we need" → capitalise "To".
- typo: "compression ratio of 1.25%" → "1.25x" _(ratio, not percentage)_
- typo: "less rewrites" → "fewer rewrites"
- typo: "the 4 and 5 node has" → "rows have"
- cosmetic [high]: All 8 images have empty/missing alt attributes (architecture diagrams, sizing image).
- cosmetic [low]: Sizing table appears as plain-text pipe block — confirm it renders as `<table>`.
- cosmetic [low]: Filename typo "OrigionalPoweredByvSAN" (should be "Original").
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: All content images have no alt text.
- seo [medium]: Stale "Explore last year (2022)" framing.
- seo [medium]: Availability claim about i4.metal launch likely outdated.
- seo [low]: Title is 62 chars — slightly over.
- seo [low]: Theme chrome emitted as H2 inside article.
- seo [low]: Generic anchor "official overview".
- seo [medium]: No inline contextual internal links (e.g. to the i7i.metal-24xl or time-sync posts).

## 2022

### /2022/01/cloudflare-workers-limits-of-the-free-tier/
**Title:** Cloudflare Workers - Limits of the free tier - James Kilby
**One-liner:** Short, readable post but missing meta description / canonical / Open Graph tags and has a couple of small grammar slips that hurt polish and SEO.
- typo: "(mainly cosmetic to this site over the last day or so)" → close parenthetical and add full stop.
- typo: "or so) On most changes" → add full stop.
- typo: "When I next tried to publish I got the following" → add colon.
- typo: "Detailed info on the limits is published here." → "…published by Cloudflare."
- cosmetic [medium]: Featured/inline image has generic alt "Iu".
- cosmetic [medium]: Unbalanced parenthetical/run-on at top of post.
- cosmetic [low]: Trailing sentence ends with link text "here".
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Generic "here" anchor for the only authoritative outbound link.
- seo [medium]: Thin content (268 words).
- seo [medium]: Stale 2022 pricing/limit numbers.
- seo [medium]: Featured image alt non-descriptive.
- seo [medium]: No internal links from body.
- seo [low]: H2 sections begin with emoji.
- seo [low]: Title could tighten the primary keyword.
- seo [low]: Image `width`/`height` not detected.

### /2022/01/lab-update-part-1-compute/
**Title:** Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup - James Kilby
**One-liner:** Short 223-word post with solid internal linking but missing meta description, canonical and Open Graph tags, and most content images lack alt text.
- typo: "lab recently. so I decided" → comma.
- typo: "2.60GHz 3 Nodes" → add full stop after GHz.
- cosmetic [medium]: Featured image missing alt text.
- cosmetic [medium]: Multiple content images missing alt text (BigTwin photo, vSAN logo, etc.).
- cosmetic [medium]: Truncated alt "Wa" on a content image.
- cosmetic [low]: Orphan caption-style line "One of the Compute nodes was removed from the server".
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (223 words).
- seo [medium]: No body H2/H3 sections.
- seo [medium]: Content images lack alt text.
- seo [low]: Title is 65 chars including suffix.
- seo [low]: Outdated "coming soon" framing for follow-ups.

### /2022/01/lab-update-part-2-storage/
**Title:** Lab Update - Part 2 Storage Truenas Scale - James Kilby
**One-liner:** Short, readable post but missing meta description, canonical, and Open Graph tags, plus a few small typos and missing alt text on most content images.
- typo: "2.5 drive bays" → `2.5"` drive bays.
- typo: "Crystel Disk Mark" → "CrystalDiskMark"
- typo: "Raid5" → "RAID 5"
- typo: "ZLOG" → "ZIL/SLOG"
- typo: "SSD's" → "SSDs"
- typo: "VM's" → "VMs"
- typo: "FreeNas"/"TrueNas"/"Truenas" → "FreeNAS"/"TrueNAS"
- cosmetic [high]: 8 of 12 `<img>` tags have no alt attribute.
- cosmetic [medium]: Image captions appear as orphan paragraphs rather than `<figcaption>`.
- cosmetic [low]: Sentence ends without period after "iSCSI/NFS".
- cosmetic [low]: First paragraph missing closing full stop after "Synology DS918+".
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Heading hierarchy thin.
- seo [medium]: No inline internal links.
- seo [low]: Title casing inconsistency ("Truenas").
- seo [low]: Thin content (~495 words).
- seo [low]: H1 uses en dash, title uses hyphen.
- seo [low]: Promise of follow-up storage testing not delivered.

### /2022/01/lab-update-part-3-network/
**Title:** Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense - James Kilby
**One-liner:** Very thin post (129 words) missing meta description, canonical, and Open Graph tags — needs expansion and SEO metadata.
- typo: "DAC's" → "DACs"
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Thin content (~129 words).
- seo [medium]: No H2/H3 inside article body.
- seo [medium]: No inline internal links to other Lab Update parts or the later 25Gb/s post.
- seo [medium]: Stale content — 25Gb/s switch follow-up isn't linked.
- seo [low]: Title is 62 chars.
- seo [low]: Content images lack intrinsic `width`/`height`.

### /2022/01/lab-update-part-5-desired-workloads/
**Title:** Lab Update - Desired Workloads - James Kilby
**One-liner:** Reachable with valid metadata, but content is very thin (~139 words), the intro has a fragment/run-on, and list formatting (" – Done" vs "-Done") is inconsistent.
- typo: "break things (not always by accident) sometimes it's a great way to learn" → use semicolon.
- typo: "Partially as I want to try new things" → "Partly because"
- typo: "learn…." → three dots.
- typo: "I decided to list the workloads I am looking to run (some of these are already in place)" → add full stop.
- cosmetic [low]: Inconsistent list formatting (` – Done` vs `-Done` vs ` -Done`).
- cosmetic [medium]: Workload lists rendered as plain paragraphs rather than `<ul>`.
- cosmetic [low]: Section labels strong but content underneath thin.
- seo [high]: Thin content (~139 words).
- seo [high]: Meta description is the first sentence and is truncated.
- seo [medium]: Title omits "homelab" used in sibling-post titles.
- seo [medium]: `og:title` / `twitter:title` don't match `<title>`/H1.
- seo [medium]: `og:description` is generic marketing fluff.
- seo [medium]: No internal links to other Lab Update parts in body.
- seo [medium]: Updated April 2026 with stale content; no status note.
- seo [low]: Workload names with their own posts (Nutanix CE, TrueNAS, Veeam) are plain text.

### /2022/01/web-development/
**Title:** Hosting This Blog on Cloudflare Workers: Why & How I Did It - James Kilby
**One-liner:** A thin (~211 word) 2022 post that's now technically outdated, has no meta description / canonical / OG tags, and uses unhelpful image alt text — primarily an SEO-metadata and content-freshness problem.
- cosmetic [low]: Featured image alt "Iu 2" — meaningless filename string.
- cosmetic [low]: Related-posts thumbnail uses unrelated alt (RNLI image labelled "VMware – Going out with a Bang!").
- cosmetic [low]: Stray sentence "The speed report looks good" with no terminal punctuation.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Outdated content — describes Cloudflare Workers + Simply Static, but site is now Pages + GitHub Actions. Add a prominent "see current setup" note.
- seo [medium]: Thin content (~211 words).
- seo [medium]: Heading hierarchy very shallow.
- seo [low]: Generic anchor "Check it out".
- seo [low]: Featured image alt unhelpful.
- seo [low]: Title is 68 chars including suffix.
- seo [low]: Generic slug `/web-development/`.

### /2022/01/wrangler-and-node-versions/
**Title:** Fixing Wrangler Node.js Version Conflicts After Brew Upgrade - James Kilby
**One-liner:** Short, useful post but missing meta description, canonical, and Open Graph tags; also contains a couple of small grammar issues and a typo in a code snippet.
- typo: "all of my Mac's I typically just upgrade everything blindly" → "Macs."
- typo: "….. Until today…" → standard ellipsis.
- typo: "rangler publish --env production" → "wrangler publish…" _(missing leading w)_
- cosmetic [low]: Featured image missing `width`/`height`.
- cosmetic [low]: Related-post thumbnails missing dimensions.
- cosmetic [low]: Featured image alt "Wranglercrab 1" is filename-derived.
- cosmetic [low]: brew search output may not preserve `<pre>` formatting.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (~374 words).
- seo [medium]: Outdated — Node 16 and Wrangler 1.19.6 EOL by 2026.
- seo [medium]: Title is 71 chars.
- seo [low]: Related Posts emit duplicate anchors per card.

### /2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/
**Title:** Static Wordpress hosting using Cloudflare - James Kilby
**One-liner:** Solid evergreen post but missing meta description / canonical / Open Graph, has a couple of small grammar slips, and the title uses "Wordpress" casing inconsistency.
- typo: "worker's product" → "workers product"
- typo: "the benefits It brought" → lowercase "it".
- typo: "using local." → close the parenthetical.
- typo: "relative URL's" / "WordPress management URL's" → "URLs"
- typo: "The page's site needs" → "The Pages site needs"
- typo: "When a page is complete and published at a WordPress level a new button" → add comma.
- typo: "Page Builds" → "Pages Builds" _(Cloudflare Pages)_
- cosmetic [medium]: Unclosed parenthesis in intro.
- cosmetic [medium]: Featured image alt is just "Iu".
- cosmetic [low]: Title casing inconsistent (`Wordpress` vs `WordPress`).
- cosmetic [low]: Two content images share identical alt.
- cosmetic [low]: Byline shows two dates jammed together with no separator.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: `<title>` says "Wordpress" (lowercase p).
- seo [medium]: Hero image alt non-descriptive.
- seo [medium]: Stale 2022-era Cloudflare free-tier numbers in body.
- seo [low]: Slug vs title angle mismatch.
- seo [low]: Two screenshots share generic alts.
- seo [low]: Outdated "follow me on Twitter" CTA.
- seo [low]: No body internal link back to predecessor `/2022/01/web-development/`.

### /2022/10/starlink/
**Title:** Starlink Satellite Internet Review: Rural Broadband Solution - James Kilby
**One-liner:** Solid content but the page is missing critical SEO metadata (meta description, canonical, Open Graph) and a couple of content images lack alt text.
- typo: "Once all the above had been done. It was a case of connecting Starlink" → comma instead of full stop.
- typo: "While waiting on the adaptor I decided to do some speed tests over Wifi from my iPhone 13 Pro" → add terminal full stop.
- typo: "(as the device is locked down by VMware Corporate IT)" → add full stop after the parenthetical.
- cosmetic [medium]: Featured/hero image has no alt text.
- cosmetic [medium]: Two iPhone screenshots have no alt text.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Heading hierarchy very thin — no in-body H2s.
- seo [medium]: Stale "Since moving to Dorset last year" framing.
- seo [medium]: No body internal links to related posts.
- seo [medium]: Featured image alt missing.
- seo [low]: Title is 71 chars.

### /2022/11/homelab-bad-days-almost/
**Title:** Homelab SSD Failure: How Synology RAID Saved My Data - James Kilby
**One-liner:** Short post with a few grammar slips, missing meta description / canonical / Open Graph tags, and only two H2s within the article body — overall thin but functional.
- typo: "I have advocating never using RAID 5" → "advocated"
- typo: "your wallet is in the line" → "on the line"
- typo: "VMUG's" → "VMUGs"
- typo: "SDD's" → "SSDs"
- typo: "the Samsung 870 QVO's" → "QVOs"
- typo: "They are def on the budget end" → "definitely"
- typo: "4x Disk" → "4x disks"
- typo: "right? )" → close space.
- cosmetic [medium]: Filename-derived image alts ("Brokenharddive 1200X630 1", "Drive Errors 2048x236").
- cosmetic [medium]: Two screenshots share generic alt "Homelab bad days (almost) Screenshot".
- cosmetic [low]: Stray unclosed parenthesis in caption-like line.
- cosmetic [low]: Trailing four/five-dot ellipses.
- cosmetic [low]: No real H2/H3 subheadings in body.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (~363 words).
- seo [medium]: Filename-derived alts.
- seo [medium]: No inline internal links in body.
- seo [low]: Featured image lacks intrinsic dimensions.
- seo [low]: Brand/model keywords (DS918+) appear only once.
- seo [low]: Stale "recently spent 3 weeks in Ireland" temporal phrasing.

### /2022/12/100gb-s-in-my-homelab-sort-of/
**Title:** MikroTik CRS504 Review: 100Gb/s Networking in My Homelab - James Kilby
**One-liner:** Thin 276-word review post with notable missing SEO metadata and a few small UK-English/punctuation fixes; content is also stale (promised follow-up never linked).
- typo: "DAC's" → "DACs"
- typo: "plus Vat" → "plus VAT"
- typo: "POE" → "PoE"
- typo: "the 100's on the switch" → "100s"
- typo: "16 usable 25 ports which are way more than I need" → "which is way more than I need"
- typo: "16 usable 25 ports" → "25Gb ports"
- typo: "2 AC supplies, A DC input" → lowercase "a"
- typo: "( It can be powered just from POE)" → drop stray space; PoE.
- cosmetic [low]: Stray whitespace inside parenthetical.
- cosmetic [low]: Mid-sentence ellipsis without clarity.
- seo [high]: Meta description missing.
- seo [high]: Open Graph tags missing.
- seo [high]: `rel=canonical` missing.
- seo [medium]: Thin content (~276 words).
- seo [medium]: Stale framing — promised follow-up never linked.
- seo [medium]: No in-body H2/H3.
- seo [medium]: No inline internal links to Intel Optane, TrueNAS, vSphere 8 posts.
- seo [low]: Title is 66 chars.
- seo [low]: Image alt "2157 Hi Res" weak.
- seo [low]: Featured image not referenced in body.

### /2022/12/forcing-an-upgrade-to-vsphere-8/
**Title:** (missing)
**One-liner:** Short, useful how-to post that's technically clean but missing core SEO metadata (title, meta description, canonical, Open Graph) and image alt text in the body.
- typo: "upgrade however a few personal things" → add commas.
- typo: "smooth however knowing" → use semicolon and comma.
- typo: "Therefore I resorted" → add comma.
- typo: "VIB's" → "VIBs"
- typo: "be ok" → "be OK"
- cosmetic [medium]: Content images have no alt text (vLCM error and install output screenshots).
- cosmetic [low]: Related Posts thumbnails lack alt text.
- cosmetic [low]: Bare "Host is not compatible" line reads like a leaked image caption.
- cosmetic [medium]: Long esxcli commands rendered as paragraph text, not `<pre>`/`<code>`.
- seo [high]: `<title>` missing.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: No inline internal links.
- seo [medium]: Content image alts missing.
- seo [low]: Thin content (343 words).
- seo [low]: Stale ESXi build referenced without update note.

### /2022/12/use-portainer-in-a-homelab-with-github/
**Title:** Use Portainer in a Homelab with GitHub - James Kilby
**One-liner:** Solid short tutorial, but missing meta description / canonical / Open Graph tags, has no alt text on any content images, and contains a couple of small grammar slips and a missing sentence-ending period.
- typo: "user and user id's" → "users and user IDs"
- typo: "Portainer It's also important" → add full stop.
- typo: "In this case /volume1/docker/grafana Therefore this folder must be created manually." → add commas/full stop.
- typo: "folder on my Synology" → add full stop.
- typo: "If for any reason this errors this is usually as the volume map is not set up correctly" → add comma; "because".
- cosmetic [high]: Every content image (10) is missing alt text.
- cosmetic [medium]: H2 "Post Tags:" leaks tag list as a heading with no separators.
- cosmetic [low]: Run-on text from missing sentence terminators.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Heading hierarchy — chrome blocks share H2 with article sections.
- seo [medium]: Generic "here" anchors on two important outbound links.
- seo [medium]: Thin content for the tutorial (~458 words).
- seo [medium]: Image alts missing across the board.
- seo [low]: Title length OK; could be more keyword-rich.
- seo [low]: Body links to private repo URL with no note about it being private.
- seo [low]: Lead image lacks dimensions.

## 2021

### /2021/01/hashicorp-packer/
**Title:** Template Deployment with Packer - James Kilby
**One-liner:** Thin post (~240 words) missing meta description, canonical, and Open Graph tags, with a heading hierarchy that jumps straight from H1 to H2 with no body subheadings; content otherwise reads cleanly.
- cosmetic [low]: Featured/logo image missing `width`/`height` (CLS).
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Anchor text "GitHub Repo" points to "(not specified in content)" — link appears broken.
- seo [medium]: Thin content (~241 words).
- seo [medium]: No H2/H3 inside article body.
- seo [medium]: Stale 2021 framing without an update note.
- seo [medium]: No inline contextual internal links.
- seo [low]: Title is 39 chars and omits "HashiCorp".
- seo [low]: Generic anchor "View Tweet".

### /2021/01/my-home-office-setup-upgrades/
**Title:** (missing)
**One-liner:** Content-rich post but the WebFetch dump reports missing title/meta/canonical/OG tags and several content images lack alt text; a few minor copy issues and outdated dates also present.
- typo: "I do everyday" → "every day"
- typo: "Cat 5e's" → "Cat 5e cables"
- typo: "Canon SLR's" → "Canon SLRs"
- typo: "Mac's" → "Macs"
- typo: "Beats Solo's" → "Beats Solos"
- typo: "USB-C This helps" → add full stop.
- typo: "stand but It took up" → lowercase "it".
- typo: "the best, It is" → split with full stop.
- typo: "audience see" → "sees"
- typo: "how It was put together" → lowercase "it".
- cosmetic [high]: Multiple content images have no alt text (only "Desk Setup" image has alt).
- cosmetic [medium]: Raw YouTube URL appears as bare text instead of embedded or linked.
- cosmetic [low]: Updated date inconsistent with body ("as of January 2021" vs Updated 2026).
- cosmetic [low]: Duplicate image source listed twice in markup.
- cosmetic [low]: Inconsistent product casing (Ipad, Macbook, Powerpoint, Wifi, Ram).
- seo [high]: `<title>` missing.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Heading hierarchy skip — "Future purchases" not a real heading.
- seo [medium]: Content image alts missing.
- seo [medium]: No internal links to homelab/Mac M1 follow-up posts.
- seo [low]: Stale forward-looking statements not followed up.
- seo [low]: Outbound product links use generic anchors; Amazon affiliate `rel` indication missing.
- seo [low]: Long opening paragraph; no TL;DR above BOM.

### /2021/02/apple-content-caching/
**Title:** How Apple Content Caching Works: Speed Up iOS & Mac Updates - James Kilby
**One-liner:** Solid evergreen post let down by missing meta description, canonical and Open Graph tags, thin word count, an overlong title, a useless "Iu" alt, and a handful of capitalisation/punctuation slips.
- typo: "Ipad Pro 9.7" → "iPad Pro 9.7"
- typo: "Ipad" → "iPad"
- typo: "iPhone Xs" → "iPhone XS" _(consistency)_
- typo: "apple devices" → "Apple devices"
- typo: "MacOS" → "macOS"
- typo: "Macbook Air 2018" → "MacBook Air 2018"
- typo: "on on my Mac M1" → drop duplicated "on".
- typo: "disk space to use it defaults to 10%" → use semicolon.
- typo: "found here" → add full stop.
- cosmetic [medium]: Image alt "Iu" meaningless.
- cosmetic [medium]: Hotlinked image from help.apple.com — fragile.
- cosmetic [low]: Four screenshots share identical generic alt.
- cosmetic [low]: Ellipsis rendered as four/five dots twice.
- cosmetic [low]: Run-on around "use it defaults to 10%".
- cosmetic [low]: Device lists rendered as plain paragraphs rather than `<ul>`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (~343 words) for a how-to.
- seo [medium]: Stale "last year" framing.
- seo [medium]: Title is 76 chars — over the SERP cap.
- seo [medium]: Generic "here" anchor for the only authority link.
- seo [medium]: Heading hierarchy absent inside the article.
- seo [low]: Lead image alt non-descriptive.
- seo [low]: No `<img>` `width`/`height`.
- seo [low]: Only three internal links, two pointing at the same post.

## 2020

### /2020/06/veeamon2020/
**Title:** VeeamON 2020: Highlights From Veeam's Virtual Conference - James Kilby
**One-liner:** Thin, mostly-clean post with a couple of grammar slips and a weak/auto-generated meta description; OG title/description diverge from the on-page title and the body lacks internal links.
- typo: "With that most (if not all IT conferences have been postponed or gone online)" → unbalanced parenthesis; rewrite.
- typo: "If you haven't managed to sign up you still can here." → rewrite with descriptive anchor.
- typo: "Covid19" → "COVID-19"
- typo: "Netapp" → "NetApp"
- typo: "MAC" → "Mac"
- typo: "Yes Veeam Backup Agent for MAC" → "Yes — Veeam Backup Agent for Mac."
- typo: "make sure you sign up and view some of the great sessions" → add full stop.
- cosmetic [medium]: Unbalanced parenthesis in body.
- cosmetic [medium]: Inconsistent bullet formatting under H3 ("Veeam Availability Suite v11") — mix of en dashes and hyphens.
- cosmetic [low]: Featured image alt is filename slug "Veeam Logo New Large 1934042827".
- cosmetic [high]: Related Posts H3 entries contain markdown link syntax leaking into the rendered heading (`[Homelab](/category/homelab/) | [Veeam](/category/veeam/)`).
- cosmetic [low]: Final sentence "Yes Veeam Backup Agent for MAC" has no terminal punctuation.
- cosmetic [low]: Empty utility H2 "Post Tags:" in outline.
- seo [high]: Meta description is auto-generated and off-topic (mentions Covid19/WFH, not VeeamON).
- seo [high]: `og:title` and `og:description` diverge significantly from on-page title and are AI-generated marketing copy.
- seo [medium]: Thin content (~312 words).
- seo [medium]: No internal links in body.
- seo [medium]: Generic "here" anchor.
- seo [medium]: Stale "now it's here!!" tense; "Office 365 v5" outdated.
- seo [low]: Title is 65 chars including suffix.
- seo [low]: Featured image alt filename-derived.
- seo [low]: Announcement list not marked as `<ul>`.

### /2020/07/i3en/
**Title:** VMware Cloud on AWS i3en Host: Specs, Storage & Performance - James Kilby
**One-liner:** Short, dated 2020 post that's structurally fine but is missing meta description, canonical, and Open Graph tags, and contains a few minor grammar slips and a stale pricing transition.
- typo: "to its lineup the \"i3en\"" → add colon.
- typo: "With such a big uplift in Storage capacity hopefully, this will trend towards" → rewrite.
- typo: "Broadwell's in the original i3" → "Broadwells"
- typo: "Intel AVX, Intel AVX2, Intel AVX-512" → add terminal full stop.
- typo: "they aren't supported in 2 node clusters" → "2-node clusters"
- typo: "this giving:" → add comma.
- typo: "VMware have now released pricing. The below is for On-Demand" → "VMware has now released pricing. The pricing below is for On-Demand…"
- cosmetic [medium]: Dangling/orphaned sentence "Assuming the VMware costs fall broadly in line with this giving:" followed by a contradiction.
- cosmetic [low]: Pricing block reads as run-on text rather than a table.
- cosmetic [low]: Featured/related image listed with no `width`/`height`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Heading hierarchy very thin — no body H2s.
- seo [medium]: Stale "At the time of writing pricing from VMware is not available".
- seo [medium]: `og:image` not surfaced.
- seo [low]: Title is 71 chars including suffix.
- seo [low]: Thin body content (~427 words).
- seo [medium]: No inline internal links to the newer i7i.metal-24xl post.

### /2020/07/nutanix-ncp/
**Title:** Passing the Nutanix NCP Exam: Free Training & My Experience - James Kilby
**One-liner:** Page loads cleanly with solid metadata, but the body contains a run-on sentence, a missing full stop at the end, and the related-posts cards show a literal "&#038;" entity instead of "&".
- typo: "the various sections this is a really useful piece of feedback" → add full stop.
- typo: "All in all top work Nutanix" → "All in all, top work Nutanix."
- cosmetic [medium]: Related-posts card titles render a literal `&#038;` (double-encoded `&`).
- cosmetic [low]: Featured image has no `width`/`height`.
- seo [medium]: Title is 77 chars — likely truncated.
- seo [medium]: Meta description is the literal first sentence; doesn't sell the click.
- seo [medium]: Thin content (~243 words).
- seo [medium]: No H2/H3 inside body.
- seo [medium]: Stale "free NCP exam" framing — offer almost certainly ended.
- seo [low]: Only one external link in body; no contextual internal links.

### /2020/09/vmc-host-errors/
**Title:** How VMware Cloud on AWS Handles Host Failures Automatically - James Kilby
**One-liner:** Reachable and clean structurally, but a very thin 161-word 2020 post with no meta description, no canonical, no Open Graph tags, an over-long title, and no in-body internal links — significant SEO upside.
- typo: "(These were cosmetic only)" → lowercase "these" inside; add full stop after parenthetical.
- typo: "Just another reason why you should look at the VMware Cloud on AWS Service" → add full stop; lowercase "service".
- typo: "Looking at the log extract above" → add comma.
- cosmetic [low]: Body references "the log extract above" but plain-text dump doesn't show a clearly captioned/inlined screenshot.
- cosmetic [low]: Final sentence missing terminal punctuation.
- cosmetic [low]: Parenthetical sentence starts with capital "These" mid-sentence.
- cosmetic [medium]: Content images missing `width`/`height` — CLS.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Thin content (~161 words).
- seo [medium]: Title is 70 chars.
- seo [medium]: Heading hierarchy very sparse.
- seo [medium]: No inline internal links.
- seo [low]: Generic alt "VMC Host Errors Screenshot" on main evidence image.
- seo [low]: Stale 2020 content without "last updated" note.
- seo [low]: Title contains "James Kilby" suffix that eats SERP space.

### /2020/09/vmware-certified-master-specialist-hci-2020/
**Title:** (missing)
**One-liner:** Thin post (~163 words) with a missing opening parenthesis in the first sentence, and the WebFetch returned no title/meta/canonical/OG — needs verification and likely SEO metadata fixes.
- typo: "I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.20)." → remove orphan `(`.
- typo: "a thought out learning path" → "thought-out"
- cosmetic [medium]: Unclosed opening parenthesis in the first sentence.
- cosmetic [low]: Featured image missing `width`/`height`.
- seo [high]: `<title>` appears missing.
- seo [high]: Meta description appears missing.
- seo [high]: `rel=canonical` appears missing.
- seo [high]: Open Graph tags appear missing.
- seo [medium]: Thin content (~163 words).
- seo [medium]: Image alt "Vmware Sp Hci20" is filename slug.
- seo [medium]: No inline internal links to related certification posts.
- seo [low]: "I recently sat…" with no temporal note for 2026 readers.
- seo [low]: No H2/H3 in body.
- seo [low]: No link to the 5V0-21.20 exam blueprint.

### /2020/12/my-first-pull/
**Title:** My First GitHub Pull Request: Contributing to Open Source - James Kilby
**One-liner:** Very thin post (~174 words) with missing meta description, canonical, and Open Graph tags, and all content images lack alt text — significant SEO gaps despite a good title and clear H1.
- typo: "errors and Improvements" → "improvements"
- cosmetic [high]: All 7 content images missing alt text.
- cosmetic [medium]: Body references "The above video" but no video/embed appears.
- cosmetic [low]: "listed as a contributor here" — relies on missing visual link context.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Thin content (~174 words).
- seo [low]: Title is 71 chars including suffix.
- seo [medium]: Generic anchor "here" for the GitHub contributors link.
- seo [medium]: No inline link to the related HashiCorp Packer post.
- seo [low]: Stale "I have worked in IT for over 10 years now" claim.

## 2019

### /2019/01/whats-in-my-backpack/
**Title:** (missing)
**One-liner:** Short, dated 2019 gear post with several grammar slips, missing alt on the lead image, and (per the fetcher) missing title/meta/canonical/OG signals worth verifying.
- typo: "A few components that I have no one seems to have mentioned yet." → rewrite.
- typo: "depending on if need to go to a datacenter" → "depending on whether I need to go to a datacenter"
- typo: "day to day" → "day-to-day"
- typo: "goto" → "go-to"
- typo: "Macbook" → "MacBook"
- typo: "Adaptor" → "Adapter"
- typo: "Headtorch" → "head torch"
- typo: "Led" → "LED"
- cosmetic [high]: Lead content image (Picture1.png) has no alt text.
- cosmetic [low]: Trailing six-dot ellipsis "Oh and a Tie……" reads as unfinished.
- cosmetic [low]: Stray space inside parentheses on multiple list items.
- cosmetic [low]: Non-standard double-prime/inch character inline (2.5″).
- seo [high]: WebFetch returned MISSING for `<title>`, meta description, canonical, and all OG tags. → Verify in rendered HTML and fix the template if absent.
- seo [medium]: Thin content (~263 words).
- seo [medium]: Stale references (ESXi 6.0/6.5/6.7, 2018 MacBook Air, Huawei 3G MiFi).
- seo [medium]: Only two internal links and they're in related/nav, not body.
- seo [low]: Generic anchor text on "Whiteboard"/"Flipchart".
- seo [medium]: H1 duplicated as the first H2.
- seo [medium]: No H2/H3 inside body.
- seo [medium]: Lead image has no alt text.
- seo [low]: Amazon affiliate links — `rel="sponsored nofollow"` not confirmed.
- seo [low]: URL slug "/whats-in-my-backpack/" doesn't match H1 phrasing ("Tech Bag").

### /2019/02/lab-storage-2/
**Title:** Homelab Storage Upgrade: Synology DS918 for VMware & NFS - James Kilby
**One-liner:** Thin 2019 post with solid title/H1 but missing meta description, canonical, and Open Graph tags, plus several content images without alt text.
- typo: "SSD's" → "SSDs"
- typo: "ISO's" → "ISOs"
- typo: "SSD's that I had giving me about 3TB" → add comma.
- typo: "Synology GUI ( It used to be a command-line-only option) I have verified" → rewrite with punctuation.
- typo: "purchased a new Synology DS918" → add full stop.
- cosmetic [low]: Stray period in H2 heading "Lab Storage Update.".
- cosmetic [low]: Post Tags rendered as single concatenated H2 (`#Homelab#Storage#Synology`).
- cosmetic [medium]: Lead/featured image (Synology DS918) has no alt text.
- cosmetic [low]: Stray space inside `( It used to be a command-line-only option)`.
- cosmetic [low]: Missing punctuation before paragraph break after "Synology DS918".
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (~207 words).
- seo [medium]: Featured image lacks alt.
- seo [medium]: Stale Updated 2026 stamp with unchanged 2019 body.
- seo [low]: URL slug `lab-storage-2` is generic.
- seo [low]: No body internal link to the later TrueNAS post.
- seo [low]: Title is 65 chars.

### /2019/12/aws-solution-architect-associate/
**Title:** AWS Solution Architect - Associate - James Kilby
**One-liner:** Page renders cleanly with valid head tags but is thin content with a truncated, auto-generated meta description, a non-descriptive alt on the lead image, and references that are now stale.
- cosmetic [low]: Lead image alt is the filename "Amazonwebservices Logo.Svg".
- seo [high]: Meta description is truncated mid-sentence at "I have been".
- seo [high]: Thin content (~180 words).
- seo [medium]: Stale content — "good for the next three years", "Professional level exam in the new year" no longer accurate.
- seo [medium]: `og:title`/`og:description` are generic marketing copy. → Override to match real post.
- seo [low]: H1 uses en dash; `<title>` uses hyphen.
- seo [low]: Only one inline internal link.

### /2019/12/monitoring-vmc-part-1/
**Title:** Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1) - James Kilby
**One-liner:** Solid short post but missing meta description, canonical, and Open Graph tags, with a stray/broken account name fragment in the body and weak alt text on key screenshots.
- typo: "All of the tests will be done with the [@vmc.local account." → `[` looks like a failed markdown link; should be `cloudadmin@vmc.local`.
- typo: "open up the relevant firewalls" → add full stop.
- typo: "ESXi 6.9.1" → likely 6.7; verify and correct.
- cosmetic [high]: Broken/stray text fragment `[@vmc.local` in body.
- cosmetic [low]: Sentence ends without a full stop before next paragraph.
- cosmetic [medium]: Auto-generated alt text on content screenshots ("Vmconaws.Png", "VMC Vms", filename screenshots).
- cosmetic [low]: Featured/related-post images lack `width`/`height`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: No internal link to Part 2 even though body teases it.
- seo [medium]: Body is thin (~520 words) and contains no inline internal links.
- seo [medium]: ESXi 6.9.1 reference factually suspect.
- seo [medium]: Featured/inline images lack descriptive alts.
- seo [low]: Title is 65 chars including suffix.

## 2018

### /2018/01/lab-storage/
**Title:** My First Homelab Storage Setup: HP Gen8 & Xpenology - James Kilby
**One-liner:** Short 2018 homelab post in reasonable shape, but lacks meta description, canonical, and Open Graph tags, has a few small grammar/punctuation issues, and is thin content under 300 words.
- typo: "for backups ISO's etc" → "for backups, ISOs, etc."
- typo: "my tier 2 lab storage. for backups" → "my tier 2 lab storage, for backups"
- typo: "The 2xWD Red's are in an SHR configuration" → "2x WD Reds"
- typo: "2x 2TB WD Red's" → "WD Reds"
- typo: "tidied up the lab/cables" → add full stop.
- cosmetic [low]: Related-post images missing `width`/`height`.
- cosmetic [low]: Author promises pics that never came.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (196 words).
- seo [medium]: Stale/outdated content with no "superseded by" notice.
- seo [low]: Title is 65 chars.
- seo [low]: Heading hierarchy — no body H2s.
- seo [low]: `#Homelab` and `#Storage` tag links use hash-prefixed anchor text.

### /2018/01/nutanix-ce/
**Title:** Running Nutanix CE at Home: AHV Setup & First Impressions - James Kilby
**One-liner:** Very thin post (190 words) with several grammar issues, a missing meta description, no canonical, and no Open Graph tags — multiple high-impact SEO gaps.
- typo: "see what was new with AHV and Nutanix CE\n\nI downloaded" → add full stop.
- typo: "The server that I chose to run this on was the same server I ran initially. a Dell T20" → use colon.
- typo: "the Xeon processor 32GB of RAM 1x240GB SSD and 1x3TB WD Red" → add commas.
- typo: "is pretty straightforward and covered a lot elsewhere" → rewrite.
- typo: "running a few VM's" → "VMs"
- typo: "Ill post back" → "I'll post back"
- typo: "Ill post back with some updates of what I get up to with it" → add full stop; "on what".
- cosmetic [low]: Hero/featured image missing `width`/`height` (CLS).
- cosmetic [medium]: Truncated/garbled alt text "Wa" on a Similar Posts thumbnail (Warp post).
- cosmetic [low]: Byline shows two dates as if both publication dates.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Thin content (190 words).
- seo [medium]: Stale "Ill post back" promise with no follow-up linked.
- seo [medium]: Heading hierarchy very sparse — no body H2/H3.
- seo [medium]: No inline internal links from body.
- seo [low]: Title is 70 chars including suffix.
- seo [low]: Trailing full stop inside `Rufus.` anchor.
- seo [low]: Similar Posts thumbnail alt "Wa" also an a11y/SEO miss.

### /2018/03/aws-for-beginners1/
**Title:** AWS For Beginners: IAM Setup, Root Security & Billing Alerts - James Kilby
**One-liner:** Thin 2018 AWS-basics post with solid title and H1 but missing meta description, canonical, and Open Graph tags, plus a few grammar/punctuation slips and stale 2FA claim only partially corrected by a one-line update.
- typo: `the cloud"\n\nMy view` → move period inside the closing quote.
- typo: "and play\n\nEnsure" → add full stop.
- typo: "AWS don't appear" → "doesn't" _(AWS is singular)_
- typo: "must, Sadly" → comma splice; use full stop.
- typo: "device. Yubikey so" → use commas around Yubikey.
- typo: "Enable Billing Alerts Create an alert" → add separator.
- typo: "billshock" → "bill shock"
- cosmetic [low]: Ellipsis rendered as four dots.
- cosmetic [medium]: Featured image has no alt text.
- cosmetic [low]: Inline AWS logo image used twice without alt.
- cosmetic [medium]: Third bullet lacks ` – ` separator used by the other two bullets.
- cosmetic [low]: "Wahoo." appended as stray sentence fragment.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Thin content (~219 words) for a tutorial-style post.
- seo [medium]: Featured/inline images missing alt text.
- seo [medium]: Stale 2FA claim only partially corrected.
- seo [medium]: Title is 75 chars.
- seo [medium]: No inline internal links.
- seo [low]: Updated 2026 stamp without visible body changes.

### /2018/03/cloudflare/
**Title:** What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained - James Kilby
**One-liner:** Short but readable post; main issues are missing meta description/canonical/Open Graph, a couple of minor grammar slips, and a US spelling ("organizations") in an otherwise UK-English site.
- typo: "sites/ organizations" → "organisations"
- typo: "POP's" → "POPs"
- typo: "2 A records Neither of which" → add comma.
- typo: "webserver lives cloudflare will do the rest" → "Cloudflare" and add comma.
- typo: "if required" → add full stop.
- cosmetic [low]: First content image has alt "Iu 2".
- cosmetic [low]: Several related-posts area images have no alt.
- cosmetic [low]: Lead image missing `width`/`height`.
- cosmetic [medium]: Body refers to screenshots that don't appear in the article body.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: Thin content (~288 words).
- seo [medium]: Stale claim "139 sites globally".
- seo [low]: "My blog is still a little bit light on readership" on a 2026-updated post reads oddly.
- seo [low]: Heading hierarchy flat.
- seo [low]: Generic anchor "139 sites".
- seo [low]: Title is 78 chars.

### /2018/05/aws-status-page-monitoring-included/
**Title:** AWS Status Page - Monitoring Included - James Kilby
**One-liner:** Very thin 2018 post (about 105 body words) missing meta description, canonical, and Open Graph tags, with generic "here" anchor text and no descriptive internal links to other AWS posts.
- typo: "at effectively zero cost" → add full stop.
- typo: "documented in the Git repo here" → add full stop.
- cosmetic [medium]: H2 "Site Response" has no content underneath.
- cosmetic [low]: Lead image alt "Amazonwebservices Logo.Svg" filename-derived.
- cosmetic [medium]: Inline screenshot alt "Screen Shot 2018 05 15 at 22.39.01" raw filename.
- cosmetic [low]: Updated April 2026 stamp with no substantive new content.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Thin content (~105 words).
- seo [medium]: Generic "here" anchors used twice.
- seo [medium]: Empty "Site Response" H2.
- seo [medium]: Outbound CloudFront-hosted status-page link likely stale/broken.
- seo [medium]: No body internal links to related AWS posts.
- seo [low]: Title uses hyphen vs H1 en dash; lacks year/specificity.
- seo [low]: Stale dated content with no freshness note.

### /2018/06/nutanix-command-reference-guide/
**Title:** Nutanix Command Reference Guide - James Kilby
**One-liner:** Thin 97-word reference post missing meta description, canonical, and Open Graph tags, with a heading-hierarchy skip and minor formatting inconsistencies in the command list.
- cosmetic [low]: Inconsistent punctuation in inline command annotations — parentheses vs no delimiter vs stray full stop (`. Find the leader`).
- cosmetic [medium]: Command lines render as plain paragraphs rather than `<pre>`/`<code>`.
- cosmetic [low]: Heading hierarchy jumps H2 → H4.
- cosmetic [low]: Featured/hero image missing `width`/`height`.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Very thin content (~97 words).
- seo [medium]: H2 → H4 heading skip.
- seo [medium]: 2018 post with no visible "last updated" marker — stale.
- seo [medium]: No body internal links to related Nutanix posts.
- seo [low]: Title could include "cheat sheet".
- seo [low]: Featured image alt is raw filename.

### /2018/10/and-now-for-something-completely-different/
**Title:** (missing)
**One-liner:** Short personal post with thin content, missing title/meta/canonical/OG tags, a featured image lacking alt text, and a few small grammar/punctuation issues.
- typo: "I have been lucky enough to be involved with all of these ( some much more than others) Although the work is never complete Zen are in a good place." → rewrite with full stops and tighter parens.
- typo: "one or two others….." → three dots.
- typo: "professional services in 2018" → add full stop.
- typo: "utilize" → "utilise"
- cosmetic [medium]: Featured image has no alt text.
- cosmetic [low]: Date line shows two dates concatenated: `October 16, 2018April 16, 2026`.
- cosmetic [low]: Stray space inside parenthesis `( some much more than others)`.
- seo [high]: `<title>` missing.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [medium]: H1/title vague — no target keywords.
- seo [medium]: Thin content (~297 words).
- seo [medium]: No inline internal links.
- seo [low]: External anchors aren't keyword-aligned with the topic.
- seo [low]: Modified date 2026-04-16 with no "updated" note.

### /2018/12/new-laptop/
**Title:** MacBook Air 2018 Retina Review: My Setup & Build Scripts - James Kilby
**One-liner:** Thin, dated 2018 post missing meta description, canonical, and Open Graph tags, with no build-scripts content actually visible despite the title promising it.
- typo: "MacBook Pro's weren't worth it" → "MacBook Pros"
- typo: "T2 Security chip" → add full stop.
- cosmetic [high]: Body promises build scripts ("They are available below") but no scripts/code block/download link appears.
- cosmetic [low]: Image `colorware.jpg` missing `width`/`height`.
- cosmetic [medium]: Thin article body (~166 words) for a "Review".
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Thin content (~166 words).
- seo [medium]: URL slug `/new-laptop/` shares no keywords with the title.
- seo [medium]: Heading hierarchy sparse — no content H2/H3.
- seo [medium]: Stale 2018 content with no update note.
- seo [low]: Title is 67 chars.
- seo [medium]: No inline internal links to other Apple posts.
- seo [low]: Nav "Home" link uses absolute URL while site uses root-relative paths.

## 2017

### /2017/05/money-saving-uk-version/
**Title:** UK Money Saving Tips: Banking, Rewards & Travel Cards - James Kilby
**One-liner:** An outdated 2017 personal-finance post that's structurally thin (no meta description, canonical, OG tags, or sub-headings), references year-nine-old interest rates as current, and promises two follow-up posts that aren't linked.
- typo: "Barclays mortgage , and" → drop space before comma.
- typo: "First direct give you" → "First Direct"
- cosmetic [high]: Intro promises a three-part split but only the first section is present; other two posts missing/unlinked.
- cosmetic [low]: "UK banking and rewards" appears twice — once inside the numbered list, then as H2.
- cosmetic [medium]: Numbered list inside the Barclays paragraph rendered as inline text, not as a list.
- cosmetic [medium]: Sub-section labels (Nationwide FlexDirect, etc.) are paragraph text rather than H3.
- cosmetic [medium]: Math/summary line `156+125+162.50+15+135+97.50+150` is a raw expression; not all numbers itemised earlier.
- seo [high]: Meta description missing.
- seo [high]: `rel=canonical` missing.
- seo [high]: Open Graph tags missing.
- seo [high]: Content from 2017 references rates and rewards that are nine years out of date.
- seo [high]: Promised follow-up posts aren't linked.
- seo [medium]: Only one heading (H2) for ~780 words; no per-bank H3s.
- seo [medium]: No internal links to other related posts.
- seo [medium]: No images on the page (no og:image fallback).
- seo [low]: Title is 64 chars including suffix.

## Pages With No Issues Found

- (none — every audited URL produced at least one finding)
