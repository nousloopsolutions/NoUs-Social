# @NCL{v=1.0;agent=claude;mod=social-engagement;tier=L2}
# #S{purpose="Aggregate-only engagement log and training export from Nous's own posts"}
# #I{1="Only counts, never who liked, replied or followed";2="Training rows hold only our own text and Brent's decisions";3="Plain JSONL"}
# #F{1="Store reply text or handles"→"Other people's personal data in a training set";2="Export any stored rejection"→"A revised and approved post carried the old text's rejection reason (Codex PR 694)"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib"}
# #T{status="python3 -m unittest discover -s social/tests"}
# #X{2026-11-26="Created for the approval-gated social pipeline"}
"""Engagement counts and the training export.

metrics.jsonl : {ts, post_id, platform, metrics:{likes, reposts, replies, ...}} (ints only)
export_training(): one JSONL row per own post with the first draft, the final text, the
human decision (approved / edited / rejected) and the latest aggregate counts.
"""
from __future__ import annotations

import json
import urllib.parse

from post_queue import Queue, now_utc
from publish import _http

ALLOWED = {"likes", "reposts", "replies", "quotes", "views", "clicks", "follows_delta"}


def clean_metrics(metrics: dict) -> dict:
    bad = set(metrics) - ALLOWED
    if bad:
        raise ValueError("only aggregate counts are kept; refused keys: " + ", ".join(sorted(bad)))
    out = {}
    for k, v in metrics.items():
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError(f"{k} must be an integer count")
        out[k] = v
    return out


def record_metrics(queue: Queue, post_id: str, metrics: dict, actor: str = "engagement") -> dict:
    post = queue.get(post_id)
    if post["status"] != "posted":
        raise ValueError("metrics only for posted posts")
    row = {"ts": now_utc(), "post_id": post_id, "platform": post["platform"], "metrics": clean_metrics(metrics)}
    with (queue.home / "metrics.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    queue._record(actor, "metrics", post, {"metrics": row["metrics"]})
    return row


def fetch_counts(post: dict, env: dict, http=_http) -> dict:
    """Reads only the count fields of our own post from the official API."""
    pid = post["posted"]["platform_post_id"]
    if post["platform"] == "mastodon":
        s = http("GET", f"{env['MASTODON_BASE'].rstrip('/')}/api/v1/statuses/{urllib.parse.quote(pid, safe='')}", {})
        return {"likes": s["favourites_count"], "reposts": s["reblogs_count"], "replies": s["replies_count"]}
    if post["platform"] == "bluesky":
        q = urllib.parse.urlencode({"uris": pid})
        p = http("GET", f"https://public.api.bsky.app/xrpc/app.bsky.feed.getPosts?{q}", {})["posts"][0]
        return {"likes": p.get("likeCount", 0), "reposts": p.get("repostCount", 0),
                "replies": p.get("replyCount", 0), "quotes": p.get("quoteCount", 0)}
    raise ValueError(f"no counts reader for {post['platform']}")


def latest_metrics(queue: Queue) -> dict:
    latest = {}
    path = queue.home / "metrics.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                latest[row["post_id"]] = row["metrics"]
    return latest


def export_training(queue: Queue) -> list[dict]:
    latest = latest_metrics(queue)
    rows = []
    for p in queue.all():
        if p["status"] == "draft":
            continue  # undecided
        # Only an approver's edits are human feedback; agent self-revisions are not corrections.
        human = [h for h in p["history"] if h.get("role") == "human"]
        first = human[0]["old_text"] if human else p["text"]
        decision = "rejected" if p["status"] == "rejected" else ("edited" if human else "approved")
        rows.append({
            "post_id": p["id"], "platform": p["platform"], "source": p.get("source"),
            "drafted_by": p["created_by"], "first_draft": first, "final_text": p["text"],
            "decision": decision, "edits": len(human),
            "agent_revisions": len(p["history"]) - len(human),
            # Only the current rejection describes final_text; an older one described replaced text.
            "rejection_reason": (p.get("rejection") or {}).get("reason") if p["status"] == "rejected" else None,
            "posted": p["status"] == "posted", "metrics": latest.get(p["id"], {}),
        })
    return rows
