"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useApp } from "@/lib/context/AppContext";
import { 
  Compass, 
  Briefcase, 
  UserCheck, 
  Menu, 
  X, 
  RotateCcw, 
  Layers,
  Sparkles
} from "lucide-react";

export function Header() {
  const pathname = usePathname();
  const { candidate, activeSessionId, clearSession } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { href: "/", label: "Home", icon: Compass },
    { href: "/jobs", label: "Target Jobs", icon: Briefcase },
    { href: "/onboarding", label: "My Assessment", icon: Layers },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.08] bg-[#080c14]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 p-[1px] shadow-lg shadow-blue-500/20">
            <div className="h-full w-full bg-[#0b1120] rounded-[11px] flex items-center justify-center group-hover:bg-transparent transition-colors duration-300">
              <Sparkles className="h-4 w-4 text-cyan-400 group-hover:text-white" />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
              DeepPrep
            </span>
            <span className="text-[10px] uppercase font-mono tracking-widest text-cyan-400/90 -mt-1">
              Role Readiness
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Icon className="h-4 w-4" />
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Candidate / Session Status Pill */}
        <div className="hidden md:flex items-center gap-3">
          {candidate ? (
            <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-700/60 rounded-full py-1 pl-3 pr-2 text-xs">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-slate-300 font-medium truncate max-w-[140px]">
                {candidate.full_name}
              </span>
              <button
                onClick={clearSession}
                title="Reset active candidate session"
                className="p-1 text-slate-500 hover:text-rose-400 rounded-full hover:bg-slate-800 transition-colors"
              >
                <RotateCcw className="h-3 w-3" />
              </button>
            </div>
          ) : (
            <Link
              href="/onboarding"
              className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 rounded-lg shadow-md shadow-blue-600/20 transition-all active:scale-[0.98]"
            >
              <UserCheck className="h-3.5 w-3.5" />
              Start Assessment
            </Link>
          )}
        </div>

        {/* Mobile menu button */}
        <div className="flex md:hidden">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu drop */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-white/[0.08] bg-[#090d16]/95 px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-base font-medium ${
                  isActive
                    ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                    : "text-slate-300 hover:bg-slate-800/50"
                }`}
              >
                <Icon className="h-5 w-5" />
                {link.label}
              </Link>
            );
          })}
          {candidate && (
            <div className="pt-2 flex items-center justify-between border-t border-slate-800 text-xs text-slate-400 px-3">
              <span>Active Candidate: <strong className="text-slate-200">{candidate.full_name}</strong></span>
              <button
                onClick={() => {
                  clearSession();
                  setMobileMenuOpen(false);
                }}
                className="text-rose-400 underline ml-2"
              >
                Reset
              </button>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
