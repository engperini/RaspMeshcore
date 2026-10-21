#!/usr/bin/env python3
"""RaspMeshcore USB radio supervisor. No radio needed at boot.

Runs native Companion only while a CH341 USB device is present. Handles crash,
USB removal, startup failures and retry backoff; never starts RF by itself
unless the operator has supplied a compiled binary and explicit radio config.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

VID, PID = "1a86", "5512"

def devices(root):
    found = []
    for node in root.glob("*"):
        try:
            if (node / "idVendor").read_text().strip().lower() == VID and (
                node / "idProduct").read_text().strip().lower() == PID:
                found.append(node.name)
        except (OSError, ValueError):
            continue
    return sorted(found)

def status(path, state, detail="", attempts=0):
    record = {"state": state, "detail": detail, "attempts": attempts,
              "timestamp": int(time.time())}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(record, ensure_ascii=False) + "\n")
        tmp.replace(path)
    except OSError as e:
        print(f"status write failed: {e}", file=sys.stderr, flush=True)
    print(json.dumps(record, ensure_ascii=False), flush=True)

def stop(proc):
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--usb-root", type=Path, default=Path("/sys/bus/usb/devices"))
    p.add_argument("--status", type=Path, default=Path("/run/raspmeshcore/radio.json"))
    p.add_argument("--interval", type=float, default=2.0)
    p.add_argument("--retry-max", type=float, default=30.0)
    p.add_argument("--radio-config", type=Path, default=Path("/etc/raspmeshcore/radio.env"),
                   help="Required explicit radio settings; no RF until configured")
    args = p.parse_args()
    if args.interval <= 0 or args.retry_max <= 0:
        p.error("interval and retry-max must be positive")
    stopping = False
    def shutdown(_sig, _frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    proc = None
    attempts = 0
    next_retry = 0.0
    last_state = None
    try:
        while not stopping:
            present = devices(args.usb_root)
            now = time.monotonic()
            if not present:
                stop(proc)
                proc = None
                attempts = 0
                next_retry = 0.0
                state, detail = "waiting_usb", "MeshStick USB not detected"
            elif not args.radio_config.is_file():
                stop(proc)
                proc = None
                state, detail = "needs_configuration", str(args.radio_config)
            elif not args.binary.is_file() or not os.access(args.binary, os.X_OK):
                stop(proc)
                proc = None
                state, detail = "missing_binary", str(args.binary)
            elif proc is not None and proc.poll() is None:
                state, detail = "running", f"pid={proc.pid} usb={','.join(present)}"
            else:
                if proc is not None:
                    rc = proc.returncode
                    proc = None
                    attempts += 1
                    next_retry = now + min(args.retry_max, 2 ** min(attempts, 5))
                    print(f"Companion exited with code {rc}; retry scheduled", flush=True)
                if now < next_retry:
                    state, detail = "retrying", f"retry_in={next_retry-now:.1f}s"
                else:
                    cmd = [str(args.binary), "--radio-driver", "sx1262",
                           "--spi-dev-prefix", "usb_ch341",
                           "--cs-pin", "0", "--reset-pin", "2",
                           "--busy-pin", "4", "--irq-pin", "6"]
                    try:
                        child_env = os.environ.copy()
                        child_env["RPI_CONFIG_FILE"] = str(args.radio_config)
                        proc = subprocess.Popen(cmd, env=child_env)
                        state, detail = "starting", f"pid={proc.pid}"
                    except OSError as e:
                        attempts += 1
                        next_retry = now + min(args.retry_max, 2 ** min(attempts, 5))
                        state, detail = "start_error", str(e)
            if (state, detail) != last_state:
                status(args.status, state, detail, attempts)
                last_state = (state, detail)
            time.sleep(args.interval)
    finally:
        stop(proc)
        status(args.status, "stopped")

if __name__ == "__main__":
    main()
