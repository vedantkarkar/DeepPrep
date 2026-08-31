import { apiFetch } from "./client";
import { ResumeExtractionResponse } from "./types";

export async function extractResume(file: File): Promise<ResumeExtractionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch<ResumeExtractionResponse>("/resumes/extract", {
    method: "POST",
    body: formData,
  });
}
