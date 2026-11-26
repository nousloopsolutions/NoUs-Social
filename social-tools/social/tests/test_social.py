# @NCL{v=1.0;agent=claude;mod=social-tests;tier=L2}
# #S{purpose="Gate, lint, publisher and engagement tests for the social pipeline"}
# #I{1="No network: publishers get a fake http"}
# #F{1="Test the gate only through the CLI"→"Misses tampering on disk; tests edit the post file directly"}
# #M{status=IMPLEMENTED;deps="Python 3 stdlib"}
# #T{status="python3 -m unittest discover -s social/tests"}
# #X{2026-11-26="Created for the approval-gated social pipeline"}
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cli  # noqa: E402
import engagement  # noqa: E402
import publish as pub  # noqa: E402
from lint import lint_post  # noqa: E402
from post_queue import GateError, Queue, content_hash  # noqa: E402

GOOD = "Small breaks help. Our new owl reminds you to stretch, on your phone, with nothing sent anywhere."


class FakeHttp:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []

    def __call__(self, method, url, headers, body=None):
        self.calls.append((method, url, headers, body))
        return self.responses.pop(0)


PASS = "correct horse battery"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.keys = Path(self.tmp.name) / "keys"
        q0 = Queue(Path(self.tmp.name) / "q", trusted_keys={})
        fp = cli.keygen(q0, "brent", PASS, self.keys)
        self.q = Queue(Path(self.tmp.name) / "q", trusted_keys={"brent": fp})
        self.sign = cli.signer("brent", PASS, self.keys)

    def tearDown(self):
        self.tmp.cleanup()

    def approve(self, p, who="brent", q=None):
        q = q or self.q
        return q.approve(p["id"], who, content_hash(p["platform"], p["text"]), self.sign)

    def approved(self, platform="mastodon", text=GOOD):
        return self.approve(self.q.draft(platform, text, agent="hermes"))


