#!/bin/sh

set -e

# environment substitute
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
# run nginx in foreground.
nginx -g 'daemon off;'