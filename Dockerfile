ARG UV_IMAGE=ghcr.io/astral-sh/uv:python3.14-trixie-slim

FROM ${UV_IMAGE} AS builder

ARG INSTALL_DEV_DEPENDENCIES=false

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN if [ "${INSTALL_DEV_DEPENDENCIES}" = "true" ]; then \
        uv sync --frozen --no-install-project; \
    else \
        uv sync --frozen --no-install-project --no-dev; \
    fi


FROM ${UV_IMAGE} AS runtime

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app

WORKDIR /app

RUN chown app:app /app

COPY --from=builder --chown=app:app /app/.venv ./.venv
COPY --chown=app:app . .

USER app

RUN pybabel compile --directory locales
