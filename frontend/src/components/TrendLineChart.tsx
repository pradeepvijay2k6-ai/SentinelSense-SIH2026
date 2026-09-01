import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { TrendingUp } from 'lucide-react';
import type { AnalysisResult } from '../types';

interface TrendLineChartProps {
  history: AnalysisResult[];
}

export const TrendLineChart: React.FC<TrendLineChartProps> = ({ history }) => {
  if (!history || history.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 bg-slate-900/60 border border-slate-800 rounded-2xl">
        No past sessions recorded yet for this officer.
      </div>
    );
  }

  const chartData = history.map((h, idx) => {
    return {
      sessionIdx: `Session ${idx + 1}`,
      riskScore: h.risk_score,
      sleepEff: h.sleep_efficiency,
      rmssd: h.hrv_rmssd,
    };
  });

  return (
    <div className="p-6 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between gap-4 mb-4">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-400" />
            <span>Longitudinal Fatigue & Autonomic Trends</span>
          </h3>
          <p className="text-xs text-slate-400">
            Monitoring chronic stress accumulation, sleep quality, and vagal recovery across duty cycles
          </p>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="sessionIdx" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={[0, 100]} />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs space-y-1">
                      <div className="font-semibold text-slate-200">{label}</div>
                      {payload.map((entry, idx) => (
                        <div key={idx} className="flex items-center justify-between gap-4" style={{ color: entry.color }}>
                          <span>{entry.name}:</span>
                          <span className="font-bold font-mono">{entry.value}</span>
                        </div>
                      ))}
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
            
            <Line
              type="monotone"
              dataKey="riskScore"
              name="Risk Score (0-100)"
              stroke="#ef4444"
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#ef4444' }}
            />
            <Line
              type="monotone"
              dataKey="sleepEff"
              name="Sleep Efficiency (%)"
              stroke="#38bdf8"
              strokeWidth={2}
              dot={{ r: 3, fill: '#38bdf8' }}
            />
            <Line
              type="monotone"
              dataKey="rmssd"
              name="HRV RMSSD (ms)"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 3, fill: '#10b981' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
