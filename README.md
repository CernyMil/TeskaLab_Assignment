# TL Assignment

Short project README — how to build, run and debug the app locally (Docker/Compose), inspect the DB and run tests.

## Overview
This service reads JSON records, validates and batches them, and upserts data into PostgreSQL. The code lives in `src/` (main.py, parser.py, writer.py, models.py). Database DDL is in `src/schema.sql`.

## Prerequisites
- Docker & Docker Compose
- `psql` client for local DB debugging
- Python 3.12 and `uv` if you work with the image builder locally

## Environment
Configuration is read from environment variables. Create a `.env` (do not commit secrets) or set variables in `docker-compose.yaml`:

Important vars:
- `DB_DSN` — Postgres DSN (e.g. `postgresql://postgres:postgres@db:5432/tl_assignment`)
- `JSON_PATH` — path inside container to JSON data (default `/data/sample-data.json`)
- `BATCH_ROWS` — batch size (int)
- `MAX_QUEUE` — asyncio queue maxsize (int, 0 = unlimited)


## Build & run (recommended: docker-compose)
Build and run the app and DB together:

```bash
docker compose up -d --build
```
