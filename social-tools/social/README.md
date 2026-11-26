# NoUs Loop social pipeline

```ncl
@NCL{v=1.0;agent=claude;tier=L1;ts=2026-11-26}
@FILE{queue;post_queue.py;drafts, approval gate, hash-chained ledger}
@FILE{lint;lint.py;brand check from ../brand-rules.json}
@FILE{publish;publish.py;Bluesky and Mastodon official APIs, dry run by default}
@FILE{engagement;engagement.py;counts only, training export}
@FILE{cli;cli.py;command line}
```

Status: built and tested, **not connected to any account**. No account exists and nothing has
been posted. Creating accounts and the first live post need Brent's go.

## What it does

Nous (Hermes, on a local model) drafts posts. Every draft passes the brand check. Brent reads
and approves the exact text. Only then can a publisher send it, through the platform's official
API, within a daily cap, with a kill switch. Every step is stamped in a hash-chained ledger.
Engagement comes back as counts only, and the training export holds only our own posts and
Brent's decisions.

```
draft (agent or local model) -> lint -> Brent approves exact text -> publish (official API) -> counts
                                  |                |                         |
                         brand-rules.json   sha256(platform+text)   kill switch, cap, schedule
```

## Rules the code enforces

| Rule | Where |
|---|---|
| An approval is an Ed25519 signature over the post id, platform, sha256 of the text, approver and time. The key is passphrase-encrypted in `~/.nous-social-approver/` (outside the queue), and its fingerprint is pinned in `NOUS_SOCIAL_TRUSTED_KEYS`. Editing the JSON cannot forge it | `post_queue.approve`, `verify_approval` |
| The approver signs the hash of the text they were shown; if the post changed during review, approval fails. Edit and approve hold a per-post lock | `approve`, `_lock` |
| The drafting agent can never approve its own post; with no pinned key, nothing can be approved | `approve`, `verify_approval` |
| `cli.py approve` needs a person at a terminal typing the post's 6-character check code and the key passphrase | `cli.py` |
| Brand check: wellness-only wording, no internal technology names, no trackers, no tagging people, no urgency tricks, platform length | `lint.py` + `../brand-rules.json` (shared with the site's copy guard) |
| A send key is saved before the first request (Bluesky rkey, Mastodon Idempotency-Key). After a failure the post can't be edited or rejected until a retry reconciles it or Brent clears it after checking the platform. Locks are OS locks that die with the process | `publish.py`, `post_queue.py` |
| Dry run unless `--live`; kill switch file `KILL`; one post per platform per UTC day by default | `publish.py`, `check_publishable` |
| Credentials from environment only, never files; HTTPS only; Mastodon gets an Idempotency-Key | `publish.py` |
| Local drafting talks only to a loopback model server (no paid or cloud API) | `draft_local.py` |
| Engagement keeps only integer counts (likes, reposts, replies, quotes, views, clicks, follows_delta), never who | `engagement.py` |

## Platforms

| Platform | How | Credentials (env) |
|---|---|---|
| Bluesky | AT Protocol createSession + createRecord | `BSKY_HANDLE`, `BSKY_APP_PASSWORD` (an app password), optional `BSKY_PDS` |
| Mastodon | `POST /api/v1/statuses` | `MASTODON_BASE`, `MASTODON_TOKEN` (scope `write:statuses`; add `read:statuses` for counts) |
| LinkedIn | Posted by hand, then `mark-posted` (company page API needs app review) | none |
| X, Reddit | Not automated (paid API; Reddit by hand only) | none |

## Use

Data lives outside the repo in `$NOUS_SOCIAL_HOME` (default `~/.nous-social`).

```bash
python3 social/cli.py approver-keygen --as brent        # once; prints the fingerprint to pin
#   then set NOUS_SOCIAL_TRUSTED_KEYS=brent:<fingerprint> in your user environment
python3 social/cli.py draft mastodon "Small breaks help." --agent hermes
python3 social/cli.py draft bluesky --topic "taking a short walk" --agent hermes   # local model
python3 social/cli.py list
python3 social/cli.py show <id>
python3 social/cli.py edit <id> "New text" --as brent
python3 social/cli.py approve <id> --as brent          # interactive: check code + passphrase
python3 social/cli.py publish <id>                      # dry run
python3 social/cli.py publish <id> --live               # sends
python3 social/cli.py clear-attempt <id> --as brent    # after a failed send, once you checked the platform
python3 social/cli.py kill | unkill
python3 social/cli.py metrics <id>                      # read counts from the API
python3 social/cli.py export > training.jsonl
python3 social/cli.py verify
```

Tests: `npm run test:social` (or `python3 -m unittest discover -s social/tests`).

## Before going live (needs Brent)

1. Brent creates the accounts himself (Bluesky handle `nousloop.com` via a DNS TXT record; a Mastodon
   instance choice), and makes an app password or token. Claude does not create accounts.
2. Put the credentials in the environment on the machine that publishes (Legion or BIGG RIGG).
3. A Telegram approve button is proposed, not built: it must keep the same check-code binding.

Residual risk: a process running as Brent's own user could change `NOUS_SOCIAL_TRUSTED_KEYS` and pin
its own key. Agents should run under a separate account, or the pin should be checked against the
fingerprint recorded in Brent's own notes before any live run.
