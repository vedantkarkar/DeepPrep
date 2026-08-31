"use client";

import React, { useState } from "react";
import { 
  Calendar, 
  Clock, 
  Sparkles, 
  Layers, 
  Target, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  ChevronRight, 
  Award,
  BookOpen,
  Code2,
  HelpCircle,
  TrendingUp
} from "lucide-react";
import { generatePlan, getPlan } from "@/lib/api/plans";
import { PreparationPlanResponse, WeeklyScheduleItem } from "@/lib/api/types";

interface PreparationRoadmapProps {
  sessionId: string;
  initialPlan?: PreparationPlanResponse | null;
}

export function PreparationRoadmap({ sessionId, initialPlan }: PreparationRoadmapProps) {
  const [plan, setPlan] = useState<PreparationPlanResponse | null>(initialPlan || null);
  const [selectedWeek, setSelectedWeek] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGeneratePlan = async () => {
    try {
      setLoading(true);
      setError(null);
      const generated = await generatePlan(sessionId);
      setPlan(generated);
      setSelectedWeek(1);
      setLoading(false);
    } catch (err: any) {
      setLoading(false);
      setError(err.message || "Failed to generate preparation plan.");
    }
  };

  if (!plan) {
    return (
      <div className="glass-panel rounded-2xl p-6 sm:p-8 text-center space-y-4 border border-blue-500/20 bg-gradient-to-b from-blue-950/20 to-slate-900/60">
        <div className="h-12 w-12 rounded-2xl bg-blue-500/10 text-cyan-400 flex items-center justify-center mx-auto shadow-inner">
          <Sparkles className="h-6 w-6" />
        </div>
        <div className="space-y-1 max-w-md mx-auto">
          <h3 className="font-bold text-white text-lg tracking-tight">
            What Should You Prepare Next?
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Generate a personalized, evidence-driven study roadmap optimized against your available hours and target deadline.
          </p>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs max-w-md mx-auto">
            {error}
          </div>
        )}

        <button
          type="button"
          disabled={loading}
          onClick={handleGeneratePlan}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs uppercase tracking-wider rounded-xl shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2 mx-auto transition-all active:scale-[0.98]"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Optimizing Study Schedule...</span>
            </>
          ) : (
            <>
              <TrendingUp className="h-4 w-4" />
              <span>Generate My Preparation Plan</span>
            </>
          )}
        </button>
      </div>
    );
  }

  const activeWeekSchedule = plan.schedule.find((s) => s.week_number === selectedWeek) || plan.schedule[0];

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 space-y-6 border border-blue-500/20">
      {/* Header & Context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/[0.06]">
        <div>
          <span className="text-[10px] font-mono uppercase tracking-widest text-cyan-400 font-semibold">
            Deterministic Optimization Engine
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2 mt-0.5">
            <TrendingUp className="h-5 w-5 text-blue-400" />
            Your Personalized Preparation Roadmap
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Optimized time allocation focused on high-priority role requirements and diminishing returns.
          </p>
        </div>

        {/* Capacity Metrics */}
        <div className="flex items-center gap-3 bg-slate-900/90 border border-slate-800 rounded-xl p-2.5 shrink-0 text-xs">
          <div className="text-center px-2">
            <span className="text-slate-500 block text-[10px] uppercase font-mono">Weeks</span>
            <span className="font-bold text-white font-mono">{plan.weeks_until_target}</span>
          </div>
          <div className="h-6 w-[1px] bg-slate-800" />
          <div className="text-center px-2">
            <span className="text-slate-500 block text-[10px] uppercase font-mono">Rate</span>
            <span className="font-bold text-white font-mono">{plan.available_hours_per_week}h/wk</span>
          </div>
          <div className="h-6 w-[1px] bg-slate-800" />
          <div className="text-center px-2">
            <span className="text-slate-500 block text-[10px] uppercase font-mono">Total</span>
            <span className="font-bold text-cyan-400 font-mono">{plan.total_hours_allocated}h</span>
          </div>
        </div>
      </div>

      {/* Capacity Note */}
      {plan.capacity_note && (
        <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl text-xs text-blue-300 flex items-start gap-2">
          <Sparkles className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />
          <span>{plan.capacity_note}</span>
        </div>
      )}

      {/* Priority Skill Areas */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Prioritized Allocation Summary
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {plan.priority_areas.map((area) => {
            let tierBadge = "bg-rose-500/20 text-rose-300 border-rose-500/30";
            if (area.priority_tier === "medium") {
              tierBadge = "bg-amber-500/20 text-amber-300 border-amber-500/30";
            } else if (area.priority_tier === "maintenance") {
              tierBadge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
            }

            return (
              <div
                key={area.skill_slug}
                className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 space-y-1.5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-white truncate">{area.canonical_name}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wider ${tierBadge}`}>
                      {area.priority_tier}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed line-clamp-2">
                    {area.rationale}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-white/[0.04] text-[11px] font-mono">
                  <span className="text-slate-500">
                    {area.gap_levels > 0 ? `Gap: ${area.gap_levels} Lvl` : "Meets Target"}
                  </span>
                  <span className="font-bold text-cyan-400">{area.allocated_hours}h allocated</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Interactive Weekly Schedule */}
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Weekly Study Plan
          </h3>
          <span className="text-xs text-slate-500 font-mono">Select a week to inspect</span>
        </div>

        {/* Week Selector Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {plan.schedule.map((s) => {
            const isSelected = s.week_number === selectedWeek;
            return (
              <button
                key={s.week_number}
                type="button"
                onClick={() => setSelectedWeek(s.week_number)}
                className={`px-4 py-2 rounded-xl text-xs font-bold shrink-0 transition-all ${
                  isSelected
                    ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                    : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                Week {s.week_number} ({s.total_hours}h)
              </button>
            );
          })}
        </div>

        {/* Active Week Activities Card */}
        {activeWeekSchedule && (
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.04]">
              <div>
                <span className="text-[10px] font-mono text-cyan-400 uppercase font-semibold">
                  Week {activeWeekSchedule.week_number} Focus Theme
                </span>
                <h4 className="text-sm font-bold text-white">{activeWeekSchedule.focus_theme}</h4>
              </div>
              <span className="px-2.5 py-1 bg-slate-800 rounded-lg text-xs font-mono text-slate-300">
                {activeWeekSchedule.total_hours} Hours Total
              </span>
            </div>

            <div className="space-y-2.5">
              {activeWeekSchedule.activities.map((act, idx) => {
                let actColor = "bg-blue-500/20 text-blue-300 border-blue-500/30";
                if (act.activity_type === "LEARN") {
                  actColor = "bg-indigo-500/20 text-indigo-300 border-indigo-500/30";
                } else if (act.activity_type === "ASSESS") {
                  actColor = "bg-cyan-500/20 text-cyan-300 border-cyan-500/30";
                } else if (act.activity_type === "MAINTAIN") {
                  actColor = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
                }

                return (
                  <div
                    key={idx}
                    className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border uppercase tracking-wider ${actColor}`}>
                          {act.activity_type}
                        </span>
                        <span className="font-bold text-white">{act.canonical_name}</span>
                      </div>
                      <p className="text-slate-400 leading-relaxed text-[11px]">
                        {act.rationale}
                      </p>
                    </div>

                    <div className="shrink-0 font-mono font-bold text-cyan-400 text-xs sm:text-right">
                      {act.allocated_hours} hr(s)
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Milestones Section */}
      {plan.milestones.length > 0 && (
        <div className="space-y-3 pt-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Target className="h-4 w-4 text-blue-400" />
            Key Preparation Milestones
          </h3>
          <div className="space-y-2">
            {plan.milestones.map((m, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/40 flex items-start gap-3 text-xs"
              >
                <div className="h-7 w-7 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center shrink-0 mt-0.5 font-bold font-mono text-[11px]">
                  W{m.week_target}
                </div>
                <div className="space-y-0.5">
                  <h4 className="font-bold text-white text-xs">{m.title}</h4>
                  <p className="text-slate-400 text-[11px] leading-relaxed">{m.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Why This Plan Accordion */}
      <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/30 text-xs text-slate-400 space-y-1.5 leading-relaxed">
        <p className="font-semibold text-slate-300 flex items-center gap-1.5">
          <HelpCircle className="h-3.5 w-3.5 text-blue-400" />
          Why this preparation allocation?
        </p>
        <p>
          DeepPrep prioritizes large competency deficits on mandatory, high-relevance interview skills.
          As preparation hours accumulate on a single skill, diminishing returns ensure secondary gaps are not neglected.
          The schedule reserves the final week for mock technical review and validation.
        </p>
      </div>
    </div>
  );
}
