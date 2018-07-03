#!/bin/sh

set -e
set -x

cd src
python manage.py jenkins \
  --noinput \
  --enable-coverage
