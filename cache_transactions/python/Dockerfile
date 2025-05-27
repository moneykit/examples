FROM python:3.11.12

# install uv and git
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y git

WORKDIR /app

COPY . /app
RUN uv sync

ENTRYPOINT [ "bash" ]
CMD ["./run.sh"]
