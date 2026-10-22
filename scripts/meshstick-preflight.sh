#!/usr/bin/env bash
# Read-only CH341/MeshStick discovery; does not claim a working MeshCore driver.
set -u
echo "=== MeshStick USB preflight (read-only) ==="
if ! command -v lsusb >/dev/null 2>&1; then
  echo "INFO: lsusb unavailable; install usbutils for USB enumeration"
  exit 0
fi
lsusb
echo
echo "Candidate CH341 devices (USB VID:PID 1a86:5512, verify against actual unit):"
if lsusb -d 1a86:5512; then
  echo "DETECTED: CH341 candidate; this does not validate SX1262 or MeshCore"
else
  echo "NOT DETECTED: no CH341 1a86:5512 found"
fi
echo
echo "INFO: do not use /dev/ttyUSB* as an SX1262 SPI interface."
echo "INFO: next checks require CH341 SPI/GPIO backend, pin mapping, TX/RX and protocol validation."
