FROM python:3.11.12

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - --version 2.1.3 && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock* /app/
RUN poetry install --no-root

COPY . /app
RUN poetry install --no-root

ENTRYPOINT [ "bash" ]
CMD ["./run.sh"]
