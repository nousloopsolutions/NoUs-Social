# @NCL{v=1.0;agent=claude;mod=voice-cli;tier=L2}
# #S{purpose="Command line for the voice module: build a profile, print a drafting card, check a draft, log the outcome"}
# #I{1="Profiles and logs go to NOUS_VOICE_HOME (default ~/.nous-voice), never the repo"}
# #F{1="Read samples into the repo for reuse"→"Private text would be committed; build reads in place and stores aggregates only"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib"}
# #T{status="python3 -m unittest discover -s voice/tests"}
# #X{2026-11-26="Created for the voice profile micro-module"}
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import importers  # noqa: E402
import voice_profile as P  # noqa: E402
import voice as V  # noqa: E402


def _wordlist():
    p = os.environ.get("NOUS_VOICE_WORDLIST")
    if p and Path(p).exists():
        return {w.strip().lower() for w in Path(p).read_text(encoding="utf-8", errors="replace").split()}
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="voice")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("voice"); b.add_argument("register"); b.add_argument("source")
    c = sub.add_parser("card"); c.add_argument("voice"); c.add_argument("register"); c.add_argument("--mode", default="personal")
    k = sub.add_parser("check"); k.add_argument("voice"); k.add_argument("register"); k.add_argument("text", nargs="?")
    k.add_argument("--mode", default="personal")
    o = sub.add_parser("outcome"); o.add_argument("check_id"); o.add_argument("action")
    o.add_argument("--draft-file", required=True); o.add_argument("--final-file")
    ln = sub.add_parser("learn", help="build profiles straight from a local export; no raw copy is written")
    ln.add_argument("voice"); ln.add_argument("source", choices=sorted(importers.SOURCES)); ln.add_argument("path")
    ln.add_argument("--owner", required=True, help="your own address (gmail, gchat) or display name (messenger)")
    aw = sub.add_parser("approve-words"); aw.add_argument("voice"); aw.add_argument("register"); aw.add_argument("words", nargs="+")
    cq = sub.add_parser("confirm-quirk"); cq.add_argument("voice"); cq.add_argument("register"); cq.add_argument("quirk")
    sh = sub.add_parser("show"); sh.add_argument("voice"); sh.add_argument("register")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        pr = P.build(P.read_samples(Path(a.source), a.register), a.voice, a.register, _wordlist())
        path = P.save(pr)
        print(json.dumps({"saved": str(path), "samples": pr["samples"], "enough_samples": pr["enough_samples"],
                          "spelling_quirks": len(pr["spelling_quirks"]), "spelling_candidates": len(pr["spelling_candidates"]),
                          "next": "review with: show, then approve-words and confirm-quirk"}))
    elif a.cmd == "learn":
        got = importers.collect(a.source, Path(a.path), a.owner)
        res = {}
        for register, texts in got.items():
            pr = P.build(texts, a.voice, register, _wordlist())
            P.save(pr)
            res[register] = {"samples": pr["samples"], "enough_samples": pr["enough_samples"],
                             "spelling_candidates": len(pr["spelling_candidates"])}
        print(json.dumps({"built": res, "next": "review with: show, then approve-words and confirm-quirk"}))
    elif a.cmd == "approve-words":
        print(json.dumps({"approved_words": P.approve_words(a.voice, a.register, a.words)["approved_words"]}))
    elif a.cmd == "confirm-quirk":
        print(json.dumps({"spelling_quirks": P.confirm_quirk(a.voice, a.register, a.quirk)["spelling_quirks"]}))
    elif a.cmd == "show":
        pr = P.load(a.voice, a.register)
        print(json.dumps({k: pr.get(k) for k in ("samples", "favorite_words", "approved_words", "spelling_quirks", "spelling_candidates")}, indent=1))
    elif a.cmd == "card":
        print(V.card(a.voice, a.register, a.mode))
    elif a.cmd == "check":
        text = a.text if a.text is not None else sys.stdin.read()
        print(json.dumps(V.check(text, a.voice, a.register, a.mode), indent=1, ensure_ascii=False))
    elif a.cmd == "outcome":
        final = Path(a.final_file).read_text(encoding="utf-8") if a.final_file else None
        print(json.dumps(V.outcome(a.check_id, a.action, Path(a.draft_file).read_text(encoding="utf-8"), final)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
