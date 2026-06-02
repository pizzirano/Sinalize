#!/bin/bash
set -e

echo "🔎 Aguardando PostgreSQL em ${DB_HOST}:${DB_PORT:-5432}..."
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER"; do
  sleep 1
done
echo "✅ PostgreSQL está pronto!"

if [ "$DEPLOY_MODE" = "prod" ]; then
  echo "📦 Garantindo dependências do Frontend..."
  cd frontend
  npm install --include=dev
  echo "📦 Compilando Tailwind CSS para Produção..."
  npm run build
  cd ..
  echo "✅ Tailwind CSS compilado"
fi

echo "🔄 Rodando migrações..."
python manage.py migrate --noinput
echo "✅ Migrações aplicadas"

echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files coletados"

echo "Iniciando servidor em modo: ${DEPLOY_MODE}"

if [ "$DEPLOY_MODE" = "prod" ]; then
  exec /venv/bin/gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120
else
  exec "$@"
fi
