FROM python:3.10-alpine
LABEL maintainer="ilikeblue"

ENV PYTHONUNBUFFERED 1
ARG ROOT_PROJECT="/recipe/"
ARG APP_HOME="/recipe/app/"
ARG DEV=false

WORKDIR ${ROOT_PROJECT}

# we also need to install additional packages for psycopg2 module. Because we are using postgres-alpine so the
# additional packages are: postgresql-client, build-base, postgresql-dev, musl-dev. All packages except
# postgresql-client only need when building and installing, no need when running app so we can uninstall it after using
# it to install what we need

# for the pillow module (use for support handling images - real image, not docker image btw), we need jpeg-dev, gcc,
# python3-dev, zlib and zlib-dev in order to install this library. Except jpeg-dev, we need this after the image is
# installed, all other packages only need for installing pillow (python image library), so we can remove it afterward.

# linux-headers, build-base, pcre, pcre-dev are required for uWSGI server installation.
RUN mkdir .venv && \
	pip install --upgrade --no-cache-dir pip && \
    apk add --update --no-cache postgresql-client jpeg-dev pcre && \
    apk add --update --no-cache --virtual .tmp-build-deps \
      build-base postgresql-dev musl-dev zlib zlib-dev gcc python3-dev pcre-dev linux-headers && \
	pip install --no-cache-dir pipenv

COPY ./Pipfile ./Pipfile.lock ${ROOT_PROJECT}
COPY ./app ${APP_HOME}
COPY ./compose/production/django/start /scripts/production/start
COPY ./compose/local/django/start /scripts/local/start

# r: only able to read, ex: cat file, ls -l directory.
# w: able to edit the file, create, rename, delete files inside that directory.
# x: able to run a file or cd to directory.
RUN pipenv install --deploy && \
	if [ ${DEV} = "true" ]; \
		then pipenv install --dev --deploy ; \
	fi && \
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

#switch user
USER django-user