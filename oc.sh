#!/usr/bin/env bash
# BioMaster-on-OpenCode dev launcher
# Usage: ./oc.sh {start|stop|restart|status|logs}
#
# Starts the opencode backend server (bound to the biomaster2-main project)
# and the SolidJS web frontend, so you can use BioMaster in a browser.

set -u

export PATH="$HOME/.bun/bin:$PATH"

SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
# ROOT is the directory that contains this script (portable across machines).
ROOT="$(cd "$(dirname "$0")" && pwd)"
BIO_DIR="$ROOT/biomaster2-main"
OC_INDEX="$ROOT/opencode/packages/opencode/src/index.ts"
APP_DIR="$ROOT/opencode/packages/app"

BACKEND_PORT=4096
FRONTEND_PORT=4444
HOSTNAME_BIND="127.0.0.1"

BACKEND_LOG="/tmp/opencode-backend.log"
FRONTEND_LOG="/tmp/opencode-frontend.log"

backend_pid() { pgrep -f "index.ts serve --port ${BACKEND_PORT}" | head -1; }
frontend_pid() { pgrep -f "vite --port ${FRONTEND_PORT}" | head -1; }

http_code() { curl -s -o /dev/null -w "%{http_code}" --max-time 4 "$1" 2>/dev/null; }

start_backend() {
  if [ -n "$(backend_pid)" ]; then
    echo "backend already running (pid $(backend_pid))"
    return
  fi
  echo "starting backend on ${HOSTNAME_BIND}:${BACKEND_PORT} (project: ${BIO_DIR}) ..."
  setsid bash -c "cd '$BIO_DIR' && bun run --conditions=browser '$OC_INDEX' serve --port ${BACKEND_PORT} --hostname ${HOSTNAME_BIND} --print-logs > '$BACKEND_LOG' 2>&1" < /dev/null &
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
  setsid bash -c "cd '$APP_DIR' && bun --bun run dev -- --port ${FRONTEND_PORT} --host ${HOSTNAME_BIND} > '$FRONTEND_LOG' 2>&1" < /dev/null &
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

case "${1:-status}" in
  start)
    start_backend
    start_frontend
    echo "waiting for services ..."
    sleep 14
    "$SELF" status
    ;;
  stop)
    stop_one "$(backend_pid)" backend
    stop_one "$(frontend_pid)" frontend
    ;;
  restart)
    "$SELF" stop
    sleep 3
    "$SELF" start
    ;;
  status)
    echo "backend  (${BACKEND_PORT}): pid=$(backend_pid || echo -) http=$(http_code http://${HOSTNAME_BIND}:${BACKEND_PORT}/agent)"
    echo "frontend (${FRONTEND_PORT}): pid=$(frontend_pid || echo -) http=$(http_code http://${HOSTNAME_BIND}:${FRONTEND_PORT}/)"
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
