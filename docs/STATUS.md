# Integration status

- RemoteTerm upstream Docker image and TCP environment variables: verified by reading upstream README.
- MeshCoreRPI native Companion and SX1262/SX127x configuration: verified by reading upstream README.
- Native Companion TCP transport framing and compatibility with RemoteTerm: NOT verified.
- Docker startup on Raspberry Pi 4: NOT tested.
- `simulator/server.py`: TCP framing observer only, NOT a MeshCore Companion emulator. It does not reply to commands, encrypt, route or implement multihop.
- End-to-end chat/bots: NOT tested.
- Radio operation: blocked by lack of HAT.

## Critical next engineering task
Read and map the native Companion TCP bridge source and RemoteTerm's meshcore client framing. Implement a protocol-correct fake Companion with golden fixtures from upstream, then integration-test the real RemoteTerm against it. Do not call a socket listener a functional simulator.

## How to run observer
`docker compose -f compose.yaml -f compose.simulator.yaml up -d --build`
RemoteTerm may report disconnected or handshake timeout; this is expected until real protocol implementation.
