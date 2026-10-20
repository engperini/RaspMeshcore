FROM python:3.12-bookworm AS builder
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential cmake libgpiod-dev pkg-config && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir platformio
ARG MESHCORE_REF=main
RUN git clone https://github.com/dabeani/MeshCoreRPI.git /src && cd /src && git checkout "$MESHCORE_REF" && pio run -e RaspberryPiMC_native_companion
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgpiod2 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/.pio/build/RaspberryPiMC_native_companion/program /usr/local/bin/meshcore-companion
ENV MESHCORE_DATA_DIR=/data RPI_COMPANION_TCP_PORT=5000
VOLUME /data
EXPOSE 5000
CMD ["/usr/local/bin/meshcore-companion"]
