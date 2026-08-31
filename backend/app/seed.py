import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from app.models.skill import Skill, SkillAlias
from app.models.job import Job, JobEligibilityRequirement, JobCompetencyRequirement
from app.models.candidate import Candidate, CandidateSkill
from app.models.evidence import CandidateEvidence

# Resolve DATA_DIR across local and container filesystem layouts
current = Path(__file__).resolve()
DATA_DIR = None
for p in [current.parent, current.parent.parent, current.parent.parent.parent, Path.cwd(), Path("/app")]:
    if (p / "data" / "skills.json").exists():
        DATA_DIR = p / "data"
        break
if not DATA_DIR:
    DATA_DIR = Path.cwd() / "data"

async def _run_seed_logic(session: AsyncSession):
    print("--- SEEDING CANONICAL SKILLS ---")
    skills_file = DATA_DIR / "skills.json"

    with open(skills_file, "r") as f:
        skills_data = json.load(f)

    skill_map = {}

    for s_data in skills_data:
        stmt = select(Skill).where(Skill.slug == s_data["slug"])
        res = await session.execute(stmt)
        skill = res.scalar_one_or_none()

        if not skill:
            skill = Skill(
                slug=s_data["slug"],
                canonical_name=s_data["canonical_name"],
                category=s_data["category"],
                description=s_data.get("description"),
            )
            session.add(skill)
            await session.flush()

            for alias in s_data.get("aliases", []):
                norm_alias = alias.lower().strip()
                alias_obj = SkillAlias(
                    skill_id=skill.id,
                    alias=alias,
                    normalized_alias=norm_alias,
                )
                session.add(alias_obj)
        else:
            skill.canonical_name = s_data["canonical_name"]
            skill.category = s_data["category"]
            skill.description = s_data.get("description")

        skill_map[s_data["slug"]] = skill

    await session.commit()
    print(f"Seeded/Verified {len(skills_data)} skills with aliases.")

    print("--- SEEDING REPRESENTATIVE JOBS ---")
    with open(DATA_DIR / "jobs" / "representative_jobs.json", "r") as f:
        jobs_data = json.load(f)

    for j_data in jobs_data:
        stmt = select(Job).where(Job.title == j_data["title"], Job.company_name == j_data["company_name"])
        res = await session.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            job = Job(
                title=j_data["title"],
                target_role=j_data["target_role"],
                company_name=j_data["company_name"],
                location=j_data.get("location"),
                raw_description=j_data["raw_description"],
                source_url=j_data.get("source_url"),
                source_type=j_data.get("source_type", "fixture"),
            )
            session.add(job)
            await session.flush()
        else:
            job.target_role = j_data["target_role"]
            job.location = j_data.get("location")
            job.raw_description = j_data["raw_description"]
            job.source_url = j_data.get("source_url")
            job.source_type = j_data.get("source_type", "fixture")
            await session.execute(delete(JobEligibilityRequirement).where(JobEligibilityRequirement.job_id == job.id))
            await session.execute(delete(JobCompetencyRequirement).where(JobCompetencyRequirement.job_id == job.id))

        for elig in j_data.get("eligibility", []):
            el_obj = JobEligibilityRequirement(
                job_id=job.id,
                criterion_type=elig["criterion_type"],
                operator=elig.get("operator", "EQUALS"),
                expected_value=elig["expected_value"],
                is_mandatory=elig.get("is_mandatory", True),
                provenance=elig.get("provenance", "extracted_from_jd"),
            )
            session.add(el_obj)

        for comp in j_data.get("competencies", []):
            skill_slug = comp["skill_slug"]
            if skill_slug in skill_map:
                comp_obj = JobCompetencyRequirement(
                    job_id=job.id,
                    skill_id=skill_map[skill_slug].id,
                    is_required=comp.get("is_required", True),
                    importance_weight=comp.get("importance_weight", 1.0),
                    importance_provenance=comp.get("importance_provenance", "curated"),
                    required_proficiency_level=comp.get("required_proficiency_level", 3),
                    interview_relevance_level=comp.get("interview_relevance_level", "medium"),
                    interview_relevance_notes=comp.get("interview_relevance_notes"),
                    evidence_expectation=comp.get("evidence_expectation"),
                )
                session.add(comp_obj)

    await session.commit()
    print(f"Seeded/Verified {len(jobs_data)} representative jobs with eligibility and competencies.")

    print("--- SEEDING DEMO CANDIDATE & EVIDENCE ---")
    with open(DATA_DIR / "candidates" / "demo_candidate.json", "r") as f:
        c_data = json.load(f)

    stmt = select(Candidate).where(Candidate.full_name == c_data["full_name"])
    res = await session.execute(stmt)
    candidate = res.scalar_one_or_none()
    if not candidate:
        candidate = Candidate(
            full_name=c_data["full_name"],
            email=c_data.get("email"),
            phone=c_data.get("phone"),
            location_city=c_data.get("location_city", "Pune"),
            location_state=c_data.get("location_state", "Maharashtra"),
            degree=c_data.get("degree"),
            branch=c_data.get("branch"),
            institution=c_data.get("institution"),
            graduation_year=c_data.get("graduation_year"),
            student_status=c_data.get("student_status"),
            education_confirmed_by_user=c_data.get("education_confirmed_by_user", False),
            raw_education_claims=c_data.get("raw_education_claims"),
        )
        session.add(candidate)
        await session.flush()
    else:
        candidate.email = c_data.get("email")
        candidate.phone = c_data.get("phone")
        candidate.location_city = c_data.get("location_city", "Pune")
        candidate.location_state = c_data.get("location_state", "Maharashtra")
        candidate.degree = c_data.get("degree")
        candidate.branch = c_data.get("branch")
        candidate.institution = c_data.get("institution")
        candidate.graduation_year = c_data.get("graduation_year")
        candidate.student_status = c_data.get("student_status")
        candidate.education_confirmed_by_user = c_data.get("education_confirmed_by_user", False)
        candidate.raw_education_claims = c_data.get("raw_education_claims")
        await session.execute(delete(CandidateSkill).where(CandidateSkill.candidate_id == candidate.id))
        await session.execute(delete(CandidateEvidence).where(CandidateEvidence.candidate_id == candidate.id))

    for sk in c_data.get("skills", []):
        slug = sk["skill_slug"]
        if slug in skill_map:
            cs_obj = CandidateSkill(
                candidate_id=candidate.id,
                skill_id=skill_map[slug].id,
                claim_source=sk.get("claim_source", "resume"),
                raw_claim_text=sk.get("raw_claim_text"),
                confirmed_by_user=sk.get("confirmed_by_user", False),
                self_assessment_level=sk.get("self_assessment_level"),
            )
            session.add(cs_obj)

    with open(DATA_DIR / "evidence" / "demo_evidence.json", "r") as f:
        evidence_data = json.load(f)

    for ev in evidence_data:
        slug = ev["skill_slug"]
        if slug in skill_map:
            d_val = None
            if ev.get("date_obtained"):
                d_val = datetime.strptime(ev["date_obtained"], "%Y-%m-%d").date()
            ev_obj = CandidateEvidence(
                candidate_id=candidate.id,
                skill_id=skill_map[slug].id,
                evidence_type=ev["evidence_type"],
                title=ev["title"],
                description=ev.get("description"),
                url=ev.get("url"),
                raw_metadata=ev.get("raw_metadata", {}),
                verification_status=ev.get("verification_status", "unverified"),
                confidence_score=ev.get("confidence_score", 0.5),
                date_obtained=d_val,
            )
            session.add(ev_obj)

    await session.commit()
    print(f"Seeded/Verified demo candidate: {candidate.full_name} with {len(c_data.get('skills', []))} claims and {len(evidence_data)} evidence records.")
    print("--- SEEDING COMPLETED SUCCESSFULLY ---")

async def seed_database(session: Optional[AsyncSession] = None):
    if session:
        await _run_seed_logic(session)
    else:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory() as s:
            await _run_seed_logic(s)
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_database())
