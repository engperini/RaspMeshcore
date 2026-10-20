import unittest
from simulator.protocol import encode, Decoder
class ProtocolTest(unittest.TestCase):
    def test_fragmentation(self):
        wire = encode(b"hello", b"<")
        d = Decoder()
        self.assertEqual(d.feed(wire[:2]), [])
        self.assertEqual(d.feed(wire[2:]), [b"hello"])
    def test_multiple_frames(self):
        d = Decoder()
        self.assertEqual(d.feed(encode(b"a", b"<") + encode(b"b", b"<")), [b"a", b"b"])
    def test_wrong_direction(self):
        self.assertEqual(Decoder().feed(encode(b"a", b">")), [])
    def test_reject_oversize(self):
        with self.assertRaises(ValueError):
            encode(b"x" * 256)
    def test_little_endian(self):
        self.assertEqual(encode(b"x", b"<")[:3], b"<\x01\x00")
if __name__ == "__main__":
    unittest.main()
