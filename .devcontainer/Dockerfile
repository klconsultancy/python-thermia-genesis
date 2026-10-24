FROM mcr.microsoft.com/devcontainers/python:3.13

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /usr/local/bin/

# Pre-create the cache mount point so the named volume is owned by vscode.
RUN install -d -o vscode -g vscode /home/vscode/.cache /home/vscode/.cache/uv
