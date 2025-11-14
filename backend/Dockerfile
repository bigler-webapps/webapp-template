# --- [1] Frontend build phase (React + pnpm) ---
FROM --platform=$BUILDPLATFORM node:24-alpine AS deps
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY frontend/package.json frontend/pnpm-lock.yaml ./

RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install --prod --no-frozen-lockfile

FROM deps AS frontend_build
ENV NODE_ENV=production
COPY frontend/ ./
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm run build

# --- [2] Python / Django phase ---
FROM python:3.12-slim

WORKDIR /app/backend

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

COPY backend/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend/ ./

# Copy built frontend into static and template folder
COPY --from=frontend_build /app/build/static/ /app/backend/static/
COPY --from=frontend_build /app/build/index.html /app/backend/templates/index.html

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "project_template_app.asgi:application"]
