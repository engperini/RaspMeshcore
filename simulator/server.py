"""Development-only TCP framing harness; NOT a MeshCore Companion emulator."""
import asyncio
import os
import struct
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
HOST = "0.0.0.0"
PORT = int(os.getenv("SIM_PORT", "5000"))
MAX_FRAME = 4096

async def handle(reader, writer):
    peer = writer.get_extra_info("peername")
    logging.info("connected peer=%s", peer)
    try:
        while True:
            header = await reader.readexactly(2)
            size = struct.unpack("<H", header)[0]
            if size > MAX_FRAME:
                logging.warning("invalid frame size=%s", size)
                break
            payload = await reader.readexactly(size)
            logging.info("frame size=%s payload_hex=%s", size, payload[:64].hex())
            # Intentionally no reply: fake protocol responses would misrepresent compatibility.
    except (asyncio.IncompleteReadError, ConnectionResetError):
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        logging.info("disconnected peer=%s", peer)

async def main():
    server = await asyncio.start_server(handle, HOST, PORT)
    logging.info("framing harness listening %s:%s (not MeshCore)", HOST, PORT)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
