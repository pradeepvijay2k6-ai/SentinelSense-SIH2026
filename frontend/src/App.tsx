import { useState } from 'react';
import type { RoleView, AnalysisResult } from './types';
import { Navbar } from './components/Navbar';
import { UploadPage } from './pages/UploadPage';
import { ResultPage } from './pages/ResultPage';
import { PersonnelHistoryPage } from './pages/PersonnelHistoryPage';
import { RosterPage } from './pages/RosterPage';
import { api } from './api/client';
import { ShieldCheck } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'upload' | 'result' | 'history' | 'roster'>('upload');
  const [role, setRole] = useState<RoleView>('MEDICAL_OFFICER');
  const [activeResult, setActiveResult] = useState<AnalysisResult | null>(null);
  const [selectedPersonnelHistoryId, setSelectedPersonnelHistoryId] = useState<number | undefined>(undefined);

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setActiveResult(result);
    setActiveTab('result');
  };

  const handleSelectResultById = async (id: number) => {
    try {
      const res = await api.getAnalysis(id);
      setActiveResult(res);
      setActiveTab('result');
    } catch (err) {
      console.error('Failed to load analysis session:', err);
    }
  };

  const handleSelectPersonnelHistory = (personnelId: number) => {
    setSelectedPersonnelHistoryId(personnelId);
    setActiveTab('history');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        role={role}
        setRole={setRole}
        hasActiveResult={!!activeResult}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'upload' && (
          <UploadPage onAnalysisComplete={handleAnalysisComplete} />
        )}

        {activeTab === 'result' && activeResult && (
          <ResultPage
            result={activeResult}
            role={role}
            onBackToUpload={() => setActiveTab('upload')}
            onViewHistory={() => {
              setSelectedPersonnelHistoryId(activeResult.personnel_id);
              setActiveTab('history');
            }}
          />
        )}

        {activeTab === 'history' && (
          <PersonnelHistoryPage
            onSelectResult={(res) => {
              setActiveResult(res);
              setActiveTab('result');
            }}
            defaultPersonnelId={selectedPersonnelHistoryId}
          />
        )}

        {activeTab === 'roster' && (
          <RosterPage
            onSelectResultById={handleSelectResultById}
            onSelectPersonnelHistory={handleSelectPersonnelHistory}
          />
        )}
      </main>

      <footer className="mt-auto border-t border-slate-900 bg-slate-950/80 py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-400 font-semibold">SentinelSense v1.0</span>
            <span>•</span>
            <span>Smart India Hackathon 2026 (PS 26186)</span>
            <span>•</span>
            <span>Ministry of Home Affairs / CAPF</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" /> Privacy-by-Design
            </span>
            <span>•</span>
            <span>PyTorch ResNet CWT Staging</span>
            <span>•</span>
            <span>Pan-Tompkins HRV</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
