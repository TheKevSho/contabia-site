# ── Hermes Gateway for Railway ─────────────────────────────────────────
# Stateless OpenAI-compatible API server + profile multiplexing.
# No Playwright, no TUI, no browser — just the API relay.

FROM python:3.11-slim-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install hermes-agent from PyPI (pre-built wheel avoids build block)
RUN pip install --no-cache-dir hermes-agent==0.19.0

# ── Runtime stage ──────────────────────────────────────────────────────
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Hermes from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/hermes /usr/local/bin/hermes
COPY --from=builder /usr/local/bin/hermes-agent /usr/local/bin/hermes-agent

# Hermes home — all config, profiles, and state live here
ENV HERMES_HOME=/etc/hermes

# Copy static config tree (no secrets)
COPY config/hermes/config.yaml /etc/hermes/config.yaml
COPY config/hermes/profiles/business/config.yaml /etc/hermes/profiles/business/config.yaml
COPY config/hermes/profiles/tayrona/config.yaml /etc/hermes/profiles/tayrona/config.yaml

# Entrypoint script — generates .env files from Railway secrets
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8642

ENTRYPOINT ["/start.sh"]