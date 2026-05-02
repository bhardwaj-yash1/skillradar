#!/usr/bin/env bash
set -e

echo "Starting container..."

# Run database migrations before starting the app if DATABASE_URL is set
if [ -n "${DATABASE_URL:-}" ]; then
  echo "Running database migrations..."
  python -m alembic upgrade head
  echo "Migrations completed."
else
  echo "No DATABASE_URL set, skipping migrations."
fi

echo "Starting application..."
exec "$@"
