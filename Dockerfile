FROM python:3.10 as production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=10 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_INSTALLER_PARALLEL=false \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    DOCKER_DEFAULT_PLATFORM=linux/amd64

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
WORKDIR /app

RUN apt-get update \
 && apt-get install --no-install-recommends -y curl build-essential \
 && rm -rf /var/lib/apt/lists/*

# install poetry
ENV POETRY_VERSION=1.1.13
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python -

# install runtime dependencies
COPY poetry.lock pyproject.toml $PYSETUP_PATH/
RUN cd $PYSETUP_PATH \
 && poetry run pip install -U pip \
 && poetry install --no-dev

# non-root user rights
RUN groupadd -r app && useradd --no-log-init -r -g app app && chown -R app /app

# copy configuration files
COPY --chown=app:app Makefile alembic.ini pyproject.toml /app/
# COPY --chown=app:app settings /app/settings

# copy app and migrations
COPY --chown=app:app price_comparison /app/price_comparison

# setup rights
USER app

CMD ["python", "-m", "price_comparison"]

