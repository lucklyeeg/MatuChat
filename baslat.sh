#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python bulunamadi. python.org uzerinden kurup tekrar dene."
  exit 1
fi

if ! "$PY" -c "import flask, requests" >/dev/null 2>&1; then
  echo "Gerekli paketler kuruluyor..."
  "$PY" -m pip install -r requirements.txt
fi

exec "$PY" app.py
