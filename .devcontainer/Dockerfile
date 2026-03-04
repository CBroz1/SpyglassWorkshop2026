FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install MySQL 8.0 directly — avoids the ghcr.io/devcontainers/features/mysql
# Feature which fails to resolve in some Codespace environments.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        mysql-server \
    && rm -rf /var/lib/apt/lists/*
