# Multi-stage build: frontend (Vite) + backend (Flask + Selenium)

###############################
# Stage 1: Frontend build
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY maiscorreios-frontend/ ./
RUN corepack enable && corepack prepare pnpm@10.4.1 --activate \
  && pnpm install --frozen-lockfile \
  && pnpm build

###############################
# Stage 2: Backend runtime
FROM python:3.10-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install Google Chrome (for Selenium)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates fonts-liberation libasound2 libnss3 libxss1 libatk-bridge2.0-0 libgtk-3-0 \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y --no-install-recommends google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Copy backend requirements and install
COPY maiscorreios-monitor/requirements.txt ./
RUN pip install -r requirements.txt

# Copy backend source
COPY maiscorreios-monitor/src ./src

# Copy frontend dist into backend static
RUN mkdir -p src/static
COPY --from=frontend /app/frontend/dist/ ./src/static/

EXPOSE 5001

CMD ["python", "src/main.py"]


