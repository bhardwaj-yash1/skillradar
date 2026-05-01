#!/usr/bin/env bash
set -e

# Run database migrations before starting the app.
# Render will provide DATABASE_URL and other env vars at runtime.
if [ -n "${DATABASE_URL:-}" ]; then
  python -m alembic upgrade head
fi

exec "$@"
