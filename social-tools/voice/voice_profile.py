# @NCL{v=1.0;agent=claude;mod=voice-profile;tier=L2}
# #S{purpose="Build, save and load a voice profile: one person's (or the brand's) writing habits per register, as open JSON"}
# #I{1="Profile holds aggregates only: rates, averages, habit lists. Never a sample sentence";2="Personal profiles live in NOUS_VOICE_HOME on the device, never in the repo or cloud";3="Words that look like names, numbers or addresses are never kept as favorite words"}
# #F{1="Store sample messages for few-shot prompting"→"Copies private text into every drafting prompt and file; rates and habits are enough"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib";next="per-recipient sub-profiles once Brent opts in"}
# #T{status="python3 -m unittest discover -s voice/tests"}
# #X{2026-11-26="Created for the voice profile micro-module"}
from __future__ import annotations

import json
import os
import re
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import features as F

SCHEMA = "nous.voice-profile.v1"
REGISTERS = ("text", "email", "social", "chat")
HOME = Path(os.environ.get("NOUS_VOICE_HOME", Path.home() / ".nous-voice"))
REPO_VOICES = Path(__file__).resolve().parent / "voices"
MIN_SAMPLES = 20  # fewer and the numbers are noise; the profile says so instead of guessing

# Common English words: favorite-word scoring ignores these so it finds what is distinctive.
_COMMON = set(F.FUNCTION_WORDS) | set(
    "the be to of and a in that have it for not on with he as you do at this but his by from they we "
    "say her she or an will my one all would there their what so up out if about who get which go me "
    "when make can like time no just him know take people into year your good some could them see "
    "other than then now look only come its over think also back after use two how our work first "
    "well way even new want because any these give day most us is was are has had were been".split())


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mean_dict(dicts: list[dict]) -> dict:
    keys = {k for d in dicts for k in d}
    return {k: round(statistics.fmean([d.get(k, 0.0) for d in dicts]), 5) for k in sorted(keys)}


