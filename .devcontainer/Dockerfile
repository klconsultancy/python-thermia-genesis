FROM ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff AS uv

FROM mcr.microsoft.com/devcontainers/python:3.13@sha256:5ea7e72d3c1beb6aefdfea8001483345c39af4898e22f2c543deb6a00802ede4

COPY --from=uv /uv /uvx /usr/local/bin/

# Pre-create the cache mount point so the named volume is owned by vscode.
RUN install -d -o vscode -g vscode /home/vscode/.cache /home/vscode/.cache/uv
