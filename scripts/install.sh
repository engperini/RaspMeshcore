#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null || { echo "Docker missing. Install Docker Engine first."; exit 1; }
docker compose version >/dev/null || { echo "Docker Compose plugin missing."; exit 1; }
[[ "$(uname -m)" == "aarch64" ]] || echo "Warning: recommended Raspberry Pi OS 64-bit (aarch64)"
if [[ ! -e .env ]]; then cp .env.example .env; fi
mkdir -p data/remoteterm
echo "Choose: 1) RemoteTerm only 2) RemoteTerm + simulator (NO RF)"
read -r -p "Mode [2]: " mode
mode="${mode:-2}"
case "$mode" in
  1) docker compose -f compose.yaml up -d ;;
  2) docker compose -f compose.yaml -f compose.simulator.yaml up -d --build ;;
  *) echo "Invalid mode"; exit 2 ;;
esac
docker compose ps
echo "UI: http://127.0.0.1:8080 on the Pi."
echo "For LAN access, edit RASPMESH_BIND in .env, then rerun."
