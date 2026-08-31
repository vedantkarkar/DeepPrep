import React from "react";
import Link from "next/link";
import { 
  ArrowRight, 
  ShieldCheck, 
  Target, 
  Layers, 
  CheckCircle2, 
  Sparkles, 
  Building2, 
  MapPin, 
  Terminal,
  Cpu
} from "lucide-react";

export default function HomePage() {
  const representativeJobs = [
    {
      company: "Persistent Systems",
      title: "Software Development Engineer (SDE-1)",
      location: "Pune, MH",
      skills: ["Java", "Spring Boot", "SQL", "DSA", "DBMS"],
      role: "Backend Engineer",
    },
    {
      company: "Razorpay",
      title: "Junior Backend Engineer",
      location: "Pune / Remote",
      skills: ["Python", "FastAPI", "PostgreSQL", "REST APIs"],
      role: "Backend Engineer",
    },
    {
      company: "Fractal Analytics",
      title: "Associate AI/ML Engineer",
      location: "Mumbai, MH",
      skills: ["Python", "PyTorch", "Machine Learning", "SQL"],
      role: "AI/ML Engineer",
    },
  ];

  return (
    <div className="space-y-16 py-6 sm:py-12">
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto space-y-6 relative">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-cyan-400 font-mono shadow-inner">
          <Sparkles className="h-3.5 w-3.5" />
          Evidence-Backed Engineering Assessment
        </div>

        <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight leading-[1.1]">
          Stop guessing if you're{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400">
            job-ready.
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Measure your preparation against the actual requirements of the role you want.
          DeepPrep transforms your verified evidence into a deterministic, explainable readiness report.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-4">
          <Link
            href="/onboarding"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 shadow-xl shadow-blue-500/25 flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
          >
            <span>Check My Readiness</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/jobs"
            className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-semibold text-sm text-slate-300 bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 transition-colors flex items-center justify-center gap-2"
          >
            <span>Explore Target Roles</span>
          </Link>
        </div>

        <p className="text-[11px] text-slate-500 font-mono pt-1">
          ✓ No hiring probability guesswork · ✓ 100% deterministic & traceable · ✓ Offline capable
        </p>
      </div>

      {/* 4 Pillars Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
        <div className="glass-panel p-5 rounded-2xl space-y-2.5 glass-panel-hover transition-all">
          <div className="h-10 w-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
            <Target className="h-5 w-5" />
          </div>
          <h3 className="font-bold text-white text-sm">Role-Specific Standards</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Readiness is never generic. It is evaluated against real employer competency vectors and level expectations.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-2.5 glass-panel-hover transition-all">
          <div className="h-10 w-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <h3 className="font-bold text-white text-sm">Evidence Over Claims</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Resume mentions are claims. DeepPrep estimates capability only from practical code, platforms, and verified coursework.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-2.5 glass-panel-hover transition-all">
          <div className="h-10 w-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
            <Cpu className="h-5 w-5" />
          </div>
          <h3 className="font-bold text-white text-sm">Deterministic Math</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            No probabilistic hallucination. Every score contribution is computed via bounded mathematical formulas.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl space-y-2.5 glass-panel-hover transition-all">
          <div className="h-10 w-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
            <Layers className="h-5 w-5" />
          </div>
          <h3 className="font-bold text-white text-sm">Eligibility Gating</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Degree, branch, and graduation year requirements are checked independently from technical scoring.
          </p>
        </div>
      </div>

      {/* Target Roles Preview */}
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Featured Maharashtra Openings
            </h2>
            <p className="text-xs text-slate-400">
              Evaluated against real employer requirements in Pune and Mumbai.
            </p>
          </div>
          <Link href="/jobs" className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1">
            View All Jobs <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {representativeJobs.map((j) => (
            <div key={j.company} className="glass-panel p-5 rounded-2xl flex flex-col justify-between space-y-4">
              <div className="space-y-1.5">
                <span className="text-[10px] font-mono uppercase text-cyan-400 font-semibold">{j.role}</span>
                <h3 className="font-bold text-white text-sm">{j.title}</h3>
                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1"><Building2 className="h-3 w-3" /> {j.company}</span>
                  <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> {j.location}</span>
                </div>
              </div>

              <div className="space-y-3 pt-2 border-t border-white/[0.04]">
                <div className="flex flex-wrap gap-1">
                  {j.skills.map((s) => (
                    <span key={s} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-medium">
                      {s}
                    </span>
                  ))}
                </div>
                <Link
                  href="/onboarding"
                  className="block text-center py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 rounded-xl text-xs font-semibold transition-colors"
                >
                  Evaluate for this Role
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
