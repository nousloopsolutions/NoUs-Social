# @NCL{v=1.0;agent=claude;mod=social-cli;tier=L2}
# #S{purpose="Command line for the social queue: draft, review, approve, publish, metrics, export"}
# #I{1="approve needs a person at a terminal typing the post's check code and key passphrase";2="publish is a dry run without --live";3="Approver private key lives outside the queue, passphrase-encrypted"}
# #F{1="Approve by flag alone"→"An agent could approve in a script; require an interactive check code"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib"}
# #T{status="python3 -m unittest discover -s social/tests"}
# #X{2026-11-26="Created for the approval-gated social pipeline"}
"""Usage: python3 social/cli.py [--home DIR] <command> ...

Home defaults to $NOUS_SOCIAL_HOME or ~/.nous-social (kept off the repo; it is local data).
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

from lint import lint_post  # noqa: E402
from post_queue import GateError, Queue, content_hash, key_fingerprint  # noqa: E402

KEY_DIR = Path(os.environ.get("NOUS_SOCIAL_KEY_DIR", str(Path.home() / ".nous-social-approver")))
import engagement  # noqa: E402
import publish as pub  # noqa: E402


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def check_code(post: dict) -> str:
    return content_hash(post["platform"], post["text"])[:6]


def keygen(q: Queue, name: str, passphrase: str, key_dir: Path = KEY_DIR) -> str:
    key_dir.mkdir(parents=True, exist_ok=True)
    priv_path = key_dir / f"{name}.key"
    if priv_path.exists():
        raise GateError(f"{priv_path} exists; refusing to overwrite")
    if len(passphrase) < 12:
        raise GateError("use a passphrase of at least 12 characters")
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.BestAvailableEncryption(passphrase.encode("utf-8")))
    fd = os.open(priv_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(pem)
    pub = key.public_key()
    (q.home / "approvers" / f"{name}.pub").write_bytes(
        pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    return key_fingerprint(pub)


def signer(name: str, passphrase: str, key_dir: Path = KEY_DIR):
    path = key_dir / f"{name}.key"
    if not path.exists():
        raise GateError(f"no approver key for {name!r}; run approver-keygen first")
    try:
        key = serialization.load_pem_private_key(path.read_bytes(), passphrase.encode("utf-8"))
    except (ValueError, TypeError):
        raise GateError("wrong passphrase") from None
    return key.sign


def main(argv=None, stdin=None) -> int:
    stdin = stdin or sys.stdin
    ap = argparse.ArgumentParser(prog="nous-social")
    ap.add_argument("--home", default=os.environ.get("NOUS_SOCIAL_HOME", str(Path.home() / ".nous-social")))
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draft"); d.add_argument("platform"); d.add_argument("text", nargs="?")
    d.add_argument("--agent", required=True); d.add_argument("--at"); d.add_argument("--topic")
    d.add_argument("--model-base", default=None)
    sub.add_parser("list")
    s = sub.add_parser("show"); s.add_argument("id")
    e = sub.add_parser("edit"); e.add_argument("id"); e.add_argument("text"); e.add_argument("--as", dest="actor", required=True)
    k = sub.add_parser("approver-keygen"); k.add_argument("--as", dest="actor", required=True)
    a = sub.add_parser("approve"); a.add_argument("id"); a.add_argument("--as", dest="actor", required=True); a.add_argument("--note", default="")
    r = sub.add_parser("reject"); r.add_argument("id"); r.add_argument("--as", dest="actor", required=True); r.add_argument("--reason", default="")
    p = sub.add_parser("publish"); p.add_argument("id"); p.add_argument("--live", action="store_true")
    p.add_argument("--as", dest="actor", default="nous-social"); p.add_argument("--cap", type=int, default=1)
    m = sub.add_parser("mark-posted"); m.add_argument("id"); m.add_argument("platform_post_id"); m.add_argument("--url", default="")
    m.add_argument("--as", dest="actor", required=True)
    ca = sub.add_parser("clear-attempt"); ca.add_argument("id"); ca.add_argument("--as", dest="actor", required=True)
    sub.add_parser("kill"); sub.add_parser("unkill")
    mt = sub.add_parser("metrics"); mt.add_argument("id"); mt.add_argument("--set", nargs="*", default=None, help="key=int ...")
    sub.add_parser("export")
    sub.add_parser("verify")
    vc = sub.add_parser("voice", help="voice and 'sounds generic' report for a post (read-only)")
    vc.add_argument("id"); vc.add_argument("--voice", default="nous-brand"); vc.add_argument("--mode", default="professional")
    args = ap.parse_args(argv)
    q = Queue(args.home)
    try:
        if args.cmd == "draft":
            text, source = args.text, "manual"
            if args.topic:
                import draft_local
                text = draft_local.draft_text(args.topic, args.platform, args.model_base or draft_local.DEFAULT_BASE)
                source = "local-model"
            if not text:
                ap.error("give text or --topic")
            _print(q.draft(args.platform, text, args.agent, args.at, source))
        elif args.cmd == "list":
            for x in q.all():
                print(f"{x['id']}  {x['status']:<8} {x['platform']:<9} lint={len(x['lint'])}  {x['text'][:60]!r}")
        elif args.cmd == "show":
            post = q.get(args.id); post["check_code"] = check_code(post); _print(post)
        elif args.cmd == "edit":
            _print(q.edit(args.id, args.text, args.actor))
        elif args.cmd == "approver-keygen":
            if not stdin.isatty():
                raise GateError("keygen needs a person at an interactive terminal")
            pw = getpass.getpass("New approval passphrase: ")
            if pw != getpass.getpass("Again: "):
                raise GateError("passphrases did not match")
            fp = keygen(q, args.actor, pw)
            print(f"Key made. Pin it by setting NOUS_SOCIAL_TRUSTED_KEYS={args.actor}:{fp}")
        elif args.cmd == "approve":
            post = q.get(args.id)
            if not stdin.isatty():
                raise GateError("approve needs a person at an interactive terminal")
            reviewed = content_hash(post["platform"], post["text"])
            if lint_post(post["text"], post["platform"]):
                raise GateError("fix lint problems before approving (see show)")
            print(f"--- {post['platform']} ---\n{post['text']}\n---")
            typed = input(f"Type the check code {reviewed[:6]} to approve: ").strip()
            if typed != reviewed[:6]:
                raise GateError("check code did not match; not approved")
            sign = signer(args.actor, getpass.getpass("Approval passphrase: "))
            _print(q.approve(args.id, args.actor, reviewed, sign, args.note))
        elif args.cmd == "reject":
            _print(q.reject(args.id, args.actor, args.reason))
        elif args.cmd == "publish":
            _print(pub.publish(q, args.id, args.actor, live=args.live, daily_cap=args.cap))
        elif args.cmd == "mark-posted":
            _print(q.mark_posted(args.id, args.actor, args.platform_post_id, args.url))
        elif args.cmd == "clear-attempt":
            if not stdin.isatty():
                raise GateError("clear-attempt needs a person at an interactive terminal")
            post = q.get(args.id)
            seen = dict(post.get("attempt") or {})
            print(f"Check {post['platform']} by hand for this text and send key {post.get('attempt', {}).get('key')}:")
            print(post["text"])
            ok = input("Type NOT POSTED if it is not on the platform: ").strip() == "NOT POSTED"
            _print(q.clear_attempt(args.id, args.actor, ok, seen))
        elif args.cmd == "kill":
            (q.home / "KILL").write_text("on\n"); print("kill switch ON: nothing publishes")
        elif args.cmd == "unkill":
            (q.home / "KILL").unlink(missing_ok=True); print("kill switch off")
        elif args.cmd == "metrics":
            if args.set is None:
                counts = engagement.fetch_counts(q.get(args.id), dict(os.environ))
            else:
                counts = {k: int(v) for k, v in (kv.split("=", 1) for kv in args.set)}
            _print(engagement.record_metrics(q, args.id, counts))
        elif args.cmd == "export":
            for row in engagement.export_training(q):
                print(json.dumps(row, ensure_ascii=False))
        elif args.cmd == "voice":
            # Report only: the post is not changed, and the score never gates approval (Brent decides).
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "voice"))
            import voice as voice_mod
            post = q.get(args.id)
            _print(voice_mod.check(post["text"], args.voice, "social", args.mode))
        elif args.cmd == "verify":
            ok = q.verify_ledger(); print("ledger OK" if ok else "LEDGER BROKEN"); return 0 if ok else 1
    except GateError as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
