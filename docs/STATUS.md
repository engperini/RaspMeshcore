# Integration status — 2026-10-19

## Source reviewed
- RemoteTerm supports TCP using MESHCORE_TCP_HOST and MESHCORE_TCP_PORT=5000 (upstream README).
- MeshCoreRPI native Companion implements TCP framing with '<' client-to-device and '>' device-to-client, 16-bit little-endian length, in LinuxTcpSerialInterface.cpp.
- MeshCoreRPI native Companion requires successful radio_init() before opening TCP.

## Delivered
- RemoteTerm Docker Compose baseline.
- Protocol-aware Python simulated Companion: app start, device query, self info, empty contacts, channel get/set, channel TX→queued local loopback RX, battery/time and unsupported-command errors.
- Separate persistent RemoteTerm data directory.
- Installer and doctor shell scripts; Compose overlay for simulator.
- Unit tests for frame codec and basic simulated commands.

## NOT validated
- Running Docker images on Raspberry Pi 4; GitHub Actions result not inspected.
- RemoteTerm full handshake and actual chat rendering. Upstream command layout/version variations may require changes.
- Bots in RemoteTerm UI, persistence and any encryption.
- Native Companion image build, radio access, real TX/RX, multihop.

**Simulation is explicitly fake loopback; it does not implement LoRa, cryptography, packet forwarding, or mesh peers.** Do not mistake TCP connection for end-to-end PASS.

## Local smoke test on Pi
```sh
bash scripts/install.sh
bash scripts/doctor.sh
docker compose -f compose.yaml -f compose.simulator.yaml logs --tail=100
```
Choose simulator in installer. The web page is bound to localhost by default; set RASPMESH_BIND to the Pi LAN IPv4 address for remote access. Keep bots disabled until HTTPS and authentication are configured.
