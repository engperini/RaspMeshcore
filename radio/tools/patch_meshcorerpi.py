#!/usr/bin/env python3
"""Opt-in source overlay for MeshCoreRPI SX1262 driver. Refuses unknown upstream versions."""
from pathlib import Path
import argparse

p=argparse.ArgumentParser()
p.add_argument("upstream",type=Path,help="Local MeshCoreRPI checkout")
p.add_argument("--apply",action="store_true",help="Write files (default: validate only)")
args=p.parse_args()
src=args.upstream/"host/rpi_native_cli/src"
h=src/"SX1262LinuxRadio.h"
c=src/"SX1262LinuxRadio.cpp"
if not h.is_file() or not c.is_file():
    p.error("MeshCoreRPI host/rpi_native_cli/src not found")
header=h.read_text()
body=c.read_text()
if "usb_transport" in header or "usb_ch341" in body:
    p.error("Already patched; refusing second application")
def once(s,old,new):
    count=s.count(old)
    if count!=1:
        raise RuntimeError(f"Expected one upstream anchor, got {count}: {old[:100]!r}")
    return s.replace(old,new,1)
header=once(header,'#include "LinuxRadioBase.h"','#include "LinuxRadioBase.h"\n#include "Ch341MeshStickTransport.h"\n#include <memory>')
header=once(header,'  int spi_fd = -1;','  int spi_fd = -1;\n  std::unique_ptr<raspmeshcore::RadioTransport> usb_transport;')
body=once(body,'  if (spi_fd >= 0) {\n    close(spi_fd);','  usb_transport.reset();\n  if (spi_fd >= 0) {\n    close(spi_fd);')
body=once(body,'void SX1262LinuxRadio::openSpi() {\n#ifdef __linux__','void SX1262LinuxRadio::openSpi() {\n#ifdef __linux__\n  if (cfg.spi_dev_prefix == "usb_ch341") {\n    usb_transport.reset(new raspmeshcore::Ch341MeshStickTransport());\n    usb_transport->open();\n    return;\n  }')
body=once(body,'  if (len == 0) return;\n  if (spi_fd < 0)','  if (len == 0) return;\n  if (usb_transport) { usb_transport->transfer(tx, rx, len); return; }\n  if (spi_fd < 0)')
body=once(body,'void SX1262LinuxRadio::gpioExport(int pin) {\n  if (pin < 0) return;','void SX1262LinuxRadio::gpioExport(int pin) {\n  if (usb_transport) return;\n  if (pin < 0) return;')
body=once(body,'void SX1262LinuxRadio::gpioDirection(int pin, const char* mode) {\n  if (pin < 0) return;','void SX1262LinuxRadio::gpioDirection(int pin, const char* mode) {\n  if (usb_transport) return;\n  if (pin < 0) return;')
def usb_gpio_lookup():
    return '''  if (usb_transport) {
    using raspmeshcore::RadioSignal;
    if (pin == cfg.cs_pin) return RadioSignal::ChipSelect;
    if (pin == cfg.reset_pin) return RadioSignal::Reset;
    if (pin == cfg.busy_pin) return RadioSignal::Busy;
    if (pin == cfg.irq_pin) return RadioSignal::Dio1;
    throw std::runtime_error("CH341: unsupported GPIO pin");
  }
'''
# Do not use upstream pin IDs to represent CH341 signal IDs directly.
# Mapping is via cfg pins; defaults are distinct for CS/reset/busy/irq.
body=once(body,'void SX1262LinuxRadio::gpioWrite(int pin, int value) {\n  if (pin < 0) return;','void SX1262LinuxRadio::gpioWrite(int pin, int value) {\n  if (usb_transport) {\n    if (pin < 0) return;\n    if (pin == cfg.cs_pin) { usb_transport->write(raspmeshcore::RadioSignal::ChipSelect, value != 0); return; }\n    if (pin == cfg.reset_pin) { usb_transport->write(raspmeshcore::RadioSignal::Reset, value != 0); return; }\n    throw std::runtime_error("CH341: unsupported output pin");\n  }\n  if (pin < 0) return;')
body=once(body,'int SX1262LinuxRadio::gpioRead(int pin) {\n  if (pin < 0) return 0;','int SX1262LinuxRadio::gpioRead(int pin) {\n  if (usb_transport) {\n    if (pin == cfg.busy_pin) return usb_transport->read(raspmeshcore::RadioSignal::Busy);\n    if (pin == cfg.irq_pin) return usb_transport->read(raspmeshcore::RadioSignal::Dio1);\n    throw std::runtime_error("CH341: unsupported input pin");\n  }\n  if (pin < 0) return 0;')
# Ensure backend exists before any GPIO setup. Existing openSpi is after gpio setup.
body=once(body,'  // GPIO setup (sysfs) for SX1262 control pins.','  if (cfg.spi_dev_prefix == "usb_ch341") {\n    if (cfg.txen_pin >= 0 || cfg.rxen_pin >= 0)\n      throw std::runtime_error("CH341: set TXEN and RXEN to -1 (DIO2 RF switch)");\n    openSpi();\n  }\n  // GPIO setup (sysfs) for SX1262 control pins.')
body=once(body,'  openSpi();\n  gpioPulseReset();','  if (!usb_transport) openSpi();\n  gpioPulseReset();')
# CS upstream is active-low, MeshStick libpinedio CS is active-high.
body=once(body,'  if (cfg.cs_pin >= 0) gpioWrite(cfg.cs_pin, 0);\n\n  spi_ioc_transfer','  if (cfg.cs_pin >= 0) gpioWrite(cfg.cs_pin, 0);\n\n  spi_ioc_transfer') # no change; usb path exits earlier
# Existing startup GPIO write sets CS high; must not select USB radio before reset.
body=once(body,'  if (cfg.cs_pin >= 0) gpioWrite(cfg.cs_pin, 1);\n\n  if (!usb_transport) openSpi();','  if (cfg.cs_pin >= 0 && !usb_transport) gpioWrite(cfg.cs_pin, 1);\n\n  if (!usb_transport) openSpi();')
# Add CH341 object and libusb to both native Companion and Repeater builds.
pio=args.upstream/"platformio.ini"
ini=pio.read_text()
ini=once(ini,'  -I host/rpi_native_cli/src\n  -I lib/ed25519',
         '  -I host/rpi_native_cli/src\n  -I host/rpi_native_cli/src/raspmeshcore_usb\n  -I lib/ed25519') if False else ini
