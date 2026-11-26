# @NCL{v=1.0;agent=claude;mod=voice-api;tier=L1}
# #S{purpose="The one interface agents call: style card for drafting, check before sending, outcome after Brent decides"}
# #I{1="check() reports; it never rewrites and never loops";2="Learning log holds scores, habit names and edit size: never draft text";3="Log records use the gap-event v1 shape so the THAOT gap bus can ingest them"}
# #F{1="Gate sends on the detector"→"A gate makes passing the detector the goal; Brent reviews instead (I do, we do, you do)"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib";next="gap_bus adapter that tails learning.jsonl; voice-out (TTS) uses the same profile for cadence"}
# #T{status="python3 -m unittest discover -s voice/tests"}
# #X{2026-11-26="Created for the voice profile micro-module"}
"""Voice micro-module.

    card(voice, register, mode)              -> markdown brief for any drafting agent
    check(text, voice, register, mode, ...)  -> report: similarity, generic signal, mode changes, check_id
    outcome(check_id, action, draft, final)  -> logs what Brent did (sent / edited / rejected)
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import detect
import voice_profile as P
import similarity
import stylize

GAP_SCHEMA = "nous.gap-event.v1"
SOURCE = "voice"
DRIFT_LINE = 0.55   # below this, the drift becomes a held gap to learn from
GENERIC_LINE = 0.5


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gap(kind: str, summary: str, dedupe_key: str, props: dict, severity: str = "INFO") -> dict:
    eid = "GAP-" + hashlib.sha256(f"{SOURCE}\x1f{dedupe_key}".encode()).hexdigest()[:16]
    return {"schema": GAP_SCHEMA, "source": SOURCE, "kind": kind, "severity": severity,
            "summary": summary[:280], "dedupe_key": dedupe_key, "properties": props,
            "created_utc": _now(), "event_id": eid}


def _log(rows: list[dict], home: Path | None) -> None:
    if not rows:
        return
    p = (home or P.HOME) / "learning.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def detectors_from_env() -> list:
    ds = [detect.HeuristicDetector()]
    base = os.environ.get("NOUS_VOICE_DETECTOR")
    if base:
        ds.append(detect.LoopbackDetector(base))
    return ds


def card(voice: str, register: str, mode: str = "personal", home: Path | None = None) -> str:
    """A short, plain brief any agent (Claude, Codex, Hermes, a local model) puts in its drafting prompt."""
    pr = P.load(voice, register, home)
    if pr.get("kind") == "brand":
        return pr["card"]
    c, pw, ps = pr["cadence"], pr["punctuation"], pr["sentences"]
    lines = [f"# Write as {voice} ({register}, {mode})", "",
             f"- Length: about {c['msg_words_median']:.0f} words (rarely over {c['msg_words_p90']:.0f}).",
             f"- Sentences average {c['sent_len_mean']:.0f} words and vary (spread {c['sent_len_sd']:.0f}). Mix short and long.",
             ]
    # Only words the person approved: learned vocabulary can carry names or private subjects (Codex PR 713).
    if pr.get("approved_words"):
        lines.append(f"- Words this voice reaches for: {', '.join(pr['approved_words'][:12])}.")
    if pw.get("exclaim", 0) < 0.002:
        lines.append("- Almost never uses exclamation marks.")
    if pw.get("emdash", 0) < 0.001:
        lines.append("- Doesn't use em dashes. Use a comma, a period or ' - ' instead.")
    if pw.get("ellipsis", 0) > 0.01:
        lines.append("- Trails off with '...' sometimes.")
    if pw.get("emoji", 0) > 0.005:
        lines.append("- Uses an emoji now and then.")
    if mode == "personal":
        if ps.get("lower_start", 0) >= 0.6:
            lines.append("- Often starts sentences lowercase.")
        if ps.get("no_end_punct", 0) >= 0.6:
            lines.append("- Often skips the final period.")
        if pr.get("spelling_quirks"):
            lines.append("- Personal mode applies this voice's own spellings after drafting; write normally.")
    else:
        lines.append("- Professional: correct spelling and casing, same plain directness.")
    lines += ["- Never: 'I hope this email finds you well', 'delve', 'feel free to', 'I'd be happy to', stock sign-offs.",
              "- Say the point first. Plain words. No hype.",
              "- Brent reviews and sends. Don't claim things he didn't say."]
    if not pr.get("enough_samples"):
        lines.append(f"- Note: built from only {pr['samples']} samples; treat as rough.")
    return "\n".join(lines)


def check(text: str, voice: str, register: str, mode: str = "personal", detectors=None,
          home: Path | None = None, log: bool = True) -> dict:
    pr = P.load(voice, register, home)
    styled, changes = stylize.apply(text, pr, mode) if pr.get("kind") != "brand" else (text, [])
    sim = similarity.score(styled, pr) if pr.get("kind") != "brand" else {"similarity": None, "confidence": "n/a", "deltas": []}
    det = detect.run_all(styled, detectors if detectors is not None else detectors_from_env())
    cid = uuid.uuid4().hex[:12]
    generic = max((d["generic"] for d in det if d.get("generic") is not None), default=None)
    report = {"check_id": cid, "voice": voice, "register": register, "mode": mode,
              "styled_text": styled, "mode_changes": changes, "similarity": sim, "detectors": det,
              "generic": generic, "note": "signals for the sender; nothing was rewritten to pass a detector"}
    rows = [{"schema": "nous.voice-check.v1", "check_id": cid, "ts": _now(), "voice": voice,
             "register": register, "mode": mode, "similarity": sim["similarity"], "confidence": sim["confidence"],
             "generic": generic, "detectors": [d["detector"] for d in det],
             "drift_habits": [d["habit"] for d in sim["deltas"]], "words": len(styled.split())}]
    if sim["similarity"] is not None and sim["similarity"] < DRIFT_LINE:
        rows.append(_gap("MISSING_VARIABLE", f"draft drifted from {voice}/{register}: " +
                         ", ".join(d["habit"] for d in sim["deltas"][:3]), f"{cid}:drift",
                         {"similarity": sim["similarity"], "register": register, "mode": mode}))
    if generic is not None and generic >= GENERIC_LINE:
        rows.append(_gap("ABSENCE", f"voice signal missing in {register} draft (reads generic)", f"{cid}:generic",
                         {"generic": generic, "register": register, "mode": mode}))
    if log:
        _log(rows, home)
    return report


def outcome(check_id: str, action: str, draft: str, final: str | None = None, home: Path | None = None) -> dict:
    """Brent's decision is the best teacher. Only the size of his edit is kept, not the words."""
    if action not in ("sent", "edited", "rejected"):
        raise ValueError("action: sent, edited or rejected")
    ratio = 1.0 if final is None else round(difflib.SequenceMatcher(None, draft, final).ratio(), 3)
    row = {"schema": "nous.voice-outcome.v1", "check_id": check_id, "ts": _now(), "action": action,
           "kept_ratio": ratio if action != "rejected" else 0.0}
    rows = [row]
    if action == "rejected" or ratio < 0.7:
        rows.append(_gap("LOOP_FAILURE", f"Brent {action} a voice draft (kept {row['kept_ratio']:.0%})",
                         f"{check_id}:outcome", {"kept_ratio": row["kept_ratio"], "action": action}, "WARNING"))
    _log(rows, home)
    return row
