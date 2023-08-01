FROM python:3.10-alpine
LABEL maintainer="ilikeblue"

ENV PYTHONUNBUFFERED 1
ARG ROOT_PROJECT="/recipe/"
ARG APP_HOME='/recipe/app/'

COPY ./Pipfile ./Pipfile.lock ${ROOT_PROJECT}
COPY ./app ${APP_HOME}
COPY --chmod=777 ./compose/local/django/start ${ROOT_PROJECT}

WORKDIR ${ROOT_PROJECT}

ARG DEV=false
RUN mkdir .venv && \
	pip install --upgrade --no-cache-dir pip && \
	pip install --no-cache-dir pipenv && \
    pipenv install --deploy && \
	if [ ${DEV} = "true" ]; \
		then pipenv install --dev --deploy ; \
	fi && \
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

