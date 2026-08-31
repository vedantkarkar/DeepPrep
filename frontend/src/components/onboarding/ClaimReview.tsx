"use client";

import React, { useState } from "react";
import { Check, X, Plus, Info, AlertTriangle, ShieldCheck } from "lucide-react";
import { NormalizedSkillClaimItem, UnresolvedSkillClaimItem } from "@/lib/api/types";
import { batchConfirmClaims } from "@/lib/api/candidates";

interface ClaimReviewProps {
  candidateId: string;
  extractedSkills: NormalizedSkillClaimItem[];
  unresolvedSkills: UnresolvedSkillClaimItem[];
  onClaimsConfirmed: (confirmedSlugs: string[]) => void;
}

export function ClaimReview({
  candidateId,
  extractedSkills,
  unresolvedSkills,
  onClaimsConfirmed,
}: ClaimReviewProps) {
  const [skillStatuses, setSkillStatuses] = useState<Record<string, "confirm" | "reject">>(() => {
    const initial: Record<string, "confirm" | "reject"> = {};
    extractedSkills.forEach((s) => {
      initial[s.skill_slug] = "confirm";
    });
    return initial;
  });
  const [customSkill, setCustomSkill] = useState("");
  const [additionalConfirmed, setAdditionalConfirmed] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleStatus = (slug: string) => {
    setSkillStatuses((prev) => ({
      ...prev,
      [slug]: prev[slug] === "confirm" ? "reject" : "confirm",
    }));
  };

  const handleAddCustom = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = customSkill.trim().toLowerCase().replace(/\s+/g, "-");
    if (!clean) return;
    if (!additionalConfirmed.includes(clean)) {
      setAdditionalConfirmed((prev) => [...prev, clean]);
    }
    setCustomSkill("");
  };

  const handleSaveAndContinue = async () => {
    try {
      setLoading(true);
      setError(null);

      const confirmedSlugs: string[] = [];
      const rejectedSlugs: string[] = [];

      Object.entries(skillStatuses).forEach(([slug, status]) => {
        if (status === "confirm") {
          confirmedSlugs.push(slug);
        } else {
          rejectedSlugs.push(slug);
        }
      });

      additionalConfirmed.forEach((slug) => {
        if (!confirmedSlugs.includes(slug)) {
          confirmedSlugs.push(slug);
        }
      });

      await batchConfirmClaims(candidateId, {
        confirmed_skill_slugs: confirmedSlugs,
        rejected_skill_slugs: rejectedSlugs,
      });

      setLoading(false);
      onClaimsConfirmed(confirmedSlugs);
    } catch (err: any) {
      setLoading(false);
      setError(err.message || "Failed to confirm claims. Please try again.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Review Extracted Skills
        </h2>
        <p className="text-sm text-slate-400 mt-1 max-w-lg mx-auto">
          We found these skills mentioned in your resume. Confirm what you actually know,
          or reject skills you don't want evaluated.
        </p>
      </div>

      {/* Product Invariant Callout */}
      <div className="p-3.5 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-start gap-2.5 text-xs text-blue-300">
        <Info className="h-4 w-4 shrink-0 text-blue-400 mt-0.5" />
        <div>
          <strong>Important:</strong> A confirmed skill is only a candidate claim. It does not give you proficiency points until you attach verifiable evidence in the next step.
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Technical Skill Claims ({extractedSkills.length})
          </span>
          <span className="text-xs text-slate-500">Click toggle to confirm or reject</span>
        </div>

        {/* Skills Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {extractedSkills.map((skill) => {
            const isConfirmed = skillStatuses[skill.skill_slug] === "confirm";
            return (
              <div
                key={skill.skill_slug}
                onClick={() => toggleStatus(skill.skill_slug)}
                className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-all duration-200 ${
                  isConfirmed
                    ? "bg-blue-950/30 border-blue-500/40 text-white"
                    : "bg-slate-900/30 border-slate-800 text-slate-500 line-through"
                }`}
              >
                <div className="flex flex-col truncate pr-2">
                  <span className="font-medium text-sm text-slate-200 truncate">
                    {skill.canonical_name}
                  </span>
                  <span className="text-[10px] text-slate-400 flex items-center gap-1 font-mono">
                    <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
                    Unconfirmed Claim
                  </span>
                </div>

                <div
                  className={`h-7 w-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 transition-colors ${
                    isConfirmed
                      ? "bg-blue-600 text-white"
                      : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {isConfirmed ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                </div>
              </div>
            );
          })}
        </div>

        {/* Additional manually added skills */}
        {additionalConfirmed.length > 0 && (
          <div className="pt-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Manually Added Claims
            </span>
            <div className="flex flex-wrap gap-2">
              {additionalConfirmed.map((slug) => (
                <span
                  key={slug}
                  className="px-2.5 py-1 bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 rounded-lg text-xs font-medium flex items-center gap-1.5"
                >
                  {slug}
                  <button
                    type="button"
                    onClick={() => setAdditionalConfirmed((prev) => prev.filter((s) => s !== slug))}
                    className="text-indigo-400 hover:text-rose-400"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Add custom skill input */}
        <form onSubmit={handleAddCustom} className="flex gap-2 pt-2">
          <input
            type="text"
            placeholder="Add missing skill (e.g. docker, redis)..."
            value={customSkill}
            onChange={(e) => setCustomSkill(e.target.value)}
            className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-medium flex items-center gap-1 transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            Add
          </button>
        </form>

        {/* Unresolved Tokens Callout */}
        {unresolvedSkills.length > 0 && (
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-300/90 flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
            <div>
              <strong>Unresolved tokens from resume:</strong>{" "}
              {unresolvedSkills.map((u) => u.raw_text).join(", ")}. (Preserved for review, not counted toward taxonomy).
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
            {error}
          </div>
        )}

        <button
          type="button"
          disabled={loading}
          onClick={handleSaveAndContinue}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/25 transition-all active:scale-[0.99]"
        >
          {loading ? "Saving Confirmed Claims..." : "Confirm Claims & Proceed to Education"}
        </button>
      </div>
    </div>
  );
}
