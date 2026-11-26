# Cheshire-Herald (Cloudflare Worker)

Weekly social content drafts via Workers AI, staged in `SOCIAL_STAGING` KV until local ratification.

## Quick start

```bash
cd cloudflare/workers/cheshire-herald
npm install
npx wrangler kv namespace create SOCIAL_STAGING
# Paste returned id into wrangler.toml [[kv_namespaces]]
npx wrangler secret put SOVEREIGN_SALT
npx wrangler secret put SCRUBBER_SECRET
npm run deploy
```

## Local review (Ghost-IP)

```bash
export HERALD_WORKER_URL=https://cheshire-herald.<your-subdomain>.workers.dev
export SOVEREIGN_SALT=...
python herald_client.py pending --open
python herald_client.py ratify --batch-id 2026-W22 --platforms linkedin,x,facebook
```

See [docs/plans/2026-05-29-cheshire-herald-cloudflare.md](docs/2026-05-29-cheshire-herald-cloudflare.md).
