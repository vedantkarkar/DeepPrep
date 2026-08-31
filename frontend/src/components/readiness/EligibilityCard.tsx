import React from "react";
import { CheckCircle2, XCircle, AlertTriangle, ShieldCheck } from "lucide-react";

interface EligibilityCardProps {
  status: "eligible" | "partially_eligible" | "ineligible" | string;
  summary: {
    is_eligible?: boolean;
    reasons?: string[];
    criteria?: Array<{
      criterion_type: string;
      expected_value: any;
      candidate_value: any;
      passed: boolean;
      is_mandatory: boolean;
      explanation: string;
    }>;
  };
}

export function EligibilityCard({ status, summary }: EligibilityCardProps) {
  const isEligible = status === "eligible";
  const isPartial = status === "partially_eligible";

  let statusHeader = "Application Prerequisites: Eligible";
  let statusBadge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
  let icon = <CheckCircle2 className="h-5 w-5 text-emerald-400" />;

  if (status === "ineligible") {
    statusHeader = "Application Prerequisites: Ineligible";
    statusBadge = "bg-rose-500/20 text-rose-300 border-rose-500/40";
    icon = <XCircle className="h-5 w-5 text-rose-400" />;
  } else if (isPartial) {
    statusHeader = "Application Prerequisites: Requires Confirmation";
    statusBadge = "bg-amber-500/20 text-amber-300 border-amber-500/40";
    icon = <AlertTriangle className="h-5 w-5 text-amber-400" />;
  }

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          {icon}
          <div>
            <h3 className="font-bold text-white text-base">{statusHeader}</h3>
            <p className="text-xs text-slate-400">
              Gating criteria evaluated independently from technical capability.
            </p>
          </div>
        </div>
        <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold border ${statusBadge}`}>
          {status.replace("_", " ").toUpperCase()}
        </span>
      </div>

      {/* Criteria Breakdown */}
      <div className="space-y-2.5">
        {summary.criteria?.map((crit, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-xl border flex items-start justify-between gap-3 text-xs ${
              crit.passed
                ? "bg-slate-900/40 border-slate-800 text-slate-300"
                : "bg-rose-950/20 border-rose-500/30 text-rose-200"
            }`}
          >
            <div className="space-y-0.5">
              <span className="font-semibold capitalize text-slate-200 block">
                {crit.criterion_type.replace(/_/g, " ")}:
              </span>
              <p className="text-slate-400">{crit.explanation}</p>
            </div>
            <div className="shrink-0 pt-0.5">
              {crit.passed ? (
                <span className="text-emerald-400 font-bold">✓ Met</span>
              ) : (
                <span className="text-rose-400 font-bold">✗ Failed</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
