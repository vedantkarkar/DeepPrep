import React from "react";
import { AlertTriangle, ArrowRight } from "lucide-react";

interface CriticalGapsCardProps {
  criticalGaps: Array<{
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
}

export function CriticalGapsCard({ criticalGaps }: CriticalGapsCardProps) {
  if (!criticalGaps || criticalGaps.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4 border-rose-500/20 bg-rose-950/10">
      <div className="flex items-center justify-between pb-3 border-b border-rose-500/20">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-rose-400" />
          <h3 className="font-bold text-white text-base">Critical Skill Gaps</h3>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30 font-mono">
          {criticalGaps.length} Priority Deficits
        </span>
      </div>

      <p className="text-xs text-slate-400">
        These competencies have significant level deficits on high-priority interview requirements.
      </p>

      <div className="space-y-2.5">
        {criticalGaps.map((gap) => (
          <div
            key={gap.skill_slug}
            className="p-3.5 rounded-xl border border-rose-500/30 bg-slate-900/80 space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-white">{gap.canonical_name}</span>
              <span className="text-xs font-mono text-rose-400 font-semibold">
                Deficit: {gap.raw_gap} Level(s)
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">{gap.reason}</p>
            <div className="flex items-center gap-3 text-[11px] font-mono text-slate-500 pt-1">
              <span>Required: L{gap.required_level}</span>
              <span>Estimated: L{gap.estimated_level}</span>
              <span>Relevance: {gap.interview_relevance.toUpperCase()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
