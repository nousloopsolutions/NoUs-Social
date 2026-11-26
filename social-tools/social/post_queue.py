# @NCL{v=1.0;agent=claude;mod=social-queue;tier=L2}
# #S{purpose="Local post queue with a human approval gate and a hash-chained provenance ledger"}
# #I{1="Nothing publishes without a human approval of the exact text";2="Editing clears approval";3="Ledger is append-only and hash-chained";4="Approver is never the drafting agent";5="Approval is an Ed25519 signature by a pinned approver key, over the hash the human saw"}
# #F{1="Approve by post id only"→"A later edit would ride on an old approval; bind approval to sha256 of platform+text";2="Plain checksum as approval"→"Anyone who can write the JSON forges it (Codex PR 694); require a signature from a passphrase-locked key";3="Re-read the post inside approve()"→"An edit during the prompt got approved; approve the hash the human saw, under a lock";4="Exclusive-create lock files"→"A crash left them stale and recovery raced (Codex PR 694); use OS locks that die with the process"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib + cryptography (Ed25519)"}
# #T{status="python3 -m unittest discover -s social/tests"}
# #X{2026-11-26="Created for the approval-gated social pipeline"}
"""Post queue. Plain JSON on disk (portable, no binary formats):

    <home>/posts/<id>.json   one file per post
    <home>/ledger.jsonl      append-only, hash-chained provenance events
    <home>/KILL              if this file exists, nothing publishes

States: draft -> approved -> posted, draft -> rejected. Editing an approved post returns it to draft.
"""
from __future__ import annotations

import base64
import contextlib
import datetime as _dt
import hashlib
import json
import os
import socket
import time
import uuid
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from lint import lint_post  # noqa: E402  (social/ is put on sys.path by cli.py and tests)

STATES = {"draft", "approved", "rejected", "posted"}


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc(ts: str) -> _dt.datetime:
    """ISO 8601 with an explicit offset or Z -> aware datetime in UTC. Naive times are refused."""
    try:
        d = _dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        raise GateError(f"bad timestamp {ts!r}") from None
    if d.tzinfo is None:
        raise GateError(f"timestamp {ts!r} needs a timezone, for example Z or -06:00")
    return d.astimezone(_dt.timezone.utc)


def to_utc_str(d: _dt.datetime) -> str:
    return d.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def content_hash(platform: str, text: str) -> str:
    return hashlib.sha256(f"{platform}\n{text}".encode("utf-8")).hexdigest()


def _try_os_lock(fd: int) -> bool:
    """Non-blocking OS lock on byte 0. The OS drops it when the process exits, so a crash
    can never leave a stale lock, and a lock file on disk means nothing by itself."""
    try:
        if os.name == "nt":
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def _os_unlock(fd: int) -> None:
    if os.name == "nt":
        import msvcrt
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_UN)


class GateError(Exception):
    """Raised when an action would bypass the approval gate."""


def approval_message(post_id: str, platform: str, sha: str, approver: str, at: str) -> bytes:
    """The exact bytes an approver signs."""
    return json.dumps({"v": 1, "post_id": post_id, "platform": platform, "content_sha256": sha,
                       "approver": approver, "at": at}, sort_keys=True).encode("utf-8")


def key_fingerprint(public_key: Ed25519PublicKey) -> str:
    raw = public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return hashlib.sha256(raw).hexdigest()


def parse_trusted(spec: str) -> dict[str, str]:
    """'brent:<sha256 fingerprint>,other:<fp>' -> {name: fp}."""
    out = {}
    for item in filter(None, (x.strip() for x in (spec or "").split(","))):
        name, _, fp = item.partition(":")
        if name and len(fp) == 64:
            out[name] = fp.lower()
    return out


