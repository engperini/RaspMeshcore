FROM python:3.12-alpine
WORKDIR /app
COPY server.py /app/server.py
USER 65534:65534
CMD ["python", "-u", "/app/server.py"]
