#!/usr/bin/env bash
set -u
echo "=== RaspMeshcore doctor ==="
uname -a
command -v docker >/dev/null && docker --version || echo "FAIL Docker not installed"
docker compose version || true
echo "SPI:"
ls /dev/spidev* 2>/dev/null || echo "No SPI devices (fine in simulator mode)"
echo "GPIO:"
ls /dev/gpiochip* 2>/dev/null || echo "No GPIO devices"
echo "Compose:"
docker compose --env-file .env.example -f compose.yaml -f compose.simulator.yaml config --quiet && echo "PASS compose" || echo "FAIL compose"
echo "Services:"
docker compose -f compose.yaml -f compose.simulator.yaml ps || true
