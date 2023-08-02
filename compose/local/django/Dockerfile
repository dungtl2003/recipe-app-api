FROM python:3.10-alpine
LABEL maintainer="ilikeblue"

ENV PYTHONUNBUFFERED 1
ARG ROOT_PROJECT="/recipe/"
ARG APP_HOME='/recipe/app/'

COPY ./Pipfile ./Pipfile.lock ${ROOT_PROJECT}
COPY ./app ${APP_HOME}
COPY --chmod=777 ./compose/local/django/start ${ROOT_PROJECT}

WORKDIR ${ROOT_PROJECT}

# we also need to install additional packages for psycopg2 module. Because we are using postgres-alpine so the
# additional packages are: postgresql-client, build-base, postgresql-dev, musl-dev. All packages except
# postgresql-client only need when building and installing, no need when running app so we can uninstall it after using
# it to install what we need
ARG DEV=false
RUN mkdir .venv && \
	pip install --upgrade --no-cache-dir pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
      build-base postgresql-dev musl-dev && \
	pip install --no-cache-dir pipenv && \
    pipenv install && \
	if [ ${DEV} = "true" ]; \
		then pipenv install --dev ; \
	fi && \
    apk del .tmp-build-deps && \
	chmod -R 777 ${APP_HOME} && \
    adduser \
	--disabled-password \
	--no-create-home \
	django-user

ENV PATH="${ROOT_PROJECT}/.venv/bin:$PATH"

WORKDIR ${APP_HOME}

EXPOSE 8000

#switch user
USER django-user

