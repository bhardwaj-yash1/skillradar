FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libmagic1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium --with-deps
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl libmagic1 poppler-utils && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright
ENV PATH=/root/.local/bin:$PATH

RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY backend ./backend
COPY scripts ./scripts
COPY alembic.ini .
COPY .env.example .
RUN mkdir -p /app/data/uploads && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
