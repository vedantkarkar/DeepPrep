import React from "react";
import { Sparkles, CheckCircle2 } from "lucide-react";

interface StrengthsCardProps {
  strengths: string[];
}

export function StrengthsCard({ strengths }: StrengthsCardProps) {
  if (!strengths || strengths.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-3 border-emerald-500/20 bg-emerald-950/10">
      <div className="flex items-center gap-2 pb-2 border-b border-emerald-500/20">
        <Sparkles className="h-4 w-4 text-emerald-400" />
        <h3 className="font-bold text-white text-base">Your Demonstrable Strengths</h3>
      </div>
      <p className="text-xs text-slate-400">
        Your evidence-backed proficiency meets or exceeds modeled job standards:
      </p>
      <div className="flex flex-wrap gap-2 pt-1">
        {strengths.map((str, idx) => (
          <span
            key={idx}
            className="px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5"
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            {str}
          </span>
        ))}
      </div>
    </div>
  );
}
