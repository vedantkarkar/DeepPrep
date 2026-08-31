from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.base import AIProvider
from app.ai.factory import get_ai_provider
from app.domains.candidate.text_extractor import ResumeTextExtractor
from app.domains.candidate.prompts import (
    RESUME_EXTRACTION_SYSTEM_PROMPT,
    RESUME_EXTRACTION_USER_PROMPT_TEMPLATE,
)
from app.domains.candidate.schemas import (
    RawResumeExtraction,
    ResumeExtractionResponse,
)
from app.domains.candidate.normalizer import TaxonomyNormalizer

class ResumeExtractionService:
    """Service coordinating file text extraction, structured claim extraction, and normalization."""

    @classmethod
    async def extract_and_normalize(
        cls,
        db: AsyncSession,
        file_bytes: bytes,
        filename: str,
        ai_provider: AIProvider | None = None,
    ) -> ResumeExtractionResponse:
        # 1. Safe text extraction
        raw_text = ResumeTextExtractor.extract_from_bytes(file_bytes, filename)

        # 2. AI Structured Extraction
        provider = ai_provider or get_ai_provider()
        prompt = RESUME_EXTRACTION_USER_PROMPT_TEMPLATE.format(resume_text=raw_text)
        
        raw_extraction: RawResumeExtraction = await provider.extract_structured(
            prompt=prompt,
            schema=RawResumeExtraction,
            system_instruction=RESUME_EXTRACTION_SYSTEM_PROMPT,
        )

        # 3. Deterministic Skill Taxonomy Normalization
        normalized_skills, unresolved_skills = await TaxonomyNormalizer.normalize_skills(
            db=db,
            raw_skill_claims=raw_extraction.skill_claims,
        )

        # 4. Education status determination
        edu_claims = raw_extraction.education_claims
        if not edu_claims or (len(edu_claims) == 1 and not edu_claims[0].degree and not edu_claims[0].graduation_year):
            education_status = "missing"
        elif len(edu_claims) > 1:
            education_status = "ambiguous"
        else:
            education_status = "extracted"

        return ResumeExtractionResponse(
            status="needs_confirmation",
            candidate_name=raw_extraction.candidate_name,
            email=raw_extraction.email,
            phone=raw_extraction.phone,
            education_status=education_status,
            education_claims=edu_claims,
            normalized_skill_claims=normalized_skills,
            unresolved_skill_claims=unresolved_skills,
            project_claims=raw_extraction.project_claims,
            experience_claims=raw_extraction.experience_claims,
            certification_claims=raw_extraction.certification_claims,
        )
