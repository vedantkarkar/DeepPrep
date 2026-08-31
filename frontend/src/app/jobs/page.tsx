"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Briefcase, Building2, MapPin, Search, ArrowRight, Loader2, CheckCircle2 } from "lucide-react";
import { listJobs } from "@/lib/api/jobs";
import { Job } from "@/lib/api/types";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRole, setSelectedRole] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listJobs()
      .then((data) => {
        setJobs(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load jobs.");
        setLoading(false);
      });
  }, []);

  const roles = ["all", "Software Engineer", "Backend Engineer", "Full Stack Engineer", "AI/ML Engineer", "Data Engineer"];

  const filteredJobs = jobs.filter((j) => {
    const matchesSearch =
      j.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      j.company_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === "all" || j.target_role === selectedRole;
    return matchesSearch && matchesRole;
  });

  return (
    <div className="space-y-6 max-w-5xl mx-auto py-4">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Target Role Catalog
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Explore structured target roles in Maharashtra with explicit competency and eligibility requirements.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="h-4 w-4 absolute left-3.5 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search by company or role..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl pl-9 pr-3.5 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {roles.map((r) => (
            <button
              key={r}
              onClick={() => setSelectedRole(r)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium shrink-0 transition-colors ${
                selectedRole === r
                  ? "bg-blue-600 text-white"
                  : "bg-slate-900 text-slate-400 hover:text-slate-200"
              }`}
            >
              {r === "all" ? "All Roles" : r}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center p-12 text-slate-400">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-2" />
          <p className="text-sm">Loading jobs...</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Jobs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredJobs.map((job) => (
          <div key={job.id} className="glass-panel p-5 rounded-2xl flex flex-col justify-between space-y-4">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase text-cyan-400 font-semibold">{job.target_role}</span>
                <span className="px-2 py-0.5 bg-slate-800 rounded text-[10px] font-mono uppercase text-slate-400">
                  {job.source_type}
                </span>
              </div>
              <h3 className="font-bold text-white text-base">{job.title}</h3>
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5" /> {job.company_name}</span>
                <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {job.location_city || "Maharashtra"}</span>
              </div>
            </div>

            {/* Competency breakdown */}
            <div className="space-y-3 pt-2 border-t border-white/[0.04]">
              <div className="flex flex-wrap gap-1">
                {job.competency_requirements?.map((comp) => (
                  <span
                    key={comp.skill_slug}
                    className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                      comp.is_required
                        ? "bg-blue-500/10 text-blue-300 border border-blue-500/20"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {comp.canonical_name} (L{comp.required_proficiency_level})
                  </span>
                ))}
              </div>

              <Link
                href="/onboarding"
                className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all shadow-md shadow-blue-600/20"
              >
                <span>Check My Readiness for this Role</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
