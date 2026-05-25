#!/bin/bash

set -e

: "${POSTGRES_HOST:=psql}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=postgres}"
: "${DEPLOY_MODE:=dev}"

# ── 1. Aguardar PostgreSQL ────────────────────────────
echo "🔎 Aguardando PostgreSQL em ${POSTGRES_HOST}:${POSTGRES_PORT}..."

until pg_isready \
  -h "${POSTGRES_HOST}" \
  -p "${POSTGRES_PORT}" \
  -U "${POSTGRES_USER}" >/dev/null 2>&1; do
  echo "🟡 PostgreSQL não disponível — tentando em 2s..."
  sleep 2
done

echo "✅ PostgreSQL disponível"

# ── 2. Build Tailwind ─────────────────────────────────
echo "🎨 Compilando Tailwind CSS..."

if [ "$DEPLOY_MODE" = "prod" ]; then
  cd /Sinalize/frontend && npm run build
else
  cd /Sinalize/frontend && npm run build:dev
fi

cd /Sinalize
echo "✅ Tailwind compilado"

# ── 3. Migrações ──────────────────────────────────────
echo "🔄 Aplicando migrações..."
python manage.py migrate --noinput
echo "✅ Migrações aplicadas"

# ── 4. Collectstatic ──────────────────────────────────
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files coletados"

# ── 5. Servidor ───────────────────────────────────────
echo "🚀 Iniciando servidor [DEPLOY_MODE=${DEPLOY_MODE}]..."

if [ "$DEPLOY_MODE" = "prod" ]; then
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120
else
  exec "$@"
fi