# Source filter paths are relative to src/. Both role targets need the CH341 source.
ini=ini.replace('  +<../host/rpi_native_cli/src/SX1262LinuxRadio.cpp>',
                '  +<../host/rpi_native_cli/src/SX1262LinuxRadio.cpp>\n  +<../host/rpi_native_cli/src/raspmeshcore_usb/Ch341MeshStickTransport.cpp>')
if ini.count('Ch341MeshStickTransport.cpp') != 3:
    raise RuntimeError("Expected three native targets")
# Native platform builds require explicit libusb link; add to all three target sections.
for section in ('env:RaspberryPiMC_native','env:RaspberryPiMC_native_repeater','env:RaspberryPiMC_native_companion'):
    marker='['+section+']'
    start=ini.index(marker)
    end=ini.find('\n[',start+len(marker))
    if end<0:end=len(ini)
    block=ini[start:end]
    if 'build_flags =' not in block:
        raise RuntimeError("No build_flags for "+section)
    block=block.replace('build_flags =','build_flags =\n  -I host/rpi_native_cli/src/raspmeshcore_usb\n  -L /usr/lib\n  -l usb-1.0',1)
    ini=ini[:start]+block+ini[end:]
# Use -lusb-1.0 in link flags too: build_flags may be reordered by PlatformIO.
# The source is copied into the upstream checkout by the --apply stage.
if args.apply:
    h.write_text(header)
    c.write_text(body)
    pio.write_text(ini)
    import shutil
    radio=Path(__file__).resolve().parents[1]
    dest=src/"raspmeshcore_usb"
    dest.mkdir(exist_ok=True)
    for name in ("Ch341MeshStickTransport.h","RadioTransport.h"):
        shutil.copy2(radio/"include"/name,dest/name)
    shutil.copy2(radio/"src"/"Ch341MeshStickTransport.cpp",dest/"Ch341MeshStickTransport.cpp")
    print("Patched upstream SX1262 radio. Link Ch341MeshStickTransport.cpp and libusb-1.0.")
else:
    print("PASS: upstream anchors matched; use --apply to modify local checkout")
