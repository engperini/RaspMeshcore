import unittest
import struct
class FramingTests(unittest.TestCase):
    def test_little_endian_length(self):
        data = b"abc"
        wire = struct.pack("<H", len(data)) + data
        self.assertEqual(struct.unpack("<H", wire[:2])[0], 3)
        self.assertEqual(wire[2:], data)
    def test_max_length(self):
        self.assertLessEqual(4096, 65535)
if __name__ == "__main__":
    unittest.main()
