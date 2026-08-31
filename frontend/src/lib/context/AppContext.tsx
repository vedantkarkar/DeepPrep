"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { Candidate, Job, PreparationSession, ReadinessReport } from "@/lib/api/types";
import { getCandidate } from "@/lib/api/candidates";

interface AppContextType {
  candidate: Candidate | null;
  candidateId: string | null;
  setCandidate: (candidate: Candidate | null) => void;
  activeSessionId: string | null;
  setActiveSessionId: (sessionId: string | null) => void;
  selectedJob: Job | null;
  setSelectedJob: (job: Job | null) => void;
  activeReport: ReadinessReport | null;
  setActiveReport: (report: ReadinessReport | null) => void;
  clearSession: () => void;
  loading: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [candidate, setCandidateState] = useState<Candidate | null>(null);
  const [candidateId, setCandidateId] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionIdState] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [activeReport, setActiveReport] = useState<ReadinessReport | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize from localStorage on mount
  useEffect(() => {
    try {
      const savedCandidateId = localStorage.getItem("deepprep_candidate_id");
      const savedSessionId = localStorage.getItem("deepprep_session_id");

      if (savedCandidateId) {
        setCandidateId(savedCandidateId);
        getCandidate(savedCandidateId)
          .then((c) => setCandidateState(c))
          .catch(() => {
            localStorage.removeItem("deepprep_candidate_id");
            setCandidateId(null);
          });
      }
      if (savedSessionId) {
        setActiveSessionIdState(savedSessionId);
      }
    } catch (e) {
      console.error("Failed to restore session from localStorage", e);
    } finally {
      setLoading(false);
    }
  }, []);

  const setCandidate = (c: Candidate | null) => {
    setCandidateState(c);
    if (c) {
      setCandidateId(c.id);
      localStorage.setItem("deepprep_candidate_id", c.id);
    } else {
      setCandidateId(null);
      localStorage.removeItem("deepprep_candidate_id");
    }
  };

  const setActiveSessionId = (id: string | null) => {
    setActiveSessionIdState(id);
    if (id) {
      localStorage.setItem("deepprep_session_id", id);
    } else {
      localStorage.removeItem("deepprep_session_id");
    }
  };

  const clearSession = () => {
    setCandidateState(null);
    setCandidateId(null);
    setActiveSessionIdState(null);
    setSelectedJob(null);
    setActiveReport(null);
    localStorage.removeItem("deepprep_candidate_id");
    localStorage.removeItem("deepprep_session_id");
  };

  return (
    <AppContext.Provider
      value={{
        candidate,
        candidateId,
        setCandidate,
        activeSessionId,
        setActiveSessionId,
        selectedJob,
        setSelectedJob,
        activeReport,
        setActiveReport,
        clearSession,
        loading,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
