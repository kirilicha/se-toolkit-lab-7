ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_NO_DEV=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/pyproject.toml,target=backend/pyproject.toml \
    --mount=type=bind,source=bot/pyproject.toml,target=bot/pyproject.toml \
    uv sync --locked --no-install-project

COPY bot /app/bot
COPY pyproject.toml uv.lock /app/
COPY backend/pyproject.toml /app/backend/pyproject.toml

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --package lms-bot

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app

USER nonroot
WORKDIR /app

CMD ["python", "bot/bot.py"]
