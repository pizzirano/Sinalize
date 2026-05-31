#!/bin/bash

# Encerra o script se qualquer comando falhar
set -e

# ─── Defaults ─────────────────────────────────────────────────────────────────
: "${POSTGRES_HOST:=psql}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=postgres}"
: "${DEPLOY_MODE:=dev}"

# ─── 1. Aguardar PostgreSQL ───────────────────────────────────────────────────
echo "🔎 Aguardando PostgreSQL em ${POSTGRES_HOST}:${POSTGRES_PORT}..."

until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" >/dev/null 2>&1; do
  echo "🟡 PostgreSQL não disponível ainda — tentando novamente em 2s..."
  sleep 2
done

echo "✅ PostgreSQL disponível"

# ─── 2. Build do Tailwind CSS ─────────────────────────────────────────────────
# Roda sempre: garante que o CSS está atualizado ao subir o container.
# Em dev: build normal (não minificado, mais rápido)
# Em prod: build minificado
echo "🎨 Compilando Tailwind CSS..."

if [ "$DEPLOY_MODE" = "prod" ]; then
  cd /Sinalize/frontend && npm run build
else
  cd /Sinalize/frontend && npm run build:dev
fi

cd /Sinalize
echo "✅ Tailwind CSS compilado"

# ─── 3. Migrações ─────────────────────────────────────────────────────────────
echo "🔄 Rodando migrações..."
python manage.py migrate --noinput
echo "✅ Migrações aplicadas"

# ─── 4. Collectstatic ─────────────────────────────────────────────────────────
# Em dev: roda mesmo assim para garantir consistência.
# Django em DEBUG=True serve arquivos de STATICFILES_DIRS diretamente,
# mas o output.css do Tailwind precisa estar em STATIC_ROOT para
# funcionar corretamente com o volume Docker.
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files coletados"

# ─── 5. Processo principal ────────────────────────────────────────────────────
# `exec "$@"` substitui o processo shell pelo CMD declarado no Dockerfile
# (ou sobrescrito pelo docker-compose). Isso garante que sinais do Docker
# (SIGTERM ao parar o container) cheguem diretamente ao Django/Gunicorn.
echo "Iniciando servidor em modo: ${DEPLOY_MODE}"

if [ "$DEPLOY_MODE" = "prod" ]; then
  exec gunicorn projeto.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120
else
  exec "$@"
fi