import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';

interface RiskGaugeProps {
  score: number;
  level: 'LOW' | 'MODERATE' | 'HIGH';
  verdict: string;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, level, verdict }) => {
  // Clamped score between 0 and 100
  const normalizedScore = Math.max(0, Math.min(100, score));
  
  // Radius = 50. Semi-circle perimeter = Math.PI * 50 = 157.08
  const strokeDashoffset = 157.08 - (157.08 * normalizedScore) / 100;

  const colorConfig = {
    LOW: {
      color: '#10b981', // emerald
      bgBadge: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80',
      icon: ShieldCheck,
      desc: 'Operational Ready / Low Risk Band'
    },
    MODERATE: {
      color: '#f59e0b', // amber
      bgBadge: 'bg-amber-950/80 text-amber-300 border-amber-800/80',
      icon: AlertTriangle,
      desc: 'Elevated Fatigue / Moderate Risk Band'
    },
    HIGH: {
      color: '#ef4444', // red
      bgBadge: 'bg-rose-950/80 text-rose-300 border-rose-800/80',
      icon: ShieldAlert,
      desc: 'Critical Stress & Fatigue / High Risk Band'
    }
  }[level] || {
    color: '#3b82f6',
    bgBadge: 'bg-blue-950 text-blue-300 border-blue-800',
    icon: ShieldCheck,
    desc: 'Assessing...'
  };

  const Icon = colorConfig.icon;

  return (
    <div className="flex flex-col items-center justify-between p-6 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm relative overflow-hidden h-full">
      <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-full blur-2xl pointer-events-none" />
      
      <div className="text-xs uppercase tracking-wider font-semibold text-slate-400 mb-1">
        Composite Fatigue & Stress Risk
      </div>

      <div className="relative w-56 h-32 flex items-center justify-center mt-2">
        {/* SVG Top Half Semi-Circle */}
        <svg className="w-56 h-32" viewBox="0 0 140 85">
          {/* Background Arc: Semi-circle path from (15, 75) to (125, 75) */}
          <path
            d="M 20 75 A 50 50 0 0 1 120 75"
            fill="none"
            stroke="#1e293b"
            strokeWidth="12"
            strokeLinecap="round"
          />
          {/* Active Colored Arc */}
          <path
            d="M 20 75 A 50 50 0 0 1 120 75"
            fill="none"
            stroke={colorConfig.color}
            strokeWidth="12"
            strokeDasharray="157.08"
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Score in center */}
        <div className="absolute bottom-1 flex flex-col items-center">
          <span className="text-4xl font-black tracking-tight text-white font-mono leading-none">
            {score.toFixed(1)}
          </span>
          <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider mt-1">
            out of 100
          </span>
        </div>
      </div>

      {/* Verdict & Badge */}
      <div className="mt-3 flex flex-col items-center text-center gap-2 w-full">
        <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${colorConfig.bgBadge}`}>
          <Icon className="w-3.5 h-3.5" />
          <span>{level} RISK ({colorConfig.desc})</span>
        </div>

        <div className="text-sm font-semibold text-slate-200 line-clamp-2 px-2">
          {verdict}
        </div>
      </div>

      {/* Scale guide */}
      <div className="w-full mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
        <span className="text-emerald-400 font-medium">0–30: Low</span>
        <span className="text-amber-400 font-medium">31–60: Mod</span>
        <span className="text-rose-400 font-medium">61–100: High</span>
      </div>
    </div>
  );
};
