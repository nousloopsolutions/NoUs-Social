# @NCL{v=1.0;agent=claude;mod=voice-stylize;tier=L2}
# #S{purpose="Apply one mode to a draft: personal keeps the person's own quirks, professional cleans them"}
# #I{1="Applied once, from the profile only: this module never sees a detector score";2="Returns every change so the sender sees exactly what was altered";3="Deterministic: same draft and profile give the same output"}
# #F{1="Random typo injection"→"Fake noise is not the person's voice; only habits seen in their own writing are used, at their own rate"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib";next="per-recipient register choice"}
# #T{status="python3 -m unittest discover -s voice/tests"}
# #X{2026-11-26="Created for the voice profile micro-module"}
from __future__ import annotations

import re

import features as F

MODES = ("personal", "professional")


def _match_case(src: str, repl: str) -> str:
    return repl[:1].upper() + repl[1:] if src[:1].isupper() else repl


def _by_rate(share: float):
    """Yield True for occurrence k when the running rate says this one keeps the quirk."""
    k = 0
    while True:
        yield int((k + 1) * share + 1e-9) > int(k * share + 1e-9)
        k += 1


def personal(text: str, profile: dict) -> tuple[str, list[str]]:
    changes = []
    pw, ps = profile["punctuation"], profile["sentences"]
    fw_i = profile["function_words"].get("i", 0.0)
    if fw_i and pw.get("lowercase_i", 0.0) / fw_i >= 0.5:
        new = re.sub(r"\bI\b(?!')", "i", text)
        new = re.sub(r"\bI'", "i'", new)
        if new != text:
            changes.append("lowercase i (your habit)")
            text = new
    both = pw.get("contraction", 0.0) + pw.get("no_apostrophe", 0.0)
    if both and pw.get("no_apostrophe", 0.0) / both >= 0.5:
        for bare in profile.get("no_apostrophe_words", []):
            full = F.NO_APOSTROPHE[bare]
            rx = re.compile(r"\b" + re.escape(full).replace("'", "['’]") + r"\b", re.I)
            new = rx.sub(lambda m: _match_case(m.group(0), bare), text)
            if new != text:
                changes.append(f"{full} -> {bare}")
                text = new
    for quirk, info in sorted(profile.get("spelling_quirks", {}).items()):
        gate = _by_rate(info["share"])
        rx = re.compile(r"\b" + re.escape(info["intended"]) + r"\b", re.I)
        new = rx.sub(lambda m: _match_case(m.group(0), quirk) if next(gate) else m.group(0), text)
        if new != text:
            changes.append(f"{info['intended']} -> {quirk} (at your rate {info['share']:.0%})")
            text = new
    if ps.get("lower_start", 0.0) >= 0.6:
        new = re.sub(r"(^|[.!?]\s+|\n)([A-Z])(?=[a-z])", lambda m: m.group(1) + m.group(2).lower(), text)
        if new != text:
            changes.append("lowercase sentence starts")
            text = new
    if ps.get("no_end_punct", 0.0) >= 0.6 and text.rstrip().endswith(".") and not text.rstrip().endswith("..."):
        text = text.rstrip()[:-1]
        changes.append("no final period")
    return text, changes


def professional(text: str, profile: dict) -> tuple[str, list[str]]:
    changes = []
    for quirk, info in sorted(profile.get("spelling_quirks", {}).items()):
        rx = re.compile(r"\b" + re.escape(quirk) + r"\b", re.I)
        new = rx.sub(lambda m: _match_case(m.group(0), info["intended"]), text)
        if new != text:
            changes.append(f"{quirk} -> {info['intended']}")
            text = new
    for bare, full in F.NO_APOSTROPHE.items():
        if bare in F.AMBIGUOUS_NO_APOSTROPHE:
            continue
        new = re.sub(r"\b" + bare + r"\b", lambda m: _match_case(m.group(0), full), text, flags=re.I)
        if new != text:
            changes.append(f"{bare} -> {full}")
            text = new
    new = re.sub(r"\bi\b", "I", text)
    new = re.sub(r"\bi'", "I'", new)
    if new != text:
        changes.append("i -> I")
        text = new
    new = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    if new != text:
        changes.append("capitalized sentence starts")
        text = new
    return text, changes


# URLs, email addresses and inline code must leave byte-for-byte unchanged: a substitution inside
# one can change a recipient or break a link (Codex PR 713).
_PROTECT = re.compile(r"https?://\S+|www\.\S+|[\w.+-]+@[\w-]+(?:\.[\w-]+)+|`[^`]*`")


def _shield(text: str) -> tuple[str, list[str]]:
    spans: list[str] = []

    def keep(m):
        spans.append(m.group(0))
        return f"\ue000{len(spans) - 1}\ue001"
    return _PROTECT.sub(keep, text), spans


def _unshield(text: str, spans: list[str]) -> str:
    return re.sub("\ue000(\\d+)\ue001", lambda m: spans[int(m.group(1))], text)


def apply(text: str, profile: dict, mode: str) -> tuple[str, list[str]]:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    shielded, spans = _shield(text)
    out, changes = (personal if mode == "personal" else professional)(shielded, profile)
    return _unshield(out, spans), changes
