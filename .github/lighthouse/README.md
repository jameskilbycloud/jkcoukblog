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

- **`budget.json` / `budget-mobile.json`** — resource and timing
  budgets (KB and ms). Picked up by the LHCI action's built-in budget
  assertion. Catch bloat regressions: an extra render-blocking
  stylesheet, a forgotten un-optimised image, font weight increase, etc.
- **`assert.assertions` inside each lighthouse-config** — explicit
  per-audit thresholds and category min-scores. Catch behavioural
  regressions: render-blocking resources reappearing, image format
  regression, performance score drop, etc. **All assertions use
  `aggregationMethod: "median"`** so a single bad run doesn't flap
  the build.

Both fire on every Lighthouse run; a failure in either fails the build.

## Thresholds

Tuned May 2026 against measured medians after the picture-srcset and
inline-CSS work. CI Lighthouse mobile has wide run-to-run variance
(LCP can swing 2 s either way on the same code), so thresholds sit
**25–35% above the measured median** rather than at the median itself.

| Metric | Desktop | Mobile | Measured median (desktop / mobile) |
|---|---|---|---|
| Performance score | ≥ 0.85 | ≥ 0.65 | 0.89 / 0.69 |
| FCP | ≤ 1500 ms | ≤ 5500 ms | 1032 ms / 4300 ms |
| LCP | ≤ 2500 ms | ≤ 7000 ms | 1942 ms / 5531 ms |
| TBT | ≤ 300 ms  | ≤ 400 ms  | 0 ms / 0 ms |
| CLS | ≤ 0.05   | ≤ 0.05    | 0.048 / 0.048 |
| Speed Index | ≤ 1500 ms | ≤ 5500 ms | 1043 ms / 4300 ms |
| Total transfer | ≤ 1100 KB | ≤ 1100 KB | ~950 KB / ~932 KB |

These bands are deliberately wide for mobile — Google's PSI runs the
site at 90+ on mobile from real-user infrastructure, but GitHub-hosted
runner Lighthouse with simulated 4G + 4× CPU throttle clusters around
0.65–0.75. The PSI score is what matters; the CI gate is there only
to catch obvious regression.

Tighten when measured medians improve materially (e.g. UbuntuExpand
gets its missing intermediate WP thumbnail sizes, or font subsetting
trims the 556 KB font budget). Loosen only with a recorded reason in
the commit message.

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
these are still being chipped away at (UbuntuExpand missing
intermediate WP thumbnail sizes is the biggest outstanding one).
Warn-level keeps them visible without flapping CI.

## What NOT to put in these JSON files

`tolerance` on timing budgets is **not** a valid Lighthouse-CI budget
field, despite looking like it should be. Including it produces
`Error: Timing Budget has unrecognized properties: [tolerance]` and
the assertion step crashes silently. Budgets are *not* enforced when
that happens. (Discovered May 2026 — every audit had been silently
passing despite obvious regressions for weeks.)

Don't add `$schema`, comments, or any other "helper" keys to budget
files — Lighthouse strict-validates them. Document changes in this
README and in the commit message instead.

Same applies to `assert.assertions` keys: they must be exact audit IDs
or category prefixes. Misspelt keys are silently ignored, not flagged.

`aggregationMethod` defaults are **different per assertion type**:
`pessimistic` for `minScore`, `optimistic` for `maxNumericValue`.
Setting it explicitly to `median` everywhere makes the assertion
behaviour consistent with how humans intuitively think about "the
typical run" and avoids surprises when one run is unusually fast or
slow.
