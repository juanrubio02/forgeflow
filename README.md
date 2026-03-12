# Industrial Request Intelligence Platform

Portfolio-ready demo of an industrial operations workspace for handling incoming commercial requests, attached documents and human-reviewed extracted data.

## What It Does

Industrial teams often receive RFQs, technical specs and purchase documents through fragmented channels. This project turns that intake into a structured operational flow:

- authenticate into an organization-scoped workspace
- create or simulate incoming requests
- review request detail, comments, assignment and status progression
- upload documents and inspect OCR / extraction output
- verify structured data before it becomes trusted operational context

The goal is not a generic CRM. It is a focused request-operations workflow for industrial quoting and document-heavy intake.

## Why It Is Useful

- centralizes scattered incoming demand into one operational queue
- makes document intelligence visible inside the workflow instead of hiding it in back-office tooling
- keeps comments, ownership, timeline and verified data tied to the same request
- provides a demoable end-to-end story without external SaaS dependencies

## Stack

- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS, TanStack Query, Vitest
- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, pytest
- Document pipeline: local document storage, OCR fallback, simple summarization / structured extraction pipeline
- Local orchestration: Docker Compose + bootstrap script

## Architecture

The repository is split into two applications:

- `frontend/`: recruiter-friendly product UI with login, request list/detail, document detail and demo intake
- `backend/`: modular FastAPI service with application/domain/infrastructure layers, tenant-safe request/document APIs and demo seed data

High-level flow:

1. user authenticates and selects an active organization access
2. requests are created manually or through demo intake scenarios
3. documents are attached to requests and stored locally
4. processing extracts text, document type, summary and structured fields
5. an operator reviews the request, comments, assignment and verified document data

## Main Features

- authentication and organization-scoped access context
- industrial request pipeline with status transitions
- request assignment and internal comments
- request activity timeline
- document upload and processing status tracking
- extracted text, summary and detected document type
- human-verified structured document fields
- demo intake scenarios that generate realistic sample requests

## Repository Layout

```text
backend/   FastAPI app, migrations, tests, demo seed and demo scenarios
frontend/  Next.js app, UI components, tests and i18n dictionaries
scripts/   Local bootstrap helpers
```

## Quick Start

### Option A: Recommended bootstrap

Requirements:

- Docker + Docker Compose
- Node.js 20+
- Python 3.13 recommended for local backend work

From the repo root:

```bash
./scripts/bootstrap_local.sh
cd frontend
npm install
npm run dev
```

What the bootstrap script does:

- picks a free backend port
- writes `frontend/.env.local`
- starts backend, PostgreSQL and Redis with Docker Compose
- runs database migrations
- seeds the demo organization and demo user

Then open:

- `http://localhost:3000/login`

Demo credentials:

- Email: `admin@acme.com`
- Password: `Admin1234`

### Option B: Manual local setup

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.local.example .env
docker compose -f ../docker-compose.yml up -d postgres redis
alembic upgrade head
python scripts/seed_demo.py
uvicorn app.main:app --host 127.0.0.1 --port 28000 --reload
```

Frontend:

```bash
cd frontend
npm install
printf 'NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:28000\n' > .env.local
npm run dev
```

## Environment Files

- `backend/.env.example`: Docker-friendly backend defaults
- `backend/.env.local.example`: local backend defaults without Docker hostnames
- `backend/.env.test.example`: optional overrides for test database/auth settings
- `frontend/.env.example`: frontend API base URL

No production secrets are required for local demo execution.

## Recommended Demo Flow

For a 3-5 minute demo:

1. Login with the seeded demo account.
2. Open `Guided demo` / `Demo guiada`.
3. Run `RFQ - Stainless Steel Mounting Brackets`.
4. Show the generated request detail.
5. Highlight assignment, internal comments and timeline.
6. Open the attached document.
7. Show extracted text, summary, detected type and verified data.
8. Return to the request list and filter by status or assignee.

## Validation Commands

Frontend:

```bash
cd frontend
npm test
npm run build
```

Backend:

```bash
docker compose up -d postgres_test
cd backend
source .venv/bin/activate
pytest
```

## Current Limitations

- authentication is demo-grade token auth, not a full production identity setup
- document intelligence is local and deterministic enough for demo purposes, not production-scale AI orchestration
- file storage is local filesystem storage
- there is no audit/export layer beyond the in-product timeline
- no background worker deployment setup is included beyond local/demo needs

## Short Roadmap

- role-based permissions per action surface
- richer verified-data schemas per document type
- external object storage and async worker deployment
- analytics around request throughput and bottlenecks

## Public Release Notes

- demo credentials are intentionally seeded and documented for local evaluation
- `.env`, test env files, caches and local build artifacts are ignored and should not be committed
- staging/production startup now rejects the placeholder auth secret