class LintTests(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(lint_post(GOOD, "bluesky"), [])

    def test_catches(self):
        cases = {"medical-claim": "This app can treat anxiety.",
                 "patent-internals": "Powered by golden memory and THAOT.",
                 "mentions-person": "Thanks @someone for the idea",
                 "urgency-trick": "Last chance to join!",
                 "personal-email": "write me at x@gmail.com",
                 "length": "a" * 301}
        for rule, text in cases.items():
            self.assertIn(rule, [p["rule"] for p in lint_post(text, "bluesky")], rule)

    def test_hidden_controls(self):
        for t in ["We endorse this.\r\x1b[2KSmall breaks help.", "abc\u202edcba", "tab\there"]:
            self.assertIn("hidden-control", [p["rule"] for p in lint_post(t, "mastodon")], repr(t))
        self.assertEqual(lint_post("line one\nline two", "mastodon"), [])

    def test_unknown_platform(self):
        self.assertIn("platform", [p["rule"] for p in lint_post(GOOD, "x")])


class GateTests(Base):
    def test_agent_cannot_approve(self):
        p = self.q.draft("mastodon", GOOD, agent="hermes")
        with self.assertRaises(GateError):
            self.approve(p, "hermes")  # not trusted
        p2 = self.q.draft("mastodon", GOOD, agent="brent")
        with self.assertRaises(GateError):
            self.approve(p2, "brent")  # drafter can never approve own post

    def test_lint_blocks_approval(self):
        p = self.q.draft("mastodon", "We diagnose stress.", agent="hermes")
        with self.assertRaises(GateError):
            self.approve(p)

    def test_edit_during_review_not_approved(self):  # Codex PR 694 finding 1
        p = self.q.draft("mastodon", GOOD, agent="hermes")
        reviewed = content_hash(p["platform"], p["text"])
        self.q.edit(p["id"], GOOD + " Buy now.", actor="hermes")
        with self.assertRaisesRegex(GateError, "changed after you reviewed"):
            self.q.approve(p["id"], "brent", reviewed, self.sign)
        self.assertEqual(self.q.get(p["id"])["status"], "draft")

    def test_forged_approval_blocked(self):  # Codex PR 694 finding 2
        p = self.q.draft("mastodon", GOOD, agent="hermes")
        path = self.q.home / "posts" / f"{p['id']}.json"
        raw = json.loads(path.read_text())
        raw["status"] = "approved"
        raw["approval"] = {"by": "brent", "at": "2026-11-26T00:00:00Z", "content_sha256": content_hash("mastodon", GOOD)}
        path.write_text(json.dumps(raw))
        http = FakeHttp([{"id": "1"}])
        with self.assertRaises(GateError):
            pub.publish(self.q, p["id"], "nous", live=True, env={"MASTODON_BASE": "https://m", "MASTODON_TOKEN": "t"}, http=http)
        raw["approval"]["signature"] = "AAAA"
        path.write_text(json.dumps(raw))
        with self.assertRaises(GateError):
            self.q.check_publishable(self.q.get(p["id"]))
        self.assertEqual(http.calls, [])

    def test_swapped_public_key_blocked(self):
        p = self.approved()
        other = Queue(Path(self.tmp.name) / "other", trusted_keys={})
        cli.keygen(other, "brent", PASS, Path(self.tmp.name) / "k2")
        (self.q.home / "approvers" / "brent.pub").write_bytes((other.home / "approvers" / "brent.pub").read_bytes())
        with self.assertRaisesRegex(GateError, "pinned"):
            self.q.check_publishable(p)

    def test_no_trusted_keys_nothing_approves(self):
        q = Queue(self.q.home, trusted_keys={})
        p = q.draft("mastodon", GOOD, agent="hermes")
        with self.assertRaises(GateError):
            self.approve(p, q=q)

    def test_wrong_passphrase(self):
        with self.assertRaisesRegex(GateError, "passphrase"):
            cli.signer("brent", "wrong wrong wrong", self.keys)

    def test_edit_clears_approval(self):
        p = self.approved()
        p = self.q.edit(p["id"], GOOD + " Try it.", actor="hermes")
        self.assertEqual(p["status"], "draft")
        with self.assertRaises(GateError):
            self.q.check_publishable(p)

    def test_tampered_text_blocked(self):
        p = self.approved()
        path = self.q.home / "posts" / f"{p['id']}.json"
        raw = json.loads(path.read_text()); raw["text"] = GOOD + "!"; path.write_text(json.dumps(raw))
        with self.assertRaisesRegex(GateError, "changed after approval"):
            self.q.check_publishable(self.q.get(p["id"]))

    def test_kill_switch(self):
        p = self.approved()
        (self.q.home / "KILL").write_text("on")
        with self.assertRaisesRegex(GateError, "kill"):
            self.q.check_publishable(p)

    def test_schedule_and_cap(self):
        p = self.q.draft("mastodon", GOOD, agent="hermes", scheduled_for="2999-01-01T00:00:00Z")
        p = self.approve(p)
        with self.assertRaisesRegex(GateError, "not due"):
            self.q.check_publishable(p)
        a = self.approved(); self.q.mark_posted(a["id"], "brent", "1")
        b = self.approved(text=GOOD + " Again.")
        with self.assertRaisesRegex(GateError, "daily cap"):
            self.q.check_publishable(b)

    def test_schedule_with_offset(self):
        p = self.q.draft("mastodon", GOOD, agent="hermes", scheduled_for="2026-11-26T09:00:00-05:00")
        self.assertEqual(p["scheduled_for"], "2026-11-26T14:00:00Z")
        p = self.approve(p)
        with self.assertRaisesRegex(GateError, "not due"):
            self.q.check_publishable(p, now="2026-11-26T12:00:00Z")
        self.q.check_publishable(p, now="2026-11-26T14:00:01Z")
        with self.assertRaisesRegex(GateError, "timezone"):
            self.q.draft("mastodon", GOOD, agent="hermes", scheduled_for="2026-11-26T09:00:00")

    def test_ledger_chain(self):
        self.approved()
        self.assertTrue(self.q.verify_ledger())
        lines = self.q.ledger.read_text().splitlines()
        ev = json.loads(lines[0]); ev["actor"] = "someone-else"; lines[0] = json.dumps(ev, sort_keys=True)
        self.q.ledger.write_text("\n".join(lines) + "\n")
        self.assertFalse(self.q.verify_ledger())


class PublishTests(Base):
    def test_dry_run_sends_nothing(self):
        p = self.approved()
        http = FakeHttp([])
        out = pub.publish(self.q, p["id"], "nous", live=False, env={}, http=http)
        self.assertTrue(out["dry_run"]); self.assertEqual(http.calls, [])
        self.assertEqual(self.q.get(p["id"])["status"], "approved")

    def test_mastodon_live(self):
        p = self.approved()
        http = FakeHttp([{"id": "42", "url": "https://m.example/@nous/42"}])
        out = pub.publish(self.q, p["id"], "nous", live=True,
                          env={"MASTODON_BASE": "https://m.example", "MASTODON_TOKEN": "t"}, http=http)
        self.assertEqual(out["platform_post_id"], "42")
        self.assertEqual(http.calls[0][2]["Idempotency-Key"], self.q.get(p["id"])["attempt"]["key"])
        self.assertEqual(self.q.get(p["id"])["status"], "posted")
        self.assertTrue(self.q.verify_ledger())

    def test_bluesky_live(self):
        p = self.approved("bluesky")
        http = FakeHttp([{"accessJwt": "j", "did": "did:plc:abc"},
                         {"uri": "at://did:plc:abc/app.bsky.feed.post/3k", "cid": "c"}])
        out = pub.publish(self.q, p["id"], "nous", live=True,
                          env={"BSKY_HANDLE": "nousloop.com", "BSKY_APP_PASSWORD": "x"}, http=http)
        self.assertEqual(out["url"], "https://bsky.app/profile/did:plc:abc/post/3k")
        self.assertEqual(json.loads(http.calls[1][3])["record"]["text"], GOOD)

    def test_bluesky_lost_response_reconciles(self):  # Codex PR 694, 4th pass
        import urllib.error
        p = self.approved("bluesky")
        env = {"BSKY_HANDLE": "h", "BSKY_APP_PASSWORD": "x"}
        sess = {"accessJwt": "j", "did": "did:plc:a"}

        class Lost:
            def __init__(self, responses):
                self.responses, self.calls = list(responses), []

            def __call__(self, method, url, headers, body=None):
                self.calls.append((method, url, body))
                r = self.responses.pop(0)
                if isinstance(r, Exception):
                    raise r
                return r
        first = Lost([sess, TimeoutError("lost response")])
        with self.assertRaises(TimeoutError):
            pub.publish(self.q, p["id"], "nous", live=True, env=env, http=first)
        key = self.q.get(p["id"])["attempt"]["key"]
        self.assertEqual(len(key), 13)
        self.assertEqual(json.loads(first.calls[1][2])["rkey"], key)
        uri = f"at://did:plc:a/app.bsky.feed.post/{key}"
        second = Lost([sess, {"uri": uri, "value": {}}])  # getRecord finds it: no second create
        out = pub.publish(self.q, p["id"], "nous", live=True, env=env, http=second)
        self.assertEqual(out["platform_post_id"], uri)
        self.assertFalse(any("createRecord" in c[1] for c in second.calls))
        third_post = self.approved("bluesky", GOOD + " Third.")
        missing = urllib.error.HTTPError("u", 400, "RecordNotFound", {}, None)
        self.q.get(third_post["id"])
        with self.assertRaisesRegex(GateError, "daily cap"):
            pub.publish(self.q, third_post["id"], "nous", live=True, env=env, http=Lost([sess, missing]))

    def test_unresolved_attempt_counts_toward_cap(self):
        a = self.approved()
        env = {"MASTODON_BASE": "https://m", "MASTODON_TOKEN": "t"}

        def boom(method, url, headers, body=None):
            raise TimeoutError("lost")
        with self.assertRaises(TimeoutError):
            pub.publish(self.q, a["id"], "nous", live=True, env=env, http=boom)
        b = self.approved(text=GOOD + " Two.")
        with self.assertRaisesRegex(GateError, "daily cap"):
            self.q.check_publishable(b)

    def test_mastodon_retry_window(self):
        p = self.approved()
        env = {"MASTODON_BASE": "https://m", "MASTODON_TOKEN": "t"}

        def boom(method, url, headers, body=None):
            raise TimeoutError("lost")
        with self.assertRaises(TimeoutError):
            pub.publish(self.q, p["id"], "nous", live=True, env=env, http=boom)
        path = self.q.home / "posts" / f"{p['id']}.json"
        raw = json.loads(path.read_text()); raw["attempt"]["at"] = "2020-01-01T00:00:00Z"; path.write_text(json.dumps(raw))
        http = FakeHttp([{"id": "9"}])
        with self.assertRaisesRegex(GateError, "expired"):
            pub.publish(self.q, p["id"], "nous", live=True, env=env, http=http)
        self.assertEqual(http.calls, [])

    def test_killed_process_still_counts_as_sent(self):  # Codex PR 694, 7th pass
        p = self.approved()
        env = {"MASTODON_BASE": "https://m", "MASTODON_TOKEN": "t"}

        def accept_then_die(method, url, headers, body=None):
            raise SystemExit("killed after the platform accepted")
        with self.assertRaises(SystemExit):
            pub.publish(self.q, p["id"], "nous", live=True, env=env, http=accept_then_die)
        self.assertEqual(len(self.q.get(p["id"])["attempt"]["sends"]), 1)
        path = self.q.home / "posts" / f"{p['id']}.json"
        raw = json.loads(path.read_text()); raw["attempt"]["at"] = "2020-01-01T00:00:00Z"; path.write_text(json.dumps(raw))
        http = FakeHttp([{"id": "2"}])
        with self.assertRaisesRegex(GateError, "expired"):
            pub.publish(self.q, p["id"], "nous", live=True, env=env, http=http)
        self.assertEqual(http.calls, [])

    def test_retry_on_new_day_charges_new_day(self):  # Codex PR 694, 7th pass
        a = self.approved("bluesky")
        path = self.q.home / "posts" / f"{a['id']}.json"
        raw = json.loads(path.read_text())
        raw["attempt"] = {"key": "3aaaaaaaaaaaa", "at": "2020-01-01T00:00:00Z", "by": "nous",
                          "sends": ["2020-01-01T00:00:00Z", __import__("post_queue").now_utc()]}
        path.write_text(json.dumps(raw))
        b = self.approved("bluesky", GOOD + " B.")
        with self.assertRaisesRegex(GateError, "daily cap"):
            self.q.check_publishable(b)

    def test_missing_credentials(self):
        p = self.approved()
        with self.assertRaisesRegex(GateError, "missing credentials"):
            pub.publish(self.q, p["id"], "nous", live=True, env={}, http=FakeHttp([]))

    def test_unapproved_never_sent(self):
        p = self.q.draft("mastodon", GOOD, agent="hermes")
        http = FakeHttp([])
        with self.assertRaises(GateError):
            pub.publish(self.q, p["id"], "nous", live=True, env={"MASTODON_BASE": "https://m", "MASTODON_TOKEN": "t"}, http=http)
        self.assertEqual(http.calls, [])

    def test_linkedin_is_manual(self):
        p = self.approved("linkedin")
        with self.assertRaisesRegex(GateError, "by hand"):
            pub.publish(self.q, p["id"], "nous", live=True, env={}, http=FakeHttp([]))


class RedirectTests(unittest.TestCase):
    def test_publisher_refuses_redirects(self):
        import email.message, urllib.error, urllib.request
        req = urllib.request.Request("https://pds.example/xrpc/x", headers={"Authorization": "Bearer t"})
        for target in ("http://pds.example/xrpc/x", "https://elsewhere.example/x"):
            with self.assertRaises(urllib.error.HTTPError):
                pub._RefuseRedirects().redirect_request(req, None, 302, "Found", email.message.Message(), target)
        self.assertTrue(any(isinstance(h, pub._RefuseRedirects) for h in pub._OPENER.handlers))


class ConcurrencyTests(Base):
    def test_concurrent_publish_respects_cap(self):
        import threading
        a, b = self.approved(), self.approved(text=GOOD + " Again.")
        env = {"MASTODON_BASE": "https://m", "MASTODON_TOKEN": "t"}
        gate = threading.Barrier(2)
        results = []

        class SlowHttp:
            def __call__(self, method, url, headers, body=None):
                import time; time.sleep(0.2)
                return {"id": headers["Idempotency-Key"], "url": ""}

        def run(p):
            gate.wait()
            try:
                pub.publish(self.q, p["id"], "nous", live=True, env=env, http=SlowHttp())
                results.append("ok")
            except GateError as e:
                results.append(str(e))
        ts = [threading.Thread(target=run, args=(p,)) for p in (a, b)]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(results.count("ok"), 1, results)

    def test_edit_during_publish_refused(self):
        p = self.approved("bluesky")
        env = {"BSKY_HANDLE": "h", "BSKY_APP_PASSWORD": "x"}
        outcome = {}
        q = self.q

        class EditingHttp:
            calls = 0

            def __call__(self, method, url, headers, body=None):
                EditingHttp.calls += 1
                if EditingHttp.calls == 1:
                    try:
                        q.edit(p["id"], GOOD + " changed", actor="hermes")
                        outcome["edit"] = "saved"
                    except GateError:
                        outcome["edit"] = "refused"
                    return {"accessJwt": "j", "did": "did:plc:a"}
                return {"uri": "at://did:plc:a/app.bsky.feed.post/1", "cid": "c"}
        pub.publish(self.q, p["id"], "nous", live=True, env=env, http=EditingHttp())
        self.assertEqual(outcome["edit"], "refused")
        self.assertEqual(self.q.get(p["id"])["text"], GOOD)

    def test_lock_released_when_process_dies(self):  # Codex PR 694, 4th/5th pass
        import subprocess
        lock = self.q.home / "publish-mastodon.lock"
        code = ("import sys; sys.path.insert(0, sys.argv[2]); from post_queue import Queue;"
                "q = Queue(sys.argv[1], trusted_keys={}); cm = q.platform_lock('mastodon'); cm.__enter__();"
                "import os; os._exit(0)")
        subprocess.run([sys.executable, "-c", code, str(self.q.home), str(Path(__file__).resolve().parent.parent)], check=True)
        with self.q.platform_lock("mastodon"):  # no stale lock left behind
            pass

    def test_held_lock_excludes(self):
        import threading
        held, release = threading.Event(), threading.Event()

        def holder():
            with self.q.platform_lock("mastodon"):
                held.set(); release.wait(2)
        t = threading.Thread(target=holder); t.start(); held.wait(2)
        with self.assertRaisesRegex(GateError, "busy"):
            with self.q._filelock(self.q.home / "publish-mastodon.lock", wait=0.1, busy="busy"):
                pass
        release.set(); t.join()

    def test_edit_blocked_while_attempt_unresolved(self):  # Codex PR 694, 5th pass
        p = self.approved()

        def boom(method, url, headers, body=None):
            raise TimeoutError("lost")
        with self.assertRaises(TimeoutError):
            pub.publish(self.q, p["id"], "nous", live=True,
                        env={"MASTODON_BASE": "https://m", "MASTODON_TOKEN": "t"}, http=boom)
        with self.assertRaisesRegex(GateError, "unresolved"):
            self.q.edit(p["id"], GOOD + " new", actor="hermes")
        with self.assertRaisesRegex(GateError, "unresolved"):
            self.q.reject(p["id"], "brent")
        seen = dict(self.q.get(p["id"])["attempt"])
        with self.assertRaises(GateError):
            self.q.clear_attempt(p["id"], "brent", False, seen)
        with self.assertRaises(GateError):  # a retry happened after the human looked
            pub_env = {"MASTODON_BASE": "https://m", "MASTODON_TOKEN": "t"}
            with self.assertRaises(TimeoutError):
                pub.publish(self.q, p["id"], "nous", live=True, env=pub_env, http=boom)
            self.q.clear_attempt(p["id"], "brent", True, seen)
        self.q.clear_attempt(p["id"], "brent", True, dict(self.q.get(p["id"])["attempt"]))
        self.q.edit(p["id"], GOOD + " new", actor="hermes")
        self.assertTrue(self.q.verify_ledger())

    def test_concurrent_edits_keep_ledger(self):
        import threading
        posts = [self.q.draft("mastodon", GOOD, agent="hermes") for _ in range(8)]
        gate = threading.Barrier(8)

        def run(p):
            gate.wait(); self.q.edit(p["id"], GOOD + " " + p["id"], actor="hermes")
        ts = [threading.Thread(target=run, args=(p,)) for p in posts]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertTrue(self.q.verify_ledger())


class EngagementTests(Base):
    def test_only_counts(self):
        p = self.approved(); self.q.mark_posted(p["id"], "brent", "1")
        engagement.record_metrics(self.q, p["id"], {"likes": 3, "replies": 1})
        with self.assertRaises(ValueError):
            engagement.record_metrics(self.q, p["id"], {"likers": ["@a"]})
        with self.assertRaises(ValueError):
            engagement.record_metrics(self.q, p["id"], {"likes": "3"})

    def test_export(self):
        a = self.q.draft("mastodon", GOOD, agent="hermes")
        a = self.q.edit(a["id"], GOOD + " Gently.", actor="brent"); self.approve(a)
        b = self.q.draft("mastodon", "Hurry, act now!", agent="hermes"); self.q.reject(b["id"], "brent", "pushy")
        self.q.draft("mastodon", GOOD, agent="hermes")  # undecided, left out
        rows = {r["post_id"]: r for r in engagement.export_training(self.q)}
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[a["id"]]["decision"], "edited")
        self.assertEqual(rows[a["id"]]["first_draft"], GOOD)
        self.assertEqual(rows[b["id"]]["rejection_reason"], "pushy")

    def test_old_rejection_not_exported_after_approval(self):  # Codex PR 694, 12th pass
        b = self.q.draft("mastodon", "Hurry, act now!", agent="hermes"); self.q.reject(b["id"], "brent", "pushy")
        b = self.q.edit(b["id"], GOOD, actor="brent"); self.approve(b)
        row = engagement.export_training(self.q)[0]
        self.assertEqual((row["decision"], row["rejection_reason"]), ("edited", None))

    def test_agent_revision_is_not_human_edit(self):  # Codex PR 694, 8th pass
        a = self.q.draft("mastodon", GOOD, agent="hermes")
        a = self.q.edit(a["id"], GOOD + " Revised.", actor="hermes")
        self.approve(a)
        row = engagement.export_training(self.q)[0]
        self.assertEqual(row["decision"], "approved")
        self.assertEqual(row["first_draft"], GOOD + " Revised.")
        self.assertEqual((row["edits"], row["agent_revisions"]), (0, 1))

    def test_edit_roles_survive_trust_changes(self):  # Codex PR 694, 9th pass
        a = self.q.draft("mastodon", GOOD, agent="hermes")
        a = self.q.edit(a["id"], GOOD + " Gently.", actor="brent"); self.approve(a)
        unpinned = Queue(self.q.home, trusted_keys={})
        row = engagement.export_training(unpinned)[0]
        self.assertEqual((row["decision"], row["edits"], row["first_draft"]), ("edited", 1, GOOD))


