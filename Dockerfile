FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml
COPY ./uv.lock /app/uv.lock
RUN uv sync --project app --frozen --compile-bytecode

COPY ./src /app
COPY ./data /data

ENV PATH="/app/.venv/bin:${PATH}"
ENV JSON_PATH=/data/sample-data.json         BATCH_ROWS=10000         MAX_QUEUE=5

CMD ["uv", "run", "--project", "app", "./main.py"]
