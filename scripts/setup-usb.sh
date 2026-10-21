#!/usr/bin/env bash
# Optional USB preparation for a clean clone. Keeps existing simulator and UI.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ "$(id -u)" == 0 ]]; then
  echo "Run as normal user with sudo privileges, not as root." >&2
  exit 2
fi
if ! command -v docker >/dev/null || ! sudo docker compose version >/dev/null 2>&1; then
  echo "Docker Engine + Compose plugin are required. See README." >&2
  exit 2
fi
if [[ ! -f .env ]]; then cp .env.example .env; fi
sudo mkdir -p data/radio data/remoteterm
sudo chown "$(id -u):$(id -g)" data/radio
if [[ ! -f data/radio/radio-mode ]]; then printf 'simulator\n' > data/radio/radio-mode; fi
echo "Preparing native Companion + USB supervisor (safe with radio unplugged)"
bash radio/tools/install-pi-usb.sh
echo "Starting UI, simulator and TCP router; preserves data/remoteterm"
sudo docker compose -p raspmeshcore -f compose.yaml -f compose.simulator.yaml -f compose.radio-router.yaml up -d --build
echo "=== Radio ==="
cat /tmp/raspmeshcore-radio.json || true
echo "=== Docker ==="
sudo docker compose -p raspmeshcore -f compose.yaml -f compose.simulator.yaml -f compose.radio-router.yaml ps
echo "UI port: 8080; RASPMESH_BIND in .env controls LAN exposure."
echo "The default mode remains simulator. RF hardware has not been validated."