class Queue:
    def __init__(self, home: str | os.PathLike, trusted_keys: dict[str, str] | None = None):
        self.home = Path(home)
        (self.home / "posts").mkdir(parents=True, exist_ok=True)
        (self.home / "approvers").mkdir(exist_ok=True)
        self.ledger = self.home / "ledger.jsonl"
        # Humans allowed to approve, each pinned to the fingerprint of their Ed25519 key.
        # Brent sets NOUS_SOCIAL_TRUSTED_KEYS himself; with none set, nothing can be approved.
        self.trusted = trusted_keys if trusted_keys is not None else parse_trusted(
            os.environ.get("NOUS_SOCIAL_TRUSTED_KEYS", ""))

    @property
    def approvers(self) -> set[str]:
        return set(self.trusted)

    def public_key(self, name: str) -> Ed25519PublicKey:
        """The approver's public key, only if it matches the pinned fingerprint."""
        if name not in self.trusted:
            raise GateError(f"{name!r} is not a trusted approver")
        path = self.home / "approvers" / f"{name}.pub"
        if not path.exists():
            raise GateError(f"no public key for {name!r}")
        key = serialization.load_pem_public_key(path.read_bytes())
        if not isinstance(key, Ed25519PublicKey) or key_fingerprint(key) != self.trusted[name]:
            raise GateError(f"public key for {name!r} does not match the pinned fingerprint")
        return key

    @contextlib.contextmanager
    def _filelock(self, lock: Path, wait: float = 0.0, busy: str = "busy"):
        """Interprocess lock held by the OS for this process's lifetime (flock / msvcrt).
        Waits up to `wait` seconds. The lock file stays on disk; only the OS lock matters."""
        deadline = time.monotonic() + wait
        fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            while not _try_os_lock(fd):
                if time.monotonic() >= deadline:
                    raise GateError(busy)
                time.sleep(0.02)
            try:
                yield
            finally:
                _os_unlock(fd)
        finally:
            os.close(fd)

    def post_lock(self, post_id: str):
        return self._lock(post_id)

    def _lock(self, post_id: str):
        return self._filelock(self._path(post_id).with_suffix(".lock"),
                              busy="post is busy (another action holds its lock)")

    def platform_lock(self, platform: str):
        """Held from the daily-cap check through recording a publication."""
        if not platform.isalnum():
            raise ValueError("bad platform")
        return self._filelock(self.home / f"publish-{platform}.lock", wait=30,
                              busy=f"another {platform} publish is in progress")

    # ---- storage -------------------------------------------------------------------------
    def _path(self, post_id: str) -> Path:
        if not post_id.replace("-", "").isalnum():
            raise ValueError("bad post id")
        return self.home / "posts" / f"{post_id}.json"

    def get(self, post_id: str) -> dict:
        return json.loads(self._path(post_id).read_text(encoding="utf-8"))

    def _save(self, post: dict) -> None:
        p = self._path(post["id"])
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(post, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, p)

    def all(self) -> list[dict]:
        return sorted((json.loads(p.read_text(encoding="utf-8")) for p in (self.home / "posts").glob("*.json")),
                      key=lambda x: x["created_at"])

    # ---- provenance ----------------------------------------------------------------------
    def _last_hash(self) -> str:
        if not self.ledger.exists():
            return "0" * 64
        last = None
        with self.ledger.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    last = line
        return json.loads(last)["hash"] if last else "0" * 64

    def _record(self, actor: str, action: str, post: dict, extra: dict | None = None) -> None:
        with self._filelock(self.home / "ledger.lock", wait=10, busy="ledger is busy"):
            self._append_event(actor, action, post, extra)

    def _append_event(self, actor: str, action: str, post: dict, extra: dict | None) -> None:
        event = {
            "ts": now_utc(),
            "actor": actor,
            "machine": os.environ.get("NOUS_MACHINE") or socket.gethostname(),
            "session": os.environ.get("NOUS_SESSION", "UNKNOWN"),
            "action": action,
            "post_id": post["id"],
            "platform": post["platform"],
            "content_sha256": content_hash(post["platform"], post["text"]),
            **(extra or {}),
            "previous_hash": self._last_hash(),
        }
        event["hash"] = hashlib.sha256(json.dumps(event, sort_keys=True).encode("utf-8")).hexdigest()
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")

    def verify_ledger(self) -> bool:
        prev = "0" * 64
        if not self.ledger.exists():
            return True
        for line in self.ledger.read_text(encoding="utf-8").splitlines():
            ev = json.loads(line)
            h = ev.pop("hash")
            if ev["previous_hash"] != prev or hashlib.sha256(json.dumps(ev, sort_keys=True).encode()).hexdigest() != h:
                return False
            prev = h
        return True

    # ---- actions -------------------------------------------------------------------------
    def draft(self, platform: str, text: str, agent: str, scheduled_for: str | None = None, source: str = "manual") -> dict:
        if scheduled_for:
            scheduled_for = to_utc_str(parse_utc(scheduled_for))  # stored normalized to UTC
        post = {
            "id": uuid.uuid4().hex[:12],
            "platform": platform,
            "text": text,
            "status": "draft",
            "created_by": agent,
            "created_at": now_utc(),
            "source": source,
            "scheduled_for": scheduled_for,
            "lint": lint_post(text, platform),
            "approval": None,
            "history": [],
            "posted": None,
        }
        self._save(post)
        self._record(agent, "draft", post, {"source": source})
        return post

    def edit(self, post_id: str, text: str, actor: str) -> dict:
        with self._lock(post_id):
            return self._edit(post_id, text, actor)

    def _edit(self, post_id: str, text: str, actor: str) -> dict:
        post = self.get(post_id)
        if post["status"] == "posted":
            raise GateError("already posted")
        self._refuse_if_unresolved(post)
        # Role is fixed at edit time, so later changes to the trust pins can't relabel history.
        role = "human" if actor in self.approvers else "agent"
        post["history"].append({"at": now_utc(), "by": actor, "role": role, "old_text": post["text"]})
        post["text"] = text
        post["lint"] = lint_post(text, post["platform"])
        post["approval"] = None
        post["status"] = "draft"
        self._save(post)
        self._record(actor, "edit", post)
        return post

    def approve(self, post_id: str, approver: str, reviewed_sha256: str, sign, note: str = "") -> dict:
        """Approve the content the human reviewed. `sign(bytes) -> bytes` signs with the
        approver's passphrase-locked key (see cli.py). Fails if the post changed since review."""
        with self._lock(post_id):
            post = self.get(post_id)
            if approver == post["created_by"]:
                raise GateError("the drafting agent cannot approve its own post")
            key = self.public_key(approver)
            if post["status"] != "draft":
                raise GateError(f"cannot approve a {post['status']} post")
            sha = content_hash(post["platform"], post["text"])
            if sha != reviewed_sha256:
                raise GateError("post changed after you reviewed it; review it again")
            post["lint"] = lint_post(post["text"], post["platform"])
            if post["lint"]:
                raise GateError("lint problems: " + ", ".join(p["rule"] for p in post["lint"]))
            at = now_utc()
            sig = sign(approval_message(post_id, post["platform"], sha, approver, at))
            try:
                key.verify(sig, approval_message(post_id, post["platform"], sha, approver, at))
            except InvalidSignature:
                raise GateError("signature does not match the approver's pinned key") from None
            post["approval"] = {"by": approver, "at": at, "note": note, "content_sha256": sha,
                                "signature": base64.b64encode(sig).decode("ascii")}
            post["status"] = "approved"
            self._save(post)
            self._record(approver, "approve", post, {"note": note})
            return post

    def verify_approval(self, post: dict) -> None:
        """Raise GateError unless the approval is a valid signature over this exact content."""
        appr = post.get("approval") or {}
        if post.get("status") != "approved" or not appr.get("signature"):
            raise GateError("not approved")
        sha = content_hash(post["platform"], post["text"])
        if appr.get("content_sha256") != sha:
            raise GateError("text changed after approval")
        if appr.get("by") == post.get("created_by"):
            raise GateError("the drafting agent cannot approve its own post")
        key = self.public_key(appr.get("by", ""))
        try:
            key.verify(base64.b64decode(appr["signature"]),
                       approval_message(post["id"], post["platform"], sha, appr["by"], appr["at"]))
        except (InvalidSignature, ValueError):
            raise GateError("approval signature is not valid") from None

    def reject(self, post_id: str, approver: str, reason: str = "") -> dict:
        with self._lock(post_id):
            return self._reject(post_id, approver, reason)

    def _reject(self, post_id: str, approver: str, reason: str = "") -> dict:
        post = self.get(post_id)
        self._refuse_if_unresolved(post)
        if approver not in self.approvers:
            raise GateError(f"{approver!r} is not an approver")
        if post["status"] == "posted":
            raise GateError("already posted")
        post["status"] = "rejected"
        post["approval"] = None
        post["rejection"] = {"by": approver, "at": now_utc(), "reason": reason}
        self._save(post)
        self._record(approver, "reject", post, {"reason": reason})
        return post

    def check_publishable(self, post: dict, now: str | None = None, daily_cap: int = 1) -> None:
        """Raise GateError unless this exact post may go out now."""
        if (self.home / "KILL").exists():
            raise GateError("kill switch is on")
        self.verify_approval(post)
        if lint_post(post["text"], post["platform"]):
            raise GateError("lint problems")
        now = now or now_utc()
        now_dt = parse_utc(now)
        if post.get("scheduled_for") and parse_utc(post["scheduled_for"]) > now_dt:
            raise GateError("not due yet")
        today = to_utc_str(now_dt)[:10]
        def used_today(p: dict) -> bool:
            # Every started send counts on its own UTC day, as does the final publication.
            stamps = list((p.get("attempt") or {}).get("sends", []))
            stamps.append((p.get("posted") or {}).get("at") or "")
            return any(st[:10] == today for st in stamps)
        # A post with an unresolved send attempt counts too, so a lost response can't free quota.
        sent_today = [p for p in self.all() if p["platform"] == post["platform"]
                      and p["id"] != post["id"] and used_today(p)]
        if len(sent_today) >= daily_cap:
            raise GateError(f"daily cap of {daily_cap} reached for {post['platform']}")

    def mark_posted(self, post_id: str, actor: str, platform_post_id: str, url: str = "",
                    daily_cap: int = 1) -> dict:
        """Manual path (for example LinkedIn, posted by hand): the gate is checked first."""
        platform = self.get(post_id)["platform"]
        with self.platform_lock(platform), self._lock(post_id):
            post = self.get(post_id)
            self.check_publishable(post, daily_cap=daily_cap)
            return self.record_posted(post, actor, platform_post_id, url)

    @staticmethod
    def _refuse_if_unresolved(post: dict) -> None:
        if post.get("attempt") and post.get("status") != "posted":
            raise GateError("a send attempt is unresolved: run publish again to reconcile it, or, "
                            "after checking the platform by hand, clear-attempt")

    def clear_attempt(self, post_id: str, approver: str, checked_not_posted: bool,
                      reviewed_attempt: dict | None = None) -> dict:
        """A human confirms on the platform that the attempt did not publish. Only then may the
        post be edited or rejected; its old send key is kept in history."""
        if approver not in self.approvers:
            raise GateError(f"{approver!r} is not an approver")
        if not checked_not_posted:
            raise GateError("confirm you checked the platform and the post is not there")
        with self._lock(post_id):
            post = self.get(post_id)
            if not post.get("attempt") or post["status"] == "posted":
                raise GateError("no unresolved attempt")
            seen = reviewed_attempt or {}
            if (seen.get("key"), seen.get("sends")) != (post["attempt"]["key"], post["attempt"].get("sends", [])):
                raise GateError("the send state changed since you checked; check the platform again")
            post.setdefault("cleared_attempts", []).append({**post["attempt"], "cleared_by": approver,
                                                            "cleared_at": now_utc()})
            post["attempt"] = None
            self._save(post)
            self._record(approver, "clear-attempt", post)
            return post

    def begin_attempt(self, post: dict, actor: str, key: str) -> dict:
        """Persist a stable send key before the first request, so a retry reuses it."""
        post["attempt"] = {"key": key, "at": now_utc(), "by": actor, "sends": []}
        self._save(post)
        self._record(actor, "attempt", post, {"attempt_key": key})
        return post

    def start_send(self, post: dict) -> int:
        """Persist that a send is starting, before any request. Returns how many sends started
        earlier; anything above 0 means an earlier send may have been accepted."""
        sends = post["attempt"].setdefault("sends", [])
        prior = len(sends)
        sends.append(now_utc())
        self._save(post)
        return prior

    def record_posted(self, post: dict, actor: str, platform_post_id: str, url: str = "") -> dict:
        """Called only after check_publishable passed and the platform accepted it, with
        platform_lock and the post lock held (publish.publish and mark_posted)."""
        post["status"] = "posted"
        post["posted"] = {"at": now_utc(), "by": actor, "platform_post_id": platform_post_id, "url": url}
        self._save(post)
        self._record(actor, "posted", post, {"platform_post_id": platform_post_id})
        return post
