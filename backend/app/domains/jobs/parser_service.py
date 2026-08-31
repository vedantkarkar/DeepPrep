from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.base import AIProvider
from app.ai.factory import get_ai_provider
from app.domains.jobs.prompts import (
    JOB_EXTRACTION_SYSTEM_PROMPT,
    JOB_EXTRACTION_USER_PROMPT_TEMPLATE,
)
from app.domains.jobs.schemas import (
    RawJobExtraction,
    ParsedJobDescriptionResponse,
)
from app.domains.jobs.normalizer import JobTaxonomyNormalizer
from app.domains.jobs.validator import JobSemanticValidator

class JobParserService:
    """Orchestrates raw JD extraction, taxonomy normalization, and semantic validation."""

    @classmethod
    async def parse_job_description(
        cls,
        db: AsyncSession,
        raw_description: str,
        title: str | None = None,
        company_name: str | None = None,
        source_url: str | None = None,
        source_type: str = "manual_entry",
        ai_provider: AIProvider | None = None,
    ) -> ParsedJobDescriptionResponse:
        if not raw_description or not raw_description.strip():
            raise ValueError("Raw job description cannot be empty.")

        provider = ai_provider or get_ai_provider()
        prompt = JOB_EXTRACTION_USER_PROMPT_TEMPLATE.format(jd_text=raw_description)

        raw_extraction: RawJobExtraction = await provider.extract_structured(
            prompt=prompt,
            schema=RawJobExtraction,
            system_instruction=JOB_EXTRACTION_SYSTEM_PROMPT,
        )

        # Normalize extracted skills against database taxonomy
        normalized_competencies, unresolved_skills = await JobTaxonomyNormalizer.normalize_competencies(
            db=db,
            raw_competencies=raw_extraction.competency_requirements,
        )

        final_title = title or raw_extraction.job_title or "Software Engineer"
        final_company = company_name or raw_extraction.company_name or "Target Company"

        parsed = ParsedJobDescriptionResponse(
            title=final_title,
            company_name=final_company,
            target_role=raw_extraction.target_role or "Software Engineer",
            location_city=raw_extraction.location_city or "Pune",
            location_state=raw_extraction.location_state or "Maharashtra",
            employment_type=raw_extraction.employment_type or "Full-time",
            source_url=source_url,
            source_type=source_type,
            eligibility_requirements=raw_extraction.eligibility_requirements,
            competency_requirements=normalized_competencies,
            unresolved_skills=unresolved_skills,
            raw_description=raw_description,
        )

        # Semantic validation
        JobSemanticValidator.validate_parsed_job(parsed)

        return parsed
