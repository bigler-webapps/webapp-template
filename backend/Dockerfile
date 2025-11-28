# --- [1] Frontend build phase ---
FROM --platform=$BUILDPLATFORM node:24-alpine AS deps
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

# 1. Package Files holen
COPY frontend/package.json frontend/pnpm-lock.yaml ./



# 4. Install
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install --prod --no-frozen-lockfile

FROM deps AS frontend_build
ENV NODE_ENV=production

# 5. Copy Source Code
# WICHTIG: Das kopiert dein lokales 'frontend/src' nach '/app/src'.
# Da Docker Ordner mergt (und nicht löscht), bleibt 'src/webapp-management' erhalten!
COPY frontend/ ./

# Build
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

# ---------------------------------------------------------------------------
# OPTIMIZATION: Split COPY to enable Docker Layer Caching
# ---------------------------------------------------------------------------

# 1. Copy only files needed for pip install
COPY backend/requirements.txt ./

# 2. Explicitly copy the injected library folder
# Docker will check ONLY these files for changes. 
# If you only changed app code (views.py), this step remains cached.
COPY backend/webapp-management/ ./webapp-management/

# 3. Install dependencies (Cached unless requirements or webapp-management change)
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------------------------------------------------------------------------

# 4. Copy the rest of the application code
# This layer will rebuild on every code change, but pip install is already done.
COPY backend/ ./

# JETZT installieren wir (Pip findet nun ./webapp-management lokal)
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy built frontend into static and template folder from Stage 1
COPY --from=frontend_build /app/build/static/ /app/backend/static/
COPY --from=frontend_build /app/build/index.html /app/backend/templates/index.html

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "project_template_app.asgi:application"]