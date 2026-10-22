#!/usr/bin/env bash
# Build native MeshCore Companion with USB CH341 backend; no installation or radio transmission.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UPSTREAM="${MESHCORE_RPI_DIR:-$HOME/MeshCoreRPI}"
if [[ ! -d "$UPSTREAM/.git" ]]; then
  echo "Missing MeshCoreRPI checkout: $UPSTREAM" >&2
  echo "Clone: git clone https://github.com/dabeani/MeshCoreRPI.git '$UPSTREAM'" >&2
  exit 2
fi
if ! command -v pio >/dev/null; then
  echo "Install PlatformIO CLI first: python3 -m pip install --user platformio" >&2
  exit 2
fi
if ! pkg-config --exists libusb-1.0; then
  echo "Install libusb headers: sudo apt install libusb-1.0-0-dev pkg-config" >&2
  exit 2
fi
if grep -q "usb_ch341" "$UPSTREAM/host/rpi_native_cli/src/SX1262LinuxRadio.cpp" && grep -q "Ch341MeshStickTransport.cpp" "$UPSTREAM/platformio.ini"; then
  echo "CH341 overlay already applied; verifying and rebuilding"
  test -f "$UPSTREAM/host/rpi_native_cli/src/raspmeshcore_usb/Ch341MeshStickTransport.cpp" || { echo "Incomplete overlay" >&2; exit 2; }
else
  python3 "$ROOT/radio/tools/patch_meshcorerpi.py" "$UPSTREAM" --apply
fi
(cd "$UPSTREAM" && pio run -e RaspberryPiMC_native_companion)
echo "Built binary: $UPSTREAM/.pio/build/RaspberryPiMC_native_companion/program"
echo "Hardware and RF operation NOT validated. Configure region before use."
