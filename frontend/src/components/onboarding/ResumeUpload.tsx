"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles, User } from "lucide-react";
import { extractResume } from "@/lib/api/resumes";
import { createCandidate } from "@/lib/api/candidates";
import { ResumeExtractionResponse, Candidate } from "@/lib/api/types";

interface ResumeUploadProps {
  onExtractionComplete: (candidate: Candidate, extraction: ResumeExtractionResponse) => void;
}

export function ResumeUpload({ onExtractionComplete }: ResumeUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [candidateName, setCandidateName] = useState("");
  const [email, setEmail] = useState("");
  const [locationCity, setLocationCity] = useState("Pune");
  const [isDragging, setIsDragging] = useState(false);
  const [loadingStage, setLoadingStage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelection = (selectedFile: File) => {
    const ext = selectedFile.name.split(".").pop()?.toLowerCase();
    if (!ext || !["pdf", "docx", "txt"].includes(ext)) {
      setError("Please upload a valid PDF, DOCX, or TXT file.");
      return;
    }
    if (selectedFile.size > 5 * 1024 * 1024) {
      setError("File size exceeds 5MB limit.");
      return;
    }
    setError(null);
    setFile(selectedFile);
  };

  const handleUploadAndAnalyze = async () => {
    if (!file) {
      setError("Please select a resume file first.");
      return;
    }

    try {
      setError(null);
      setLoadingStage("Reading document & verifying file structure...");
      await new Promise((r) => setTimeout(r, 400));

      setLoadingStage("Extracting candidate claims, education & projects...");
      const extraction = await extractResume(file);

      setLoadingStage("Creating candidate profile...");
      const nameToUse = candidateName.trim() || extraction.candidate_name || "Engineering Candidate";
      const emailToUse = email.trim() || extraction.email || "candidate@example.com";

      const candidate = await createCandidate({
        full_name: nameToUse,
        email: emailToUse,
        location_city: locationCity,
        location_state: "Maharashtra",
      });

      setLoadingStage(null);
      onExtractionComplete(candidate, extraction);
    } catch (err: any) {
      setLoadingStage(null);
      setError(err.message || "Resume extraction failed. Please try again.");
    }
  };

  const handleLoadDemoResume = async () => {
    try {
      setError(null);
      setLoadingStage("Loading demo resume fixture (Aarav Deshmukh)...");
      const resp = await fetch("/demo_resume.txt");
      let textContent = "";
      if (resp.ok) {
        textContent = await resp.text();
      } else {
        textContent = `AARAV DESHMUKH\naarav.deshmukh@example.com | Pune, Maharashtra\nEDUCATION:\nB.Tech Computer Science and Engineering, COEP Pune (2025)\nTECHNICAL SKILLS:\nC++, Java, Python, PostgreSQL, Spring Boot, DSA, SQL\nPROJECTS:\nFastAPI Placement Portal with PostgreSQL`;
      }
      const demoFile = new File([textContent], "demo_resume.txt", { type: "text/plain" });
      setFile(demoFile);
      setCandidateName("Aarav Deshmukh");
      setEmail("aarav.deshmukh@example.com");
      setLocationCity("Pune");
      setLoadingStage(null);
    } catch (err) {
      setError("Failed to load demo resume fixture.");
      setLoadingStage(null);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Upload Your Resume
        </h2>
        <p className="text-sm text-slate-400 mt-1.5 max-w-md mx-auto">
          DeepPrep extracts your claimed technical skills and background.{" "}
          <strong className="text-cyan-400 font-medium">
            You review everything before it affects your profile.
          </strong>
        </p>
      </div>

      <div className="glass-panel rounded-2xl p-6 sm:p-8 space-y-6">
        {/* Candidate Identity Details */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-4 border-b border-white/[0.06]">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Your Full Name
            </label>
            <input
              type="text"
              placeholder="e.g. Aarav Deshmukh"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Location / City
            </label>
            <input
              type="text"
              placeholder="e.g. Pune, Maharashtra"
              value={locationCity}
              onChange={(e) => setLocationCity(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300 ${
            isDragging
              ? "border-cyan-400 bg-cyan-500/10 scale-[1.01]"
              : file
              ? "border-emerald-500/50 bg-emerald-500/5"
              : "border-slate-700/80 hover:border-slate-500 bg-slate-900/40 hover:bg-slate-900/70"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => e.target.files?.[0] && handleFileSelection(e.target.files[0])}
            className="hidden"
          />

          {file ? (
            <div className="flex flex-col items-center">
              <div className="h-12 w-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-3">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <p className="font-semibold text-white text-base">{file.name}</p>
              <p className="text-xs text-slate-400 mt-1">
                {(file.size / 1024).toFixed(1)} KB · Click or drag to replace
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="h-12 w-12 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center mb-3">
                <UploadCloud className="h-6 w-6" />
              </div>
              <p className="font-semibold text-slate-200 text-sm">
                Click to browse or drop your resume here
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Supported formats: PDF, DOCX, TXT (Max 5MB)
              </p>
            </div>
          )}
        </div>

        {/* Demo Shortcut */}
        <div className="flex items-center justify-between pt-2">
          <button
            type="button"
            onClick={handleLoadDemoResume}
            className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 font-medium transition-colors"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Quick Demo: Load sample candidate resume
          </button>
          <span className="text-xs text-slate-500 font-mono">Offline / Mock AI supported</span>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Button */}
        <button
          type="button"
          disabled={!file || !!loadingStage}
          onClick={handleUploadAndAnalyze}
          className={`w-full py-3 px-4 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
            !file || loadingStage
              ? "bg-slate-800 text-slate-500 cursor-not-allowed"
              : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-500/25 active:scale-[0.99]"
          }`}
        >
          {loadingStage ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />
              <span>{loadingStage}</span>
            </>
          ) : (
            <>
              <FileText className="h-4 w-4" />
              <span>Extract & Review Claims</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
