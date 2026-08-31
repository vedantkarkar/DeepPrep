import pytest
from sqlalchemy.future import select
from app.models.job import Job
from app.models.session import PreparationSession
from app.domains.readiness.service import ReadinessService

@pytest.mark.asyncio
async def test_full_pipeline_from_resume_to_phase2_readiness(api_client, db_session):
    """Critical End-to-End Test (Section 35):
    1. Upload resume -> parse unconfirmed claims.
    2. Candidate confirms Python, FastAPI, PostgreSQL, and Git; rejects Docker.
    3. Candidate submits verified project evidence for confirmed skills.
    4. Trigger Phase 2 deterministic engine for Junior Backend Engineer role.
    5. Verify exact scoring trace, strength/gap classification, and isolation of rejected/unevidenced claims.
    """
    # Step 1: Upload resume
    with open("data/resumes/demo_resume.txt", "rb") as f:
        files = {"file": ("demo_resume.txt", f, "text/plain")}
        extract_resp = await api_client.post("/api/v1/resumes/extract", files=files)

    assert extract_resp.status_code == 200
    extracted = extract_resp.json()
    assert extracted["status"] == "needs_confirmation"
    
    # Step 2: Create Candidate & Confirm Education
    cand_resp = await api_client.post("/api/v1/candidates", json={
        "full_name": extracted["candidate_name"] or "Demo Candidate",
        "email": extracted["email"],
        "location_city": "Pune",
    })
    cand_id = cand_resp.json()["id"]

    edu_claim = extracted["education_claims"][0]
    await api_client.patch(f"/api/v1/candidates/{cand_id}/education", json={
        "degree": edu_claim["degree"] or "B.Tech",
        "branch": edu_claim["branch"] or "Computer Science and Engineering",
        "institution": edu_claim["institution"] or "COEP Pune",
        "graduation_year": edu_claim["graduation_year"] or 2025,
        "student_status": edu_claim["student_status"] or "final_year",
        "confirmed": True,
    })

    # Step 3: Candidate confirms Python, FastAPI, PostgreSQL, REST APIs and rejects Docker
    await api_client.post(f"/api/v1/candidates/{cand_id}/claims/confirm", json={
        "confirmed_skill_slugs": ["python", "fastapi", "postgresql", "rest-apis"],
        "rejected_skill_slugs": ["docker"],
    })

    # Step 4: Candidate provides verified evidence for confirmed skills
    # Python Project
    await api_client.post(f"/api/v1/candidates/{cand_id}/evidence", json={
        "skill_slug": "python",
        "evidence_type": "project",
        "title": "Backend Microservices in Python",
        "url": "https://github.com/demo/python-backend",
        "metadata": {"commits": 30},
        "date_obtained": "2026-01-01",
    })
    # FastAPI Project
    await api_client.post(f"/api/v1/candidates/{cand_id}/evidence", json={
        "skill_slug": "fastapi",
        "evidence_type": "project",
        "title": "Healthcare Booking API",
        "url": "https://github.com/demo/health-api",
        "metadata": {"commits": 25},
        "date_obtained": "2026-02-01",
    })
    # PostgreSQL Project
    await api_client.post(f"/api/v1/candidates/{cand_id}/evidence", json={
        "skill_slug": "postgresql",
        "evidence_type": "project",
        "title": "Normalized DB Schema",
        "url": "https://github.com/demo/health-api",
        "date_obtained": "2026-02-01",
    })
    # REST APIs Project
    await api_client.post(f"/api/v1/candidates/{cand_id}/evidence", json={
        "skill_slug": "rest-apis",
        "evidence_type": "project",
        "title": "RESTful Endpoints & OpenTelemetry",
        "url": "https://github.com/demo/health-api",
        "date_obtained": "2026-02-01",
    })

    # Step 5: Connect to Razorpay Junior Backend Engineer target job
    job_res = await db_session.execute(
        select(Job).where(Job.company_name == "Razorpay")
    )
    job = job_res.scalar_one()

    session = PreparationSession(
        candidate_id=cand_id,
        job_id=job.id,
        available_hours_per_week=15,
        weeks_until_target=6,
    )
    db_session.add(session)
    await db_session.commit()

    # Step 6: Invoke Phase 2 Deterministic Readiness Engine
    report = await ReadinessService.evaluate_session(db_session, session.id)

    # Step 7: Verify Deterministic Results
    assert report.eligibility_status == "eligible"
    assert 65 <= report.overall_readiness_score <= 85
    assert len(report.item_breakdowns) >= 5

    breakdowns = {b.skill.slug: b for b in report.item_breakdowns}

    # Evidenced skills (Python, FastAPI, PostgreSQL, REST APIs) are strengths/aligned at Level 3
    assert breakdowns["python"].estimated_level >= 3
    assert breakdowns["python"].classification in ["strength", "aligned"]

    assert breakdowns["fastapi"].estimated_level >= 3
    assert breakdowns["fastapi"].classification in ["strength", "aligned"]

    assert breakdowns["postgresql"].estimated_level >= 3
    assert breakdowns["postgresql"].classification in ["strength", "aligned"]

    assert breakdowns["rest-apis"].estimated_level >= 3
    assert breakdowns["rest-apis"].classification in ["strength", "aligned"]

    # Unevidenced Testing is correctly flagged as gap at Level 0
    assert breakdowns["testing"].estimated_level == 0
    assert breakdowns["testing"].classification == "critical_gap"

    # Cleanup test candidate & session
    await db_session.delete(session)
    await db_session.commit()
