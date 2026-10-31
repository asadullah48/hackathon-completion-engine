# Stage 1: Builder — install dependencies with build tools
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*
COPY services/discord-bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime — lean image with only what we need
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY services/discord-bot/bot/ ./bot/

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app
CMD ["python", "-m", "bot.main"]
