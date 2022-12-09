FROM python:3.10

ENV POETRY_VERSION 1.2.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
ARG NO_DEV
RUN poetry install --no-interaction ${NO_DEV:---without dev}

COPY . /app

EXPOSE 8000
