# Build stage
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Upgrade system-level core packages to resolve vulnerabilities in the base image
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel

# Create a non-root user
RUN groupadd -r botgroup && useradd -r -g botgroup botuser && \
    chown -R botuser:botgroup /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=botuser:botgroup . .

USER botuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Healthcheck to ensure the bot script is present and potentially runnable
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('hub.py') else 1)"

CMD ["python", "hub.py"]
