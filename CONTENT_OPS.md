# NoUs-Social — Content Operations Design

This document describes HOW the agent-assisted content pipeline works and WHAT the
human must provision. It is a design/spec doc — no live credentials live in this repo.

Mission backbone: "safety through severance" — advancing data rights and severance
from Big Tech. All content ladders up to that.

## Roles
- AGENTS (Nous Social Town): gather project news, draft posts, summarize community
  activity, propose a calendar. They STAGE only. They never publish and never hold secrets.
  - HUMAN (owner): reviews drafts, approves, provisions all credentials, triggers publish.
  - PUBLISH LAYER: a small script/service that runs with the HUMAN's secrets and posts
    approved items. It is the ONLY thing that touches platform APIs.

    ## Pipeline
    1. Gather → agents collect project news + relevant external news into source notes.
    2. Draft → agents write per-platform drafts into `drafts/<platform>/`.
    3. Review → human reads drafts (via PR or folder), edits, approves.
    4. Approve → approved files move to `approved/<platform>/` with status: approved.
    5. Publish → publish layer posts approved items using the human's tokens.
    6. Log → every action recorded in SOCIAL_PROGRESS.md.
    7. Listen → a read-only listener pulls community posts + engagement, agents summarize.

    ## Per-platform feasibility
    | Platform | Auto-publish via API? | Notes |
    |----------|----------------------|-------|
    | X | Yes | X API v2 app + OAuth2 user tokens |
    | LinkedIn | Yes | LinkedIn API; company page needs org permissions |
    | Reddit | Yes | Reddit script app; respect subreddit rules/flair |
    | Discord | Yes | Bot token or channel webhook (simplest) |
    | Facebook | Yes (Page only) | Meta Graph API; Facebook Page + app review |
    | Instagram | Yes (Business only) | Meta Graph API; IG Business account linked to a Page |
    | TikTok | Draft-prep only | Content Posting API gated; finish/post manually in app |

    ## Credentials checklist — HUMAN PROVISIONS ALL OF THESE
    The agent and assistant will NEVER create, request, or enter these. Store them as repo
    / deploy secrets yourself (never commit them):
    - X: API key, API secret, OAuth2 client ID/secret, user access token
    - LinkedIn: client ID/secret, access token (+ org URN for company page)
    - Reddit: client ID/secret, username, app-specific password/refresh token
    - Discord: bot token OR channel webhook URL
    - Facebook/Instagram: Meta app ID/secret, Page access token, IG Business account ID
    - TikTok: (manual posting; no auto-publish token expected initially)

    ## Hard safety rules
    - Nothing publishes without explicit human approval of that specific item.
    - No secret is ever committed to the repo or pasted into chat.
    - Listener access is READ-ONLY; it never posts or replies on its own.
    - Branches + PRs only; no merge to main without owner sign-off.
    - Archive, never delete. Small batches, no spam, respect each platform's rate limits and ToS.
    
