"use client";

import React, { useState } from "react";
import { Plus, CheckCircle2, Globe, GitBranch, Code2, Award, BookOpen, ExternalLink, X, ShieldCheck } from "lucide-react";
import { submitEvidence } from "@/lib/api/evidence";
import { CandidateEvidence } from "@/lib/api/types";

interface EvidenceCollectionProps {
  candidateId: string;
  confirmedSkillSlugs: string[];
  onProceedToJobs: () => void;
}

export function EvidenceCollection({
  candidateId,
  confirmedSkillSlugs,
  onProceedToJobs,
}: EvidenceCollectionProps) {
  const [evidenceList, setEvidenceList] = useState<CandidateEvidence[]>([]);
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [evidenceType, setEvidenceType] = useState<string>("project");
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [description, setDescription] = useState("");
  const [commitsOrSolved, setCommitsOrSolved] = useState<number>(20);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const evidenceCountBySkill = evidenceList.reduce<Record<string, number>>((acc, ev) => {
    acc[ev.skill_slug] = (acc[ev.skill_slug] || 0) + 1;
    return acc;
  }, {});

  const handleOpenAddModal = (slug: string) => {
    setSelectedSkill(slug);
    setTitle(`${slug.toUpperCase()} Project / Verification`);
    setUrl("");
    setDescription("");
    setError(null);
  };

  const handleSaveEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSkill || !title.trim()) return;

    try {
      setSubmitting(true);
      setError(null);

      const metadata: Record<string, any> = {};
      if (evidenceType === "assessment") {
        metadata.total_solved = commitsOrSolved;
        metadata.contest_rating = 1600;
      } else if (evidenceType === "project" || evidenceType === "github") {
        metadata.commits = commitsOrSolved;
      }

      const created = await submitEvidence(candidateId, {
        skill_slug: selectedSkill,
        evidence_type: evidenceType,
        title: title.trim(),
        description: description.trim() || undefined,
        url: url.trim() || undefined,
        metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
        date_obtained: new Date().toISOString().split("T")[0],
      });

      setEvidenceList((prev) => [...prev, created]);
      setSubmitting(false);
      setSelectedSkill(null);
    } catch (err: any) {
      setSubmitting(false);
      setError(err.message || "Failed to submit evidence.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Now Prove What You Know
        </h2>
        <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
          Your resume tells us what you claim.{" "}
          <strong className="text-cyan-400 font-medium">Your evidence helps us estimate capability.</strong>
        </p>
      </div>

      <div className="glass-panel rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Confirmed Skills Requiring Evidence ({confirmedSkillSlugs.length})
          </span>
          <span className="text-xs text-emerald-400 font-mono">
            {evidenceList.length} evidence record(s) added
          </span>
        </div>

        <div className="space-y-3">
          {confirmedSkillSlugs.map((slug) => {
            const count = evidenceCountBySkill[slug] || 0;
            const skillEvidences = evidenceList.filter((e) => e.skill_slug === slug);

            return (
              <div
                key={slug}
                className="p-4 rounded-xl border border-slate-800/90 bg-slate-900/50 flex flex-col gap-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-white capitalize">
                      {slug.replace("-", " ")}
                    </span>
                    {count > 0 ? (
                      <span className="px-2 py-0.5 bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 rounded-full text-[11px] font-medium flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" />
                        {count} Evidence Attached
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-full text-[11px]">
                        No evidence yet (Level 0)
                      </span>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={() => handleOpenAddModal(slug)}
                    className="px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 rounded-lg text-xs font-medium flex items-center gap-1 transition-colors"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Add Evidence
                  </button>
                </div>

                {skillEvidences.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    {skillEvidences.map((ev) => (
                      <div
                        key={ev.id}
                        className="text-xs bg-slate-800/60 rounded-lg p-2 flex items-center justify-between text-slate-300"
                      >
                        <div className="flex items-center gap-2 truncate">
                          <span className="font-mono text-[10px] uppercase bg-slate-700 px-1.5 py-0.5 rounded text-slate-300">
                            {ev.evidence_type}
                          </span>
                          <span className="truncate">{ev.title}</span>
                        </div>
                        {ev.url && (
                          <a
                            href={ev.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-cyan-400 hover:text-cyan-300 p-1"
                          >
                            <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <button
          type="button"
          onClick={onProceedToJobs}
          className="w-full py-3.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/25 transition-all active:scale-[0.99]"
        >
          Proceed to Target Job Selection →
        </button>
      </div>

      {selectedSkill && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel max-w-lg w-full rounded-2xl p-6 space-y-4 border border-slate-700">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
              <h3 className="font-bold text-white text-base capitalize">
                Add Evidence for {selectedSkill.replace("-", " ")}
              </h3>
              <button
                onClick={() => setSelectedSkill(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSaveEvidence} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                  Evidence Type
                </label>
                <select
                  value={evidenceType}
                  onChange={(e) => setEvidenceType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                >
                  <option value="project">Practical Project</option>
                  <option value="github">GitHub Repository</option>
                  <option value="assessment">Platform Assessment (LeetCode / HackerRank)</option>
                  <option value="academic_coursework">University Coursework</option>
                  <option value="internship">Internship Experience</option>
                  <option value="course">Online Video Course / Certificate</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Placement Portal REST API"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                  Repository / Verification URL (Optional)
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://github.com/your-username/project"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                />
              </div>

              {(evidenceType === "project" || evidenceType === "assessment") && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                    {evidenceType === "assessment" ? "Problems Solved" : "Commits / Scope Metric"}
                  </label>
                  <input
                    type="number"
                    value={commitsOrSolved}
                    onChange={(e) => setCommitsOrSolved(parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
              )}

              {error && (
                <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-300 text-xs">
                  {error}
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedSkill(null)}
                  className="flex-1 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold"
                >
                  {submitting ? "Saving..." : "Save Evidence"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
