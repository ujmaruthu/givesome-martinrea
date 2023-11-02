#!/usr/bin/env sh
set -eo pipefail

# Create mount directory for service
mkdir -p $MNT_DIR

echo "Mounting GCS Fuse."
gcsfuse --debug_gcs \
        --debug_fuse \
        --implicit-dirs \
        --only-dir var \
        -o allow_other \
        $BUCKET $MNT_DIR 
echo "Mounting completed."

# Run django
memcached -u root -m 256 &

nginx -g 'daemon off;' &

uwsgi --socket givesome.socket \
           --home /opt/venv/ \
           --chdir /opt/app/ \
           --wsgi project.wsgi \
           --workers 3 \
           --chmod-socket=666 \
           --enable-threads
