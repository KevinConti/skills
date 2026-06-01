#!/usr/bin/env python3
"""wait.py - block until a new intent (seq > cursor) appears, print it, exit.

This is the "doorbell". The agent runs it via the Bash tool with
run_in_background: true. While no new intent exists it sleeps at the OS level
(near-zero CPU, ZERO model tokens - the agent is not in the loop). The instant
a fresh intent lands it prints the new intent(s) as JSON lines and exits, which
causes the harness to re-invoke the agent with those lines in the tool result.

It does NOT advance inbox.cursor - the agent does that after it has actually
processed the intents, so nothing is lost if the agent is interrupted.

Usage: wait.py <session-dir> [timeout-seconds]
"""
import json
import os
import sys
import time


def read_cursor(path):
    try:
        with open(path) as f:
            return int((f.read().strip() or "0"))
    except Exception:
        return 0


def new_intents(inbox, cursor):
    out = []
    if not os.path.exists(inbox):
        return out
    with open(inbox) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if int(obj.get("seq", 0)) > cursor:
                out.append(obj)
    return out


def main():
    if len(sys.argv) < 2:
        print("usage: wait.py <session-dir> [timeout-seconds]", file=sys.stderr)
        return 2
    directory = sys.argv[1]
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 1800.0
    inbox = os.path.join(directory, "inbox.ndjson")
    cursor_file = os.path.join(directory, "inbox.cursor")
    cursor = read_cursor(cursor_file)
    deadline = time.time() + timeout

    # Debounce: once we see something, wait a beat for a flurry to settle,
    # then emit everything new at once so rapid clicks become one wake.
    while time.time() < deadline:
        fresh = new_intents(inbox, cursor)
        if fresh:
            time.sleep(0.3)
            fresh = new_intents(inbox, cursor)
            for obj in fresh:
                print(json.dumps(obj))
            return 0
        time.sleep(0.25)

    print(json.dumps({"timeout": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
