#!/usr/bin/env bash
set -e

echo "Starting container..."

# Debug: print python version and sys.path
python --version
python -c "import sys; print('Python path:', sys.path)"
python -c '
try:
    import alembic
    print("alembic ok")
except ImportError as e:
    print("alembic not found:", e)
'

# Run database migrations before starting the app if DATABASE_URL is set
if [ -n "${DATABASE_URL:-}" ]; then
  echo "Running database migrations..."
  python -m alembic upgrade head
  echo "Migrations completed."
else
  echo "No DATABASE_URL set, skipping migrations."
fi

echo "Starting application..."
if [ "$1" = "uvicorn" ]; then
  for arg in "$@"; do
    if [ "$arg" = "--port" ]; then
      exec "$@"
    fi
  done
  exec "$@" --port "${PORT:-8000}"
fi

exec "$@"
