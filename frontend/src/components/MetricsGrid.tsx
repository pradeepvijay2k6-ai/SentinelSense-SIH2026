import React from 'react';
import {
  Bed,
  Layers,
  Sparkles,
  Heart,
  Activity,
  Wind,
  Droplet,
  Move
} from 'lucide-react';
import type { AnalysisResult, RoleView } from '../types';

interface MetricsGridProps {
  result: AnalysisResult;
  role: RoleView;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ result, role }) => {
  const isMedical = role === 'MEDICAL_OFFICER';

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3.5">
      {/* 1. Sleep Efficiency */}
      <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-xs font-medium">Sleep Efficiency</span>
          <Bed className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-white font-mono">
            {result.sleep_efficiency.toFixed(1)}%
          </span>
          <span className={`text-[11px] font-medium ${result.sleep_efficiency >= 80 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {result.sleep_efficiency >= 80 ? 'Optimal' : 'Deficit'}
          </span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          TST: {result.total_sleep_time_min.toFixed(0)} mins
        </div>
      </div>

      {/* 2. Deep Sleep N3 */}
      <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-xs font-medium">Deep Slow-Wave (N3)</span>
          <Layers className="w-4 h-4 text-blue-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-white font-mono">
            {result.deep_sleep_pct.toFixed(1)}%
          </span>
          <span className={`text-[11px] font-medium ${result.deep_sleep_pct >= 15 ? 'text-emerald-400' : 'text-amber-400'}`}>
            {result.deep_sleep_pct >= 15 ? 'Restorative' : 'Low'}
          </span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          Normal: 15–25% of sleep
        </div>
      </div>

      {/* 3. REM Sleep */}
      <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-xs font-medium">REM Stage</span>
          <Sparkles className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-white font-mono">
            {result.rem_sleep_pct.toFixed(1)}%
          </span>
          <span className="text-[11px] text-slate-400 font-medium">
            Cognitive
          </span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          Wake: {result.wake_pct.toFixed(1)}%
        </div>
      </div>

      {/* 4. Average Heart Rate */}
      <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-xs font-medium">Mean Heart Rate</span>
          <Heart className="w-4 h-4 text-rose-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-white font-mono">
            {result.avg_heart_rate.toFixed(0)}
          </span>
          <span className="text-xs text-slate-400">bpm</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {result.avg_heart_rate > 80 ? 'Sympathetic Arousal' : 'Resting Baseline'}
        </div>
      </div>

      {/* 5. HRV RMSSD (Vagal Autonomic Tone) */}
      <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-xs font-medium">HRV RMSSD</span>
          <Activity className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-white font-mono">
            {result.hrv_rmssd.toFixed(1)}
          </span>
          <span className="text-xs text-slate-400">ms</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {result.hrv_rmssd >= 45 ? (
            <span className="text-emerald-400">High Parasympathetic</span>
          ) : result.hrv_rmssd >= 25 ? (
            <span className="text-amber-400">Moderate Strain</span>
          ) : (
            <span className="text-rose-400 font-semibold">Acute Vagal Suppression</span>
          )}
        </div>
      </div>

      {/* 6. Baevsky Stress Index (Medical Officer Detailed) / Autonomic Balance */}
      <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-xs font-medium">
            {isMedical ? 'Baevsky Stress Index' : 'Autonomic Stress Index'}
          </span>
          <Wind className="w-4 h-4 text-purple-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-white font-mono">
            {result.baevsky_stress_index.toFixed(0)}
          </span>
          <span className="text-xs text-slate-400">
            {isMedical ? 'a.u.' : 'pts'}
          </span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {isMedical ? (
            <span>LF/HF: {result.hrv_lf_hf_ratio.toFixed(2)}</span>
          ) : (
            <span>{result.baevsky_stress_index > 150 ? 'High Tension' : 'Normal Equilibrium'}</span>
          )}
        </div>
      </div>

      {/* 7. SpO2 Minimum & Desaturation Dips */}
      <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-xs font-medium">Oximetry & Desaturations</span>
          <Droplet className="w-4 h-4 text-sky-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-white font-mono">
            {result.odi_dips_per_hour.toFixed(1)}
          </span>
          <span className="text-xs text-slate-400">dips/hr</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          Nadir: <span className="font-mono text-slate-200">{result.spo2_min.toFixed(0)}%</span> (Avg: {result.avg_spo2.toFixed(1)}%)
        </div>
      </div>

      {/* 8. Restlessness Index */}
      <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-xs font-medium">Motor Restlessness</span>
          <Move className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-white font-mono">
            {result.restlessness_index.toFixed(1)}%
          </span>
          <span className="text-xs text-slate-400">epochs</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {result.restlessness_index > 40 ? 'High Agitation / Shifts' : 'Quiet Sleep Posture'}
        </div>
      </div>
    </div>
  );
};
