#!/usr/bin/env python3
"""
Cheshire-Herald local client — Ghost-IP pull model (outbound HTTPS only).

Usage:
  python scripts/herald_client.py pending
  python scripts/herald_client.py ratify --batch-id 2026-W22 --platforms linkedin,x,facebook
  python scripts/herald_client.py reject --batch-id 2026-W22
  python scripts/herald_client.py draft   # trigger cron draft (dev)

Env:
  HERALD_WORKER_URL — default https://cheshire-herald.<account>.workers.dev or api route
  SOVEREIGN_SALT — Bearer token (required for staging/ratify)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from typing import Any, Dict, List, Optional

import httpx

DEFAULT_BASE = os.environ.get(
    "HERALD_WORKER_URL",
    "https://cheshire-herald.nousloopsolutions.workers.dev",
).rstrip("/")


def _headers() -> Dict[str, str]:
    salt = os.environ.get("SOVEREIGN_SALT", "")
    h = {"Content-Type": "application/json"}
    if salt:
        h["Authorization"] = f"Bearer {salt}"
    return h


def _require_salt() -> None:
    if not os.environ.get("SOVEREIGN_SALT"):
        print("SOVEREIGN_SALT env var required", file=sys.stderr)
        sys.exit(1)


def cmd_pending(open_md: bool = False) -> int:
    _require_salt()
    r = httpx.get(f"{DEFAULT_BASE}/staging/pending", headers=_headers(), timeout=30.0)
    r.raise_for_status()
    data = r.json()
    print(json.dumps(data, indent=2))
    batch = data.get("batch")
    if open_md and batch:
        md = _batch_to_markdown(batch)
        path = os.path.join(tempfile.gettempdir(), f"herald_{batch.get('batch_id', 'draft')}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"\nWrote review file: {path}", file=sys.stderr)
    return 0


def _batch_to_markdown(batch: Dict[str, Any]) -> str:
    lines = [
        f"# Cheshire-Herald Draft — {batch.get('batch_id', '')}",
        f"Status: {batch.get('status', '')}",
        "",
        "## News context",
    ]
    for h in batch.get("news_context") or []:
        lines.append(f"- [{h.get('source', '')}] {h.get('title', '')}")
    platforms = batch.get("platforms") or {}
    lines.extend(["", "## LinkedIn", platforms.get("linkedin", {}).get("text", "")])
    lines.extend(["", "## X", platforms.get("x", {}).get("text", "")])
    lines.extend(["", "## Facebook", platforms.get("facebook", {}).get("text", "")])
    ig = platforms.get("instagram") or {}
    lines.extend(
        [
            "",
            "## Instagram (draft only)",
            f"### Script\n{ig.get('script_60s', '')}",
            f"### Visual\n{ig.get('visual_prompt', '')}",
            f"### Caption\n{ig.get('caption', '')}",
        ]
    )
    tt = platforms.get("tiktok") or {}
    lines.extend(
        [
            "",
            "## TikTok (draft only)",
            f"### Script\n{tt.get('script_60s', '')}",
            f"### Visual\n{tt.get('visual_prompt', '')}",
            f"### Caption\n{tt.get('caption', '')}",
        ]
    )
    return "\n".join(lines) + "\n"


def cmd_ratify(batch_id: str, platforms: List[str]) -> int:
    _require_salt()
    body = {"batch_id": batch_id, "platforms": platforms}
    r = httpx.post(
        f"{DEFAULT_BASE}/ratify-and-publish",
        headers=_headers(),
        json=body,
        timeout=60.0,
    )
    print(r.text)
    r.raise_for_status()
    return 0


def cmd_reject(batch_id: str) -> int:
    _require_salt()
    r = httpx.post(
        f"{DEFAULT_BASE}/staging/reject",
        headers=_headers(),
        json={"batch_id": batch_id},
        timeout=30.0,
    )
    print(r.text)
    r.raise_for_status()
    return 0


def cmd_draft() -> int:
    _require_salt()
    r = httpx.post(f"{DEFAULT_BASE}/cron/draft", headers=_headers(), timeout=120.0)
    print(r.text)
    r.raise_for_status()
    return 0


def cmd_health() -> int:
    r = httpx.get(f"{DEFAULT_BASE}/health", timeout=15.0)
    print(r.text)
    r.raise_for_status()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Cheshire-Herald local ratification client")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pending = sub.add_parser("pending", help="Fetch PENDING_HUMAN_PIVOT batch")
    p_pending.add_argument("--open", action="store_true", help="Write temp markdown for review")

    p_ratify = sub.add_parser("ratify", help="Ratify and publish to platforms")
    p_ratify.add_argument("--batch-id", required=True)
    p_ratify.add_argument(
        "--platforms",
        default="linkedin,x,facebook",
        help="Comma-separated: linkedin,x,facebook",
    )

    p_reject = sub.add_parser("reject", help="Reject batch without publishing")
    p_reject.add_argument("--batch-id", required=True)

    sub.add_parser("draft", help="Trigger weekly draft (dev)")
    sub.add_parser("health", help="GET /health")

    args = parser.parse_args()

    try:
        if args.command == "pending":
            return cmd_pending(open_md=getattr(args, "open", False))
        if args.command == "ratify":
            plats = [p.strip() for p in args.platforms.split(",") if p.strip()]
            return cmd_ratify(args.batch_id, plats)
        if args.command == "reject":
            return cmd_reject(args.batch_id)
        if args.command == "draft":
            return cmd_draft()
        if args.command == "health":
            return cmd_health()
    except httpx.HTTPError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
