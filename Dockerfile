FROM python:3.11-slim-buster

ENV APP_DIR=/boardgame \
    POETRY_VERSION=1.5.1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR ${APP_DIR}

COPY poetry.lock ${APP_DIR}/poetry.lock
COPY pyproject.toml ${APP_DIR}/pyproject.toml

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends nginx curl vim && \
    pip --no-cache-dir install poetry==${POETRY_VERSION} && \
    poetry install --no-interaction --no-ansi && \
    apt-get clean && \
    apt-get remove --purge -y build-essential && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/ /tmp/* /var/tmp/* ~/.cache/*

COPY . ${APP_DIR}

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
