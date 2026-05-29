# Lighthouse CI configuration

Two passes — desktop and mobile — share the same code paths in
[`quality-checks.yml`](../workflows/quality-checks.yml) (scheduled +
push, against production) and
[`lighthouse-pr.yml`](../workflows/lighthouse-pr.yml) (every PR,
against the CF Pages preview URL).

| Pass | Config | Budget | Behaviour |
|------|--------|--------|-----------|
| Desktop | `lighthouse-config.json`        | `budget.json`        | Fast Wi-Fi (10 Mbps), no CPU throttle, 1350×940 viewport |
| Mobile  | `lighthouse-config-mobile.json` | `budget-mobile.json` | Slow-4G (1.6 Mbps), 4× CPU slowdown, 360×640 viewport     |

## What enforces what

There are **two** enforcement layers and they assert different things:

- **`budget.json` / `budget-mobile.json`** — resource and timing budgets
  (KB and ms). Run by the LHCI action's built-in budget assertion. Catch
  bloat regressions: an extra render-blocking stylesheet, a forgotten
  un-optimised image, font weight increase, etc.
- **`assert.assertions` inside each lighthouse-config** — explicit
  per-audit thresholds and category min-scores. Catch behavioural
  regressions: render-blocking resources reappearing, image format
  regression, performance score drop, etc.

Both fire on every Lighthouse run; a failure in either fails the build.

## Why these thresholds

Tuned in May 2026 against measured medians after the picture-srcset
and inline-CSS work:

| Metric | Desktop budget | Desktop measured median | Mobile budget | Mobile measured median |
|---|---|---|---|---|
| Performance score | ≥ 0.90 | 0.93 | ≥ 0.80 | 0.84–0.91 |
| FCP                  | ≤ 1000 ms | 0.9 s | ≤ 2500 ms | 1.5–2.6 s |
| LCP                  | ≤ 1500 ms | 1.3 s | ≤ 3000 ms | 1.8–3.8 s |
| TBT                  | ≤  200 ms | 0 ms  | ≤  400 ms | 0–220 ms  |
| CLS                  | ≤ 0.05   | 0.048 | ≤ 0.05    | 0.048      |
| Speed Index          | ≤ 1300 ms | 1.0 s | ≤ 3500 ms | 1.5–3.0 s |
| **Total transfer**   | ≤ 1100 KB | ~ 950 KB | ≤ 1100 KB | ~ 932 KB |

Budgets sit ~10–30% above the measured median so run-to-run Lighthouse
variance doesn't flap, but a real regression (e.g. a re-introduced
render-blocking stylesheet adding 300 ms FCP) fails the check.

Mobile performance score is set lower (0.80) than desktop (0.90)
because Lighthouse mobile throttles aggressively and the **server
response time** (KV cache cold-start) routinely varies between 60 ms
and 1000+ ms across runs, dominating the score independent of the
code change being measured.

## Zero-tolerance audits (both desktop and mobile)

| Audit | Threshold | Why |
|---|---|---|
| `render-blocking-resources`   | 0 ms savings  | Inline-CSS work removed all of them; re-introducing one is a regression. |
| `uses-text-compression`        | 0 ms savings  | Brotli/gzip pre-compression is part of the pipeline; missing it points at a deploy bug. |
| `efficient-animated-content`   | 0 ms savings  | No animated content on the site — any flagged saving means an unconverted GIF. |
| `duplicated-javascript`        | 0 ms savings  | Catches accidental vendor double-bundling. |
| `legacy-javascript`            | 0 ms savings  | All current JS is ES2017+. |
| `modern-image-formats`         | < 5 KB        | AVIF/WebP everywhere; small slack for SVGs/favicons that the audit can flag. |
| `uses-optimized-images`        | < 5 KB        | Same idea — small slack for icons. |

## Warnings (don't fail the build, but show up in the report)

`uses-responsive-images`, `unused-css-rules`, `unused-javascript` —
these are still being chipped away at (UbuntuExpand missing intermediate
WP thumbnail sizes is the biggest outstanding one). Warn-level keeps
them visible without flapping CI.

## What NOT to put in these JSON files

`tolerance` on timing budgets is **not** a valid Lighthouse-CI budget
field, despite looking like it should be. Including it produces
`Error: Timing Budget has unrecognized properties: [tolerance]` and
the assertion step crashes silently. Budgets are *not* enforced when
that happens. (We discovered this only because every audit was
silently passing despite obvious regressions.)

Don't add `$schema`, comments, or any other "helper" keys to budget
files — Lighthouse strict-validates them. Document changes in this
README and in the commit message instead.

Same applies to `assert.assertions` keys: they must be exact audit IDs
or category prefixes. Misspelt keys are silently ignored, not flagged.
