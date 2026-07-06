#!/usr/bin/env bash
# BioMaster-on-OpenCode dev launcher
# Usage: ./oc.sh {start|stop|restart|status|logs}
#
# Starts the opencode backend server (bound to this BioMaster project root)
# and the SolidJS web frontend, so you can use BioMaster in a browser.

set -u

export PATH="$HOME/.bun/bin:$PATH"

SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
# ROOT is the directory that contains this script (portable across machines).
ROOT="$(cd "$(dirname "$0")" && pwd)"
BIO_DIR="$ROOT"
OC_INDEX="$ROOT/opencode/packages/opencode/src/index.ts"
APP_DIR="$ROOT/opencode/packages/app"

BACKEND_PORT="${BACKEND_PORT:-4096}"
FRONTEND_PORT="${FRONTEND_PORT:-4444}"
HOSTNAME_BIND="${HOSTNAME_BIND:-127.0.0.1}"
BACKEND_HOSTNAME_BIND="${BACKEND_HOSTNAME_BIND:-127.0.0.1}"
HEALTHCHECK_HOST="$HOSTNAME_BIND"
if [ "$HEALTHCHECK_HOST" = "0.0.0.0" ]; then
  HEALTHCHECK_HOST="127.0.0.1"
fi
BACKEND_HEALTHCHECK_HOST="$BACKEND_HOSTNAME_BIND"
if [ "$BACKEND_HEALTHCHECK_HOST" = "0.0.0.0" ]; then
  BACKEND_HEALTHCHECK_HOST="127.0.0.1"
fi

BACKEND_LOG="${BACKEND_LOG:-$ROOT/.logs/opencode-${USER:-user}-backend.log}"
FRONTEND_LOG="${FRONTEND_LOG:-$ROOT/.logs/opencode-${USER:-user}-frontend.log}"
mkdir -p "$(dirname "$BACKEND_LOG")" "$(dirname "$FRONTEND_LOG")"

require_safe_remote() {
  if [ "$HOSTNAME_BIND" != "0.0.0.0" ]; then
    return
  fi
  if [ -n "${OPENCODE_SERVER_PASSWORD:-}" ]; then
    return
  fi
  if [ "${ALLOW_UNSAFE_REMOTE:-0}" = "1" ]; then
    echo "warning: HOSTNAME_BIND=0.0.0.0 without OPENCODE_SERVER_PASSWORD is unsecured"
    return
  fi
  cat >&2 <<'EOF'
Refusing to bind BioMaster to 0.0.0.0 without authentication.

Set a password for remote access:
  HOSTNAME_BIND=0.0.0.0 OPENCODE_SERVER_PASSWORD='<strong-password>' ./oc.sh restart

For trusted isolated networks only, override with:
  ALLOW_UNSAFE_REMOTE=1 HOSTNAME_BIND=0.0.0.0 ./oc.sh restart
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

backend_pids() { pgrep -f "opencode/packages/opencode/src/index.ts serve .*--port ${BACKEND_PORT}"; }
backend_pid() { backend_pids | head -1; }
frontend_pids() { pgrep -f "(npm exec bun@1.3.14.*run dev|bun.*run dev|vite).*--port ${FRONTEND_PORT}"; }
frontend_pid() { frontend_pids | head -1; }

http_code() { curl -s -o /dev/null -w "%{http_code}" --max-time 4 "$1" 2>/dev/null; }

start_backend() {
  if [ -n "$(backend_pid)" ]; then
    echo "backend already running (pid $(backend_pid))"
    return
  fi
  echo "starting backend on ${BACKEND_HOSTNAME_BIND}:${BACKEND_PORT} (internal API, project: ${BIO_DIR}) ..."
  setsid bash -c "cd '$BIO_DIR' && ${BUN_CMD} --conditions=browser '$OC_INDEX' serve --port ${BACKEND_PORT} --hostname ${BACKEND_HOSTNAME_BIND} --print-logs > '$BACKEND_LOG' 2>&1" < /dev/null &
  disown
}

start_frontend() {
  if [ -n "$(frontend_pid)" ]; then
    echo "frontend already running (pid $(frontend_pid))"
    return
  fi
  echo "starting frontend on ${HOSTNAME_BIND}:${FRONTEND_PORT} ..."
  # Use `bun --bun` so vite runs on bun's runtime instead of whatever `node`
  # happens to be first in PATH (background shells can pick up an ancient node).
  setsid bash -c "cd '$APP_DIR' && VITE_OPENCODE_SINGLE_PORT=1 VITE_BIOMASTER_PROJECT_PATH='$BIO_DIR' VITE_OPENCODE_SERVER_HOST=${HEALTHCHECK_HOST} VITE_OPENCODE_SERVER_PORT=${BACKEND_PORT} VITE_OPENCODE_BACKEND_PROXY_TARGET=http://${BACKEND_HEALTHCHECK_HOST}:${BACKEND_PORT} ${BUN_CMD} --bun run dev -- --port ${FRONTEND_PORT} --host ${HOSTNAME_BIND} > '$FRONTEND_LOG' 2>&1" < /dev/null &
  disown
}

stop_one() {
  local pid="$1" name="$2"
  if [ -n "$pid" ]; then
    kill "$pid" 2>/dev/null && echo "stopped $name (pid $pid)"
  else
    echo "$name not running"
  fi
}

stop_backend() {
  local pids
  pids="$(backend_pids)"
  if [ -n "$pids" ]; then
    echo "$pids" | while read -r pid; do
      [ -n "$pid" ] && kill "$pid" 2>/dev/null && echo "stopped backend (pid $pid)"
    done
  else
    echo "backend not running"
  fi
}

stop_frontend() {
  local pids
  pids="$(frontend_pids)"
  if [ -n "$pids" ]; then
    echo "$pids" | while read -r pid; do
      [ -n "$pid" ] && kill "$pid" 2>/dev/null && echo "stopped frontend (pid $pid)"
    done
  else
    echo "frontend not running"
  fi
}

case "${1:-status}" in
  start)
    require_safe_remote
    start_backend
    start_frontend
    echo "waiting for services ..."
    sleep 14
    "$SELF" status
    ;;
  stop)
    stop_backend
    stop_frontend
    ;;
  restart)
    "$SELF" stop
    sleep 3
    "$SELF" start
    ;;
  status)
    echo "backend  (${BACKEND_PORT}, internal): pid=$(backend_pid || echo -) http=$(http_code http://${BACKEND_HEALTHCHECK_HOST}:${BACKEND_PORT}/global/health)"
    echo "frontend (${FRONTEND_PORT}): pid=$(frontend_pid || echo -) http=$(http_code http://${HEALTHCHECK_HOST}:${FRONTEND_PORT}/)"
    if [ "$HOSTNAME_BIND" = "0.0.0.0" ]; then
      echo "app:       http://<server-ip>:${FRONTEND_PORT}"
      echo "bioskills: http://<server-ip>:${FRONTEND_PORT}${BIOSKILLS_PATH}"
      echo "local:     http://${HEALTHCHECK_HOST}:${FRONTEND_PORT}"
    else
      echo "app:       http://${HOSTNAME_BIND}:${FRONTEND_PORT}"
      echo "bioskills: http://${HOSTNAME_BIND}:${FRONTEND_PORT}${BIOSKILLS_PATH}"
    fi
    ;;
  logs)
    echo "=== backend ($BACKEND_LOG) ==="; tail -n 20 "$BACKEND_LOG" 2>/dev/null
    echo "=== frontend ($FRONTEND_LOG) ==="; tail -n 20 "$FRONTEND_LOG" 2>/dev/null
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs}"
    exit 1
    ;;
esac
