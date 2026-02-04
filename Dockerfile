# Build stage
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Create a non-root user
RUN groupadd -r botgroup && useradd -r -g botgroup botuser && \
    chown -R botuser:botgroup /app

COPY --from=builder /install /usr/local
COPY --chown=botuser:botgroup . .

USER botuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Healthcheck to ensure the bot script is present and potentially runnable
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('bot.py') else 1)"

CMD ["python", "bot.py"]
