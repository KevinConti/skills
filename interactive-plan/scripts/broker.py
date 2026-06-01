#!/usr/bin/env python3
"""broker.py - static file server + POST /intent inbox for interactive-plan.

GET  *        -> serve files from <dir> (the session folder), like http.server
POST /intent  -> validate one intent and append it (one JSON line) to inbox.ndjson

The browser is the only writer of intents; this server is the only thing that
can write to disk on the agent's behalf. It binds 127.0.0.1 ONLY, validates the
`kind`, coerces/truncates every field, and size-limits the body. Single local
user, loopback-only, no auth by design.

Usage: broker.py <port> <session-dir>
"""
import json
import os
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ALLOWED_KINDS = {"answer", "freeform", "skip", "goback"}
MAX_BODY = 16 * 1024
_lock = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/intent":
            self._json(404, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._json(413, {"ok": False, "error": "bad length"})
            return
        try:
            data = json.loads(self.rfile.read(length))
        except Exception:
            self._json(400, {"ok": False, "error": "bad json"})
            return
        kind = data.get("kind")
        if kind not in ALLOWED_KINDS:
            self._json(400, {"ok": False, "error": "bad kind"})
            return
        try:
            qid = int(data.get("qid", 0))
        except (TypeError, ValueError):
            qid = 0
        intent = {
            "id": str(data.get("id", ""))[:64],
            "qid": qid,
            "kind": kind,
            "value": str(data.get("value", ""))[:2000],
            "note": str(data.get("note", ""))[:2000],
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        inbox = os.path.join(self.directory, "inbox.ndjson")
        with _lock:
            seq = 0
            if os.path.exists(inbox):
                with open(inbox) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            seq = max(seq, int(json.loads(line).get("seq", 0)))
                        except Exception:
                            pass
            intent["seq"] = seq + 1
            with open(inbox, "a") as f:
                f.write(json.dumps(intent) + "\n")
                f.flush()
                os.fsync(f.fileno())
        self._json(200, {"ok": True, "seq": intent["seq"]})

    def log_message(self, *args):
        pass  # quiet; stdout/stderr go to .server.log


def main():
    if len(sys.argv) < 3:
        print("usage: broker.py <port> <session-dir>", file=sys.stderr)
        return 2
    port = int(sys.argv[1])
    directory = sys.argv[2]
    httpd = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=directory))
    httpd.serve_forever()


if __name__ == "__main__":
    sys.exit(main() or 0)
