# @NCL{v=1.0;agent=claude;mod=voice-detect;tier=L2}
# #S{purpose="'Sounds generic' signal for drafts: a stdlib heuristic plus an optional local detector (Binoculars-style) on loopback"}
# #I{1="A detector score is a signal for Brent and the learning log, never a target: nothing here rewrites text";2="Local detector endpoints must be loopback; no cloud detector gets Brent's drafts";3="Every result names which detector ran and its known weakness"}
# #F{1="Rewrite until the detector passes"→"Optimizes for evasion, not authenticity (N32); detectors also misfire on non-native and autistic writing (Liang 2023; Chambers and Kelley 2026)";2="Google SynthID as the detector"→"Only finds Google's own watermark; Claude, Codex and local models carry none"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib; optional local Binoculars server";next="Hermes runs Binoculars (Falcon-7B pair) on Legion or BIGG RIGG behind 127.0.0.1"}
# #T{status="python3 -m unittest discover -s voice/tests"}
# #X{2026-11-26="Created for the voice profile micro-module"}
from __future__ import annotations

import json
import re
import statistics
import urllib.error
import urllib.parse
import urllib.request

import features as F

# Stock phrases that chat assistants overuse. Matching one is not proof; it is a cue a person would notice.
STOCK_PHRASES = [
    r"\bi hope this (email|message) finds you well\b", r"\bdelve\b", r"\bit'?s (important|worth) (to note|noting)\b",
    r"\bin today'?s (fast-paced|digital) world\b", r"\bplease don'?t hesitate to\b", r"\bi'?d be happy to\b",
    r"\bfeel free to\b", r"\bi wanted to reach out\b", r"\bjust circling back\b", r"\bas an ai\b",
    r"\bcertainly!", r"\bgreat question\b", r"\btapestry\b", r"\bnavigat(e|ing) the (complexities|landscape)\b",
    r"\bseamless(ly)?\b", r"\brobust\b", r"\bleverag(e|ing)\b", r"\bunlock (the|your)\b", r"\bgame[- ]changer\b",
    r"\bin conclusion\b", r"\bmoreover\b", r"\bfurthermore\b", r"\bi hope this helps\b", r"\blet me know if you have any (other )?questions\b",
]
_STOCK = [re.compile(p, re.I) for p in STOCK_PHRASES]


class HeuristicDetector:
    """No model needed. Looks for stock phrases, em-dash density and flat sentence rhythm.
    Weak on purpose: it can only say 'this reads generic', never 'a machine wrote this'."""
    name = "heuristic-v1"
    caveat = "phrase and rhythm cues only; not a machine-authorship test"

    def score(self, text: str) -> dict:
        t = F.clean_sample(text)
        ws = F.words(t)
        lens = [len(F.words(s)) for s in F.sentences(t)]
        hits = sorted({m.group(0).lower() for rx in _STOCK for m in [rx.search(t)] if m})
        emd = (t.count("—") / max(1, len(ws))) * 100
        # Burstiness: people vary sentence length more than default model output does (GPTZero's public explainer).
        cv = statistics.pstdev(lens) / statistics.fmean(lens) if len(lens) >= 3 and statistics.fmean(lens) else None
        s = min(1.0, 0.25 * len(hits) + min(0.3, emd * 0.15) + (0.3 if cv is not None and cv < 0.25 else 0.0))
        reasons = [f"stock phrase: {h}" for h in hits]
        if emd >= 1.0:
            reasons.append(f"em dashes: {emd:.1f} per 100 words")
        if cv is not None and cv < 0.25:
            reasons.append(f"flat rhythm: sentence lengths barely vary (cv {cv:.2f})")
        return {"detector": self.name, "generic": round(s, 3), "reasons": reasons, "caveat": self.caveat}


LOOPBACK = {"127.0.0.1", "localhost", "::1"}


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"redirect refused (to {newurl})", headers, fp)


_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _RefuseRedirects())


class LoopbackDetector:
    """A local model detector (for example Binoculars, Hans et al. 2024) served on this machine.
    Contract: POST {base}/score {"text": ...} -> {"score": float, "machine_like": bool}."""
    caveat = ("zero-shot model detector; strong on stock model output, weaker on edited, short or "
              "non-native text; can flag real human writing")

    def __init__(self, base: str, name: str = "binoculars-local"):
        if urllib.parse.urlparse(base).hostname not in LOOPBACK:
            raise ValueError("the detector must run on this machine (loopback only)")
        self.base, self.name = base.rstrip("/"), name

    def score(self, text: str) -> dict:
        req = urllib.request.Request(self.base + "/score", data=json.dumps({"text": text}).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with _OPENER.open(req, timeout=60) as r:
                out = json.loads(r.read())
        except (urllib.error.URLError, OSError, ValueError) as e:
            return {"detector": self.name, "generic": None, "reasons": [f"detector unavailable: {e}"], "caveat": self.caveat}
        return {"detector": self.name, "generic": 1.0 if out.get("machine_like") else 0.0,
                "raw_score": out.get("score"), "reasons": [], "caveat": self.caveat}


def run_all(text: str, detectors) -> list[dict]:
    return [d.score(text) for d in detectors]
