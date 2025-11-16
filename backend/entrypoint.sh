#!/bin/sh
set -e

echo "🐘 Esperando a la base de datos..."
until nc -z db 5432; do
  sleep 1
done
echo "✅ Base de datos lista."

echo "🔄 Ejecutando migraciones..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput || true

echo "🚀 Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
