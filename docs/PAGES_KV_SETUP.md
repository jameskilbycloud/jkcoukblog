# Cloudflare Pages KV Bindings Setup

The Cloudflare Pages Advanced Mode Worker (`_worker.template.js` → `public/_worker.js`) reads two KV namespaces and one secret from the Pages project bindings. These have to be configured in the **Cloudflare dashboard**, not in `wrangler.toml` — Pages does not read `wrangler.toml` for binding configuration.

If you ever recreate the Pages project (or move it to a new Cloudflare account) you need to redo these steps once. After that the worker just picks them up automatically on every deploy.

## What needs binding

| Binding | Type | Used by |
|---|---|---|
| `HTML_CACHE` | KV namespace | `env.HTML_CACHE` in `_worker.template.js` — smart-TTL HTML cache with view counts |
| `SEARCH_INDEX` | KV namespace | `env.SEARCH_INDEX` — search index uploaded by CI via `wrangler kv:key put` |
| `PURGE_TOKEN` | Encrypted environment variable | Token check on `/.purge`, `/diagnostic`, `/trace` in the worker |

The current namespace IDs (also documented in `wrangler.toml` for ad-hoc CLI use):

- `HTML_CACHE`: `5528672ccf0644c9bd65e7de8b629189`
- `SEARCH_INDEX`: `da75861d372642d4979c8611b4856ab0`

## Steps

1. Go to <https://dash.cloudflare.com> → **Workers & Pages** → **jkcoukblog** → **Settings** → **Functions**.
2. Under **KV namespace bindings**, click **Add binding** twice:
   - Variable name `HTML_CACHE`, namespace `HTML_CACHE` (ID above).
   - Variable name `SEARCH_INDEX`, namespace `SEARCH_INDEX` (ID above).
3. Under **Environment variables**, add:
   - Variable name `PURGE_TOKEN`, type **Encrypted**, environment **Production**, value = whatever you set as the `CACHE_PURGE_TOKEN` repository secret. The worker compares incoming `X-Purge-Token` headers against this value.
4. Save. Bindings take effect on the next Pages deploy (or you can redeploy from the dashboard).

## Verify

The Advanced Mode Worker exposes two diagnostic endpoints, both gated by `PURGE_TOKEN`:

```bash
# Confirms HTML_CACHE / SEARCH_INDEX / PURGE_TOKEN / ASSETS bindings + a live KV write/read test
curl -H "X-Purge-Token: $PURGE_TOKEN" https://jameskilby.co.uk/diagnostic | jq

# Shows what cache decision the worker would make for a given path
curl -H "X-Purge-Token: $PURGE_TOKEN" "https://jameskilby.co.uk/trace?path=/2026/04/some-post/" | jq
```

A request without the token returns `401 Unauthorized` from `_worker.template.js`. A successful `/diagnostic` response should show `HTML_CACHE: BOUND`, `SEARCH_INDEX: BOUND`, `PURGE_TOKEN: SET`, `ASSETS: BOUND`, and `kv_test.status: WORKING`.

## Note on cache fingerprints

`X-Worker: advanced-worker-kv` and `X-Cache-Status: HIT/MISS` are set by the worker but are stripped by Cloudflare Managed Transforms before reaching the client. To confirm the worker is actually serving cached HTML, use `/diagnostic` or check `cf-ray` plus the response timing rather than looking for those headers in normal page responses.
