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


# --- Stage 2: Python / Django ---
FROM python:3.14-slim

RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    gettext \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libraqm0 \
    libcairo2-dev \
    python3-cffi \
    python3-brotli \
    libpangoft2-1.0-0 \
    libopenjp2-7 \
    fonts-liberation \
    fontconfig \
    fonts-dejavu \
    procps \
    curl

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN export GDAL_LIBRARY_PATH=$(find /usr/lib -name libgdal.so | head -n 1) && \
    echo "GDAL_LIBRARY_PATH=${GDAL_LIBRARY_PATH}" >> /etc/environment

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
COPY --chown=deploy:deploy --from=frontend_build /app/build/static/ ./static/
COPY --chown=deploy:deploy --from=frontend_build /app/build/index.html ./templates/index.html

RUN mkdir -p media static staticfiles && chown -R deploy:deploy media static staticfiles

USER deploy

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]
