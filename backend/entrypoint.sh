#!/bin/sh
set -e

mkdir -p /app/data

# If this script is running as root, fix ownership so the non-root user can write.
# (In Dockerfile we switch to appuser after this script in practice,
# but keep this safe if invoked differently.)
chown -R appuser:appuser /app/data || true

exec "$@"
