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

# ── 2. Frontend ─────────────────────────────────────
echo "🎨 Configurando Frontend (Tailwind CSS)..."
cd /Sinalize/frontend

if [ "$DEPLOY_MODE" = "dev" ]; then
  echo "📦 Instalando dependências do frontend..."
  npm install
  echo "🏗️ Executando build de desenvolvimento..."
  npm run build:dev
else
  echo "🏗️ Executando build de produção..."
  npm run build
fi

cd /Sinalize
echo "✅ Frontend pronto"

# ── 3. Migrações ──────────────────────────────────────
echo "🔄 Processando migrações..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo "✅ Migrações concluídas"

# ── 4. Collectstatic ──────────────────────────────────
if [ "$DEPLOY_MODE" = "prod" ]; then
  echo "📦 Coletando arquivos estáticos..."
  python manage.py collectstatic --noinput --clear
  echo "✅ Static files coletados"
fi

# ── 5. Servidor ───────────────────────────────────────
echo "🚀 Iniciando servidor [DEPLOY_MODE=${DEPLOY_MODE}]..."

if [ "$DEPLOY_MODE" = "prod" ]; then
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120
else
  # No modo dev, o CMD do Dockerfile ou docker-compose passa os argumentos aqui ($@)
  # Geralmente: python manage.py runserver 0.0.0.0:8000
  exec "$@"
fi
