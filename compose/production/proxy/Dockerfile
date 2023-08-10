# By default, nginx runs with root mode, not good for sercurity. So we will use unprivileged.
FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="ilikeblue"

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./start /start

ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

USER root

RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /start

VOLUME /vol/static

USER nginx

CMD ["/start"]