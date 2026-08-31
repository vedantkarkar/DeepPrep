"use client";

import React, { useState } from "react";
import { HelpCircle, ChevronDown, ChevronUp } from "lucide-react";

export function MethodologyExplainer() {
  const [open, setOpen] = useState(false);

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800/80">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between text-left text-xs font-semibold text-slate-300 hover:text-white transition-colors"
      >
        <span className="flex items-center gap-2">
          <HelpCircle className="h-4 w-4 text-blue-400" />
          How does DeepPrep calculate your role readiness?
        </span>
        {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {open && (
        <div className="mt-4 pt-3 border-t border-white/[0.06] text-xs text-slate-400 space-y-2 leading-relaxed">
          <p>
            1. <strong>Evidence-Backed Capability:</strong> Raw resume mentions are candidate claims only. DeepPrep estimates capability (Levels 1 to 5) based solely on concrete projects, repositories, assessments, and verified coursework.
          </p>
          <p>
            2. <strong>Role-Specific Weighted Formula:</strong> Each required competency contributes according to its importance weight (Weight × min(Estimated Level, Required Level)). Exceeding a requirement does not award unearned bonus points.
          </p>
          <p>
            3. <strong>Application Eligibility:</strong> Degree, branch, and graduation year requirements are evaluated as strict gating criteria separately from technical readiness.
          </p>
        </div>
      )}
    </div>
  );
}
