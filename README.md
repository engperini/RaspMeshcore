# RaspMeshcore

Docker-first integration project for Raspberry Pi 4 + native MeshCore Companion + RemoteTerm web UI.

## Stage 1 — RemoteTerm container baseline (delivered)

This stage packages **RemoteTerm only** using the upstream published image. It does **not** yet bundle or start MeshCoreRPI, emulate a radio, or demonstrate successful Companion connectivity. No hardware is required to inspect/start this service, but messaging requires a compatible Companion TCP server.

Prerequisites: Raspberry Pi OS with working Docker Engine and Docker Compose plugin. No host package upgrade is performed.

```bash
git clone https://github.com/engperini/RaspMeshcore.git
cd RaspMeshcore
cp .env.example .env
docker compose config
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 remoteterm
```

Default web bind is localhost only: `http://127.0.0.1:8080` **on the Pi**. For LAN access change `RASPMESH_BIND` to the Pi's LAN IPv4 address in `.env` after securing access. Do **not** expose RemoteTerm directly to the internet: its bot editor can execute arbitrary Python. The baseline disables bots by default; enable only after authentication and HTTPS are deployed.

Companion TCP is expected on `host.docker.internal:5000` (mapped to Docker host gateway). If Companion is not running, RemoteTerm may show disconnected; this is expected at this stage.

```bash
docker compose down
```

Persistent data: `./data/remoteterm`. Back up before upgrading. `latest` is used for initial exploration, not a reproducible production release; pin a verified digest/tag in the next stage.

## Upstream evidence
- https://github.com/jkingsman/Remote-Terminal-for-MeshCore (TCP host/port env, Docker Hub image, warnings)
- https://github.com/dabeani/MeshCoreRPI (native Pi Companion/repeater and SPI radio configuration)
- https://wiki.seeedstudio.com/get_started_with_meshcore_remote_terminal/

## Next stage
Containerize native MeshCoreRPI Companion with a reproducible ARM64 build and verify its actual TCP transport compatibility with RemoteTerm. Then implement a real protocol-aware simulation mode for no-HAT testing. Do not claim mesh messaging works until integration tests pass.

See [PLAN.md](PLAN.md).
