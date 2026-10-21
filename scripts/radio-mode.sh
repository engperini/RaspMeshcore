#!/usr/bin/env bash
# Switch the stable RemoteTerm TCP router between simulator and USB.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="${1:-}"
if [[ "$MODE" != simulator && "$MODE" != usb ]]; then
  echo "Usage: bash scripts/radio-mode.sh simulator|usb" >&2
  exit 2
fi
mkdir -p "$ROOT/data/radio"
printf '%s\n' "$MODE" > "$ROOT/data/radio/radio-mode"
echo "Selected $MODE for NEW RemoteTerm TCP connections."
echo "Existing TCP connections remain on their prior backend until reconnected."
echo "For USB mode ensure host Companion listens on a Docker-reachable address."
