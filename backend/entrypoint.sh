#!/bin/sh
set -e

# Si DJANGO_DEBUG=1 asumimos entorno de desarrollo (Docker local)
if [ "${DJANGO_DEBUG:-0}" = "1" ]; then
  DB_HOST="${POSTGRES_HOST:-news-db}"
  DB_PORT="${POSTGRES_PORT:-5432}"

  echo "🐘 [DEV] Esperando a la base de datos en $DB_HOST:$DB_PORT..."
  until nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 1
  done
  echo "✅ [DEV] Base de datos lista."

  echo "🔄 [DEV] Ejecutando migraciones..."
  python manage.py makemigrations --noinput || true
  python manage.py migrate --noinput || true

  echo "🚀 [DEV] Iniciando servidor Django (runserver)..."
  exec python manage.py runserver 0.0.0.0:8000

else
  echo "🔄 [PROD] Ejecutando migraciones..."
  python manage.py migrate --noinput || true

  echo "🚀 [PROD] Iniciando servidor con Gunicorn..."
  exec gunicorn news_service.wsgi:application --bind 0.0.0.0:${PORT:-8000}
fi

