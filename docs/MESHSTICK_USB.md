# ELECROW MeshStick USB / CH341 integration

Status: **hardware purchased, not yet received; USB radio driver NOT implemented**.

## Non-breaking migration

- Keep RemoteTerm UI, bots, database, simulator, Docker baseline and existing SPI path untouched.
- Target radio: ELECROW MeshStick SX1262 915 MHz, USB CH341 bridge (USB SPI + GPIO), no Companion MCU.
- Target design: existing Linux MeshCore Companion/radio core, replace only hardware access layer with a CH341 transport. Do not assume the current Companion already exposes a reusable HAL: audit upstream first.
- openHop may be studied as a **reference** for CH341 transactions; it is not an added runtime dependency.
- Desired configuration values: `RADIO_BACKEND=simulator|spi|usb_ch341`. These are **design targets**, not currently active settings.
- Keep `simulator` as default until USB backend is implemented and validated. Do not add nonfunctional Compose switches.

## Acceptance gates

1. Read actual MeshStick USB VID:PID and CH341 GPIO wiring, check board revision and permissions.
2. Verify correct CH341 SPI chip-select framing, SX1262 RESET, BUSY and DIO1 handling.
3. Prove SX1262 register/status reads, TX and RX with real hardware and packet lengths representative of MeshCore.
4. Confirm existing Companion TCP framing and RemoteTerm compatibility, identity, crypto, ACK and multihop.
5. Only then enable a USB backend via an **opt-in** profile. Preserve SPI and simulator regressions.
6. Test unplug/replug, recovery, boot without radio and nonprivileged USB device access.

## Before hardware arrival

Run `bash scripts/meshstick-preflight.sh` on the Pi. This script only enumerates USB devices; it does not modify host drivers, enable radio or send data.

## References

- MeshStick hardware and pin map: https://github.com/markbirss/MESHSTICK
- Existing candidate Companion: https://github.com/dabeani/MeshCoreRPI
- RemoteTerm: https://github.com/jkingsman/Remote-Terminal-for-MeshCore

Do not report MeshCore USB compatibility as proven before actual integration testing.

## Source audit (2026-10-20)

Inspected upstream `dabeani/MeshCoreRPI` files:
- `host/rpi_native_cli/src/SX1262LinuxRadio.cpp`
- `host/rpi_native_cli/src/SX1262LinuxRadio.h`
- `host/rpi_native_cli/src/LinuxRadioBase.h`

The native SX1262 class currently opens `/dev/spidev*` and manipulates Raspberry sysfs GPIO directly. Its SPI transaction method controls CS and uses `SPI_IOC_MESSAGE(1)`. USB CH341 cannot be selected merely by changing `RPI_SPI_DEV_PREFIX`: the upstream driver requires a transport refactor.

An isolated C++ transport contract and mock test now live in `radio/include/RadioTransport.h` and `radio/tests/transport_contract_test.cpp`, with GitHub Actions compile/test. This is a **contract only**, not a CH341 hardware driver. Next: implement libusb CH341 backend, integrate through a pinned/forked upstream Companion source, validate USB VID:PID and board GPIO mapping. The current app is not changed.
