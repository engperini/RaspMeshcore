#!/usr/bin/env python3
"""Offline tests for USB supervisor (no hardware, Docker, or root required)."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "tools" / "usb_supervisor.py"
spec = importlib.util.spec_from_file_location("usb_supervisor", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class SupervisorTests(unittest.TestCase):
    def test_usb_enumeration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertEqual(mod.devices(root), [])
            usb = root / "1-1"
            usb.mkdir()
            (usb / "idVendor").write_text("1a86\n")
            (usb / "idProduct").write_text("5512\n")
            self.assertEqual(mod.devices(root), ["1-1"])
            (usb / "idProduct").write_text("0000\n")
            self.assertEqual(mod.devices(root), [])

    def test_missing_usb_stays_waiting(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            usb = root / "usb"
            usb.mkdir()
            status = root / "status.json"
            p = subprocess.Popen([sys.executable, str(SOURCE),
                                  "--usb-root", str(usb),
                                  "--binary", str(root / "missing"),
                                  "--status", str(status),
                                  "--interval", "0.1"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + 4
                while not status.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(status.exists())
                self.assertEqual(json.loads(status.read_text())["state"], "waiting_usb")
                self.assertIsNone(p.poll())
            finally:
                p.terminate()
                p.wait(timeout=5)

if __name__ == "__main__":
    unittest.main()
