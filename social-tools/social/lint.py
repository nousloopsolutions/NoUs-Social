# @NCL{v=1.0;agent=claude;mod=social-lint;tier=L2}
# #S{purpose="Brand and safety check for social drafts, shared rules with the site copy guard"}
# #I{1="Rules live in brand-rules.json only";2="A post that fails lint cannot be approved";3="No control or bidi characters: the approver must see every character"}
# #F{1="Separate rule lists per surface"→"They drift; one JSON file feeds JS and Python"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib"}
# #T{status="python3 -m unittest discover -s social/tests"}
# #X{2026-11-26="Created for the approval-gated social pipeline"}
"""Lint a social post: wellness-only, no patent internals, no trackers, no tagging people,
no urgency tricks, and the platform's length limit."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent.parent / "brand-rules.json"

# Character limits per platform (Bluesky counts graphemes; NFC code points is a close, conservative proxy).
LIMITS = {"bluesky": 300, "mastodon": 500, "linkedin": 3000}


def _flags(f: str) -> int:
    return re.IGNORECASE if "i" in (f or "") else 0


def load_rules(path: Path = RULES_PATH):
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for r in data["rules"]:
        if r.get("scope") not in (None, "social"):
            continue
        out.append((r["id"], re.compile(r["pattern"], _flags(r.get("flags", ""))),
                    re.compile(r["allow"], _flags(r.get("allow_flags", ""))) if r.get("allow") else None))
    return out


RULES = load_rules()


# Invisible or terminal-control characters could hide text from the person approving it.
_BIDI = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A)) | {0x200E, 0x200F, 0x061C}


def hidden_chars(text: str) -> list[str]:
    bad = []
    for ch in text:
        cp = ord(ch)
        if (unicodedata.category(ch) == "Cc" and ch != "\n") or cp in _BIDI:
            bad.append(f"U+{cp:04X}")
    return bad


def lint_post(text: str, platform: str) -> list[dict]:
    problems = []
    bad = hidden_chars(text or "")
    if bad:
        problems.append({"rule": "hidden-control", "detail": "control characters: " + ", ".join(sorted(set(bad)))})
    if platform not in LIMITS:
        problems.append({"rule": "platform", "detail": f"unknown platform {platform!r}"})
    if not text or not text.strip():
        problems.append({"rule": "empty", "detail": "post is empty"})
    for rule_id, rx, allow in RULES:
        for line in text.splitlines() or [text]:
            if rx.search(line) and not (allow and allow.search(line)):
                problems.append({"rule": rule_id, "detail": line.strip()[:120]})
    n = len(unicodedata.normalize("NFC", text))
    if platform in LIMITS and n > LIMITS[platform]:
        problems.append({"rule": "length", "detail": f"{n} > {LIMITS[platform]}"})
    return problems
