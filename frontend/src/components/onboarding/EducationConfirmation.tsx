"use client";

import React, { useState } from "react";
import { GraduationCap, CheckCircle, AlertCircle, Building2, Calendar, BookOpen } from "lucide-react";
import { confirmEducation } from "@/lib/api/candidates";
import { ExtractedEducationClaim, Candidate } from "@/lib/api/types";

interface EducationConfirmationProps {
  candidateId: string;
  extractedEducation?: ExtractedEducationClaim;
  onEducationConfirmed: (candidate: Candidate) => void;
}

export function EducationConfirmation({
  candidateId,
  extractedEducation,
  onEducationConfirmed,
}: EducationConfirmationProps) {
  const [degree, setDegree] = useState(extractedEducation?.degree || "B.Tech");
  const [branch, setBranch] = useState(extractedEducation?.branch || "Computer Science and Engineering");
  const [institution, setInstitution] = useState(extractedEducation?.institution || "COEP Technological University");
  const [gradYear, setGradYear] = useState<number>(extractedEducation?.graduation_year || 2025);
  const [studentStatus, setStudentStatus] = useState(extractedEducation?.student_status || "final_year");
  const [confirmed, setConfirmed] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!degree.trim() || !branch.trim()) {
      setError("Please specify your degree and branch.");
      return;
    }
    if (gradYear < 1980 || gradYear > 2035) {
      setError("Please enter a valid graduation year.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const updated = await confirmEducation(candidateId, {
        degree: degree.trim(),
        branch: branch.trim(),
        institution: institution.trim() || "University",
        graduation_year: gradYear,
        student_status: studentStatus,
        confirmed,
      });
      setLoading(false);
      onEducationConfirmed(updated);
    } catch (err: any) {
      setLoading(false);
      setError(err.message || "Failed to confirm education.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Confirm Your Education
        </h2>
        <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
          Role eligibility checks compare your degree, branch, and graduation cutoff.
          Verify this data before continuing.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-6 sm:p-8 space-y-5">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
              <GraduationCap className="h-3.5 w-3.5 text-blue-400" />
              Degree Program
            </label>
            <select
              value={degree}
              onChange={(e) => setDegree(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
            >
              <option value="B.Tech">B.Tech (Bachelor of Technology)</option>
              <option value="B.E.">B.E. (Bachelor of Engineering)</option>
              <option value="MCA">MCA (Master of Computer Applications)</option>
              <option value="M.Tech">M.Tech (Master of Technology)</option>
              <option value="B.Sc CS">B.Sc Computer Science</option>
              <option value="BCA">BCA (Bachelor of Computer Applications)</option>
              <option value="Other">Other Degree</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
              <BookOpen className="h-3.5 w-3.5 text-blue-400" />
              Branch / Discipline
            </label>
            <input
              type="text"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="e.g. Computer Science and Engineering"
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <Building2 className="h-3.5 w-3.5 text-blue-400" />
                College / Institution
              </label>
              <input
                type="text"
                value={institution}
                onChange={(e) => setInstitution(e.target.value)}
                placeholder="e.g. COEP Technological University"
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-blue-400" />
                Graduation Year
              </label>
              <input
                type="number"
                value={gradYear}
                onChange={(e) => setGradYear(parseInt(e.target.value) || 2025)}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Confirmation Toggle */}
        <div className="p-3.5 bg-slate-900/80 border border-slate-700/60 rounded-xl flex items-center justify-between">
          <div className="pr-4">
            <p className="text-xs font-medium text-slate-200">Confirm accuracy of education data</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Required for eligible application status</p>
          </div>
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="h-5 w-5 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-0 cursor-pointer"
          />
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/25 transition-all active:scale-[0.99]"
        >
          {loading ? "Saving Education..." : "Confirm Education & Proceed to Evidence"}
        </button>
      </form>
    </div>
  );
}
