# PassMyPass - Self-Hosting Docker Image
# Multi-stage build: frontend build + Python backend

# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY src/ src/
COPY static/ static/
COPY svelte.config.js vite.config.ts tsconfig.json ./
RUN npm run build

# Stage 2: Python backend + static frontend
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY server/app/ app/
COPY server/alembic/ alembic/
COPY server/alembic.ini .

# Copy frontend build
COPY --from=frontend-build /app/build /app/static_frontend

# Environment defaults (override in docker-compose or .env)
ENV DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/passmypass
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
