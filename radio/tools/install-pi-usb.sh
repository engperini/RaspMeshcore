#!/usr/bin/env bash
# Safe Pi installer: preserves existing Docker/RemoteTerm/simulator.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UPSTREAM="${MESHCORE_RPI_DIR:-$HOME/MeshCoreRPI}"
PIN="5f7def6f14fbd0562a81d71c18d93739b65e029c"
echo "[1/6] Dependencies"
sudo apt-get update
sudo apt-get install -y git build-essential cmake pkg-config libusb-1.0-0-dev python3-venv
echo "[2/6] PlatformIO venv"
if [[ ! -x "$HOME/platformio-venv/bin/pio" ]]; then
  python3 -m venv "$HOME/platformio-venv"
  "$HOME/platformio-venv/bin/pip" install platformio
fi
export PATH="$HOME/platformio-venv/bin:$PATH"
echo "[3/6] MeshCoreRPI pinned checkout"
if [[ ! -d "$UPSTREAM/.git" ]]; then
  git clone https://github.com/dabeani/MeshCoreRPI.git "$UPSTREAM"
fi
if [[ -n "$(git -C "$UPSTREAM" status --porcelain)" ]]; then
  echo "ERROR: $UPSTREAM contains local changes; refusing to overwrite" >&2
  exit 1
fi
git -C "$UPSTREAM" fetch origin "$PIN"
git -C "$UPSTREAM" checkout --detach "$PIN"
echo "[4/6] CH341 overlay and native build"
bash "$ROOT/radio/tools/build-usb-companion.sh"
BIN="$UPSTREAM/.pio/build/RaspberryPiMC_native_companion/program"
test -x "$BIN"
echo "[5/6] Install isolated systemd service (waiting for USB)"
SUPERVISOR="$ROOT/radio/tools/usb_supervisor.py"
SERVICE=/etc/systemd/system/raspmeshcore-radio.service
sudo tee "$SERVICE" >/dev/null <<EOF
[Unit]
Description=RaspMeshcore USB radio supervisor (does not manage Docker)
After=network.target

[Service]
Type=simple
User=$(id -un)
Group=$(id -gn)
ExecStart=/usr/bin/python3 $SUPERVISOR --binary $BIN --status /tmp/raspmeshcore-radio.json
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now raspmeshcore-radio.service
echo "[6/6] Service status"
sudo systemctl --no-pager --full status raspmeshcore-radio.service || true
echo "Radio status: /tmp/raspmeshcore-radio.json"
echo "No changes were made to Docker, main branch, or simulator."
echo "NOTE: no USB hardware validation; configure legal frequency and radio settings before transmitting."
