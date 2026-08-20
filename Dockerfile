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

# Runtime image without a package manager. `hub.py` never installs anything at
# run time, and pip ships a vendored tree (msgpack, setuptools' pkg_resources)
# that no `pip install --upgrade` can patch — it was the only source of HIGH
# findings in the Trivy container scan. Dropping pip removes the finding and
# the attack surface at once.
RUN rm -rf /opt/venv/lib/python3.11/site-packages/pip \
           /opt/venv/lib/python3.11/site-packages/pip-*.dist-info \
           /opt/venv/bin/pip /opt/venv/bin/pip3 /opt/venv/bin/pip3.11 \
           /usr/local/lib/python3.11/site-packages/pip \
           /usr/local/lib/python3.11/site-packages/pip-*.dist-info \
           /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.11 \
           /usr/local/lib/python3.11/ensurepip

COPY --chown=botuser:botgroup . .

USER botuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Healthcheck to ensure the bot script is present and potentially runnable
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('hub.py') else 1)"

CMD ["python", "hub.py"]
