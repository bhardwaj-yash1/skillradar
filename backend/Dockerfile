# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libmagic1 \
    poppler-utils \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libxkbcommon0 \
    libgbm1 \
    libcups2 \
    libdrm2 \
    libatspi2.0-0 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libxfixes3 \
    libxinerama1 \
    libxcursor1 \
    fonts-liberation \
    fonts-noto \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium

RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data/uploads \
    && chown -R appuser:appuser /app

COPY backend ./backend
COPY scripts ./scripts
COPY alembic.ini .
COPY requirements.txt .
COPY .env.example .
COPY docker-entrypoint.sh .
RUN chmod +x /app/docker-entrypoint.sh && chown -R appuser:appuser /app

# USER appuser

EXPOSE 8000
HEALTHCHECK CMD curl -f "http://localhost:${PORT:-8000}/health" || exit 1
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