def _safe_word(w: str, seen_lower: Counter, seen_any: Counter) -> bool:
    """Keep a word as a habit only if it is plain lowercase text the person types lowercase.
    Capitalized-only words are probably names; anything with digits is dropped by the tokenizer."""
    return len(w) >= 3 and seen_lower[w] >= max(1, seen_any[w] // 2) and w.isalpha()


def build(samples: list[str], voice: str, register: str, wordlist: set[str] | None = None,
          top_n: int = 25) -> dict:
    """Aggregate many messages into one register profile."""
    if register not in REGISTERS:
        raise ValueError(f"register must be one of {REGISTERS}")
    texts = [F.clean_sample(s) for s in samples]
    texts = [t for t in texts if F.words(t)]
    ms = [F.measure(t) for t in texts]
    all_words = [w for t in texts for w in F.words(t)]
    lower_seen = Counter(w for w in all_words if w.islower())
    any_seen = Counter(w.lower() for w in all_words)
    tri = Counter()
    for t in texts:
        tri.update(F.char_ngrams(t))
    total_tri = sum(tri.values()) or 1
    distinctive = [(w, c) for w, c in any_seen.most_common()
                   if w not in _COMMON and c >= 2 and _safe_word(w, lower_seen, any_seen)]
    quirks = F.spelling_quirks(Counter({w: c for w, c in lower_seen.items()}), wordlist)
    no_apos = sorted({w.lower() for w in all_words if w.lower() in F.NO_APOSTROPHE
                      and w.lower() not in F.AMBIGUOUS_NO_APOSTROPHE})
    lens = [m["words"] for m in ms] or [0]
    return {
        "schema": SCHEMA,
        "voice": voice,
        "register": register,
        "built_utc": _now(),
        "samples": len(ms),
        "enough_samples": len(ms) >= MIN_SAMPLES,
        "cadence": {
            "msg_words_median": statistics.median(lens),
            "msg_words_p90": sorted(lens)[int(0.9 * (len(lens) - 1))],
            "sent_len_mean": round(statistics.fmean([m["sent_len_mean"] for m in ms]), 3) if ms else 0.0,
            "sent_len_sd": round(statistics.fmean([m["sent_len_sd"] for m in ms]), 3) if ms else 0.0,
            "word_len_mean": round(statistics.fmean([m["word_len_mean"] for m in ms]), 3) if ms else 0.0,
            "type_token": round(statistics.fmean([m["type_token"] for m in ms]), 3) if ms else 0.0,
        },
        "punctuation": _mean_dict([m["per_word"] for m in ms]),
        "sentences": _mean_dict([m["per_sentence"] for m in ms]),
        "function_words": _mean_dict([m["function_words"] for m in ms]),
        "char3": {g: round(c / total_tri, 6) for g, c in tri.most_common(300)},
        # Learned words can be names or private subjects, so they stay local and never reach a drafting
        # card until the person approves each one (approved_words). Codex PR 713.
        "favorite_words": [w for w, _ in distinctive[:top_n]],
        "approved_words": [],
        # Applied by personal/professional mode only when confirmed: a dictionary says the quirk is not a
        # word, or the person confirmed it. Letter swaps without a dictionary can be real words
        # (form/from), so they wait in spelling_candidates. Codex PR 713.
        "spelling_quirks": {k: v for k, v in quirks.items() if wordlist is not None},
        "spelling_candidates": {} if wordlist is not None else quirks,
        "no_apostrophe_words": no_apos,
        "privacy": "aggregates only; no sample text stored; favorite_words stay local until approved",
    }


def path_for(voice: str, register: str, home: Path | None = None) -> Path:
    if not re.fullmatch(r"[a-z0-9-]{1,40}", voice):
        raise ValueError("voice id: lowercase letters, digits and dashes")
    return (home or HOME) / "profiles" / f"{voice}.{register}.json"


def save(profile: dict, home: Path | None = None) -> Path:
    p = path_for(profile["voice"], profile["register"], home)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(profile, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, p)
    return p


def load(voice: str, register: str, home: Path | None = None) -> dict:
    """Device profile first; then a shareable seed in the repo (only the brand voice has one)."""
    p = path_for(voice, register, home)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    seed = REPO_VOICES / f"{voice}.seed.json"
    if seed.exists():
        data = json.loads(seed.read_text(encoding="utf-8"))
        return data.get("registers", {}).get(register) or data["registers"]["social"]
    raise FileNotFoundError(f"no profile for {voice}/{register}; build one with: cli.py build")


def read_samples(src: Path, register: str | None = None) -> list[str]:
    """Read samples from a folder of .txt files (one message each) or a JSONL file of
    {"text": ..., "register": ...}. Samples are read, measured and never copied."""
    if src.is_dir():
        return [p.read_text(encoding="utf-8", errors="replace") for p in sorted(src.glob("*.txt"))]
    out = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if register is None or row.get("register", register) == register:
            out.append(row["text"])
    return out


def approve_words(voice: str, register: str, words: list[str], home: Path | None = None) -> dict:
    """The person picks which learned words may appear in drafting cards."""
    pr = load(voice, register, home)
    pr["approved_words"] = sorted(set(pr.get("approved_words", [])) | {w.lower() for w in words if w.lower() in pr["favorite_words"]})
    save(pr, home)
    return pr


def confirm_quirk(voice: str, register: str, quirk: str, home: Path | None = None) -> dict:
    """Move a spelling candidate into the applied quirks after the person confirms it is their habit."""
    pr = load(voice, register, home)
    if quirk not in pr.get("spelling_candidates", {}):
        raise KeyError(f"{quirk!r} is not a spelling candidate")
    pr.setdefault("spelling_quirks", {})[quirk] = pr["spelling_candidates"].pop(quirk)
    save(pr, home)
    return pr
