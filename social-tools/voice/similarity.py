# @NCL{v=1.0;agent=claude;mod=voice-similarity;tier=L2}
# #S{purpose="Score how close a draft is to a voice profile, and say in plain words where it drifts"}
# #I{1="Explains every score with named deltas";2="Short drafts get a low-confidence flag, not a confident number"}
# #F{1="Single opaque score"→"Brent can't act on a number; deltas name the habit that is off"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib";next="calibrate weights on Brent's approve/edit outcomes (learning.jsonl)"}
# #T{status="python3 -m unittest discover -s voice/tests"}
# #X{2026-11-26="Created for the voice profile micro-module"}
from __future__ import annotations

import math

import features as F

LABELS = {
    "comma": "commas", "exclaim": "exclamation marks", "question": "question marks",
    "ellipsis": "ellipses (...)", "dash": "dashes", "emdash": "em dashes", "semicolon": "semicolons",
    "colon": "colons", "paren": "parentheses", "emoji": "emoji", "all_caps_word": "ALL CAPS words",
    "lowercase_i": "lowercase 'i'", "no_apostrophe": "contractions without apostrophes",
    "contraction": "contractions", "lower_start": "lowercase sentence starts",
    "no_end_punct": "sentences without end punctuation", "and_start": "sentences starting with and/but/so",
}


def cosine(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _closeness(draft: float, habit: float, floor: float) -> float:
    """1.0 when equal, falling toward 0 as the gap grows relative to the habit (or a floor rate)."""
    return 1.0 / (1.0 + abs(draft - habit) / max(habit, floor))


def score(text: str, profile: dict) -> dict:
    m = F.measure(text)
    tri = F.char_ngrams(F.clean_sample(text))
    total = sum(tri.values()) or 1
    tri_n = {g: c / total for g, c in tri.items()}
    fw = cosine(m["function_words"], profile["function_words"])
    c3 = cosine(tri_n, profile["char3"])
    deltas, closes = [], []
    for group, key in (("punctuation", "per_word"), ("sentences", "per_sentence")):
        for name, habit in profile[group].items():
            d = m[key].get(name, 0.0)
            cl = _closeness(d, habit, 0.01 if key == "per_word" else 0.1)
            closes.append(cl)
            if cl < 0.6:
                more = "more" if d > habit else "fewer"
                deltas.append({"habit": name, "draft": d, "profile": habit,
                               "say": f"draft uses {more} {LABELS.get(name, name)} than this voice"})
    cad = profile["cadence"]
    sl = _closeness(m["sent_len_mean"], cad["sent_len_mean"], 3.0)
    if sl < 0.6:
        longer = "longer" if m["sent_len_mean"] > cad["sent_len_mean"] else "shorter"
        deltas.append({"habit": "sent_len_mean", "draft": m["sent_len_mean"], "profile": cad["sent_len_mean"],
                       "say": f"sentences are {longer} than usual ({m['sent_len_mean']:.0f} vs {cad['sent_len_mean']:.0f} words)"})
    habits = sum(closes) / len(closes) if closes else 0.0
    total_score = round(0.35 * fw + 0.25 * c3 + 0.25 * habits + 0.15 * sl, 3)
    confidence = "low" if m["words"] < 40 or not profile.get("enough_samples", False) else "normal"
    deltas.sort(key=lambda d: abs(d["draft"] - d["profile"]), reverse=True)
    return {"similarity": total_score, "confidence": confidence,
            "parts": {"function_words": round(fw, 3), "char3": round(c3, 3), "habits": round(habits, 3),
                      "sentence_length": round(sl, 3)},
            "deltas": deltas[:6]}
