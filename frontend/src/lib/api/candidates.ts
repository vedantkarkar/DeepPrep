import { apiFetch } from "./client";
import { Candidate, CandidateSkillClaim } from "./types";

export async function createCandidate(data: {
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
}): Promise<Candidate> {
  return apiFetch<Candidate>("/candidates", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getCandidate(id: string): Promise<Candidate> {
  return apiFetch<Candidate>(`/candidates/${id}`);
}

export async function confirmEducation(
  candidateId: string,
  data: {
    degree: string;
    branch: string;
    institution: string;
    graduation_year: number;
    student_status: string;
    confirmed: boolean;
  }
): Promise<Candidate> {
  return apiFetch<Candidate>(`/candidates/${candidateId}/education`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function getCandidateClaims(
  candidateId: string
): Promise<CandidateSkillClaim[]> {
  return apiFetch<CandidateSkillClaim[]>(`/candidates/${candidateId}/claims`);
}

export async function batchConfirmClaims(
  candidateId: string,
  data: {
    confirmed_skill_slugs: string[];
    rejected_skill_slugs: string[];
  }
): Promise<CandidateSkillClaim[]> {
  return apiFetch<CandidateSkillClaim[]>(`/candidates/${candidateId}/claims/confirm`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}
