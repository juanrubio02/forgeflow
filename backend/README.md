# Backend

Backend service for the Industrial Request Intelligence Platform.

The public project overview, demo flow and bootstrap instructions live in the root [`README.md`](../README.md).

## Local backend only

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.local.example .env
alembic upgrade head
python scripts/seed_demo.py
uvicorn app.main:app --host 127.0.0.1 --port 28000 --reload
```

## Tests

```bash
docker compose up -d postgres_test
cd backend
source .venv/bin/activate
pytest
```
