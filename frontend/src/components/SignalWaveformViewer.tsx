import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { Activity, Waves, Eye, Droplet, Move, Filter } from 'lucide-react';
import type { WaveformPoint } from '../types';

interface SignalWaveformViewerProps {
  waveform: WaveformPoint[];
}

type VisibleChannel = 'ecg' | 'emg' | 'eog' | 'spo2' | 'motion';

export const SignalWaveformViewer: React.FC<SignalWaveformViewerProps> = ({ waveform }) => {
  const [selectedChannel, setSelectedChannel] = useState<VisibleChannel>('ecg');
  const [showFilteredOverlay, setShowFilteredOverlay] = useState<boolean>(true);

  if (!waveform || waveform.length === 0) {
    return (
      <div className="p-6 bg-slate-900/70 border border-slate-800 rounded-2xl text-center text-slate-400">
        No waveform telemetry available for this recording session.
      </div>
    );
  }

  const channelConfig = {
    ecg: {
      name: 'Electrocardiogram (ECG)',
      unit: 'mV',
      icon: Activity,
      color: '#10b981',
      filterColor: '#06b6d4',
      description: 'Lead II waveform showing P-QRS-T complexes and respiratory baseline wander removal (0.5-45 Hz)'
    },
    emg: {
      name: 'Submental Electromyogram (EMG)',
      unit: 'µV',
      icon: Waves,
      color: '#a855f7',
      filterColor: '#d946ef',
      description: 'Chin muscle tone reflecting sleep depth (prominent atonia during REM stage)'
    },
    eog: {
      name: 'Electrooculogram (EOG)',
      unit: 'µV',
      icon: Eye,
      color: '#f59e0b',
      filterColor: '#fbbf24',
      description: 'Ocular potential detecting slow rolling eye movements (N1) vs rapid eye bursts (REM)'
    },
    spo2: {
      name: 'Pulse Oximetry (SpO2)',
      unit: '%',
      icon: Droplet,
      color: '#ef4444',
      filterColor: '#f87171',
      description: 'Continuous blood oxygen saturation with automated nadir desaturation dip tracking'
    },
    motion: {
      name: 'Actigraphy / Motion Residual',
      unit: 'g',
      icon: Move,
      color: '#38bdf8',
      filterColor: '#60a5fa',
      description: 'Tri-axial accelerometer dynamic norm measuring nocturnal restlessness and postural shifts'
    }
  };

  const currentConfig = channelConfig[selectedChannel];

  return (
    <div className="p-6 bg-slate-900/70 border border-cyan-900/40 rounded-2xl shadow-xl backdrop-blur-sm relative">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 text-[10px] font-bold uppercase tracking-wider">
              Medical Officer Telemetry
            </span>
            <h3 className="text-base font-semibold text-white">
              Multimodal Biosignal Oscilloscope
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            {currentConfig.description}
          </p>
        </div>

        {/* Channel Selector Pills */}
        <div className="flex flex-wrap items-center gap-1.5 bg-slate-950/80 p-1 rounded-xl border border-slate-800">
          {(['ecg', 'emg', 'eog', 'spo2', 'motion'] as VisibleChannel[]).map((ch) => {
            const cfg = channelConfig[ch];
            const Icon = cfg.icon;
            const isSelected = selectedChannel === ch;
            return (
              <button
                key={ch}
                onClick={() => setSelectedChannel(ch)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                  isSelected
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{ch.toUpperCase()}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Filter Toggle for ECG */}
      {selectedChannel === 'ecg' && (
        <div className="flex items-center gap-3 mb-3 text-xs">
          <button
            onClick={() => setShowFilteredOverlay(!showFilteredOverlay)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border transition-all ${
              showFilteredOverlay
                ? 'bg-cyan-950/70 border-cyan-700 text-cyan-300'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Cleaned (Butterworth + 50Hz Notch) vs Raw</span>
          </button>
          <div className="flex items-center gap-3 text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <span className="w-3 h-0.5 bg-slate-400" /> Raw Signal
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-0.5 bg-cyan-400" /> Filtered Signal
            </span>
          </div>
        </div>
      )}

      {/* Waveform Graph */}
      <div className="h-60 w-full bg-slate-950/60 rounded-xl p-2 border border-slate-800/60">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={waveform} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="time_sec"
              stroke="#64748b"
              fontSize={11}
              tickFormatter={(v) => `${v.toFixed(0)}s`}
              tickLine={false}
            />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              unit={` ${currentConfig.unit}`}
              domain={
                selectedChannel === 'spo2'
                  ? [75, 100]
                  : selectedChannel === 'motion'
                  ? [0, 'auto']
                  : ['auto', 'auto']
              }
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const pt = payload[0].payload as WaveformPoint;
                  return (
                    <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs space-y-1">
                      <div className="text-slate-400 font-mono">Time: {pt.time_sec.toFixed(2)}s</div>
                      {selectedChannel === 'ecg' ? (
                        <>
                          <div className="text-slate-300">Raw: {pt.ecg_raw.toFixed(3)} mV</div>
                          <div className="text-cyan-300 font-bold">Filtered: {pt.ecg_clean.toFixed(3)} mV</div>
                        </>
                      ) : selectedChannel === 'emg' ? (
                        <div className="text-purple-300 font-bold">EMG: {pt.emg.toFixed(2)} µV</div>
                      ) : selectedChannel === 'eog' ? (
                        <div className="text-amber-300 font-bold">EOG: {pt.eog.toFixed(2)} µV</div>
                      ) : selectedChannel === 'spo2' ? (
                        <div className="text-rose-300 font-bold">SpO2: {pt.spo2.toFixed(1)}%</div>
                      ) : (
                        <div className="text-sky-300 font-bold">Motion: {pt.motion.toFixed(4)} g</div>
                      )}
                    </div>
                  );
                }
                return null;
              }}
            />

            {selectedChannel === 'ecg' ? (
              <>
                <Line
                  type="monotone"
                  dataKey="ecg_raw"
                  stroke="#64748b"
                  strokeWidth={1}
                  dot={false}
                  isAnimationActive={false}
                  opacity={0.6}
                />
                {showFilteredOverlay && (
                  <Line
                    type="monotone"
                    dataKey="ecg_clean"
                    stroke="#06b6d4"
                    strokeWidth={1.75}
                    dot={false}
                    isAnimationActive={false}
                  />
                )}
              </>
            ) : selectedChannel === 'emg' ? (
              <Line
                type="monotone"
                dataKey="emg"
                stroke="#a855f7"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
            ) : selectedChannel === 'eog' ? (
              <Line
                type="monotone"
                dataKey="eog"
                stroke="#f59e0b"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
            ) : selectedChannel === 'spo2' ? (
              <Line
                type="monotone"
                dataKey="spo2"
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            ) : (
              <Line
                type="monotone"
                dataKey="motion"
                stroke="#38bdf8"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
        <span>High-resolution downsampled window (~60s telemetry)</span>
        <span className="font-mono text-cyan-400">QRS Pan-Tompkins Peak Detection Synchronized</span>
      </div>
    </div>
  );
};
