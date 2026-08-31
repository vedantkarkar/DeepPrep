"use client";

import React, { useState, useEffect } from "react";
import { Briefcase, Building2, MapPin, CheckCircle, Clock, Sparkles, Loader2, ExternalLink } from "lucide-react";
import { listJobs } from "@/lib/api/jobs";
import { createSession, evaluateSession } from "@/lib/api/sessions";
import { Job, ReadinessReport } from "@/lib/api/types";

interface JobSelectionProps {
  candidateId: string;
  onEvaluationComplete: (report: ReadinessReport) => void;
}

export function JobSelection({ candidateId, onEvaluationComplete }: JobSelectionProps) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [hoursPerWeek, setHoursPerWeek] = useState<number>(15);
  const [weeksTarget, setWeeksTarget] = useState<number>(6);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listJobs()
      .then((data) => {
        setJobs(data);
        if (data.length > 0) {
          setSelectedJobId(data[0].id);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load jobs.");
        setLoading(false);
      });
  }, []);

  const handleRunEvaluation = async () => {
    if (!selectedJobId) return;

    try {
      setEvaluating(true);
      setError(null);

      // 1. Create Preparation Session
      const session = await createSession({
        candidate_id: candidateId,
        job_id: selectedJobId,
        available_hours_per_week: hoursPerWeek,
        weeks_until_target: weeksTarget,
      });

      // 2. Run Phase 2 Deterministic Readiness Engine
      const report = await evaluateSession(session.id);

      setEvaluating(false);
      onEvaluationComplete(report);
    } catch (err: any) {
      setEvaluating(false);
      setError(err.message || "Readiness evaluation failed. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-400">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-3" />
        <p className="text-sm">Loading available target roles...</p>
      </div>
    );
  }

  const selectedJob = jobs.find((j) => j.id === selectedJobId);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Choose Your Target Role
        </h2>
        <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
          DeepPrep will calculate your deterministic role-readiness score against this specific opening.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Jobs List */}
        <div className="lg:col-span-2 space-y-3">
          {jobs.map((job) => {
            const isSelected = job.id === selectedJobId;
            const requiredCount = job.competency_requirements?.filter((c) => c.is_required).length || 0;
            const preferredCount = job.competency_requirements?.filter((c) => !c.is_required).length || 0;

            return (
              <div
                key={job.id}
                onClick={() => setSelectedJobId(job.id)}
                className={`glass-panel p-4 rounded-xl border cursor-pointer transition-all duration-200 ${
                  isSelected
                    ? "border-blue-500 bg-blue-950/20 ring-2 ring-blue-500/20 shadow-lg shadow-blue-500/10"
                    : "border-slate-800/80 hover:border-slate-700 bg-slate-900/40"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-cyan-400 font-mono">
                      {job.target_role}
                    </span>
                    <h3 className="font-bold text-white text-base mt-0.5">{job.title}</h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1.5">
                      <span className="flex items-center gap-1">
                        <Building2 className="h-3.5 w-3.5 text-slate-500" />
                        {job.company_name}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-slate-500" />
                        {job.location_city || "Maharashtra"}
                      </span>
                      <span className="px-2 py-0.5 bg-slate-800 rounded text-[10px] uppercase font-mono">
                        {job.source_type}
                      </span>
                    </div>
                  </div>

                  <div
                    className={`h-6 w-6 rounded-full flex items-center justify-center border ${
                      isSelected
                        ? "bg-blue-600 border-blue-500 text-white"
                        : "border-slate-700 bg-slate-800"
                    }`}
                  >
                    {isSelected && <CheckCircle className="h-4 w-4" />}
                  </div>
                </div>

                {/* Skills tags preview */}
                <div className="flex flex-wrap gap-1.5 mt-3 pt-2.5 border-t border-white/[0.04]">
                  <span className="text-[11px] text-slate-500 py-0.5 font-medium">Requirements:</span>
                  {job.competency_requirements?.slice(0, 5).map((comp) => (
                    <span
                      key={comp.skill_slug}
                      className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                        comp.is_required
                          ? "bg-blue-500/10 text-blue-300 border border-blue-500/20"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {comp.canonical_name}
                    </span>
                  ))}
                  {(job.competency_requirements?.length || 0) > 5 && (
                    <span className="text-[10px] text-slate-500 py-0.5">
                      +{(job.competency_requirements?.length || 0) - 5} more
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Preparation Parameters Card */}
        <div className="lg:col-span-1">
          <div className="glass-panel p-5 rounded-2xl space-y-5 sticky top-20">
            <h3 className="font-bold text-white text-sm pb-2 border-b border-white/[0.06] flex items-center gap-2">
              <Clock className="h-4 w-4 text-blue-400" />
              Preparation Context
            </h3>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1.5">
                <span>Available Hours / Week</span>
                <span className="text-cyan-400 font-mono">{hoursPerWeek} hrs/wk</span>
              </div>
              <input
                type="range"
                min={5}
                max={40}
                step={5}
                value={hoursPerWeek}
                onChange={(e) => setHoursPerWeek(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1.5">
                <span>Weeks Until Interview</span>
                <span className="text-cyan-400 font-mono">{weeksTarget} weeks</span>
              </div>
              <input
                type="range"
                min={2}
                max={16}
                step={1}
                value={weeksTarget}
                onChange={(e) => setWeeksTarget(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            {selectedJob && (
              <div className="p-3 bg-slate-900/80 rounded-xl text-xs space-y-1 text-slate-400 border border-slate-800">
                <p className="font-semibold text-slate-200">Evaluating against:</p>
                <p className="truncate text-white font-medium">{selectedJob.title}</p>
                <p>{selectedJob.company_name}</p>
              </div>
            )}

            {error && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
                {error}
              </div>
            )}

            <button
              type="button"
              disabled={!selectedJobId || evaluating}
              onClick={handleRunEvaluation}
              className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                !selectedJobId || evaluating
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-xl shadow-blue-500/25 active:scale-[0.98]"
              }`}
            >
              {evaluating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Computing Readiness...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Analyze My Readiness</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
