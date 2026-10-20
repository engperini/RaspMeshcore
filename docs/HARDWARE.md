# Native Companion container (experimental)

Source: dabeani/MeshCoreRPI, native target RaspberryPiMC_native_companion. Build uses multi-stage image, so host does not need PlatformIO, compilers or libgpiod packages. **Docker Engine and Compose must already exist.**

Run after HAT purchase and host SPI configuration:
```sh
cp .env.example .env
# Set RPI_FREQ_HZ and radio/GPIO settings matching the exact HAT.
docker compose -f compose.yaml -f compose.hardware.yaml build companion
docker compose -f compose.yaml -f compose.hardware.yaml up -d
```

No host OS upgrade is required by this procedure, but host kernel must expose /dev/spidev0.0 and /dev/gpiochip0. Actual chip numbering may differ and requires changing the device mapping. The GPIO ABI/library compatibility must be checked on the user's Raspberry Pi OS. The image build has NOT been validated. The upstream Companion exits if radio initialization fails; this is expected without hardware.

Important: upstream MeshCoreRPI is a fork based on MeshCore v1.13.0; compatibility with current RemoteTerm, particularly newer pathing and multihop, requires actual integration testing. Pin upstream commit once the build is validated. Do not transmit before checking local band rules, power, and radio settings.
