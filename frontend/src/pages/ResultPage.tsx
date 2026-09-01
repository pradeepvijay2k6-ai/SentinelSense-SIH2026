import React from 'react';
import {
  FileText,
  Calendar,
  Clock,
  ArrowLeft,
  EyeOff
} from 'lucide-react';
import type { AnalysisResult, RoleView } from '../types';
import { RiskGauge } from '../components/RiskGauge';
import { MetricsGrid } from '../components/MetricsGrid';
import { HypnogramChart } from '../components/HypnogramChart';
import { SignalWaveformViewer } from '../components/SignalWaveformViewer';
import { ExplainableVerdictCard } from '../components/ExplainableVerdictCard';

interface ResultPageProps {
  result: AnalysisResult;
  role: RoleView;
  onBackToUpload: () => void;
  onViewHistory: () => void;
}

export const ResultPage: React.FC<ResultPageProps> = ({
  result,
  role,
  onBackToUpload,
  onViewHistory
}) => {
  const isMedical = role === 'MEDICAL_OFFICER';

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Top Banner / Actions */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToUpload}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 transition-colors"
            title="Back to upload"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>

          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-xl font-bold text-white font-mono">{result.personnel_code}</span>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                result.risk_level === 'LOW'
                  ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80'
                  : result.risk_level === 'MODERATE'
                  ? 'bg-amber-950/80 text-amber-300 border-amber-800/80'
                  : 'bg-rose-950/80 text-rose-300 border-rose-800/80'
              }`}>
                {result.risk_level} RISK
              </span>
              {result.scenario_tag && (
                <span className="text-[11px] px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/60 font-mono">
                  Scenario: {result.scenario_tag}
                </span>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-1">
              <span className="flex items-center gap-1">
                <FileText className="w-3.5 h-3.5" />
                {result.filename}
              </span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                {new Date(result.uploaded_at).toLocaleString()}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                Duration: {result.total_recording_time_min.toFixed(1)} mins
              </span>
            </div>
          </div>
        </div>

        <button
          onClick={onViewHistory}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition-all shadow-sm flex items-center gap-1.5"
        >
          <Clock className="w-3.5 h-3.5 text-indigo-400" />
          <span>Officer History</span>
        </button>
      </div>

      {/* Main Row: Risk Gauge + Key Metrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4">
          <RiskGauge score={result.risk_score} level={result.risk_level} verdict={result.readiness_verdict} />
        </div>
        <div className="lg:col-span-8">
          <MetricsGrid result={result} role={role} />
        </div>
      </div>

      {/* Sleep Hypnogram Chart */}
      <HypnogramChart epochs={result.hypnogram} />

      {/* Raw Biosignal Oscilloscope (Medical Officer) OR Privacy Callout (Commander) */}
      {isMedical ? (
        <SignalWaveformViewer waveform={result.waveform_preview} />
      ) : (
        <div className="p-6 bg-slate-900/40 border border-slate-800/80 rounded-2xl flex items-center gap-4 text-slate-400">
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 shrink-0">
            <EyeOff className="w-6 h-6 text-amber-400/80" />
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-semibold text-slate-200">
              Biometric Waveform Redacted (Commander Privacy Mode)
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              In accordance with CAPF welfare data privacy principles, continuous raw ECG, EMG, and EOG signals are restricted to the Medical Officer view. Commanders receive actionable operational readiness scores and duty clearance recommendations without exposure of intimate personal biometrics.
            </p>
          </div>
        </div>
      )}

      {/* Plain-Language AI Clinical & Tactical Verdict */}
      <ExplainableVerdictCard result={result} role={role} />
    </div>
  );
};
