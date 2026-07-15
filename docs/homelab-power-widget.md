# Homelab live-power widget

A live "homelab power draw" widget on the [lab page](https://jameskilby.co.uk/lab/):
current wattage + a 30-minute sparkline, updated every 30s. It shows "offline"
if no fresh reading is available.

```
Home Assistant ──POST /api/power (X-Power-Token)──▶ Pages Worker ──▶ HTML_CACHE KV
                                                          │
Lab-page widget ◀──GET /api/power (public, same-origin)──┘
```

## Pieces

| Piece | Where |
|-------|-------|
| Widget markup/CSS/JS | `scripts/partials/homelab-power-widget.html` (a build-injected partial) |
| Build injection | `wp_to_static_generator.inject_power_widget()` — inserts the partial into `public/lab/index.html` before the Table of Contents |
| API route | `/api/power` in `_worker.template.js` (POST token-gated, GET public) |
| Write secret | `POWER_TOKEN` — Cloudflare Pages dashboard secret (see [DEPLOYMENT.md](DEPLOYMENT.md)) |
| Storage | `HTML_CACHE` KV under `power:latest` (180s TTL, ~30-min rolling history) |

The widget is **not** WordPress content — it is injected at build time, so its
markup and styling are versioned and reviewed in this repo. Editing the partial
changes the widget on the next full build; do not hand-edit `public/`.

## Deploy checklist

1. **`POWER_TOKEN` secret** set in Cloudflare Pages (Settings → Variables and
   secrets), then **redeploy** — Pages only binds secret changes on a new
   deployment.
2. **Home Assistant** pushing wattage (below).
3. That's it — the widget ships automatically with the site build. No
   WordPress edit required.

## Home Assistant push

HA POSTs the whole-homelab wattage every ~30s (the KV key has a 180s TTL, so
~6 missed pushes → the widget shows "offline").

`secrets.yaml`:

```yaml
power_token: <the POWER_TOKEN value set in Cloudflare Pages>
```

`configuration.yaml` (swap `sensor.homelab_total_power` for your own
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

Reload REST commands + automations (or restart HA).

## Verify

```bash
# Live reading once HA is pushing:
curl -s https://jameskilby.co.uk/api/power
# → {"ok":true,"w":423,"ts":"…","history":[…]}

# Manual smoke test (expires after 180s):
curl -X POST https://jameskilby.co.uk/api/power \
  -H "X-Power-Token: $POWER_TOKEN" -H "Content-Type: application/json" \
  -d '{"w": 123}'
```
