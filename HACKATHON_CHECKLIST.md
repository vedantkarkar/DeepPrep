# DeepPrep — Hackathon Demo Checklist

### 1. Pre-Demo Setup (Run 10 Minutes Before Judging)
- [ ] Ensure PostgreSQL database is running (`localhost:5433` or Docker).
- [ ] Run seed verification: `PYTHONPATH=backend python backend/app/seed.py`.
- [ ] Verify backend is healthy: `curl http://localhost:8000/health` returns `{"status": "healthy"}`.
- [ ] Verify frontend is serving: `http://localhost:3000` loads hero page.
- [ ] Ensure `AI_PROVIDER=mock` in `.env` for zero-latency, 100% offline reliability.
- [ ] Open clean browser tab at `http://localhost:3000` with Developer Tools Console open (0 errors).

---

### 2. During-Demo Execution Checklist
- [ ] **Hero Landing Page**: Highlight "Stop guessing if you're job-ready".
- [ ] **Step 1 (Upload)**: Click "Quick Demo" shortcut $\rightarrow$ Aarav Deshmukh.
- [ ] **Step 2 (Claims)**: Emphasize "Unconfirmed Claim" status badge.
- [ ] **Step 3 (Education)**: Confirm B.Tech CS, COEP Pune 2025.
- [ ] **Step 4 (Evidence)**: Demonstrate project and GitHub verification links.
- [ ] **Step 5 (Target Job)**: Select Persistent Systems SDE-1 (Pune, MH).
- [ ] **Readiness Dashboard**:
  - [ ] Show 0–100 Score Gauge (46/100 · Not a hiring probability).
  - [ ] Show Application Eligibility (Prerequisites checked independently).
  - [ ] Expand "Why this score?" mathematical trace.
  - [ ] Point out Critical Gaps (OOP, SQL, DBMS, OS).
- [ ] **Preparation Roadmap**:
  - [ ] Click "Generate My Preparation Plan".
  - [ ] Click Week 1 to Week 4 tabs showing 48 total hours and activity pills.
  - [ ] Show Milestone targets.

---

### 3. Emergency Backup & Reset Actions
- **Fast Reset**: Click the "Reset Session" button in the top-right header, or run:
  ```bash
  PYTHONPATH=backend python backend/app/seed.py
  ```
- **If offline without internet**: DeepPrep works 100% offline via local mock providers and cached frontend bundles.
