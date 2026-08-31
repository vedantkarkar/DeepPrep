"""
Weekly Preparation Scheduler & Milestone Generator.
"""

from typing import List, Dict
from app.domains.planning.prioritizer import CandidateSkillGap
from app.domains.planning.models import PreparationActivity, WeeklySchedule, PreparationMilestone
from app.domains.planning.rules import FINAL_WEEK_REVIEW_RATIO

class WeeklyScheduler:
    @staticmethod
    def generate_schedule(
        prioritized_skills: List[CandidateSkillGap],
        allocations: Dict[str, float],
        weeks_until_target: int,
        hours_per_week: int,
    ) -> List[WeeklySchedule]:
        """
        Distribute allocated hours across weeks with early exposure for high-priority skills
        and a final consolidation / mock review week.
        """
        schedule: List[WeeklySchedule] = []
        if weeks_until_target <= 0 or hours_per_week <= 0:
            return schedule

        # Track remaining hours per skill to distribute
        remaining_skill_hours = dict(allocations)
        skill_map = {s.skill_slug: s for s in prioritized_skills}

        # Filter active skills that received > 0 hours
        active_skills = [s for s in prioritized_skills if remaining_skill_hours.get(s.skill_slug, 0.0) > 0]

        for week in range(1, weeks_until_target + 1):
            is_final_week = (week == weeks_until_target)
            week_capacity = float(hours_per_week)
            week_activities: List[PreparationActivity] = []

            if is_final_week and weeks_until_target > 1:
                theme = "Final Mock Interview & Comprehensive Review"
                # Reserve 25% for general mock assessment
                review_hours = min(week_capacity, max(1.0, round(week_capacity * FINAL_WEEK_REVIEW_RATIO)))
                week_capacity -= review_hours

                # Add consolidation review activity
                top_skills = [s.canonical_name for s in active_skills[:3]]
                week_activities.append(
                    PreparationActivity(
                        skill_slug="final-mock-assessment",
                        canonical_name="Mock Technical Interview & Consolidation",
                        activity_type="ASSESS",
                        allocated_hours=float(review_hours),
                        rationale=f"Simulated technical interview and final gap review covering {', '.join(top_skills)}.",
                    )
                )
            elif week == 1:
                theme = "Foundational Concepts & Core Deficits"
            elif week <= weeks_until_target // 2:
                theme = "Practical Implementation & Project Work"
            else:
                theme = "Advanced Problem-Solving & Pattern Practice"

            # Allocate remaining skills to this week
            for skill in active_skills:
                if week_capacity <= 0:
                    break

                avail_for_skill = remaining_skill_hours.get(skill.skill_slug, 0.0)
                if avail_for_skill <= 0:
                    continue

                # Determine week chunk
                chunk = min(week_capacity, avail_for_skill, max(1.0, avail_for_skill / (weeks_until_target - week + 1)))
                chunk = round(chunk)
                if chunk < 1.0 and avail_for_skill >= 1.0:
                    chunk = 1.0
                chunk = min(chunk, week_capacity, avail_for_skill)

                if chunk > 0:
                    activity_type = "LEARN" if skill.gap_levels >= 2 and week <= 2 else "PRACTICE"
                    if skill.gap_levels == 0:
                        activity_type = "MAINTAIN"
                    elif is_final_week:
                        activity_type = "ASSESS"

                    week_activities.append(
                        PreparationActivity(
                            skill_slug=skill.skill_slug,
                            canonical_name=skill.canonical_name,
                            activity_type=activity_type,
                            allocated_hours=float(chunk),
                            rationale=skill.rationale,
                        )
                    )
                    remaining_skill_hours[skill.skill_slug] -= chunk
                    week_capacity -= chunk

            total_week_hours = sum(a.allocated_hours for a in week_activities)
            schedule.append(
                WeeklySchedule(
                    week_number=week,
                    focus_theme=theme,
                    total_hours=total_week_hours,
                    activities=week_activities,
                )
            )

        return schedule

    @staticmethod
    def generate_milestones(
        prioritized_skills: List[CandidateSkillGap],
        weeks_until_target: int,
    ) -> List[PreparationMilestone]:
        """Generate progressive, non-prescriptive learning milestones."""
        milestones: List[PreparationMilestone] = []
        top_skills = [s.canonical_name for s in prioritized_skills if s.gap_levels > 0][:3]
        if not top_skills:
            top_skills = [s.canonical_name for s in prioritized_skills[:2]]

        # Milestone 1
        w1 = max(1, weeks_until_target // 3)
        milestones.append(
            PreparationMilestone(
                week_target=w1,
                title="Foundational Knowledge Milestone",
                description=f"Complete foundational concepts and practical setup for {', '.join(top_skills)}.",
                skills_involved=top_skills,
            )
        )

        # Milestone 2 (if weeks >= 3)
        if weeks_until_target >= 3:
            w2 = max(2, (weeks_until_target * 2) // 3)
            milestones.append(
                PreparationMilestone(
                    week_target=w2,
                    title="Hands-On Implementation & Mini-Project",
                    description="Implement end-to-end practical exercises addressing target role competency gaps.",
                    skills_involved=top_skills,
                )
            )

        # Final Milestone
        milestones.append(
            PreparationMilestone(
                week_target=weeks_until_target,
                title="Role-Readiness Mock Assessment",
                description="Simulate complete interview problem-solving and verify readiness across all role requirements.",
                skills_involved=top_skills,
            )
        )

        return milestones
