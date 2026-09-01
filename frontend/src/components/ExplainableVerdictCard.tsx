import React from 'react';
import {
  AlertTriangle,
  ClipboardList,
  CheckCircle2,
  Stethoscope,
  Shield
} from 'lucide-react';
import type { AnalysisResult, RoleView } from '../types';

interface ExplainableVerdictCardProps {
  result: AnalysisResult;
  role: RoleView;
}

export const ExplainableVerdictCard: React.FC<ExplainableVerdictCardProps> = ({
  result,
  role
}) => {
  const isMedical = role === 'MEDICAL_OFFICER';

  return (
    <div className="space-y-4">
      {/* 1. Primary AI Verdict & Narrative */}
      <div className="p-6 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm">
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            {isMedical ? (
              <Stethoscope className="w-5 h-5 text-cyan-400" />
            ) : (
              <Shield className="w-5 h-5 text-amber-400" />
            )}
            <h3 className="text-base font-semibold text-white">
              {isMedical ? 'Medical Officer Physiological Evaluation' : 'Commander Operational Welfare Briefing'}
            </h3>
          </div>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
            {result.personnel_code}
          </span>
        </div>

        <p className="text-sm leading-relaxed text-slate-300">
          {isMedical ? result.clinical_explanation : result.commander_summary}
        </p>

        {/* Key Risk Drivers */}
        {result.key_drivers && result.key_drivers.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-800">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>Primary Risk Drivers</span>
            </h4>
            <div className="space-y-1.5">
              {result.key_drivers.map((driver, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-2 text-xs text-slate-200 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                  <span>{driver}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 2. Actionable Directives & Recommendations */}
      <div className="p-6 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm">
        <div className="flex items-center gap-2 mb-3">
          <ClipboardList className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-semibold text-white">
            {isMedical ? 'Clinical Recommendations & Protocol' : 'Tactical Duty Directives'}
          </h3>
        </div>

        <ul className="space-y-2">
          {result.recommendations && result.recommendations.map((rec, idx) => (
            <li
              key={idx}
              className="flex items-start gap-2.5 text-xs text-slate-300 bg-indigo-950/20 p-2.5 rounded-lg border border-indigo-900/30"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{rec}</span>
            </li>
          ))}
        </ul>

        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <span>Standard CAPF Health & Vigilance Directive</span>
          <span className="font-mono text-slate-300">Auth: Medical HQ / Ops Wing</span>
        </div>
      </div>
    </div>
  );
};
