#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e

# Ensure defaults if env vars missing
: "${POSTGRES_HOST:=psql}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=postgres}"

echo "🔎 Waiting for Postgres to accept connections on ${POSTGRES_HOST}:${POSTGRES_PORT}..."

# Prefer pg_isready (provided by postgresql-client). Exit code 0 = accepting connections.
until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" >/dev/null 2>&1; do
  echo "🟡 Postgres not ready yet (${POSTGRES_HOST}:${POSTGRES_PORT}) — retrying in 2s..."
  sleep 2
done

echo "✅ Postgres Database Started Successfully (${POSTGRES_HOST}:${POSTGRES_PORT})"

echo "🔄 migrate..."
python manage.py migrate --noinput

echo "iniciando servidor..."

if [ "$DEPLOY_MODE" = "prod" ]; then
    echo "🔄 collectstatic..."
    python manage.py collectstatic --noinput
  gunicorn projeto.wsgi:application --bind 0.0.0.0:8000
else
    python manage.py runserver 0.0.0.0:8000
fi