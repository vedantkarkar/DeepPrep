import { apiFetch } from "./client";
import { PreparationSession, ReadinessReport } from "./types";

export async function createSession(data: {
  candidate_id: string;
  job_id: string;
  available_hours_per_week: number;
  weeks_until_target: number;
}): Promise<PreparationSession> {
  return apiFetch<PreparationSession>("/sessions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getSession(sessionId: string): Promise<PreparationSession> {
  return apiFetch<PreparationSession>(`/sessions/${sessionId}`);
}

export async function evaluateSession(sessionId: string): Promise<ReadinessReport> {
  return apiFetch<ReadinessReport>(`/sessions/${sessionId}/evaluate`, {
    method: "POST",
  });
}

export async function getSessionReport(sessionId: string): Promise<ReadinessReport> {
  return apiFetch<ReadinessReport>(`/sessions/${sessionId}/report`);
}
