import pytest
from pydantic import ValidationError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Skill, SkillAlias
from app.schemas.evidence import CandidateEvidenceCreate, EvidenceType

def test_evidence_type_enum_support():
    valid_types = [
        "self_report", "academic_coursework", "project", "github",
        "assessment", "internship", "professional_experience",
        "course", "certification", "other"
    ]
    for vt in valid_types:
        ev = CandidateEvidenceCreate(
            skill_slug="python",
            evidence_type=vt,
            title=f"Sample {vt}"
        )
        assert ev.evidence_type == vt

    with pytest.raises(ValidationError):
        CandidateEvidenceCreate(
            skill_slug="python",
            evidence_type="invalid_speculative_type",
            title="Invalid"
        )

@pytest.mark.asyncio
async def test_deterministic_alias_lookup(db_session):
    # Test lookups for normalized aliases
    test_lookups = [
        ("postgres", "postgresql"),
        ("postgresql db", "postgresql"),
        ("cpp", "cpp"),
        ("c plus plus", "cpp"),
        ("core java", "java"),
        ("java 17", "java"),
        ("dsa", "dsa"),
        ("hld", "system-design"),
    ]

    for alias_text, expected_slug in test_lookups:
        stmt = select(SkillAlias).options(selectinload(SkillAlias.skill)).where(
            SkillAlias.normalized_alias == alias_text.lower().strip()
        )
        res = await db_session.execute(stmt)
        alias_match = res.scalar_one_or_none()
        assert alias_match is not None, f"Alias '{alias_text}' should resolve"
        assert alias_match.skill.slug == expected_slug
