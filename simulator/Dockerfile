FROM python:3.12-alpine
WORKDIR /app
COPY protocol.py companion.py /app/
USER 65534:65534
EXPOSE 5000
CMD ["python", "-u", "/app/companion.py"]
