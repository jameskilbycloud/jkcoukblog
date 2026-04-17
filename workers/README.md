# Cloudflare Workers

This directory contains the standalone Cloudflare Workers used alongside the
main site. Edge HTML caching is **not** in here — it's handled by the Pages
Advanced Mode Worker at [`../_worker.template.js`](../_worker.template.js),
which is copied to `public/_worker.js` during deploy. Do not reintroduce a
standalone HTML cache worker here; Cloudflare Pages ignores anything that
would conflict with `public/_worker.js`.

## Active workers

### `search-api.js`

Edge search API backed by the `SEARCH_INDEX` KV namespace. Serves the
compressed search index and a search endpoint so the browser doesn't have to
download `search-index.json` in full.

KV binding: `SEARCH_INDEX` (namespace ID in [`../wrangler.toml`](../wrangler.toml)).

### `slack-notification-handler.js`

Receives Cloudflare Pages deployment webhooks and forwards formatted
notifications to Slack. Deployed as a standalone Worker whose URL is
registered as the Pages notification endpoint.

## Archived

[`archive/`](archive/) contains superseded workers kept only for reference —
do not edit or redeploy them.

- `html-cache.js` — original edge HTML cache. Replaced by the Advanced Mode
  Worker in [`../_worker.template.js`](../_worker.template.js), which adds
  KV-backed caching, smart TTLs, view tracking, and security headers.
- `slack-notification-handler-improved.js` — experimental rewrite, never
  promoted.

## Deployment

Active workers are deployed manually with Wrangler when their source changes:

```bash
npx wrangler deploy workers/search-api.js --name <worker-name>
npx wrangler deploy workers/slack-notification-handler.js --name <worker-name>
```

They are **not** part of the `deploy-static-site.yml` pipeline — that
workflow only builds the static site, uploads the search index to KV, and
purges caches.

## Monitoring

Cloudflare Dashboard → Workers & Pages → `<worker>` → Metrics.

Tail live logs:

```bash
npx wrangler tail <worker-name>
```
