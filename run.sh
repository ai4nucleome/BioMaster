#!/usr/bin/env bash
# BioMaster single-process launcher
#
# Examples:
#   ./run.sh local
#   ./run.sh remote --password '<strong-password>'
#   ./run.sh restart --host 0.0.0.0 --port 18080 --password '<strong-password>'
#   ./run.sh stop

set -u

ROOT="$(cd "$(dirname "$0")" && pwd)"
BIO_DIR="$ROOT"
OC_INDEX="$ROOT/BioMaster/packages/opencode/src/index.ts"
APP_DIST="$ROOT/BioMaster/packages/app/dist"

ACTION="status"
HOSTNAME_BIND="${HOSTNAME_BIND:-127.0.0.1}"
PORT="${PORT:-4096}"
ALLOW_UNSAFE_REMOTE="${ALLOW_UNSAFE_REMOTE:-0}"

usage() {
  cat <<'EOF'
Usage:
  ./run.sh [action] [options]

Actions:
  local                 Start locally on 127.0.0.1:4096 (default safe mode)
  remote                Start on 0.0.0.0; requires --password unless --unsafe
  start                 Start with the selected host/port
  restart               Stop, then start
  stop                  Stop BioMaster
  status                Show process and HTTP status
  logs                  Show recent server logs

Options:
  --host <host>         Bind host, e.g. 127.0.0.1 or 0.0.0.0
  --port <port>         Browser-facing server port (default: 4096)
  --password <value>    Basic auth password for remote access
  --unsafe             Allow 0.0.0.0 without a password (trusted networks only)
  -h, --help            Show this help

Examples:
  ./run.sh local
  ./run.sh remote --password '<strong-password>'
  ./run.sh restart --host 0.0.0.0 --port 18080 --password '<strong-password>'
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    local)
      ACTION="restart"
      HOSTNAME_BIND="127.0.0.1"
      shift
      ;;
    remote)
      ACTION="restart"
      HOSTNAME_BIND="0.0.0.0"
      shift
      ;;
    start|restart|stop|status|logs)
      ACTION="$1"
      shift
      ;;
    --host)
      HOSTNAME_BIND="${2:-}"
      shift 2
      ;;
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --password)
      export OPENCODE_SERVER_PASSWORD="${2:-}"
      shift 2
      ;;
    --unsafe)
      ALLOW_UNSAFE_REMOTE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

export PATH="$HOME/.bun/bin:$PATH"

if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Port must be numeric." >&2
  exit 1
fi

HEALTHCHECK_HOST="$HOSTNAME_BIND"
if [ "$HEALTHCHECK_HOST" = "0.0.0.0" ]; then
  HEALTHCHECK_HOST="127.0.0.1"
fi

SERVER_LOG="${SERVER_LOG:-$ROOT/.logs/opencode-${USER:-user}-server.log}"
mkdir -p "$(dirname "$SERVER_LOG")"

require_safe_remote() {
  if [ "$HOSTNAME_BIND" != "0.0.0.0" ]; then
    return
  fi
  if [ -n "${OPENCODE_SERVER_PASSWORD:-}" ]; then
    return
  fi
  if [ "$ALLOW_UNSAFE_REMOTE" = "1" ]; then
    echo "warning: binding to 0.0.0.0 without OPENCODE_SERVER_PASSWORD is unsecured"
    return
  fi
  cat >&2 <<'EOF'
Refusing to bind BioMaster to 0.0.0.0 without authentication.

Use:
  ./run.sh remote --password '<strong-password>'

For trusted isolated networks only:
  ./run.sh remote --unsafe
EOF
  exit 1
}

if command -v bun >/dev/null 2>&1; then
  BUN_CMD="bun"
else
  BUN_CMD="npx -y --package bun@1.3.14 bun"
fi

BIOSKILLS_PATH="$(python3 - <<PY
import base64
path = "${BIO_DIR}"
slug = base64.urlsafe_b64encode(path.encode()).decode().rstrip("=")
print(f"/{slug}/skills")
PY
)"

