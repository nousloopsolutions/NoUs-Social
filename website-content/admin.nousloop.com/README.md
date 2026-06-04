# Sovereign Console (admin.nousloop.com)

**The Glass:** Static HTML/JS dashboard that polls `https://api.nousloop.com/v1/vault` every 5s and renders the Merkle-chained pulse archive (VDS 90000). Dark mode: background `#0A0A0B`, navy `#0f172a`, gold `#f59e0b`.

**Routing:** Worker siteMap `admin.nousloop.com` → R2 prefix `admin`. Sync via `npm run r2:sync` (content/admin.nousloop.com → admin).

---

**Part 2 — The Lock (Outie execution):** So that discovery of admin.nousloop.com does not grant access, the Architect should add a cryptographic or auth layer in front of this surface, e.g.:

- **Cloudflare Access:** Create an Access application for `admin.nousloop.com`; require email/OIDC or one-time PIN so only authorized identities reach the console.
- **WAF + IP allowlist:** Restrict to known admin IPs (Enterprise).
- **Custom auth:** A small Worker that checks a signed cookie or bearer token before serving the admin R2 content.

Until the lock is in place, treat the console as internal-only and rely on obscurity only for short-term use.
