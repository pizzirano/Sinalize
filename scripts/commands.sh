#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
  sleep 2
done

echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

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