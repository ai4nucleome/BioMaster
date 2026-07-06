#!/usr/bin/env bash
# BioMaster v0.5 first-time installer
# Usage:
#   ./install.sh          # install/update dependencies
#   ./install.sh --clean  # remove dependency folders before installing

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLEAN=0

for arg in "$@"; do
  case "$arg" in
    --clean)
      CLEAN=1
      ;;
    -h|--help)
      sed -n '1,8p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: ./install.sh [--clean]" >&2
      exit 1
      ;;
  esac
done

log() {
  printf '\n==> %s\n' "$*"
}

need_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

ensure_bun() {
  export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"
  export PATH="$BUN_INSTALL/bin:$PATH"
  if command -v bun >/dev/null 2>&1; then
    return
  fi
  log "Installing Bun"
  curl -fsSL https://bun.sh/install | bash
  export PATH="$BUN_INSTALL/bin:$PATH"
}

load_nvm() {
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck disable=SC1091
    . "$NVM_DIR/nvm.sh"
  fi
}

node_major() {
  node -p 'Number(process.versions.node.split(".")[0])' 2>/dev/null || echo 0
}

ensure_node22() {
  load_nvm
  if command -v node >/dev/null 2>&1 && [ "$(node_major)" -ge 22 ]; then
    return
  fi

  if ! command -v nvm >/dev/null 2>&1; then
    log "Installing nvm"
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    load_nvm
  fi

  log "Installing and selecting Node.js 22"
  nvm install 22
  nvm use 22
  nvm alias default 22
}

ensure_node_gyp() {
  log "Installing modern node-gyp"
  npm install -g node-gyp
  export npm_config_node_gyp="$HOME/.nvm/versions/node/$(node -v)/lib/node_modules/node-gyp/bin/node-gyp.js"
  if [ ! -f "$npm_config_node_gyp" ]; then
    npm_config_node_gyp="$(npm root -g)/node-gyp/bin/node-gyp.js"
    export npm_config_node_gyp
  fi
}

install_bun_dependencies() {
  local dir="$1"
  log "Installing Bun dependencies in $dir"
  if [ "$CLEAN" -eq 1 ]; then
    rm -rf "$dir/node_modules"
  fi
  (cd "$dir" && bun install)
}

log "Preparing BioMaster v0.5 under $ROOT"
need_command curl
need_command python3
python3 -m pip --version >/dev/null 2>&1 || {
  echo "Missing Python pip. Install python3-pip, then rerun ./install.sh." >&2
  exit 1
}

ensure_bun
ensure_node22
ensure_node_gyp

log "Runtime versions"
node -v
bun -v
if [ -f "$npm_config_node_gyp" ]; then
  node "$npm_config_node_gyp" --version
else
  echo "node-gyp path is not available: $npm_config_node_gyp" >&2
  exit 1
fi

log "Installing Python dependencies"
python3 -m pip install -r "$ROOT/requirements.txt"

install_bun_dependencies "$ROOT/opencode"
install_bun_dependencies "$ROOT/.opencode"

log "Building BioMaster indexes"
(cd "$ROOT" && make validate && make index)

cat <<EOF

BioMaster installation completed.

Start locally:
  ./run.sh local

Start on a remote server:
  ./run.sh remote --password '<strong-password>'

EOF
