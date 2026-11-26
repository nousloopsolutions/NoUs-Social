# @NCL{v=1.0;agent=claude;mod=social-draft-local;tier=L2}
# #S{purpose="Ask a local model (OpenAI-compatible, loopback only) for a post draft"}
# #I{1="Loopback endpoints only: no paid or cloud API";2="Output is only a draft; the gate still applies"}
# #F{1="Point the drafter at a cloud API"→"Cost and data leaving the machine; refused";2="Default urlopen"→"Honors HTTP(S)_PROXY and sent the prompt to a proxy (Codex PR 694); use a proxy-free opener";3="Follow redirects"→"A loopback 302 sent the request to a non-loopback host (Codex PR 694); redirects are refused"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib; a local model server such as Ollama or LiteLLM"}
# #T{status="python3 -m unittest discover -s social/tests"}
# #X{2026-11-26="Created for the approval-gated social pipeline"}
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from lint import LIMITS

DEFAULT_BASE = "http://127.0.0.1:11435/v1"
LOOPBACK = {"127.0.0.1", "localhost", "::1"}
# Never use HTTP(S)_PROXY from the environment: the prompt must not leave the machine.
class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect could point off the machine, so the loopback check would no longer hold."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"redirect refused (to {newurl})", headers, fp)


_NO_PROXY_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _RefuseRedirects())

SYSTEM = ("You write short social posts for NoUs Loop, a privacy-first wellbeing tools company. "
          "Plain, warm, specific. Wellness language only: never medical claims. Never describe "
          "internal technology. No hashtags spam, no urgency tricks, never tag or name people.")


def draft_text(topic: str, platform: str, base: str = DEFAULT_BASE, model: str = "local") -> str:
    host = urllib.parse.urlparse(base).hostname
    if host not in LOOPBACK:
        raise ValueError("local drafting only talks to a loopback model server")
    body = json.dumps({"model": model, "temperature": 0.7, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"One {platform} post, under {LIMITS[platform]} characters, about: {topic}"},
    ]}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with _NO_PROXY_OPENER.open(req, timeout=120) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"].strip()
