#!/usr/bin/env bash
#
# session.sh - manage an interactive-plan session (broker server + watcher).
#
# Usage:
#   session.sh start <slug>    create folder, copy viewer.html, seed files,
#                              start broker.py, open browser. Idempotent.
#   session.sh status <slug>   print URL + exit 0 if running, else exit 1.
#   session.sh stop <slug>     kill the broker, remove bookkeeping.
#   session.sh url <slug>      print the viewer URL (no opening).
#   session.sh wait <slug>     block until a new intent lands, print it, exit.
#                              Run via the Bash tool with run_in_background: true.
#
# Session folder: ~/.agent/interactive-plan/<slug>/
# Override the root with INTERACTIVE_PLAN_ROOT.
#
# Requires: python3, curl, and `open` (macOS) or `xdg-open` (Linux).

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$SKILL_DIR/scripts"
TEMPLATE="$SKILL_DIR/templates/viewer.html"
ROOT="${INTERACTIVE_PLAN_ROOT:-$HOME/.agent/interactive-plan}"

usage() { sed -n '3,18p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

cmd="${1:-}"
slug="${2:-}"
[[ -z "$cmd" || -z "$slug" ]] && usage

# Allow only safe slug characters.
[[ "$slug" =~ ^[a-z0-9][a-z0-9._-]*$ ]] || { echo "bad slug: $slug" >&2; exit 2; }

dir="$ROOT/$slug"
port_file="$dir/.port"
pid_file="$dir/.server.pid"
log_file="$dir/.server.log"

pick_port() {
  python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()'
}

is_running() {
  [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null
}

url_for() {
  [[ -f "$port_file" ]] || return 1
  echo "http://localhost:$(cat "$port_file")/viewer.html"
}

open_browser() {
  local url="$1"
  if command -v open >/dev/null 2>&1; then
    open "$url"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 &
  else
    echo "no opener found; visit: $url"
  fi
}

case "$cmd" in
  start)
    mkdir -p "$dir"
    cp -f "$TEMPLATE" "$dir/viewer.html"
    [[ -f "$dir/inbox.ndjson" ]] || : >"$dir/inbox.ndjson"
    [[ -f "$dir/inbox.cursor" ]] || echo 0 >"$dir/inbox.cursor"

    if [[ ! -f "$dir/session.json" ]]; then
      cat >"$dir/session.json" <<JSON
{
  "slug": "$slug",
  "startedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "contextPath": null,
  "currentQuestion": null,
  "questions": [],
  "glossary": [],
  "adrs": []
}
JSON
    fi

    if is_running; then
      url="$(url_for)"
      echo "already running: $url"
      open_browser "$url"
      exit 0
    fi

    port="$(pick_port)"
    nohup python3 "$SCRIPTS/broker.py" "$port" "$dir" >"$log_file" 2>&1 &
    echo $! >"$pid_file"
    echo "$port" >"$port_file"

    url="http://localhost:$port/viewer.html"
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      if curl -sf -o /dev/null "$url"; then break; fi
      sleep 0.1
    done
    echo "$url"
    open_browser "$url"
    ;;

  status)
    if is_running; then
      url_for || true
      exit 0
    else
      exit 1
    fi
    ;;

  stop)
    if is_running; then
      kill "$(cat "$pid_file")" 2>/dev/null || true
      sleep 0.2
      kill -9 "$(cat "$pid_file")" 2>/dev/null || true
    fi
    rm -f "$pid_file" "$port_file"
    echo "stopped"
    ;;

  url)
    url_for || { echo "not running" >&2; exit 1; }
    ;;

  wait)
    python3 "$SCRIPTS/wait.py" "$dir" "${3:-1800}"
    ;;

  *)
    usage
    ;;
esac
