"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, Layers, CheckCircle2, AlertTriangle, XCircle, Info } from "lucide-react";
import { ReadinessItemBreakdown } from "@/lib/api/types";

interface SkillBreakdownProps {
  items: ReadinessItemBreakdown[];
}

export function SkillBreakdown({ items }: SkillBreakdownProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleExpand = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.06]">
        <div>
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <Layers className="h-4 w-4 text-blue-400" />
            Skill Capability Alignment
          </h3>
          <p className="text-xs text-slate-400">
            Line-by-line comparison between modeled job requirement and evidence-backed capability.
          </p>
        </div>
        <span className="text-xs text-slate-500 font-mono">{items.length} competencies</span>
      </div>

      <div className="space-y-3">
        {items.map((item, idx) => {
          const isExpanded = expandedIndex === idx;
          const percentage = Math.min(100, Math.round((item.estimated_level / item.required_level) * 100));

          let statusBadge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
          if (item.classification === "critical_gap") {
            statusBadge = "bg-rose-500/20 text-rose-300 border-rose-500/30";
          } else if (item.classification === "moderate_gap") {
            statusBadge = "bg-amber-500/20 text-amber-300 border-amber-500/30";
          } else if (item.classification === "aligned") {
            statusBadge = "bg-blue-500/20 text-blue-300 border-blue-500/30";
          }

          return (
            <div
              key={item.skill_slug}
              className="rounded-xl border border-slate-800 bg-slate-900/40 overflow-hidden transition-all duration-200"
            >
              {/* Main Row */}
              <div
                onClick={() => toggleExpand(idx)}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer hover:bg-slate-800/40"
              >
                <div className="space-y-1 sm:w-1/3 truncate">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-white truncate">
                      {item.canonical_name}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wider ${statusBadge}`}>
                      {item.classification.replace("_", " ")}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500 font-mono capitalize">
                    {item.category} · Weight: {item.importance_weight.toFixed(2)}
                  </span>
                </div>

                {/* Level indicators */}
                <div className="flex-1 flex items-center gap-4">
                  <div className="flex-1 space-y-1">
                    <div className="flex justify-between text-xs text-slate-400 font-mono">
                      <span>Estimated: Level {item.estimated_level} / 5</span>
                      <span>Target: Level {item.required_level}</span>
                    </div>
                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          item.classification === "strength"
                            ? "bg-emerald-500"
                            : item.classification === "critical_gap"
                            ? "bg-rose-500"
                            : "bg-blue-500"
                        }`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>

                  <button className="text-slate-400 hover:text-white p-1">
                    {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Expandable Traceability Drawer */}
              {isExpanded && (
                <div className="p-4 bg-slate-950/80 border-t border-slate-800/80 text-xs space-y-2 text-slate-300">
                  <div className="flex items-center gap-1.5 font-semibold text-cyan-400">
                    <Info className="h-3.5 w-3.5" />
                    Why this score? (Deterministic Mathematical Trace)
                  </div>
                  <p className="text-slate-300 leading-relaxed">{item.explanation}</p>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 text-[11px] font-mono text-slate-400 border-t border-white/[0.04]">
                    <div>Required Level: <strong className="text-white">{item.required_level}</strong></div>
                    <div>Estimated Level: <strong className="text-white">{item.estimated_level}</strong></div>
                    <div>Gap Score: <strong className="text-white">{item.gap_score.toFixed(2)}</strong></div>
                    <div>Weight: <strong className="text-white">{item.importance_weight.toFixed(2)}</strong></div>
                  </div>
                  {item.supporting_evidence_ids.length > 0 && (
                    <div className="text-[11px] text-slate-500 pt-1">
                      Supporting Evidence IDs: {item.supporting_evidence_ids.join(", ")}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
