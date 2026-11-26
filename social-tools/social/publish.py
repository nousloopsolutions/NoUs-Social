# @NCL{v=1.0;agent=claude;mod=social-publish;tier=L2}
# #S{purpose="Send approved posts through official platform APIs only"}
# #I{1="Dry run unless live=True";2="check_publishable runs right before every send";3="Credentials come from env only, never files";4="No scraping, no reading other people's content";5="Redirects are refused, so credentials never follow one"}
# #F{1="Retry without idempotency"→"Double posts; a send key (TID) is saved before the first request: Bluesky rkey, Mastodon Idempotency-Key";2="Retry after a lost response by re-creating"→"Duplicate public post; Bluesky retries look the rkey up first";3="Count failed tries in an except block"→"A killed process skipped it; every send start is saved before the request and counts toward its day's cap";4="Default urlopen follows redirects"→"An HTTPS 302 to HTTP forwarded the bearer token in plaintext (Codex PR 694)"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib (urllib)"}
# #T{status="python3 -m unittest discover -s social/tests"}
# #X{2026-11-26="Created for the approval-gated social pipeline"}
"""Publishers. Each takes (post, env) and returns (platform_post_id, url).

Bluesky  : AT Protocol com.atproto.server.createSession + com.atproto.repo.createRecord.
           Env BSKY_HANDLE, BSKY_APP_PASSWORD (an app password, never the account password),
           optional BSKY_PDS (default https://bsky.social).
Mastodon : POST /api/v1/statuses. Env MASTODON_BASE (https://instance), MASTODON_TOKEN
           (scope write:statuses only).
LinkedIn : no API publisher. Post by hand, then `cli.py mark-posted`.
"""
from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request

import datetime as _dt

from post_queue import GateError, Queue, now_utc, parse_utc

TIMEOUT = 20


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Official APIs answer directly. Following a redirect could downgrade to HTTP or carry
    the Authorization header to another origin, so every redirect is an error."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"redirect refused (to {newurl})", headers, fp)


_OPENER = urllib.request.build_opener(_RefuseRedirects())


def _http(method: str, url: str, headers: dict, body: bytes | None = None, opener=_OPENER.open) -> dict:
    if not url.startswith("https://"):
        raise ValueError("publishers only talk HTTPS")
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    with opener(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _need(env: dict, *names: str) -> list[str]:
    missing = [n for n in names if not env.get(n)]
    if missing:
        raise GateError("missing credentials in env: " + ", ".join(missing))
    return [env[n] for n in names]


_B32 = "234567abcdefghijklmnopqrstuvwxyz"


def new_tid() -> str:
    """AT Protocol TID record key: 53-bit microsecond time + 10-bit clock id, base32-sortable."""
    n = (int(time.time() * 1_000_000) << 10) | random.getrandbits(10)
    return "".join(_B32[(n >> (5 * i)) & 31] for i in range(12, -1, -1))


def bluesky(post: dict, env: dict, http=_http) -> tuple[str, str]:
    handle, app_pw = _need(env, "BSKY_HANDLE", "BSKY_APP_PASSWORD")
    pds = env.get("BSKY_PDS", "https://bsky.social").rstrip("/")
    js = {"Content-Type": "application/json"}
    sess = http("POST", f"{pds}/xrpc/com.atproto.server.createSession", js,
                json.dumps({"identifier": handle, "password": app_pw}).encode())
    attempt = post["attempt"]
    rkey, did = attempt["key"], sess["did"]
    auth = {**js, "Authorization": f"Bearer {sess['accessJwt']}"}
    def web(uri: str) -> str:
        return f"https://bsky.app/profile/{did}/post/{uri.rsplit('/', 1)[-1]}"
    if post.get("_prior_sends", 0) > 0:  # an earlier send may have landed: reconcile, don't re-create
        q = urllib.parse.urlencode({"repo": did, "collection": "app.bsky.feed.post", "rkey": rkey})
        try:
            got = http("GET", f"{pds}/xrpc/com.atproto.repo.getRecord?{q}", auth)
            return got["uri"], web(got["uri"])
        except urllib.error.HTTPError as exc:
            if exc.code not in (400, 404):
                raise
    record = {"$type": "app.bsky.feed.post", "text": post["text"], "createdAt": attempt["at"], "langs": ["en"]}
    out = http("POST", f"{pds}/xrpc/com.atproto.repo.createRecord", auth,
               json.dumps({"repo": did, "collection": "app.bsky.feed.post", "rkey": rkey,
                           "record": record}).encode())
    return out["uri"], web(out["uri"])


# Mastodon keeps Idempotency-Keys "for up to 1 hour"; past that a retry could duplicate.
MASTODON_RETRY_WINDOW_S = 50 * 60


def mastodon(post: dict, env: dict, http=_http) -> tuple[str, str]:
    base, token = _need(env, "MASTODON_BASE", "MASTODON_TOKEN")
    attempt = post["attempt"]
    if post.get("_prior_sends", 0) > 0:
        age = (_dt.datetime.now(_dt.timezone.utc) - parse_utc(attempt["at"])).total_seconds()
        if age > MASTODON_RETRY_WINDOW_S:
            raise GateError("Mastodon's duplicate protection has expired for this send; check the "
                            "account by hand, then mark-posted or clear-attempt")
    body = urllib.parse.urlencode({"status": post["text"], "visibility": "public", "language": "en"}).encode()
    out = http("POST", f"{base.rstrip('/')}/api/v1/statuses",
               {"Authorization": f"Bearer {token}", "Idempotency-Key": post["attempt"]["key"],
                "Content-Type": "application/x-www-form-urlencoded"}, body)
    return str(out["id"]), out.get("url", "")


PUBLISHERS = {"bluesky": bluesky, "mastodon": mastodon}


def publish(queue: Queue, post_id: str, actor: str, live: bool = False, env: dict | None = None,
            daily_cap: int = 1, http=_http) -> dict:
    """Publish one approved post. Returns a result dict; never raises past the gate silently."""
    env = dict(os.environ) if env is None else env
    post = queue.get(post_id)
    sender = PUBLISHERS.get(post["platform"])
    if sender is None:
        raise GateError(f"no API publisher for {post['platform']}; post by hand, then mark-posted")
    # One publish per platform at a time, from the cap check through recording the result.
    # Lock order: platform, then post. The post lock keeps edit/reject out until the result
    # is recorded, so an edit can't be overwritten or its approval revocation ignored.
    with queue.platform_lock(post["platform"]), queue.post_lock(post_id):
        post = queue.get(post_id)
        queue.check_publishable(post, daily_cap=daily_cap)  # kill switch, signature, lint, schedule, cap
        if not live:
            return {"dry_run": True, "post_id": post_id, "platform": post["platform"], "text": post["text"]}
        if not post.get("attempt"):
            post = queue.begin_attempt(post, actor, new_tid())
        # Recorded before the request, so even a killed process leaves evidence of the send.
        prior = queue.start_send(post)
        platform_id, url = sender({**post, "_prior_sends": prior}, env, http=http)
        queue.record_posted(post, actor, platform_id, url)
    return {"dry_run": False, "post_id": post_id, "platform_post_id": platform_id, "url": url}
