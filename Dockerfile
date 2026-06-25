# syntax=docker/dockerfile:1
#
# One image that builds the React frontend and serves it from the FastAPI
# backend at the same origin as the API. The result is a single web service:
# one URL to give participants, and no cross-origin/CORS setup.

# ---- Stage 1: build the React frontend ----
FROM node:20-slim AS frontend
WORKDIR /app/frontend
# Install dependencies first for better layer caching. The build needs the dev
# dependencies (vite, @vitejs/plugin-react, @babel/standalone), so do NOT omit
# them here.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# frontend/.env.production sets VITE_API_BASE="" so the built app calls /api on
# its own origin (i.e. this combined service).
RUN npm run build

# ---- Stage 2: the Python backend, which also serves the built frontend ----
FROM python:3.12-slim AS app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FRONTEND_DIST=/app/frontend/dist \
    STUDY_LOG_DIR=/data/logs
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
# The compiled UI from stage 1, served by FastAPI at the same origin as /api.
COPY --from=frontend /app/frontend/dist /app/frontend/dist
EXPOSE 8000
# Render and most hosts inject $PORT; default to 8000 for a plain `docker run`.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