server_pids() { pgrep -u "${USER:-$(id -un)}" -f "${OC_INDEX}.*serve .*--port ${PORT}"; }
server_pid() { server_pids | head -1; }
legacy_frontend_pids() { pgrep -u "${USER:-$(id -un)}" -f "(npm exec bun@1.3.14.*run dev|bun.*run dev|vite).*--port ${PORT}"; }
port_listener_pids() {
  python3 - "$PORT" <<'PY'
import os
import socket
import struct
import sys
from pathlib import Path

port = int(sys.argv[1])
uid = os.getuid()
inodes = set()
for table in ("/proc/net/tcp", "/proc/net/tcp6"):
    try:
        lines = Path(table).read_text().splitlines()[1:]
    except OSError:
        continue
    for line in lines:
        cols = line.split()
        local = cols[1]
        state = cols[3]
        inode = cols[9]
        if state != "0A":
            continue
        local_port = int(local.rsplit(":", 1)[1], 16)
        if local_port == port:
            inodes.add(inode)

if not inodes:
    raise SystemExit

for proc in Path("/proc").iterdir():
    if not proc.name.isdigit():
        continue
    try:
        if proc.stat().st_uid != uid:
            continue
        fds = proc / "fd"
        for fd in fds.iterdir():
            try:
                target = os.readlink(fd)
            except OSError:
                continue
            if target.startswith("socket:[") and target[8:-1] in inodes:
                print(proc.name)
                break
    except OSError:
        continue
PY
}
managed_pids() { { server_pids; port_listener_pids; } | awk 'NF && !seen[$0]++'; }

http_code() { curl -s -o /dev/null -w "%{http_code}" --max-time 4 "$1" 2>/dev/null; }

start_server() {
  if [ -n "$(managed_pids)" ]; then
    echo "server already running (pid $(managed_pids | head -1))"
    return
  fi
  if [ ! -f "$APP_DIST/index.html" ]; then
    echo "missing Web UI build: $APP_DIST/index.html" >&2
    echo "Run ./install.sh before starting BioMaster." >&2
    exit 1
  fi
  echo "starting BioMaster on ${HOSTNAME_BIND}:${PORT} (project: ${BIO_DIR}) ..."
  setsid bash -c "cd '$BIO_DIR' && OPENCODE_CONFIG_DIR='$BIO_DIR/.opencode' OPENCODE_WEB_UI_DIST='$APP_DIST' ${BUN_CMD} --conditions=browser '$OC_INDEX' serve --port ${PORT} --hostname ${HOSTNAME_BIND} --print-logs > '$SERVER_LOG' 2>&1" < /dev/null &
  disown
}

stop_server() {
  local pids legacy
  pids="$(managed_pids)"
  if [ -n "$pids" ]; then
    echo "$pids" | while read -r pid; do
      [ -n "$pid" ] && kill "$pid" 2>/dev/null && echo "stopped server (pid $pid)"
    done
    sleep 2
    pids="$(managed_pids)"
    if [ -n "$pids" ]; then
      echo "$pids" | while read -r pid; do
        [ -n "$pid" ] && kill -KILL "$pid" 2>/dev/null && echo "force stopped server (pid $pid)"
      done
    fi
  else
    echo "server not running"
  fi

  legacy="$(legacy_frontend_pids)"
  if [ -n "$legacy" ]; then
    echo "$legacy" | while read -r pid; do
      [ -n "$pid" ] && kill "$pid" 2>/dev/null && echo "stopped legacy frontend (pid $pid)"
    done
  fi
}

show_status() {
  echo "server (${PORT}): pid=$(managed_pids | head -1 || echo -) http=$(http_code http://${HEALTHCHECK_HOST}:${PORT}/global/health)"
  if [ "$HOSTNAME_BIND" = "0.0.0.0" ]; then
    echo "app:       http://<server-ip>:${PORT}"
    echo "bioskills: http://<server-ip>:${PORT}${BIOSKILLS_PATH}"
    echo "local:     http://${HEALTHCHECK_HOST}:${PORT}"
  else
    echo "app:       http://${HOSTNAME_BIND}:${PORT}"
    echo "bioskills: http://${HOSTNAME_BIND}:${PORT}${BIOSKILLS_PATH}"
  fi
}

case "$ACTION" in
  start)
    require_safe_remote
    start_server
    echo "waiting for service ..."
    sleep 8
    show_status
    ;;
  restart)
    stop_server
    sleep 2
    require_safe_remote
    start_server
    echo "waiting for service ..."
    sleep 8
    show_status
    ;;
  stop)
    stop_server
    ;;
  status)
    show_status
    ;;
  logs)
    echo "=== server ($SERVER_LOG) ==="
    tail -n 40 "$SERVER_LOG" 2>/dev/null
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac
