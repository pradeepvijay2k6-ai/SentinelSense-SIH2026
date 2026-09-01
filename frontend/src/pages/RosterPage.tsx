import { useState, useEffect } from 'react';
import {
  Users,
  ShieldCheck,
  Activity,
  History
} from 'lucide-react';
import { api } from '../api/client';
import type { RosterSummary } from '../types';

interface RosterPageProps {
  onSelectResultById: (id: number) => void;
  onSelectPersonnelHistory: (personnelId: number) => void;
}

export const RosterPage: React.FC<RosterPageProps> = ({
  onSelectResultById,
  onSelectPersonnelHistory
}) => {
  const [roster, setRoster] = useState<RosterSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [forceFilter, setForceFilter] = useState<string>('ALL');

  useEffect(() => {
    loadRoster();
  }, []);

  const loadRoster = async () => {
    try {
      setLoading(true);
      const data = await api.getRoster();
      setRoster(data);
    } catch (err) {
      console.error('Failed to load roster:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !roster) {
    return <div className="p-12 text-center text-slate-400">Loading battalion roster overview...</div>;
  }

  const filteredItems = (roster.roster || []).filter((item) => {
    if (forceFilter === 'ALL') return true;
    return item.force_type === forceFilter;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Users className="w-6 h-6 text-indigo-400" />
            <span>Tactical Unit Readiness & Fatigue Roster</span>
          </h2>
          <p className="text-xs text-slate-400">
            Commander High-Level Operational Overview • Privacy-Preserved Stress & Sleep Vigilance Monitoring
          </p>
        </div>

        {/* Force Filter */}
        <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 p-1 rounded-xl">
          {['ALL', 'CRPF', 'BSF', 'ITBP', 'CISF', 'SSB'].map((f) => (
            <button
              key={f}
              onClick={() => setForceFilter(f)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                forceFilter === f
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Aggregate Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl">
          <div className="text-xs font-semibold text-slate-400">Total Monitored Personnel</div>
          <div className="text-2xl font-extrabold text-white mt-1 font-mono">{roster.total_personnel}</div>
          <div className="text-[11px] text-slate-500 mt-1">Across all CAPF deployed sectors</div>
        </div>

        <div className="p-5 bg-emerald-950/20 border border-emerald-900/40 rounded-2xl shadow-xl">
          <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Fit For Tactical Duty</span>
          </div>
          <div className="text-2xl font-extrabold text-emerald-300 mt-1 font-mono">{roster.fit_for_duty}</div>
          <div className="text-[11px] text-emerald-500/80 mt-1">Low fatigue / optimal recovery</div>
        </div>

        <div className="p-5 bg-amber-950/20 border border-amber-900/40 rounded-2xl shadow-xl">
          <div className="text-xs font-semibold text-amber-400">Mild / Elevated Fatigue</div>
          <div className="text-2xl font-extrabold text-amber-300 mt-1 font-mono">{roster.monitoring_required}</div>
          <div className="text-[11px] text-amber-500/80 mt-1">Monitor next shift & rotate duties</div>
        </div>

        <div className="p-5 bg-rose-950/20 border border-rose-900/40 rounded-2xl shadow-xl">
          <div className="text-xs font-semibold text-rose-400">High Stress / Severe Fatigue</div>
          <div className="text-2xl font-extrabold text-rose-300 mt-1 font-mono">{roster.critical_fatigue_stress}</div>
          <div className="text-[11px] text-rose-500/80 mt-1">Mandatory rest / medical review</div>
        </div>
      </div>

      {/* Roster Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl overflow-hidden backdrop-blur-sm">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-base font-semibold text-white">Personnel Roster Status</h3>
          <span className="text-xs text-slate-400 font-mono">Showing {filteredItems.length} Officers</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Personnel ID</th>
                <th className="py-3.5 px-4">Force / Unit</th>
                <th className="py-3.5 px-4">Status & Risk</th>
                <th className="py-3.5 px-4">Latest Verdict</th>
                <th className="py-3.5 px-4">Last Tested</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredItems.map((item) => {
                const hasSession = item.risk_level !== null && item.risk_level !== undefined;
                return (
                  <tr key={item.id} className="hover:bg-slate-950/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-white">
                      <div>{item.personnel_id}</div>
                      <div className="text-[11px] font-normal text-slate-400">{item.name}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px] mr-2">
                        {item.force_type}
                      </span>
                      <span className="text-slate-400 text-[11px]">{item.unit}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      {hasSession ? (
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-semibold text-[11px] border ${
                            item.risk_level === 'LOW'
                              ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80'
                              : item.risk_level === 'MODERATE'
                              ? 'bg-amber-950/80 text-amber-300 border-amber-800/80'
                              : 'bg-rose-950/80 text-rose-300 border-rose-800/80'
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              item.risk_level === 'LOW'
                                ? 'bg-emerald-400'
                                : item.risk_level === 'MODERATE'
                                ? 'bg-amber-400'
                                : 'bg-rose-400'
                            }`}
                          />
                          {item.risk_level} ({item.risk_score?.toFixed(0)}/100)
                        </span>
                      ) : (
                        <span className="text-slate-500 italic text-[11px]">No Sessions</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      {item.readiness_verdict ? (
                        <span className="text-slate-300 text-xs">{item.readiness_verdict}</span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px]">
                      {item.latest_upload_time
                        ? new Date(item.latest_upload_time).toLocaleDateString()
                        : '—'}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {item.latest_upload_id && (
                          <button
                            onClick={() => onSelectResultById(item.latest_upload_id!)}
                            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded-lg transition-colors"
                            title="View latest analysis"
                          >
                            <Activity className="w-3.5 h-3.5" />
                          </button>
                        )}
                        <button
                          onClick={() => onSelectPersonnelHistory(item.id)}
                          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
                          title="View officer history"
                        >
                          <History className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
