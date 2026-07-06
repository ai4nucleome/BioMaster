#!/usr/bin/env bash
# Compatibility wrapper. Prefer ./run.sh for new deployments.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "notice: oc.sh is kept for compatibility; prefer ./run.sh" >&2
exec "$ROOT/run.sh" "$@"
