import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { Moon, AlertCircle, Zap } from 'lucide-react';
import type { HypnogramEpoch } from '../types';

interface HypnogramChartProps {
  epochs: HypnogramEpoch[];
}

const STAGE_NUMERIC_MAP: Record<string, number> = {
  W: 4,
  REM: 3,
  N1: 2,
  N2: 1,
  N3: 0
};

const STAGE_LABELS: Record<number, string> = {
  4: 'Wake (W)',
  3: 'REM',
  2: 'N1 (Light)',
  1: 'N2 (Core)',
  0: 'N3 (Deep)'
};

const STAGE_COLORS: Record<string, string> = {
  W: '#f59e0b', // Amber
  REM: '#06b6d4', // Cyan
  N1: '#818cf8', // Indigo light
  N2: '#6366f1', // Indigo
  N3: '#3b82f6'  // Deep Blue
};

export const HypnogramChart: React.FC<HypnogramChartProps> = ({ epochs }) => {
  const chartData = epochs.map((ep) => ({
    timeStr: ep.time_str,
    timeSec: ep.timestamp_sec,
    stage: ep.stage,
    stageNumeric: STAGE_NUMERIC_MAP[ep.stage] ?? 4,
    confidence: (ep.confidence * 100).toFixed(0),
    isApnea: ep.is_apnea_event,
    isMotion: ep.is_motion_event
  }));

  // Calculate quick stage breakdown
  const total = Math.max(1, epochs.length);
  const counts: Record<string, number> = { W: 0, REM: 0, N1: 0, N2: 0, N3: 0 };
  epochs.forEach((e) => {
    if (counts[e.stage] !== undefined) counts[e.stage]++;
  });

  return (
    <div className="p-6 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Moon className="w-4 h-4 text-indigo-400" />
            <span>AASM Sleep Architecture Hypnogram</span>
          </h3>
          <p className="text-xs text-slate-400">
            Continuous 30s epoch staging derived from CWT scalograms via SentinelSleepNet
          </p>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-amber-500" />
            <span className="text-slate-300">Wake ({((counts.W / total) * 100).toFixed(0)}%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-cyan-400" />
            <span className="text-slate-300">REM ({((counts.REM / total) * 100).toFixed(0)}%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-indigo-400" />
            <span className="text-slate-300">N1/N2 ({(((counts.N1 + counts.N2) / total) * 100).toFixed(0)}%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-blue-600" />
            <span className="text-slate-300">N3 Deep ({((counts.N3 / total) * 100).toFixed(0)}%)</span>
          </div>
          <div className="flex items-center gap-1.5 pl-2 border-l border-slate-700">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            <span className="text-rose-300 text-[11px]">SpO2 Dip</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="timeStr"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
            />
            <YAxis
              domain={[-0.5, 4.5]}
              ticks={[0, 1, 2, 3, 4]}
              tickFormatter={(v) => STAGE_LABELS[v] || ''}
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
              width={90}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs space-y-1.5">
                      <div className="font-semibold text-slate-200">Elapsed Time: {data.timeStr}</div>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-400">Classified Stage:</span>
                        <span
                          className="font-bold px-2 py-0.5 rounded text-xs"
                          style={{
                            backgroundColor: `${STAGE_COLORS[data.stage]}25`,
                            color: STAGE_COLORS[data.stage]
                          }}
                        >
                          {STAGE_LABELS[data.stageNumeric]}
                        </span>
                      </div>
                      <div className="text-slate-400">Model Confidence: <span className="text-white font-mono">{data.confidence}%</span></div>
                      {data.isApnea && (
                        <div className="text-rose-400 font-semibold flex items-center gap-1">
                          <AlertCircle className="w-3.5 h-3.5" /> Nocturnal Desaturation Dip (&lt;92%)
                        </div>
                      )}
                      {data.isMotion && (
                        <div className="text-amber-400 flex items-center gap-1">
                          <Zap className="w-3.5 h-3.5" /> Motor Restlessness / Posture Shift
                        </div>
                      )}
                    </div>
                  );
                }
                return null;
              }}
            />

            {/* Stepped Hypnogram Line */}
            <Line
              type="stepAfter"
              dataKey="stageNumeric"
              stroke="#6366f1"
              strokeWidth={2.5}
              dot={{ r: 3, fill: '#818cf8', strokeWidth: 0 }}
              activeDot={{ r: 6, fill: '#38bdf8', stroke: '#0f172a', strokeWidth: 2 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Stage Timeline Summary */}
      <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
        <div className="flex items-center gap-2">
          <span>Total Monitored Epochs:</span>
          <span className="font-mono text-white font-bold">{epochs.length}</span>
          <span>(30 seconds / epoch)</span>
        </div>
        <div className="flex items-center gap-3">
          <span>Standards: <strong className="text-slate-300">AASM Manual v2.6</strong></span>
          <span>•</span>
          <span className="text-indigo-400 font-medium">Deep Slow-Wave (N3) = Autonomic Restorative Phase</span>
        </div>
      </div>
    </div>
  );
};
