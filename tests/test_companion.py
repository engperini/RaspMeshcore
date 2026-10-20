import sys
import unittest
sys.path.insert(0, "simulator")
from companion import Companion
class CompanionTests(unittest.TestCase):
    def setUp(self):
        self.c = Companion()
    def test_handshake(self):
        self.assertEqual(self.c.process(b"\x01")[0], self.c.process(b"\x02")[0])
        self.assertEqual(self.c.process(b"\x01")[0][0], 5)
        self.assertEqual(self.c.process(b"\x16")[0][0], 13)
        self.assertEqual(self.c.process(b"\x17"), [b"\x0f"])
        self.assertEqual(self.c.process(b"\x05")[0][0], 9)
        self.assertEqual(self.c.process(b"\x06" + bytes(4)), [b"\x00"])
    def test_channel_roundtrip(self):
        self.assertEqual(self.c.process(bytes([31, 0]))[0][0], 18)
        self.assertEqual(self.c.process(bytes([32, 1]) + b"test".ljust(32, b"\0") + bytes(16)), [b"\x00"])
        self.assertIn(b"test", self.c.process(bytes([31, 1]))[0])
    def test_loopback(self):
        import struct
        msg = bytes([3, 0, 0]) + struct.pack("<I", 123) + b"hello"
        responses = self.c.process(msg)
        self.assertEqual(responses[0], b"\x00")
        self.assertEqual(responses[1], b"\x83")
        self.assertEqual(self.c.process(b"\x0a")[0][-5:], b"hello")
        self.assertEqual(self.c.process(b"\x0a"), [b"\x0a"])
if __name__ == "__main__":
    unittest.main()
