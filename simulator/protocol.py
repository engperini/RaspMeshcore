"""MeshCore serial-over-TCP frame codec based on LinuxTcpSerialInterface.cpp."""
import struct

MAX_FRAME_SIZE = 255

def encode(payload: bytes, marker: bytes = b">") -> bytes:
    if marker not in (b"<", b">"):
        raise ValueError("invalid direction")
    if not 0 < len(payload) <= MAX_FRAME_SIZE:
        raise ValueError("invalid payload length")
    return marker + struct.pack("<H", len(payload)) + payload

class Decoder:
    def __init__(self, expected=b"<"):
        self.expected = expected
        self.buffer = bytearray()
    def feed(self, data: bytes):
        self.buffer.extend(data)
        result = []
        while len(self.buffer) >= 3:
            marker = bytes(self.buffer[:1])
            length = int.from_bytes(self.buffer[1:3], "little")
            if length > MAX_FRAME_SIZE:
                raise ValueError("invalid length")
            if len(self.buffer) < 3 + length:
                break
            payload = bytes(self.buffer[3:3 + length])
            del self.buffer[:3 + length]
            if marker == self.expected and length:
                result.append(payload)
        return result