class DraftLocalTests(unittest.TestCase):
    def test_refuses_redirects(self):  # Codex PR 694, 12th pass
        import email.message, urllib.error, urllib.request, draft_local
        req = urllib.request.Request("http://127.0.0.1:1/v1/chat/completions", data=b"{}")
        with self.assertRaises(urllib.error.HTTPError):
            draft_local._RefuseRedirects().redirect_request(req, None, 302, "Found", email.message.Message(),
                                                            "http://192.0.2.1/x")
        self.assertTrue(any(isinstance(h, draft_local._RefuseRedirects) for h in draft_local._NO_PROXY_OPENER.handlers))

    def test_refuses_remote_and_ignores_proxy(self):  # Codex PR 694, 10th pass
        import http.server, os, threading, draft_local
        with self.assertRaises(ValueError):
            draft_local.draft_text("x", "mastodon", base="https://api.example.com/v1")
        hits = {"proxy": 0, "model": 0}

        def server(kind, reply):
            class H(http.server.BaseHTTPRequestHandler):
                def do_POST(self):
                    hits[kind] += 1
                    self.rfile.read(int(self.headers.get("Content-Length", 0)))
                    body = json.dumps(reply).encode()
                    self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers()
                    self.wfile.write(body)

                def log_message(self, *a):
                    pass
            srv = http.server.HTTPServer(("127.0.0.1", 0), H)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            return srv
        model = server("model", {"choices": [{"message": {"content": "hi"}}]})
        proxy = server("proxy", {"choices": [{"message": {"content": "via proxy"}}]})
        old = {k: os.environ.get(k) for k in ("http_proxy", "HTTP_PROXY", "no_proxy", "NO_PROXY")}
        try:
            os.environ["http_proxy"] = os.environ["HTTP_PROXY"] = f"http://127.0.0.1:{proxy.server_port}"
            os.environ.pop("no_proxy", None); os.environ.pop("NO_PROXY", None)
            out = draft_local.draft_text("walks", "mastodon", base=f"http://127.0.0.1:{model.server_port}/v1")
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            model.shutdown(); proxy.shutdown()
        self.assertEqual((out, hits["proxy"], hits["model"]), ("hi", 0, 1))


class CliTests(Base):
    def test_approve_refuses_non_tty(self):
        p = self.q.draft("mastodon", GOOD, agent="hermes")
        rc = cli.main(["--home", str(self.q.home), "approve", p["id"], "--as", "brent"], stdin=io.StringIO("x\n"))
        self.assertEqual(rc, 2)
        self.assertEqual(self.q.get(p["id"])["status"], "draft")


if __name__ == "__main__":
    unittest.main()
