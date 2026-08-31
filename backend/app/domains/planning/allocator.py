"""
Deterministic Time Allocator with Diminishing Returns.
"""

from typing import List, Dict
from app.domains.planning.prioritizer import CandidateSkillGap
from app.domains.planning.rules import (
    MINIMUM_ALLOCATION_UNIT_HOURS,
    DIMINISHING_RETURN_DECAY_RATE,
    MAX_SINGLE_SKILL_TIME_RATIO,
    MAX_MAINTENANCE_TIME_RATIO,
)

class TimeAllocator:
    @staticmethod
    def allocate_hours(
        prioritized_skills: List[CandidateSkillGap],
        total_available_hours: int,
    ) -> Dict[str, float]:
        """
        Greedily allocate available hours in discrete 1.0-hour increments
        based on diminishing marginal utility.
        """
        if total_available_hours <= 0 or not prioritized_skills:
            return {s.skill_slug: 0.0 for s in prioritized_skills}

        allocations: Dict[str, float] = {s.skill_slug: 0.0 for s in prioritized_skills}
        max_single_skill_cap = max(2.0, total_available_hours * MAX_SINGLE_SKILL_TIME_RATIO)
        max_maintenance_cap = max(1.0, total_available_hours * MAX_MAINTENANCE_TIME_RATIO)

        remaining_hours = float(total_available_hours)
        total_maintenance_allocated = 0.0

        # Run greedy incremental allocation
        while remaining_hours >= MINIMUM_ALLOCATION_UNIT_HOURS:
            best_skill: CandidateSkillGap = None
            best_marginal_value = -1.0

            for skill in prioritized_skills:
                curr_allocated = allocations[skill.skill_slug]

                # Check caps
                if curr_allocated >= max_single_skill_cap:
                    continue

                if skill.gap_levels == 0 and total_maintenance_allocated >= max_maintenance_cap:
                    continue

                # Diminishing return function
                decay = 1.0 + DIMINISHING_RETURN_DECAY_RATE * (curr_allocated / max(1.0, skill.effort_units))
                marginal_val = skill.base_priority / decay

                if marginal_val > best_marginal_value:
                    best_marginal_value = marginal_val
                    best_skill = skill

            if not best_skill:
                # If all caps are reached, distribute remaining to highest priority skills under total cap
                for skill in prioritized_skills:
                    if remaining_hours < MINIMUM_ALLOCATION_UNIT_HOURS:
                        break
                    allocations[skill.skill_slug] += MINIMUM_ALLOCATION_UNIT_HOURS
                    remaining_hours -= MINIMUM_ALLOCATION_UNIT_HOURS
                break

            allocations[best_skill.skill_slug] += MINIMUM_ALLOCATION_UNIT_HOURS
            if best_skill.gap_levels == 0:
                total_maintenance_allocated += MINIMUM_ALLOCATION_UNIT_HOURS
            remaining_hours -= MINIMUM_ALLOCATION_UNIT_HOURS

        return allocations
