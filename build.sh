#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python manage.py migrate --noinput
python manage.py check

if grep -q "STATIC_ROOT" "classproject/settings.py"; then
  python manage.py collectstatic --noinput
fi
