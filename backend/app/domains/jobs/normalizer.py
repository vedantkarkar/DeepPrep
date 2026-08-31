from typing import Tuple, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.skill import Skill, SkillAlias
from app.domains.jobs import rules
from app.domains.jobs.schemas import (
    ExtractedCompetencyItem,
    NormalizedCompetencyItem,
    UnresolvedJobSkillItem,
)

class JobTaxonomyNormalizer:
    """Normalizes raw JD skill requirements against the database canonical taxonomy."""

    @classmethod
    async def normalize_competencies(
        cls,
        db: AsyncSession,
        raw_competencies: List[ExtractedCompetencyItem],
    ) -> Tuple[List[NormalizedCompetencyItem], List[UnresolvedJobSkillItem]]:
        stmt = select(Skill).options(selectinload(Skill.aliases))
        res = await db.execute(stmt)
        skills = res.scalars().all()

        alias_to_skill: Dict[str, Skill] = {}
        for s in skills:
            alias_to_skill[s.slug.lower()] = s
            alias_to_skill[s.canonical_name.lower().strip()] = s
            for a in s.aliases:
                alias_to_skill[a.normalized_alias.lower().strip()] = s

        normalized_items: List[NormalizedCompetencyItem] = []
        unresolved_items: List[UnresolvedJobSkillItem] = []
        seen_skill_ids = set()

        for comp in raw_competencies:
            raw_token = comp.raw_skill_text.strip()
            norm_key = raw_token.lower()

            matched_skill = alias_to_skill.get(norm_key)
            if matched_skill:
                if matched_skill.id not in seen_skill_ids:
                    seen_skill_ids.add(matched_skill.id)

                    # Determine required level deterministically from rules
                    supporting_lower = (comp.supporting_text or "").lower()
                    if not comp.is_required or comp.importance_level in ("preferred", "nice_to_have"):
                        req_level = rules.DEFAULT_PREFERRED_COMPETENCY_LEVEL
                    elif any(kw in supporting_lower for kw in rules.ADVANCED_LEVEL_KEYWORDS):
                        req_level = rules.DEFAULT_ADVANCED_COMPETENCY_LEVEL
                    else:
                        req_level = rules.DEFAULT_REQUIRED_COMPETENCY_LEVEL

                    # Determine importance weight deterministically from rules
                    if not comp.is_required or comp.importance_level in ("preferred", "nice_to_have"):
                        weight = rules.WEIGHT_PREFERRED_SKILL
                        interview_rel = "low"
                    elif matched_skill.slug in rules.CORE_INTERVIEW_SKILL_SLUGS:
                        weight = rules.WEIGHT_CORE_INTERVIEW_SKILL
                        interview_rel = "high"
                    elif matched_skill.category in ("framework", "database", "programming"):
                        weight = rules.WEIGHT_STANDARD_REQUIRED_SKILL
                        interview_rel = "medium"
                    else:
                        weight = rules.WEIGHT_SECONDARY_REQUIRED_SKILL
                        interview_rel = "low"

                    normalized_items.append(
                        NormalizedCompetencyItem(
                            skill_id=matched_skill.id,
                            skill_slug=matched_skill.slug,
                            canonical_name=matched_skill.canonical_name,
                            category=matched_skill.category,
                            required_proficiency_level=req_level,
                            importance_weight=weight,
                            is_required=comp.is_required,
                            interview_relevance_level=comp.interview_relevance or interview_rel,
                            supporting_text=comp.supporting_text,
                            importance_provenance=rules.PROVENANCE_DERIVED,
                        )
                    )
            else:
                unresolved_items.append(
                    UnresolvedJobSkillItem(
                        raw_term=comp.raw_skill_text,
                        supporting_text=comp.supporting_text,
                        reason="Term not found in canonical skill catalog or alias dictionary",
                    )
                )

        return normalized_items, unresolved_items
