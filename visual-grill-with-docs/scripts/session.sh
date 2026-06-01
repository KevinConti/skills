#!/usr/bin/env bash
#
# session.sh — manage a visual-grill-with-docs session HTTP server.
#
# Usage:
#   session.sh start <slug>      # create folder, copy viewer.html, pick port,
#                                # start python http.server in background,
#                                # open browser. Idempotent — re-uses the
#                                # existing server if one is already running.
#   session.sh status <slug>     # print PORT or empty + exit 0 if running
#                                # else exit 1.
#   session.sh stop <slug>       # kill server PID, remove .port/.server.pid.
#   session.sh url <slug>        # print the viewer URL (no opening).
#
# Session folder: ~/.agent/grill-sessions/<slug>/
#
# Requires: python3 (ships with macOS), `open` (macOS) or `xdg-open` (Linux).

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$SKILL_DIR/templates/viewer.html"
ROOT="${VISUAL_GRILL_ROOT:-$HOME/.agent/grill-sessions}"

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
  python3 - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
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

    # Seed session.json if missing so the viewer has something to render.
    if [[ ! -f "$dir/session.json" ]]; then
      cat >"$dir/session.json" <<JSON
{
  "slug": "$slug",
  "aesthetic": "editorial",
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
    nohup python3 -m http.server "$port" --bind 127.0.0.1 --directory "$dir" >"$log_file" 2>&1 &
    echo $! >"$pid_file"
    echo "$port" >"$port_file"

    url="http://localhost:$port/viewer.html"
    # Wait briefly for the server to bind, then open.
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      if curl -sf -o /dev/null "http://localhost:$port/viewer.html"; then break; fi
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

  *)
    usage
    ;;
esac
