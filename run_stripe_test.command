#!/bin/zsh

cd /Users/jamesabrams/Documents/Codex/2026-05-31/https-chatgpt-com-g-g-p/dunedogsmerch

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

exec /Users/jamesabrams/Downloads/ready_ecommerce-2/.venv/bin/python manage.py runserver 127.0.0.1:8014
