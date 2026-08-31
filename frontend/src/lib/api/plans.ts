import { apiFetch } from "./client";
import { PreparationPlanResponse } from "./types";

export async function generatePlan(sessionId: string): Promise<PreparationPlanResponse> {
  return apiFetch<PreparationPlanResponse>(`/sessions/${sessionId}/plan`, {
    method: "POST",
  });
}

export async function getPlan(sessionId: string): Promise<PreparationPlanResponse> {
  return apiFetch<PreparationPlanResponse>(`/sessions/${sessionId}/plan`);
}
