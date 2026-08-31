import React from "react";
import { Check } from "lucide-react";

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
  steps: string[];
}

export function StepIndicator({ currentStep, steps }: StepIndicatorProps) {
  return (
    <div className="w-full py-4 mb-6">
      <div className="flex items-center justify-between max-w-2xl mx-auto px-2">
        {steps.map((label, index) => {
          const stepNum = index + 1;
          const isCompleted = stepNum < currentStep;
          const isCurrent = stepNum === currentStep;

          return (
            <React.Fragment key={label}>
              <div className="flex flex-col items-center group">
                <div
                  className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                    isCompleted
                      ? "bg-emerald-500 text-white shadow-md shadow-emerald-500/20"
                      : isCurrent
                      ? "bg-blue-600 text-white ring-4 ring-blue-500/20 shadow-md shadow-blue-500/30"
                      : "bg-slate-800 text-slate-400 border border-slate-700/60"
                  }`}
                >
                  {isCompleted ? <Check className="h-4 w-4 stroke-[3]" /> : stepNum}
                </div>
                <span
                  className={`text-[11px] mt-1.5 font-medium hidden sm:block ${
                    isCurrent
                      ? "text-blue-400 font-semibold"
                      : isCompleted
                      ? "text-slate-300"
                      : "text-slate-500"
                  }`}
                >
                  {label}
                </span>
              </div>

              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-[2px] mx-2 transition-colors duration-300 ${
                    stepNum < currentStep ? "bg-emerald-500/60" : "bg-slate-800"
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
