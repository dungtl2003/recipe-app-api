#!/bin/sh

# if any commands below this fails, it will fail the whole script.
set -e

# collect all static files in project and put it into configure static directory.
python3 manage.py collectstatic --noinput
python3 manage.py migrate

# run the uWSGI server.
# socket :9000: binds the server to a TCP socket on port 9000
# workers 4: spawns 4 worker processes to handle requests
# master: enables master process mode
# enable-threads: allows each worker to run multiple threads
# module app.wsgi: loads the WSGI module from the app package
uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi