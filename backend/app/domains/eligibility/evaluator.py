from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.models.candidate import Candidate
from app.models.job import JobEligibilityRequirement
from app.domains.eligibility.rules import EligibilityStatus, EvaluationOperator

@dataclass
class CriterionEvaluation:
    criterion_type: str
    expected_value: Any
    candidate_value: Any
    operator: str
    is_mandatory: bool
    passed: bool
    explanation: str

@dataclass
class EligibilityResult:
    status: EligibilityStatus
    is_eligible: bool
    criteria_evaluations: List[CriterionEvaluation] = field(default_factory=list)
    summary_reasons: List[str] = field(default_factory=list)

class EligibilityEvaluator:
    """Pure deterministic evaluator for job application prerequisites.
    
    Evaluates candidate education, graduation year, experience, and location
    strictly against job eligibility criteria without touching skill competencies.
    """

    @classmethod
    def evaluate(
        cls,
        candidate: Candidate,
        requirements: List[JobEligibilityRequirement]
    ) -> EligibilityResult:
        if not requirements:
            return EligibilityResult(
                status=EligibilityStatus.ELIGIBLE,
                is_eligible=True,
                criteria_evaluations=[],
                summary_reasons=["No explicit gating eligibility requirements specified for this role."]
            )

        evaluations: List[CriterionEvaluation] = []
        mandatory_failures = 0
        non_mandatory_failures = 0
        reasons: List[str] = []

        for req in requirements:
            crit_type = req.criterion_type.lower()
            op = (req.operator or "EQUALS").upper()
            expected = req.expected_value
            cand_val = cls._get_candidate_value(candidate, crit_type)
            
            passed, explanation = cls._evaluate_single_criterion(crit_type, op, expected, cand_val)
            
            if not passed:
                if req.is_mandatory:
                    mandatory_failures += 1
                else:
                    non_mandatory_failures += 1
            
            evaluations.append(CriterionEvaluation(
                criterion_type=crit_type,
                expected_value=expected,
                candidate_value=cand_val,
                operator=op,
                is_mandatory=req.is_mandatory,
                passed=passed,
                explanation=explanation,
            ))
            reasons.append(explanation)

        # Determine overall status
        if mandatory_failures > 0:
            status = EligibilityStatus.INELIGIBLE
            is_eligible = False
        elif not candidate.education_confirmed_by_user:
            status = EligibilityStatus.PARTIALLY_ELIGIBLE
            is_eligible = True
            reasons.insert(0, "Candidate education claims are unconfirmed by candidate; explicit confirmation needed.")
        elif non_mandatory_failures > 0:
            status = EligibilityStatus.PARTIALLY_ELIGIBLE
            is_eligible = True
        else:
            status = EligibilityStatus.ELIGIBLE
            is_eligible = True

        return EligibilityResult(
            status=status,
            is_eligible=is_eligible,
            criteria_evaluations=evaluations,
            summary_reasons=reasons,
        )

    @classmethod
    def _get_candidate_value(cls, candidate: Candidate, crit_type: str) -> Any:
        if crit_type == "degree":
            return candidate.degree
        elif crit_type == "branch":
            return candidate.branch
        elif crit_type in ("min_graduation_year", "max_graduation_year"):
            return candidate.graduation_year
        elif crit_type == "location_constraint":
            return f"{candidate.location_city or ''}, {candidate.location_state or ''}".strip(", ")
        elif crit_type == "min_experience_years":
            # For students / recent graduates, default experience is 0 unless recorded
            return 0
        return None

    @classmethod
    def _evaluate_single_criterion(cls, crit_type: str, op: str, expected: Any, cand_val: Any) -> tuple[bool, str]:
        if cand_val is None:
            return False, f"Missing candidate {crit_type} detail."

        norm_cand = str(cand_val).lower().strip()

        if op == EvaluationOperator.IN.value:
            if isinstance(expected, list):
                norm_expected = [str(x).lower().strip() for x in expected]
                # Match exact or substring token for branch/degree (e.g. 'Computer Science' matches 'Computer Science and Engineering')
                matches = any(
                    (exp in norm_cand or norm_cand in exp) for exp in norm_expected
                )
                if matches:
                    return True, f"{crit_type.capitalize()} '{cand_val}' matches accepted requirements ({', '.join(map(str, expected))})."
                else:
                    return False, f"{crit_type.capitalize()} '{cand_val}' does not match accepted requirements ({', '.join(map(str, expected))})."
            else:
                passed = norm_cand == str(expected).lower().strip()
                return passed, f"{crit_type.capitalize()} is '{cand_val}' (Expected: {expected})."

        elif op == EvaluationOperator.GREATER_EQUAL.value:
            try:
                cand_num = float(cand_val)
                exp_num = float(expected)
                passed = cand_num >= exp_num
                if passed:
                    return True, f"{crit_type.capitalize()} ({cand_val}) satisfies minimum threshold (>= {expected})."
                else:
                    return False, f"{crit_type.capitalize()} ({cand_val}) is below required threshold (>= {expected})."
            except (ValueError, TypeError):
                return False, f"Invalid numeric comparison for {crit_type}."

        elif op == EvaluationOperator.LESS_EQUAL.value:
            try:
                cand_num = float(cand_val)
                exp_num = float(expected)
                passed = cand_num <= exp_num
                if passed:
                    return True, f"{crit_type.capitalize()} ({cand_val}) satisfies maximum cutoff (<= {expected})."
                else:
                    return False, f"{crit_type.capitalize()} ({cand_val}) exceeds maximum cutoff (<= {expected})."
            except (ValueError, TypeError):
                return False, f"Invalid numeric comparison for {crit_type}."

        elif op == EvaluationOperator.EQUALS.value:
            passed = norm_cand == str(expected).lower().strip()
            if passed:
                return True, f"{crit_type.capitalize()} '{cand_val}' matches expected '{expected}'."
            else:
                return False, f"{crit_type.capitalize()} '{cand_val}' does not match expected '{expected}'."

        return False, f"Unknown evaluation operator '{op}'."
