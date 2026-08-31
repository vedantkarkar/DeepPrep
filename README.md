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

### Option 1: Docker Compose Setup

```bash
# 1. Clone repository
git clone https://github.com/your-username/DeepPrep.git
cd DeepPrep

# 2. Launch PostgreSQL, Backend, and Frontend
docker compose up --build

# 3. Open Application
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
```

### Option 2: Local Development Setup

#### 1. Backend Setup
```bash
# Activate Python environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# Run migrations and seed representative dataset
alembic upgrade head
PYTHONPATH=backend python backend/app/seed.py

# Start FastAPI server
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- -p 3000
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
