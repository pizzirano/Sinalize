#!/bin/bash

# Encerra o script se qualquer comando falhar
set -e

# --- Defaults -------------------------------------------------------
: "${POSTGRES_HOST:=psql}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=postgres}"
: "${DEPLOY_MODE:=dev}"

# --- 1. Aguardar PostgreSQL ------------------------------------------
echo "[STARTUP] Aguardando PostgreSQL em ${POSTGRES_HOST}:${POSTGRES_PORT}..."

until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" >/dev/null 2>&1; do
  echo "[STARTUP] PostgreSQL nao disponivel - tentando novamente em 2s..."
  sleep 2
done

echo "[STARTUP] PostgreSQL disponivel"

# --- 2. Build do Tailwind CSS ----------------------------------------
# Roda sempre: garante que o CSS esta atualizado ao subir o container.
# Em dev: build normal (nao minificado, mais rapido)
# Em prod: build minificado
echo "[STARTUP] Compilando Tailwind CSS..."

if [ "$DEPLOY_MODE" = "prod" ]; then
  cd /Sinalize/frontend && npm run build
else
  cd /Sinalize/frontend && npm run build:dev
fi

cd /Sinalize
echo "[STARTUP] Tailwind CSS compilado"

# --- 3. Migracoes ---------------------------------------------------
echo "[STARTUP] Rodando migracoes..."
python manage.py migrate --noinput
echo "[STARTUP] Migracoes aplicadas"

# --- 4. Collectstatic ------------------------------------------------
# Em dev: roda mesmo assim para garantir consistencia.
# Django em DEBUG=True serve arquivos de STATICFILES_DIRS diretamente,
# mas o output.css do Tailwind precisa estar em STATIC_ROOT para
# funcionar corretamente com o volume Docker.
echo "[STARTUP] Coletando arquivos estaticos..."
python manage.py collectstatic --noinput --clear
echo "[STARTUP] Static files coletados"

# --- 5. Processo principal -------------------------------------------
# exec "$@" substitui o processo shell pelo CMD declarado no Dockerfile
# (ou sobrescrito pelo docker-compose). Isso garante que sinais do Docker
# (SIGTERM ao parar o container) cheguem diretamente ao Django/Gunicorn.
echo "[STARTUP] Iniciando servidor em modo: ${DEPLOY_MODE}"

if [ "$DEPLOY_MODE" = "prod" ]; then
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --access-logformat '[%(h)s] %(t)s "%(r)s" %(s)s %(b)s %(D)sus'
else
  exec "$@"
fi
