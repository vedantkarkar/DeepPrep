"""
Orchestrator for the Deterministic Preparation Optimizer.
"""

from typing import List, Dict, Any
from app.domains.planning.prioritizer import CandidateSkillGap, GapPrioritizer
from app.domains.planning.allocator import TimeAllocator
from app.domains.planning.scheduler import WeeklyScheduler
from app.domains.planning.models import PriorityArea
from app.models.readiness import ReadinessReport
from app.models.session import PreparationSession

class PreparationOptimizer:
    @staticmethod
    def optimize(
        session: PreparationSession,
        report: ReadinessReport,
    ) -> Dict[str, Any]:
        """
        Transforms ReadinessReport + PreparationSession into a complete, deterministic preparation plan.
        """
        hours_per_week = session.available_hours_per_week
        weeks_target = session.weeks_until_target
        total_capacity = hours_per_week * weeks_target

        # 1. Build CandidateSkillGap items from ReadinessItemBreakdowns
        skill_gaps: List[CandidateSkillGap] = []
        for b in report.item_breakdowns:
            is_required = True
            relevance = "medium"
            if b.competency_requirement_id and session.job:
                for c in session.job.competency_requirements:
                    if c.id == b.competency_requirement_id:
                        is_required = c.is_required
                        relevance = c.interview_relevance_level or "medium"
                        break

            skill_gaps.append(
                CandidateSkillGap(
                    skill_slug=b.skill.slug if b.skill else "unknown",
                    canonical_name=b.skill.canonical_name if b.skill else "Unknown Skill",
                    category=b.skill.category if b.skill else "other",
                    required_level=b.required_level,
                    estimated_level=b.estimated_level,
                    importance_weight=b.importance_weight,
                    is_required=is_required,
                    interview_relevance=relevance,
                    confidence_score=report.evidence_confidence_score,
                    classification=b.classification,
                )
            )

        # 2. Prioritize Gaps
        prioritized = GapPrioritizer.prioritize_gaps(skill_gaps)

        # 3. Allocate Hours
        allocations = TimeAllocator.allocate_hours(
            prioritized_skills=prioritized,
            total_available_hours=total_capacity,
        )

        # 4. Generate Weekly Schedule & Milestones
        schedule = WeeklyScheduler.generate_schedule(
            prioritized_skills=prioritized,
            allocations=allocations,
            weeks_until_target=weeks_target,
            hours_per_week=hours_per_week,
        )

        milestones = WeeklyScheduler.generate_milestones(
            prioritized_skills=prioritized,
            weeks_until_target=weeks_target,
        )

        # 5. Build Priority Areas summary
        priority_areas = [
            PriorityArea(
                skill_slug=s.skill_slug,
                canonical_name=s.canonical_name,
                category=s.category,
                required_level=s.required_level,
                estimated_level=s.estimated_level,
                gap_levels=s.gap_levels,
                priority_tier=s.priority_tier,
                allocated_hours=allocations.get(s.skill_slug, 0.0),
                rationale=s.rationale,
            )
            for s in prioritized
        ]

        total_hours_allocated = sum(int(round(s.total_hours)) for s in schedule)

        unclosed_high_gaps = [s for s in prioritized if s.priority_tier == "high" and allocations.get(s.skill_slug, 0.0) < s.effort_units * 3]
        if unclosed_high_gaps and total_capacity < 40:
            capacity_note = "Your available preparation time is constrained. High-priority interview deficits have been front-loaded."
        else:
            capacity_note = "Preparation hours are distributed evenly across prioritized gaps with final-week consolidation."

        return {
            "total_hours_allocated": total_hours_allocated,
            "available_hours_per_week": hours_per_week,
            "weeks_until_target": weeks_target,
            "capacity_note": capacity_note,
            "priority_areas": [p.model_dump() for p in priority_areas],
            "schedule": [s.model_dump() for s in schedule],
            "milestones": [m.model_dump() for m in milestones],
        }
