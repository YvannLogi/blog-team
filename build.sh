#!/usr/bin/env bash
# Script de build (ex. Render : Build Command = ./build.sh)
set -o errexit

# Installe uv s'il n'est pas déjà présent, puis les dépendances du uv.lock
command -v uv >/dev/null 2>&1 || pip install uv
uv sync --frozen --no-dev

cd david

uv run python manage.py collectstatic --no-input
uv run python manage.py migrate --no-input
uv run python manage.py create_admin
