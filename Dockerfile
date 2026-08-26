# ── Stage 1: build React app ─────────────────────────────────────
FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python / FastAPI app ────────────────────────────────
FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app/backend

# Install Python dependencies (pure Python — no C extensions to compile)
COPY backend/pyproject.toml ./
RUN uv pip install --system --no-cache \
        "fastapi>=0.115" \
        "uvicorn[standard]>=0.32" \
        "pydantic>=2.9" \
        "anthropic>=0.40"

# Copy backend source
COPY backend/ ./

# Copy built frontend into static/
COPY --from=frontend-builder /app/frontend/dist ./static/

# SQLite DB lives in a mounted volume
ENV DB_PATH=/data/smoothiemixer.db

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
