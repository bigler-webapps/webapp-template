# syntax=docker/dockerfile:1.24

# --- Stage 1: Frontend Build ---
FROM --platform=$BUILDPLATFORM node:24.15.0-alpine AS frontend_build

WORKDIR /app

ARG VITE_APP_MUI_LICENSE_KEY
ENV VITE_APP_MUI_LICENSE_KEY=$VITE_APP_MUI_LICENSE_KEY

# Pin pnpm version to the one declared in frontend/package.json
RUN corepack enable && corepack prepare pnpm@11.1.3 --activate

COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml frontend/.npmrc ./
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install

COPY frontend/ ./
ENV NODE_ENV=production
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm run build


# --- Stage 2: Python / Django base (deps + source, no frontend/collectstatic) ---
FROM python:3.14-slim AS backend_base

RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd \
    gettext \
    libraqm0 \
    fonts-liberation \
    fontconfig \
    fonts-dejavu \
    procps \
    curl

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system --gid 1000 deploy && \
    adduser --system --uid 1000 --ingroup deploy --home /app deploy

WORKDIR /app/backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

COPY backend/requirements.txt ./

ARG UV_FLAGS=""
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install ${UV_FLAGS} -r requirements.txt

COPY --chown=deploy:deploy backend/ ./


# --- Stage 3a: CI test target (CI-6) — pytest needs deps + source only, not the
# frontend static/collectstatic below. Building with `--target backend_test`
# skips the frontend_build stage entirely and stops here. ---
FROM backend_base AS backend_test


# --- Stage 3b: final deployed image — adds frontend static + collectstatic ---
FROM backend_base AS final

COPY --chown=deploy:deploy --from=frontend_build /app/build/static/ ./static/
COPY --chown=deploy:deploy --from=frontend_build /app/build/index.html ./templates/index.html

RUN mkdir -p media static staticfiles && chown -R deploy:deploy media static staticfiles

USER deploy

# Force IS_LOCAL=True during build so all non-local env guards
# (DJANGO_SECRET_KEY, EMAIL_HOST/PASSWORD, …) are skipped.
# Runtime: generate-env writes ENV_TYPE=production/staging to .env;
# docker-compose env_file overrides this build-time value.
ENV ENV_TYPE=local
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]
