import React, { useState, useEffect } from 'react';
import {
  FileText,
  Clock,
  ArrowRight,
  Activity,
  UserCheck
} from 'lucide-react';
import { api } from '../api/client';
import type { Personnel, AnalysisResult } from '../types';
import { TrendLineChart } from '../components/TrendLineChart';

interface PersonnelHistoryPageProps {
  onSelectResult: (result: AnalysisResult) => void;
  defaultPersonnelId?: number;
}

export const PersonnelHistoryPage: React.FC<PersonnelHistoryPageProps> = ({
  onSelectResult,
  defaultPersonnelId
}) => {
  const [personnelList, setPersonnelList] = useState<Personnel[]>([]);
  const [selectedPersonnel, setSelectedPersonnel] = useState<Personnel | null>(null);
  const [history, setHistory] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    loadAllPersonnel();
  }, []);

  const loadAllPersonnel = async () => {
    try {
      const list = await api.getPersonnel();
      setPersonnelList(list);
      if (list.length > 0) {
        if (defaultPersonnelId) {
          const match = list.find((p) => p.id === defaultPersonnelId);
          if (match) {
            handleSelectOfficer(match);
            return;
          }
        }
        handleSelectOfficer(list[0]);
      }
    } catch (err) {
      console.error('Failed to load personnel list:', err);
    }
  };

  const handleSelectOfficer = async (p: Personnel) => {
    setSelectedPersonnel(p);
    setLoading(true);
    try {
      const historyData = await api.getPersonnelHistory(p.id);
      setHistory(historyData.history || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      <div>
        <h2 className="text-2xl font-bold text-white">Personnel Health & Stress History</h2>
        <p className="text-xs text-slate-400">
          Track longitudinal physiological resilience, sleep architecture, and autonomic recovery over time.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Personnel List Selector */}
        <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Select Personnel
          </h3>
          <div className="space-y-1.5 max-h-[500px] overflow-y-auto pr-1">
            {personnelList.map((p) => {
              const isSelected = selectedPersonnel?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => handleSelectOfficer(p)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-indigo-950/70 border-indigo-500 shadow-sm'
                      : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-xs text-white">{p.personnel_id}</span>
                    <span className="text-[10px] px-1.5 rounded bg-slate-800 text-slate-300">
                      {p.force_type}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1 truncate">{p.name}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{p.unit}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* History Details & Trend Charts */}
        <div className="lg:col-span-3 space-y-6">
          {selectedPersonnel && (
            <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-950 border border-indigo-700 flex items-center justify-center font-bold text-indigo-300 font-mono text-sm">
                  {selectedPersonnel.force_type}
                </div>
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>{selectedPersonnel.name}</span>
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {selectedPersonnel.personnel_id}
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400">{selectedPersonnel.unit}</p>
                </div>
              </div>

              <div className="flex items-center gap-4 text-xs text-slate-400">
                <span className="flex items-center gap-1.5">
                  <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Active Duty
                </span>
                <span>•</span>
                <span>{history.length} Analysis Sessions Recorded</span>
              </div>
            </div>
          )}

          {/* Trend Chart */}
          <TrendLineChart history={history} />

          {/* Past Sessions List */}
          <div className="p-6 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-400" />
              <span>Historical Session Logs</span>
            </h3>

            {loading ? (
              <div className="p-8 text-center text-slate-400">Loading session history...</div>
            ) : history.length === 0 ? (
              <div className="p-8 text-center text-slate-400 bg-slate-950/40 rounded-xl border border-slate-800">
                No telemetry recordings uploaded for this officer yet.
              </div>
            ) : (
              <div className="divide-y divide-slate-800">
                {history.map((h) => (
                  <div
                    key={h.id}
                    className="py-3.5 flex flex-wrap items-center justify-between gap-4 hover:bg-slate-950/40 px-3 rounded-xl transition-colors"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-white flex items-center gap-1">
                          <FileText className="w-3.5 h-3.5 text-slate-400" />
                          {h.filename}
                        </span>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${
                            h.risk_level === 'LOW'
                              ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                              : h.risk_level === 'MODERATE'
                              ? 'bg-amber-950 text-amber-300 border-amber-800'
                              : 'bg-rose-950 text-rose-300 border-rose-800'
                          }`}
                        >
                          {h.risk_level} ({h.risk_score.toFixed(0)}/100)
                        </span>
                        {h.scenario_tag && (
                          <span className="text-[10px] px-1.5 rounded bg-slate-800 text-slate-300 font-mono">
                            {h.scenario_tag}
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-3">
                        <span>{new Date(h.uploaded_at).toLocaleString()}</span>
                        <span>•</span>
                        <span>Sleep Eff: {h.sleep_efficiency.toFixed(1)}%</span>
                        <span>•</span>
                        <span>RMSSD: {h.hrv_rmssd.toFixed(1)} ms</span>
                        <span>•</span>
                        <span>Min SpO2: {h.spo2_min.toFixed(1)}%</span>
                      </div>
                    </div>

                    <button
                      onClick={() => onSelectResult(h)}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-indigo-600 text-slate-200 hover:text-white rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5"
                    >
                      <Activity className="w-3.5 h-3.5" />
                      <span>View Session</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
