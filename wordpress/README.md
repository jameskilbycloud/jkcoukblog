# WordPress-embedded content

Snippets that live in **WordPress** (the source of truth), version-controlled
here for reference. These are **not** part of the Python build pipeline and are
**not** served from `public/` — they are pasted into WordPress blocks by hand.
Editing a file here does not change the live site; you must also update the
corresponding WordPress block.

## `homelab-power-widget.html`

A self-contained live power-draw widget for the blog. No external scripts,
fonts, or styles, so it passes the site CSP (`script-src 'self' 'unsafe-inline'`,
`connect-src 'self'`). It polls the same-origin `/api/power` endpoint every 30s.

### Install

Paste the entire file into a WordPress **Custom HTML** block (or a reusable
block / template part) wherever the widget should appear.

### Data flow

```
Home Assistant ──POST /api/power (X-Power-Token)──▶ Pages Worker ──▶ HTML_CACHE KV
                                                          │
Blog widget ◀──GET /api/power (public, same-origin)──────┘
```

The `/api/power` route lives in `_worker.template.js`. Writes are gated by the
`POWER_TOKEN` secret (set in the Cloudflare Pages dashboard, mirrors
`PURGE_TOKEN`); reads are public and same-origin, so no Home Assistant token
ever reaches the browser. If HA stops pushing, the KV key expires (180s TTL)
and the endpoint reports `stale`, so the widget shows "offline" instead of a
frozen number.

### Home Assistant push

HA POSTs the whole-homelab wattage every ~30s. Add to `secrets.yaml`:

```yaml
power_token: <the POWER_TOKEN value set in Cloudflare Pages>
```

and to `configuration.yaml` (swap `sensor.homelab_total_power` for your own
whole-homelab power sensor):

```yaml
rest_command:
  homelab_power_push:
    url: https://jameskilby.co.uk/api/power
    method: POST
    content_type: application/json
    headers:
      X-Power-Token: !secret power_token
    payload: '{"w": {{ states("sensor.homelab_total_power") | float(0) }} }'

automation:
  - alias: Push homelab power to blog
    mode: single
    trigger:
      - platform: time_pattern
        seconds: "/30"
    condition:
      - condition: template
        value_template: >
          {{ states('sensor.homelab_total_power') not in
             ['unknown','unavailable','none'] }}
    action:
      - service: rest_command.homelab_power_push
```

### Verify

```bash
# Should return a live reading once HA is pushing:
curl -s https://jameskilby.co.uk/api/power
# → {"ok":true,"w":423,"ts":"…","history":[…]}

# Manual smoke test (expires after 180s):
curl -X POST https://jameskilby.co.uk/api/power \
  -H "X-Power-Token: $POWER_TOKEN" -H "Content-Type: application/json" \
  -d '{"w": 123}'
```
