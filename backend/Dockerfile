# syntax=docker/dockerfile:1.4

# --- [1] Frontend build phase ---
FROM --platform=$BUILDPLATFORM node:24-alpine AS frontend_build

WORKDIR /app

# pnpm aktivieren
RUN corepack enable && corepack prepare pnpm@latest --activate

# Nur für die Installation notwendige Dateien kopieren (Cache-freundlich)
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Dependencies installieren (öffentliches npm, keine Secrets mehr)
# Voraussetzung: pnpm-lock.yaml ist konsistent mit package.json
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install

# Rest des Frontend-Codes
COPY frontend/ ./

ENV NODE_ENV=production

# Build erzeugen
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm run build

# Optional, nur zum Debuggen:
# RUN ls -R build


# --- [2] Python / Django phase ---
FROM python:3.12-slim

WORKDIR /app/backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Systemabhängigkeiten
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so

# 1. Nur requirements kopieren (für Layer-Cache)
COPY backend/requirements.txt ./

# 2. Python-Dependencies EINMAL installieren
# WICHTIG: in requirements.txt muss jetzt z.B. stehen:
#   django-core-micha==0.1.1
# und KEIN "-e ./webapp-management" mehr.
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 3. Restlichen Backend-Code kopieren
COPY backend/ ./

# 4. Frontend-Build übernehmen
COPY --from=frontend_build /app/build/static/ ./static/
COPY --from=frontend_build /app/build/index.html ./templates/index.html

# 5. Static Files sammeln
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]
