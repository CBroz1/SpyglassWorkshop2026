FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install MySQL 8.0 directly — avoids the ghcr.io/devcontainers/features/mysql
# Feature which fails to resolve in some Codespace environments.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        mysql-server \
    && rm -rf /var/lib/apt/lists/*

# Install Miniforge3 (conda + mamba) to /opt/conda.
# The postCreateCommand (setup-db.sh) creates the 'spyglass' conda env.
ENV CONDA_DIR=/opt/conda
RUN curl -fsSL \
        "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-$(uname -m).sh" \
        -o /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p "${CONDA_DIR}" && \
    rm /tmp/miniforge.sh && \
    # Make the conda installation usable by the non-root vscode user.
    chmod -R a+rwX "${CONDA_DIR}" && \
    ln -s "${CONDA_DIR}/etc/profile.d/conda.sh" /etc/profile.d/conda.sh

ENV PATH="${CONDA_DIR}/bin:${PATH}"
