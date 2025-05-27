FROM python:3.11.12

# install uv and git
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y git

WORKDIR /app

COPY . /app
RUN uv sync

ENV PORT=8000
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000", "--reload"]
