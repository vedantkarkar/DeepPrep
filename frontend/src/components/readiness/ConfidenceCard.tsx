import React from "react";
import { ShieldCheck, Info } from "lucide-react";

interface ConfidenceCardProps {
  confidence: "low" | "medium" | "high" | string;
}

export function ConfidenceCard({ confidence }: ConfidenceCardProps) {
  let label = "High Evidence Confidence";
  let badgeColor = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
  let explanation =
    "Readiness is supported by multiple diverse, verified practical projects and assessments.";

  if (confidence === "medium") {
    label = "Medium Evidence Confidence";
    badgeColor = "bg-blue-500/20 text-blue-300 border-blue-500/30";
    explanation =
      "Core skills have evidence, but some secondary requirements rely on unverified or single-source records.";
  } else if (confidence === "low") {
    label = "Low Evidence Confidence";
    badgeColor = "bg-amber-500/20 text-amber-300 border-amber-500/30";
    explanation =
      "Most required skills lack verifiable evidence. Add repository links or problem-solving metrics to increase confidence.";
  }

  return (
    <div className="glass-panel rounded-2xl p-5 flex items-start gap-3.5">
      <div className="h-9 w-9 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center shrink-0 mt-0.5">
        <ShieldCheck className="h-5 w-5" />
      </div>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <h4 className="font-bold text-white text-sm">Evidence Confidence Rating</h4>
          <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase tracking-wider ${badgeColor}`}>
            {confidence}
          </span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">{explanation}</p>
      </div>
    </div>
  );
}
