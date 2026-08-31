export interface Candidate {
  id: string;
  full_name: string;
  email?: string | null;
  phone?: string | null;
  location_city?: string | null;
  location_state?: string | null;
  degree?: string | null;
  branch?: string | null;
  institution?: string | null;
  graduation_year?: number | null;
  student_status?: string | null;
  education_confirmed_by_user: boolean;
  created_at: string;
}

export interface ExtractedEducationClaim {
  degree?: string | null;
  branch?: string | null;
  institution?: string | null;
  graduation_year?: number | null;
  student_status?: string | null;
  source_context?: string | null;
}

export interface NormalizedSkillClaimItem {
  skill_id: string;
  skill_slug: string;
  canonical_name: string;
  category: string;
  raw_text: string;
  source_context?: string | null;
  confirmed: boolean;
  claim_source: string;
}

export interface UnresolvedSkillClaimItem {
  raw_text: string;
  source_context?: string | null;
  reason: string;
}

export interface ResumeExtractionResponse {
  status: string;
  candidate_name?: string | null;
  email?: string | null;
  phone?: string | null;
  education_status: "extracted" | "missing" | "ambiguous";
  education_claims: ExtractedEducationClaim[];
  normalized_skill_claims: NormalizedSkillClaimItem[];
  unresolved_skill_claims: UnresolvedSkillClaimItem[];
  project_claims: Array<{ name: string; description?: string; source_context?: string }>;
}

export interface CandidateSkillClaim {
  id: string;
  candidate_id: string;
  skill_id: string;
  skill_slug: string;
  canonical_name: string;
  claim_source: string;
  raw_claim_text?: string | null;
  confirmed_by_user: boolean;
  self_assessment_level?: number | null;
  created_at: string;
}

export interface CandidateEvidence {
  id: string;
  candidate_id: string;
  skill_id: string;
  skill_slug: string;
  canonical_name: string;
  evidence_type: string;
  title: string;
  description?: string | null;
  url?: string | null;
  raw_metadata?: Record<string, any> | null;
  verification_status: string;
  confidence_score: number;
  date_obtained?: string | null;
  created_at: string;
}

export interface JobEligibilityItem {
  id?: string;
  criterion_type: string;
  operator: string;
  expected_value: any;
  is_mandatory: boolean;
  provenance?: string;
}

export interface JobCompetencyItem {
  id?: string;
  skill_id?: string;
  skill_slug?: string;
  canonical_name?: string;
  category?: string;
  is_required: boolean;
  importance_weight: number;
  importance_provenance?: string;
  required_proficiency_level: number;
  interview_relevance_level?: string;
}

export interface Job {
  id: string;
  title: string;
  target_role: string;
  company_name: string;
  location_city?: string | null;
  location_state?: string | null;
  raw_description: string;
  source_url?: string | null;
  source_type: string;
  posted_date?: string | null;
  is_active: boolean;
  eligibility_requirements: JobEligibilityItem[];
  competency_requirements: JobCompetencyItem[];
}

export interface PreparationSession {
  id: string;
  candidate_id: string;
  job_id: string;
  available_hours_per_week: number;
  weeks_until_target: number;
  target_date?: string | null;
  status: string;
  created_at: string;
}

export interface ReadinessItemBreakdown {
  skill_slug: string;
  canonical_name: string;
  category: string;
  required_level: number;
  estimated_level: number;
  importance_weight: number;
  gap_score: number;
  classification: "strength" | "aligned" | "moderate_gap" | "critical_gap";
  supporting_evidence_ids: string[];
  explanation: string;
}

export interface ReadinessReport {
  report_id: string;
  session_id: string;
  candidate_id: string;
  job_id: string;
  overall_readiness_score: number;
  technical_readiness_score: number;
  evidence_confidence_score: "low" | "medium" | "high";
  eligibility_status: "eligible" | "partially_eligible" | "ineligible";
  eligibility_summary: {
    is_eligible?: boolean;
    status?: string;
    reasons?: string[];
    criteria?: Array<{
      criterion_type: string;
      expected_value: any;
      candidate_value: any;
      passed: boolean;
      is_mandatory: boolean;
      explanation: string;
    }>;
  };
  strengths_summary: string[];
  critical_gaps_summary: Array<{
    skill_slug: string;
    canonical_name: string;
    required_level: number;
    estimated_level: number;
    raw_gap: number;
    weighted_gap: number;
    importance_weight: number;
    interview_relevance: string;
    reason: string;
  }>;
  item_breakdowns: ReadinessItemBreakdown[];
  generated_at: string;
}

export interface PreparationActivityItem {
  skill_slug: string;
  canonical_name: string;
  activity_type: "LEARN" | "PRACTICE" | "ASSESS" | "MAINTAIN" | string;
  allocated_hours: number;
  rationale: string;
}

export interface WeeklyScheduleItem {
  week_number: number;
  focus_theme: string;
  total_hours: number;
  activities: PreparationActivityItem[];
}

export interface PreparationMilestoneItem {
  week_target: number;
  title: string;
  description: string;
  skills_involved: string[];
}

export interface PriorityAreaItem {
  skill_slug: string;
  canonical_name: string;
  category: string;
  required_level: number;
  estimated_level: number;
  gap_levels: number;
  priority_tier: "high" | "medium" | "maintenance" | string;
  allocated_hours: number;
  rationale: string;
}

export interface PreparationPlanResponse {
  id: string;
  session_id: string;
  report_id: string;
  total_hours_allocated: number;
  available_hours_per_week: number;
  weeks_until_target: number;
  capacity_note: string;
  priority_areas: PriorityAreaItem[];
  schedule: WeeklyScheduleItem[];
  milestones: PreparationMilestoneItem[];
  created_at: string;
}
