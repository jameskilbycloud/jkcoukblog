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

## Why these timing budgets

After the May-2026 perf work the site lands at LCP ~530 ms / total
transfer ~940 KB in GTmetrix terms — Lighthouse measures around
800–1000 ms LCP under its desktop throttling profile.

The desktop budget sits **~50 %** above current measured state so
normal Lighthouse run-to-run variance stays green but a real
regression (LCP +300 ms or bigger) fails the check. Bump down when
measured performance improves; bump up only with a recorded reason
in the commit message.

The mobile budget is **2–3×** looser than desktop because slow-4G +
4× CPU throttling roughly doubles real timings. The mobile targets
align with Google's "Good" Core Web Vitals thresholds (LCP < 2500 ms,
CLS < 0.1, TBT < 200 ms with tolerance).

## Resource budgets

Identical between desktop and mobile — assets don't change between
form factors, only the timing of fetching/parsing them does.

| Resource type | Budget (KB) |
|--------------|-------------|
| document     |  30 |
| stylesheet   |  80 |
| script       |  70 |
| image        | 250 |
| font         | 200 (intentionally loose, will tighten to ~80 once font subsetting has been live for a deploy or two) |
| third-party  |  60 |
| **total**    | **800** |

## What NOT to put in these JSON files

Lighthouse CI validates budget JSON strictly: `Budget has unrecognized
properties: [...]`. Comments inside the JSON (`_comment_about_this_file`,
`$schema`, etc.) cause the assertion step to crash silently — the
workflow appears green but no budgets are actually enforced.

Document changes here in this README. Recorded by PR #42 after a
fixed silent-failure of the budget assertion that masked weeks of
unenforced gates.
