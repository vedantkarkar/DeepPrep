import { apiFetch } from "./client";
import { Job } from "./types";

export async function listJobs(): Promise<Job[]> {
  return apiFetch<Job[]>("/jobs");
}

export async function getJob(jobId: string): Promise<Job> {
  return apiFetch<Job>(`/jobs/${jobId}`);
}
