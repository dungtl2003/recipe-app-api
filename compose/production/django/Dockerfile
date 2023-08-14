FROM python:3.10-alpine
LABEL maintainer="ilikeblue"

ENV PYTHONUNBUFFERED 1
ARG ROOT_PROJECT="/recipe/"
ARG APP_HOME="/recipe/app/"

COPY ./Pipfile ./Pipfile.lock ${ROOT_PROJECT}
COPY ./app ${APP_HOME}
COPY ./compose/production/django/start /scripts/production/start

WORKDIR ${ROOT_PROJECT}

RUN mkdir .venv && \
    pip install --upgrade --no-cache-dir pip && \
    apk add --update --no-cache postgresql-client jpeg-dev pcre && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev gcc python3-dev pcre-dev linux-headers && \
    pip install --no-cache-dir pipenv && \
    pipenv install --deploy && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol ${ROOT_PROJECT} && \
    chmod -R 755 /vol ${ROOT_PROJECT} && \
    chmod -R +x /scripts

ENV PATH="/scripts:${ROOT_PROJECT}.venv/bin:$PATH"

WORKDIR ${APP_HOME}

EXPOSE 8000

USER django-user