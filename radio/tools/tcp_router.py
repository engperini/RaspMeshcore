#!/usr/bin/env python3
"""TCP stream router for RemoteTerm. Simulator remains default until USB mode is selected.

Mode is read for every new connection; changing mode requires restarting the
RemoteTerm TCP connection. No silent simulator fallback in USB mode.
"""
import os
import select
import socket
import socketserver

SIM = (os.getenv("SIMULATOR_HOST", "simulator"), int(os.getenv("SIMULATOR_PORT", "5000")))
USB = (os.getenv("USB_HOST", "host.docker.internal"), int(os.getenv("USB_PORT", "5000")))
MODE_FILE = os.getenv("MODE_FILE", "/config/radio-mode")

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            with open(MODE_FILE, encoding="utf-8") as f:
                mode = f.read().strip().lower()
        except FileNotFoundError:
            mode = "simulator"
        if mode not in ("simulator", "usb"):
            print(f"Invalid radio mode: {mode!r}; refusing connection", flush=True)
            return
        target = SIM if mode == "simulator" else USB
        try:
            upstream = socket.create_connection(target, timeout=5)
        except OSError as exc:
            print(f"Cannot connect to {mode} at {target}: {exc}", flush=True)
            return
        print(f"TCP client connected: mode={mode} target={target}", flush=True)
        with upstream:
            self.request.settimeout(None)
            upstream.settimeout(None)
            while True:
                ready, _, _ = select.select([self.request, upstream], [], [], 10)
                for source in ready:
                    data = source.recv(65536)
                    if not data:
                        return
                    (upstream if source is self.request else self.request).sendall(data)

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    with Server(("0.0.0.0", 5000), Handler) as server:
        print(f"RaspMeshcore TCP router listening, mode file: {MODE_FILE}", flush=True)
        server.serve_forever()
