# drafts/ — Staged Content Awaiting Approval

Agents place prepared, UNPUBLISHED content here. Each post lives as its own markdown
file under the relevant platform folder. Nothing here is live.

## Folder layout (one per platform)
- `drafts/x/` — X / Twitter posts (text ≤ 280 chars per item; threads as numbered files)
- `drafts/linkedin/` — LinkedIn posts (longer-form OK)
- `drafts/facebook/` — Facebook Page posts (Meta Business API)
- `drafts/instagram/` — Instagram captions + media notes (IG Business account)
- `drafts/tiktok/` — TikTok caption + video brief (DRAFT-PREP ONLY; posted manually in app)
- `drafts/discord/` — Discord announcements (webhook/bot)
- `drafts/reddit/` — Reddit posts (note target subreddit + flair)

## Draft file format
Each draft starts with a small front-matter block so the human and the publish layer
know exactly what it is:

```
---
platform: x
status: draft            # draft | approved | published | archived
topic: <short topic>
schedule: <YYYY-MM-DD HH:MM TZ or "on approval">
sources:
  - <url or note backing the claim>
  ---

  <the post body goes here>
  ```

  ## Approval flow
  1. Agent writes a draft file here with `status: draft`.
  2. Human reviews. To approve, the human (or a reviewer step) moves the file to
     `approved/<platform>/` and sets `status: approved`.
     3. The publish layer (run with the HUMAN's credentials — never the agent's) posts
        approved items and sets `status: published`, logging to SOCIAL_PROGRESS.md.

        Agents NEVER move a file to `approved/` themselves and NEVER publish.
        
