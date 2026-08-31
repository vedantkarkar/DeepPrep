from typing import Tuple, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.skill import Skill, SkillAlias
from app.domains.candidate.schemas import (
    ExtractedSkillClaim,
    NormalizedSkillClaimItem,
    UnresolvedSkillClaimItem,
)

class TaxonomyNormalizer:
    """Normalizes extracted raw skill tokens against canonical catalog and aliases."""

    @classmethod
    async def normalize_skills(
        cls,
        db: AsyncSession,
        raw_skill_claims: List[ExtractedSkillClaim],
    ) -> Tuple[List[NormalizedSkillClaimItem], List[UnresolvedSkillClaimItem]]:
        # Load all canonical skills and aliases
        stmt = select(Skill).options(selectinload(Skill.aliases))
        res = await db.execute(stmt)
        skills = res.scalars().all()

        alias_to_skill: Dict[str, Skill] = {}
        for s in skills:
            alias_to_skill[s.slug.lower()] = s
            alias_to_skill[s.canonical_name.lower().strip()] = s
            for a in s.aliases:
                alias_to_skill[a.normalized_alias.lower().strip()] = s

        normalized_items: List[NormalizedSkillClaimItem] = []
        unresolved_items: List[UnresolvedSkillClaimItem] = []
        seen_skill_ids = set()

        for claim in raw_skill_claims:
            raw_token = claim.raw_text.strip()
            norm_key = raw_token.lower()

            matched_skill = alias_to_skill.get(norm_key)
            if matched_skill:
                if matched_skill.id not in seen_skill_ids:
                    seen_skill_ids.add(matched_skill.id)
                    normalized_items.append(
                        NormalizedSkillClaimItem(
                            skill_id=matched_skill.id,
                            skill_slug=matched_skill.slug,
                            canonical_name=matched_skill.canonical_name,
                            category=matched_skill.category,
                            raw_text=claim.raw_text,
                            source_context=claim.source_context,
                            confirmed=False,
                            claim_source="resume",
                        )
                    )
            else:
                unresolved_items.append(
                    UnresolvedSkillClaimItem(
                        raw_text=claim.raw_text,
                        source_context=claim.source_context,
                        reason="Token does not match canonical skill catalog or alias dictionary",
                    )
                )

        return normalized_items, unresolved_items
