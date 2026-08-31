import React from "react";
import { Award, ShieldCheck, AlertCircle } from "lucide-react";

interface ReadinessScoreCardProps {
  score: number;
  jobTitle: string;
  companyName: string;
  eligibilityStatus: string;
}

export function ReadinessScoreCard({
  score,
  jobTitle,
  companyName,
  eligibilityStatus,
}: ReadinessScoreCardProps) {
  let alignmentLabel = "Strong Alignment";
  let badgeColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
  let ringColor = "stroke-emerald-500";

  if (score < 60) {
    alignmentLabel = "Significant Deficits";
    badgeColor = "text-rose-400 bg-rose-500/10 border-rose-500/30";
    ringColor = "stroke-rose-500";
  } else if (score < 80) {
    alignmentLabel = "Moderate Gaps";
    badgeColor = "text-amber-400 bg-amber-500/10 border-amber-500/30";
    ringColor = "stroke-amber-500";
  }

  // Circular gauge calculations
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-96 h-96 radial-glow pointer-events-none opacity-40" />

      {/* Title & Context */}
      <div className="space-y-2 text-center md:text-left z-10">
        <span className="text-xs font-semibold uppercase tracking-widest text-cyan-400 font-mono">
          Target Role Assessment
        </span>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          {jobTitle}
        </h1>
        <p className="text-sm text-slate-400 font-medium">{companyName}</p>

        <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 pt-2">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${badgeColor}`}>
            {alignmentLabel}
          </span>
          <span className="text-xs text-slate-500 font-mono">
            Deterministic Role-Readiness Score
          </span>
        </div>
      </div>

      {/* Circular Gauge */}
      <div className="relative flex items-center justify-center shrink-0 z-10">
        <svg className="w-36 h-36 -rotate-90 transform">
          <circle
            cx="72"
            cy="72"
            r={radius}
            className="stroke-slate-800"
            strokeWidth="10"
            fill="transparent"
          />
          <circle
            cx="72"
            cy="72"
            r={radius}
            className={`${ringColor} transition-all duration-1000 ease-out`}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>

        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
            {score}
          </span>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Out of 100
          </span>
        </div>
      </div>
    </div>
  );
}
