import pytest

@pytest.mark.asyncio
async def test_candidate_onboarding_and_claim_confirmation_api(api_client):
    # 1. Create candidate
    create_resp = await api_client.post("/api/v1/candidates", json={
        "full_name": "Rohan Sharma",
        "email": "rohan.sharma@example.com",
        "location_city": "Pune",
    })
    assert create_resp.status_code == 201
    cand_data = create_resp.json()
    cand_id = cand_data["id"]
    assert cand_data["education_confirmed_by_user"] is False

    # 2. Confirm education
    edu_resp = await api_client.patch(f"/api/v1/candidates/{cand_id}/education", json={
        "degree": "B.Tech",
        "branch": "Information Technology",
        "institution": "Pune University",
        "graduation_year": 2025,
        "student_status": "final_year",
        "confirmed": True,
    })
    assert edu_resp.status_code == 200
    updated_cand = edu_resp.json()
    assert updated_cand["education_confirmed_by_user"] is True
    assert updated_cand["degree"] == "B.Tech"

    # 3. Batch confirm and reject claims
    confirm_resp = await api_client.post(f"/api/v1/candidates/{cand_id}/claims/confirm", json={
        "confirmed_skill_slugs": ["python", "postgresql", "fastapi"],
        "rejected_skill_slugs": ["docker"],
    })
    assert confirm_resp.status_code == 200
    claims = confirm_resp.json()
    confirmed_slugs = [c["skill_slug"] for c in claims if c["confirmed_by_user"]]
    assert "python" in confirmed_slugs
    assert "postgresql" in confirmed_slugs
    assert "fastapi" in confirmed_slugs
    assert "docker" not in confirmed_slugs

    # 4. Register evidence for a confirmed skill
    ev_resp = await api_client.post(f"/api/v1/candidates/{cand_id}/evidence", json={
        "skill_slug": "fastapi",
        "evidence_type": "project",
        "title": "Inventory Management API",
        "description": "Full async FastAPI microservice",
        "url": "https://github.com/rohan/inventory-api",
        "metadata": {"commits": 24},
        "date_obtained": "2026-03-01",
    })
    assert ev_resp.status_code == 201
    ev_data = ev_resp.json()
    assert ev_data["skill_slug"] == "fastapi"
    assert ev_data["verification_status"] == "verified"

    # 5. List evidence
    list_ev_resp = await api_client.get(f"/api/v1/candidates/{cand_id}/evidence")
    assert list_ev_resp.status_code == 200
    ev_list = list_ev_resp.json()
    assert len(ev_list) == 1
    assert ev_list[0]["title"] == "Inventory Management API"
