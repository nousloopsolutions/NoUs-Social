# PIVOT_LOG_ENTRY — Cheshire-Herald (Cloudflare Edition)

**Date:** 2026-05-29  
**PIVOT_ID:** PIV-SOCIAL-HERALD-CLOUDFLARE  
**State:** IMPLEMENTED  

## Creation Origin Log

- **Thread log date:** 2026-05-28  
- **Creation date:** 2026-05-29  
- **Origin:** Cursor Agent — branch `cursor/cheshire-herald-cloudflare-5be9`  
- **Scope:** New satellite Worker + local CLI client  

## Context & Alignment

- **Cloudflare Worker Optimization:** Ratified deployment of `Cheshire-Herald` as an isolated Cloudflare Worker rather than a local desktop cron service.  
- **Ghost-IP Compliance:** Cloud cannot write to local `social_staging.md`. Drafts stage in KV namespace `SOCIAL_STAGING` with status `PENDING_HUMAN_PIVOT`. Local machine pulls via `scripts/herald_client.py` and ratifies over HTTPS.  
- **Ratification Loop:** Dual-trigger architecture — weekly `cron` for research/draft (Workers AI + RSS), secure `fetch` for `POST /ratify-and-publish` after human approval.  
- **Severance Protocol:** No inbound firewall piercing; outbound-only local client.  

## Implementation Summary

| Artifact | Path |
|----------|------|
| Worker | `cloudflare/workers/cheshire-herald/` |
| Wrangler config | `cloudflare/workers/cheshire-herald/wrangler.toml` |
| Local client | `scripts/herald_client.py` |
| Structure doc | `CLOUDFLARE_STRUCTURE.md` (Herald section) |

## Platform Asymmetry (v1)

| Platform | Cron draft | Auto-publish on ratify |
|----------|------------|-------------------------|
| LinkedIn | Long-form advocacy | Yes (if tokens set) |
| X | ≤280 chars | Yes |
| Facebook | Community narrative | Yes |
| Instagram | 60s script + visual prompt | No (draft only) |
| TikTok | 60s script + visual prompt | No (draft only) |

## Deploy Checklist

1. `npx wrangler kv namespace create SOCIAL_STAGING` — update `wrangler.toml` id  
2. `wrangler secret put SOVEREIGN_SALT`  
3. `wrangler secret put SCRUBBER_SECRET`  
4. Optional: LinkedIn / X / Facebook tokens for publish phase  
5. `npm run deploy` from `cloudflare/workers/cheshire-herald/`  

## Knowledge Gaps / Follow-ups

- Wonderland HILGate panel for social batches (deferred)  
- OAuth token refresh for social APIs (deferred)  
- D1 audit log for publish events (v2)  
- Route `api.nousloop.com/herald/*` when DNS ready  

## Chain-of-Thought (accumulative)

1. Initial pivot rejected cloud→local file write (Severance violation).  
2. KV staging + pull ratification preserves Ghost-IP while keeping RTX 4090 free of cron polling.  
3. Reused Cheshire scrubber semantics and Hall of Doors AI model (`@cf/meta/llama-3-8b-instruct`).  
4. Cron skip-if-pending prevents overwriting unreviewed drafts.  
