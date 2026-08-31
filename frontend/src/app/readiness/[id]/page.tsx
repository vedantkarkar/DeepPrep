"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, RotateCcw, Loader2, Sparkles, AlertCircle } from "lucide-react";
import { getSessionReport } from "@/lib/api/sessions";
import { getJob } from "@/lib/api/jobs";
import { getPlan } from "@/lib/api/plans";
import { ReadinessReport, Job, PreparationPlanResponse } from "@/lib/api/types";
import { ReadinessScoreCard } from "@/components/readiness/ReadinessScoreCard";
import { EligibilityCard } from "@/components/readiness/EligibilityCard";
import { ConfidenceCard } from "@/components/readiness/ConfidenceCard";
import { SkillBreakdown } from "@/components/readiness/SkillBreakdown";
import { CriticalGapsCard } from "@/components/readiness/CriticalGapsCard";
import { StrengthsCard } from "@/components/readiness/StrengthsCard";
import { PreparationRoadmap } from "@/components/readiness/PreparationRoadmap";
import { MethodologyExplainer } from "@/components/readiness/MethodologyExplainer";

export default function ReadinessDashboardPage() {
  const params = useParams();
  const sessionId = params.id as string;

  const [report, setReport] = useState<ReadinessReport | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [plan, setPlan] = useState<PreparationPlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    getSessionReport(sessionId)
      .then((rep) => {
        setReport(rep);
        return Promise.all([
          getJob(rep.job_id),
          getPlan(sessionId).catch(() => null), // Optional existing plan
        ]);
      })
      .then(([j, existingPlan]) => {
        setJob(j);
        if (existingPlan) {
          setPlan(existingPlan);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load readiness report.");
        setLoading(false);
      });
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-blue-500" />
        <p className="text-sm text-slate-400 font-mono">
          Loading deterministic readiness assessment...
        </p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-xl mx-auto py-12 text-center space-y-4">
        <div className="h-12 w-12 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h2 className="text-xl font-bold text-white">Assessment Not Found</h2>
        <p className="text-xs text-slate-400">{error || "Please run a readiness check first."}</p>
        <Link
          href="/onboarding"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-semibold"
        >
          Start New Assessment
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Top action bar */}
      <div className="flex items-center justify-between">
        <Link
          href="/jobs"
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors font-medium"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Jobs
        </Link>

        <Link
          href="/onboarding"
          className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 font-medium"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Re-evaluate with New Evidence
        </Link>
      </div>

      {/* 1. Readiness Score Gauge Card */}
      <ReadinessScoreCard
        score={report.overall_readiness_score}
        jobTitle={job?.title || "Target Role"}
        companyName={job?.company_name || "Company"}
        eligibilityStatus={report.eligibility_status}
      />

      {/* 2. Prerequisite Eligibility Card */}
      <EligibilityCard
        status={report.eligibility_status}
        summary={report.eligibility_summary}
      />

      {/* 3. Evidence Confidence Card */}
      <ConfidenceCard confidence={report.evidence_confidence_score} />

      {/* 4. Phase 6 Deterministic Preparation Roadmap */}
      <PreparationRoadmap sessionId={sessionId} initialPlan={plan} />

      {/* 5. Critical Gaps Card */}
      <CriticalGapsCard criticalGaps={report.critical_gaps_summary} />

      {/* 6. Strengths Card */}
      <StrengthsCard strengths={report.strengths_summary} />

      {/* 7. Line-by-Line Skill Readiness Matrix */}
      <SkillBreakdown items={report.item_breakdowns} />

      {/* 8. Explainer Footer */}
      <MethodologyExplainer />
    </div>
  );
}
