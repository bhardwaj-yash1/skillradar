#!/usr/bin/env bash
set -e

echo "Starting container..."
python --version
python -c "import sys; print('Python path:', sys.path)"
python -c '
try:
    import alembic
    print("alembic ok")
except ImportError as exc:
    print("alembic not found:", exc)
'

if [ -z "${DATABASE_URL:-}" ] && [ -n "${DATABASE_PRIVATE_URL:-}" ]; then
  export DATABASE_URL="${DATABASE_PRIVATE_URL}"
fi

if [ -z "${DATABASE_URL:-}" ] && [ -n "${DATABASE_PUBLIC_URL:-}" ]; then
  export DATABASE_URL="${DATABASE_PUBLIC_URL}"
fi

if [ -n "${DATABASE_URL:-}" ] || [ -n "${DATABASE_PRIVATE_URL:-}" ] || [ -n "${PGHOST:-}" ]; then
  echo "Running database migrations..."
  ATTEMPTS="${MIGRATION_MAX_ATTEMPTS:-12}"
  SLEEP_SECONDS="${MIGRATION_RETRY_SECONDS:-5}"
  for attempt in $(seq 1 "${ATTEMPTS}"); do
    if python -m alembic upgrade head; then
      echo "Migrations completed."
      break
    fi
    if [ "${attempt}" -eq "${ATTEMPTS}" ]; then
      echo "Migration failed after ${ATTEMPTS} attempts."
      exit 1
    fi
    echo "Migration attempt ${attempt}/${ATTEMPTS} failed. Retrying in ${SLEEP_SECONDS}s..."
    sleep "${SLEEP_SECONDS}"
  done
else
  echo "No database environment found, skipping migrations."
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
