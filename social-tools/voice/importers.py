# @NCL{v=1.0;agent=claude;mod=voice-importers;tier=L2}
# #S{purpose="Read the owner's own sent messages from local exports: Gmail (Takeout mbox), Google Chat (Takeout JSON), Facebook Messenger (Download Your Information JSON)"}
# #I{1="Runs on the device only; nothing is uploaded";2="Keeps only messages the owner sent: other people's words are never read into a profile";3="Yields text in memory for build(); writes no raw copy"}
# #F{1="Pull mail through a cloud connector"→"Brent's private messages would pass through the cloud container; exports stay on Legion"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib";next="SMS backup (XML) importer when Brent picks a phone source"}
# #T{status="python3 -m unittest discover -s voice/tests"}
# #X{2026-11-26="Created after Brent picked Gmail, Google Chat and Messenger as sources"}
from __future__ import annotations

import email.policy
import json
import mailbox
import re
from email.utils import getaddresses
from pathlib import Path
from typing import Iterator


def _plain_body(msg) -> str:
    """Only the text/plain part. HTML-only mail is skipped: flattening HTML erases the quote
    boundaries (blockquote, gmail_quote), so other people's words would leak in (Codex PR 713)."""
    part = msg.get_body(preferencelist=("plain",))
    if part is None:
        return ""
    try:
        return part.get_content()
    except (LookupError, ValueError):
        return ""


def gmail_mbox(path: Path, owner_email: str) -> Iterator[tuple[str, str]]:
    """Google Takeout mail export (.mbox). Only messages whose From is the owner."""
    owner = owner_email.strip().lower()
    box = mailbox.mbox(str(path), factory=lambda f: email.message_from_binary_file(f, policy=email.policy.default))
    for msg in box:
        if msg is None:
            continue
        senders = [a.lower() for _, a in getaddresses([str(msg.get("From", ""))])]
        if owner not in senders:
            continue
        body = _plain_body(msg)
        if body.strip():
            yield "email", body


def google_chat(root: Path, owner_email: str) -> Iterator[tuple[str, str]]:
    """Google Takeout 'Google Chat' folder: Groups/*/messages.json and Users/*/messages.json."""
    owner = owner_email.strip().lower()
    for f in sorted(root.rglob("messages.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for m in data.get("messages", []):
            if (m.get("creator") or {}).get("email", "").lower() == owner and m.get("text", "").strip():
                yield "chat", m["text"]


def _fb_fix(s: str) -> str:
    """Facebook exports write UTF-8 bytes as Latin-1 escapes ('Ã©' for 'é'); undo that."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def messenger(root: Path, owner_name: str) -> Iterator[tuple[str, str]]:
    """Facebook 'Download Your Information' in JSON format: messages/inbox/*/message_*.json.
    Also reads the newer export shape (senderName/text)."""
    owner = owner_name.strip()
    for f in sorted(root.rglob("message_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for m in data.get("messages", []):
            sender = _fb_fix(m.get("sender_name") or m.get("senderName") or "")
            text = _fb_fix(m.get("content") or m.get("text") or "")
            if sender == owner and text.strip() and not m.get("is_unsent"):
                yield "text", text


SOURCES = {"gmail": gmail_mbox, "gchat": google_chat, "messenger": messenger}


def collect(kind: str, path: Path, owner: str) -> dict[str, list[str]]:
    if kind not in SOURCES:
        raise ValueError(f"source must be one of {sorted(SOURCES)}")
    out: dict[str, list[str]] = {}
    for register, text in SOURCES[kind](path, owner):
        out.setdefault(register, []).append(text)
    return out
