"""Partial MeshCore Companion simulator: TCP framing + documented command subset.
NOT a cryptographic/RF/multihop emulator. Explicitly development-only.
"""
import asyncio
import logging
import os
import struct
import time
from protocol import Decoder, encode

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
PORT = int(os.getenv("SIM_PORT", "5000"))
NAME = b"RaspMeshcore SIMULATOR - NO RF"
KEY = bytes.fromhex("2a" * 32)  # fake, public, never a real identity

class Companion:
    def __init__(self):
        self.channels = {0: (b"Public", bytes(32))}
        self.messages = []

    def process(self, p):
        if not p:
            return []
        cmd = p[0]
        if cmd == 1:  # app start
            return [b"\x00"]
        if cmd == 22:  # device query
            return [bytes([13, 3, 32, 8]) + struct.pack("<I", 0) +
                    b"SIM-2026".ljust(12, b"\0") +
                    b"RaspMeshcore simulator".ljust(40, b"\0") +
                    b"0.1".ljust(20, b"\0")]
        if cmd == 2:  # get self info (documented response format)
            return [bytes([5, 0, 14, 14]) + KEY + bytes(12) +
                    struct.pack("<II", 915000, 62500) + bytes([8, 8]) + NAME]
        if cmd == 4:  # contacts
            return [b"\x02", b"\x04"]
        if cmd == 31 and len(p) >= 2:  # get channel
            i = p[1]
            name, secret = self.channels.get(i, (b"", bytes(32)))
            return [bytes([18, i]) + name.ljust(32, b"\0") + secret]
        if cmd == 32 and len(p) >= 66:  # set channel
            self.channels[p[1]] = (p[2:34].split(b"\0")[0], p[34:66])
            return [b"\x00"]
        if cmd == 3 and len(p) >= 7:  # send channel message
            i = p[2]
            if i not in self.channels:
                return [b"\x01\x03"]
            # Queue loopback RX, not RF, to test UI path
            self.messages.append(bytes([8, i, 0, 0]) + p[3:7] + p[7:])
            return [bytes([6, 0]) + bytes(4) + struct.pack("<I", 1), b"\x83"]
        if cmd == 10:  # sync next message
            return [self.messages.pop(0)] if self.messages else [b"\x0a"]
        if cmd == 20:  # battery
            return [b"\x0c" + struct.pack("<H", 100)]
        if cmd == 21:  # get time
            return [b"\x09" + struct.pack("<I", int(time.time()))]
        if cmd == 23:  # set time
            return [b"\x00"]
        logging.info("unsupported command 0x%02x", cmd)
        return [b"\x01\x01"]

async def client(reader, writer):
    sim = Companion()
    dec = Decoder()
    logging.info("simulated Companion client connected")
    try:
        while True:
            chunk = await reader.read(4096)
            if not chunk:
                break
            for payload in dec.feed(chunk):
                logging.info("cmd=%02x len=%d", payload[0], len(payload))
                for response in sim.process(payload):
                    writer.write(encode(response))
                await writer.drain()
    except (ConnectionError, ValueError) as exc:
        logging.warning("client error %s", exc)
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(client, "0.0.0.0", PORT)
    logging.warning("SIMULATOR ONLY - NO RF - NO CRYPTO - NO REAL MESH")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
