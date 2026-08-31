import { apiFetch } from "./client";
import { CandidateEvidence } from "./types";

export async function submitEvidence(
  candidateId: string,
  data: {
    skill_slug: string;
    evidence_type: string;
    title: string;
    description?: string;
    url?: string;
    metadata?: Record<string, any>;
    date_obtained?: string;
  }
): Promise<CandidateEvidence> {
  return apiFetch<CandidateEvidence>(`/candidates/${candidateId}/evidence`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function listCandidateEvidence(
  candidateId: string,
  skillSlug?: string
): Promise<CandidateEvidence[]> {
  const query = skillSlug ? `?skill_slug=${encodeURIComponent(skillSlug)}` : "";
  return apiFetch<CandidateEvidence[]>(`/candidates/${candidateId}/evidence${query}`);
}
