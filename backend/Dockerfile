# --- [1] Frontend build phase (React + pnpm) ---
FROM --platform=$BUILDPLATFORM node:24-alpine AS deps
WORKDIR /app

# ENTFERNT: Hier keine Python-Sachen kopieren oder installieren!
# Node Image hat kein Pip.

# Setup Node tools
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy only Frontend dependency definitions
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install Frontend Dependencies
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install --prod --no-frozen-lockfile

FROM deps AS frontend_build
ENV NODE_ENV=production

# Copy Frontend Source Code
COPY frontend/ ./

# Build React App
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm run build


# --- [2] Python / Django phase ---
FROM python:3.12-slim

WORKDIR /app/backend

# System dependencies (PostGIS, etc.)
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

# 1. Requirements kopieren
COPY backend/requirements.txt ./

# 2. Python Dependencies installieren
# WICHTIG: Da wir die "Injector"-Methode nutzen, müssen wir hier sicherstellen, 
# dass der Ordner 'webapp-management' (falls vorhanden) VOR dem pip install kopiert wird,
# falls er in requirements.txt referenziert wird.
# ABER: Deine requirements.txt referenziert ./webapp-management.
# Das bedeutet, dieser Ordner MUSS existieren, BEVOR pip läuft.

# KORREKTUR DER REIHENFOLGE FÜR INJECTOR-STRATEGIE:
# Wir kopieren ALLES aus backend (inkl. requirements.txt UND webapp-management Ordner)
COPY backend/ ./

# JETZT installieren wir (Pip findet nun ./webapp-management lokal)
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy built frontend into static and template folder from Stage 1
COPY --from=frontend_build /app/build/static/ /app/backend/static/
COPY --from=frontend_build /app/build/index.html /app/backend/templates/index.html

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "project_template_app.asgi:application"]