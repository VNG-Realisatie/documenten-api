#!/bin/sh

set -ex

uwsgi_port=${UWSGI_PORT:-8000}

# Wait for the database container
# See: https://docs.docker.com/compose/startup-order/

export PGHOST=${DB_HOST:-db}
export PGUSER=${DB_USER:-postgres}
export PGPASSWORD=${DB_PASSWORD}
export PGPORT=${DB_PORT:-5432}

until psql -c '\q'; do
  >&2 echo "Waiting for database connection..."
  sleep 1
done

>&2 echo "Database is up."

# Apply database migrations
>&2 echo "Apply database migrations"
python src/manage.py migrate

# Load any JSON fixtures present
if [ -d $fixtures_dir ]; then
    echo "Loading fixtures from $fixtures_dir"

    for fixture in $(ls "$fixtures_dir/"*.json)
    do
        echo "Loading fixture $fixture"
        src/manage.py loaddata $fixture
    done
fi

# Start server
>&2 echo "Starting server"
uwsgi \
    --http :$uwsgi_port \
    --module drc.wsgi \
    --static-map /static=/app/static \
    --static-map /media=/app/media  \
    --static-map /_docs=/app/docs/_build/html  \
    --chdir src \
    --processes 2 \
    --threads 2 \
    --buffer-size=32768
    # processes & threads are needed for concurrency without nginx sitting inbetween
