"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/lib/context/AppContext";
import { StepIndicator } from "@/components/onboarding/StepIndicator";
import { ResumeUpload } from "@/components/onboarding/ResumeUpload";
import { ClaimReview } from "@/components/onboarding/ClaimReview";
import { EducationConfirmation } from "@/components/onboarding/EducationConfirmation";
import { EvidenceCollection } from "@/components/onboarding/EvidenceCollection";
import { JobSelection } from "@/components/onboarding/JobSelection";
import { ResumeExtractionResponse, Candidate, ReadinessReport } from "@/lib/api/types";

const STEPS = [
  "Upload Resume",
  "Review Claims",
  "Education",
  "Add Evidence",
  "Target Job",
];

export default function OnboardingPage() {
  const router = useRouter();
  const { setCandidate, setActiveSessionId, setActiveReport } = useApp();

  const [currentStep, setCurrentStep] = useState(1);
  const [candidate, setLocalCandidate] = useState<Candidate | null>(null);
  const [extraction, setExtraction] = useState<ResumeExtractionResponse | null>(null);
  const [confirmedSkills, setConfirmedSkills] = useState<string[]>([]);

  const handleExtractionComplete = (cand: Candidate, ext: ResumeExtractionResponse) => {
    setLocalCandidate(cand);
    setCandidate(cand);
    setExtraction(ext);
    setCurrentStep(2);
  };

  const handleClaimsConfirmed = (confirmedSlugs: string[]) => {
    setConfirmedSkills(confirmedSlugs);
    setCurrentStep(3);
  };

  const handleEducationConfirmed = (updatedCand: Candidate) => {
    setLocalCandidate(updatedCand);
    setCandidate(updatedCand);
    setCurrentStep(4);
  };

  const handleProceedToJobs = () => {
    setCurrentStep(5);
  };

  const handleEvaluationComplete = (report: ReadinessReport) => {
    setActiveReport(report);
    setActiveSessionId(report.session_id);
    router.push(`/readiness/${report.session_id}`);
  };

  return (
    <div className="max-w-4xl mx-auto py-4">
      <StepIndicator currentStep={currentStep} totalSteps={5} steps={STEPS} />

      <div className="mt-4">
        {currentStep === 1 && (
          <ResumeUpload onExtractionComplete={handleExtractionComplete} />
        )}

        {currentStep === 2 && candidate && extraction && (
          <ClaimReview
            candidateId={candidate.id}
            extractedSkills={extraction.normalized_skill_claims}
            unresolvedSkills={extraction.unresolved_skill_claims}
            onClaimsConfirmed={handleClaimsConfirmed}
          />
        )}

        {currentStep === 3 && candidate && (
          <EducationConfirmation
            candidateId={candidate.id}
            extractedEducation={extraction?.education_claims?.[0]}
            onEducationConfirmed={handleEducationConfirmed}
          />
        )}

        {currentStep === 4 && candidate && (
          <EvidenceCollection
            candidateId={candidate.id}
            confirmedSkillSlugs={confirmedSkills}
            onProceedToJobs={handleProceedToJobs}
          />
        )}

        {currentStep === 5 && candidate && (
          <JobSelection
            candidateId={candidate.id}
            onEvaluationComplete={handleEvaluationComplete}
          />
        )}
      </div>
    </div>
  );
}
