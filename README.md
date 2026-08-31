# DeepPrep — AI Role-Readiness & Preparation Platform

DeepPrep is an evidence-backed intelligence platform that tells engineering candidates how prepared they are for a specific job, based on verified practical evidence and the actual requirements of that job.

---

## The Problem
Most engineering candidates rely on guesswork or generic resume scoring algorithms that falsely equate keyword mentions with real capability. Candidates often don't know:
1. Whether they meet strict gating application prerequisites (degree, branch, graduation cutoff).
2. How their actual evidence (projects, GitHub repositories, competitive programming) measures up against role competency standards.
3. Where to focus their limited preparation time before an upcoming interview.

---

## Core Product Pipeline

```text
Resume Upload (PDF / DOCX / TXT)
            │
            ▼
Candidate Claims Extraction (Skills & Background)
            │
            ▼
Candidate Verification & Education Confirmation
            │
            ▼
Candidate Evidence Attachment (Projects, GitHub, Assessments)
            │
            ▼
Structured Target Job Requirements & Eligibility Gating
            │
            ▼
Phase 2 Deterministic Readiness Engine (0–100 Score + Explainable Trace)
            │
            ▼
Phase 6 Deterministic Preparation Optimizer (Personalized Weekly Roadmap)
```

---

## Architecture

```text
 ┌─────────────────────────────────────────────────────────────┐
 │               Next.js 14+ Frontend (App Router)            │
 │     Mobile-First UI · Glassmorphic Design · Inter Font     │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                   FastAPI REST Backend                      │
 │     OpenAPI Docs · Typed Pydantic Schemas · Safe Errors     │
 └───────┬──────────────────────┬───────────────────────┬──────┘
         │                      │                       │
         ▼                      ▼                       ▼
 ┌───────────────┐      ┌───────────────┐       ┌───────────────┐
 │   Candidate   │      │ Job Intel &   │       │ Readiness &   │
 │   & Evidence  │      │ Normalization │       │ Planning      │
 └───────┬───────┘      └───────┬───────┘       └───────┬───────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                PostgreSQL 16 Database                       │
 │      Alembic Migrations · Relational Schema · JSONB         │
 └─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, Lucide React
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy 2.0 (AsyncIO), Alembic
- **Database**: PostgreSQL 16 (Port 5433 / 5432)
- **Document Extractors**: PyPDF, python-docx
- **Testing**: pytest, pytest-asyncio (57 comprehensive unit/integration tests)

---

## Quick Start Guide

### Option 1: Docker Compose Setup (Full Stack)

Runs PostgreSQL (port 5433), FastAPI Backend (port 8000), and Next.js Frontend (port 3000) inside Docker containers.

```bash
# 1. Clone repository
git clone https://github.com/vedantkarkar/DeepPrep.git
cd DeepPrep

# 2. Launch all services (PostgreSQL, Backend, Frontend)
docker compose up --build
```

> [!TIP]
> **Linux Permission Note**: If you encounter `permission denied while trying to connect to the docker API`, either run with `sudo docker compose up --build` or add your user to the docker group:
> ```bash
> sudo usermod -aG docker $USER && newgrp docker
> ```

**Access URLs:**
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Option 2: Local Development Setup

#### 1. Database Setup
Start PostgreSQL on port `5433` (either via Docker or native service):

```bash
# Start only the PostgreSQL service using Docker Compose:
docker compose up -d postgres
```

#### 2. Backend Setup
```bash
# Create and activate Python virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# (Optional) Copy environment configuration
cp .env.example .env

# Run database migrations and seed canonical skills, jobs & demo candidate
alembic upgrade head
PYTHONPATH=backend python backend/app/seed.py

# Start FastAPI server with live-reloading
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- -p 3000
```

---

### Troubleshooting & Common Fixes

- **`[Errno 98] address already in use (port 8000)`**:
  An earlier backend process is already running. Check or terminate it with:
  ```bash
  kill -9 $(lsof -t -i:8000)
  ```
- **Database Re-seeding**:
  The seeding script (`backend/app/seed.py`) is idempotent and can be safely re-run at any time:
  ```bash
  PYTHONPATH=backend python backend/app/seed.py
  ```
- **Reset Database Schema**:
  To completely reset and re-apply all migrations:
  ```bash
  alembic downgrade base
  alembic upgrade head
  PYTHONPATH=backend python backend/app/seed.py
  ```

---

## AI Execution Modes
DeepPrep supports 3 interchangeable AI providers:
- `AI_PROVIDER="mock"` *(Default)*: 100% deterministic, zero-latency, works completely offline without API keys or internet.
- `AI_PROVIDER="cloud"`: Supports Google Gemini (`gemini-1.5-flash`) or OpenAI (`gpt-4o-mini`) via structured JSON schema enforcement.
- `AI_PROVIDER="local"`: Compatible with local Ollama instances (`llama3.2`).

---

## Running the Automated Test Suite

```bash
# Run all 57 backend unit and integration tests:
PYTHONPATH=backend ./backend/.venv/bin/pytest backend/tests/

# Run frontend production compilation:
cd frontend && npm run build
```

---

## Product Disclaimers & Invariants
1. **Evidence-Driven**: A skill extracted from a resume is solely a candidate claim. It confers 0 capability points until supported by verifiable evidence.
2. **Deterministic Readiness**: DeepPrep measures evidence-backed role alignment; it does **not** predict hiring probability or guarantee selection.
3. **Independent Eligibility Gating**: Application prerequisites (degree, branch, graduation cutoff) are strictly evaluated separately from technical readiness scores.
4. **Planning Strategy**: Preparation hour allocations are recommended heuristics based on priority and diminishing returns, not guaranteed learning outcomes.
