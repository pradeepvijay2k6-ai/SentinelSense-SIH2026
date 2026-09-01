import React, { useState, useEffect } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  Play,
  UserPlus,
  Users,
  Shield,
  Sparkles,
  Zap,
  Loader2
} from 'lucide-react';
import { api } from '../api/client';
import type { Personnel, SampleScenario, AnalysisResult } from '../types';

interface UploadPageProps {
  onAnalysisComplete: (result: AnalysisResult) => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ onAnalysisComplete }) => {
  const [personnelList, setPersonnelList] = useState<Personnel[]>([]);
  const [selectedPersonnelCode, setSelectedPersonnelCode] = useState<string>('CRPF-0101');
  const [isCreatingPersonnel, setIsCreatingPersonnel] = useState<boolean>(false);
  const [newPersonnelId, setNewPersonnelId] = useState<string>('');
  const [newPersonnelName, setNewPersonnelName] = useState<string>('');
  const [newForceType, setNewForceType] = useState<string>('CRPF');

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [scenarios, setScenarios] = useState<SampleScenario[]>([]);
  const [processing, setProcessing] = useState<boolean>(false);
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    loadPersonnel();
    loadScenarios();
  }, []);

  const loadPersonnel = async () => {
    try {
      const list = await api.getPersonnel();
      setPersonnelList(list);
      if (list.length > 0) {
        setSelectedPersonnelCode(list[0].personnel_id);
      }
    } catch (err) {
      console.error('Failed to load personnel:', err);
    }
  };

  const loadScenarios = async () => {
    try {
      const data = await api.getSampleScenarios();
      setScenarios(data);
    } catch (err) {
      console.error('Failed to load sample scenarios:', err);
    }
  };

  const handleCreatePersonnel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPersonnelId.trim()) return;
    setErrorMessage(null);
    try {
      const created = await api.createPersonnel({
        personnel_id: newPersonnelId.trim().toUpperCase(),
        name: newPersonnelName.trim() || undefined,
        force_type: newForceType,
        unit: `${newForceType} Tactical Unit`
      });
      await loadPersonnel();
      setSelectedPersonnelCode(created.personnel_id);
      setIsCreatingPersonnel(false);
      setNewPersonnelId('');
      setNewPersonnelName('');
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }, message?: string };
      const detailMsg = axiosErr.response?.data?.detail || axiosErr.message || 'Failed to create personnel profile.';
      setErrorMessage(`Profile Creation Error: ${detailMsg}`);
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select a sensor CSV/EDF file to upload.');
      return;
    }
    setProcessing(true);
    setErrorMessage(null);
    setProcessingStatus('Parsing multimodal telemetry & validating channels...');

    try {
      setTimeout(() => setProcessingStatus('Applying Butterworth bandpass & 50Hz notch filters...'), 600);
      setTimeout(() => setProcessingStatus('Generating CWT scalograms & running PyTorch SentinelSleepNet...'), 1200);
      setTimeout(() => setProcessingStatus('Computing HRV spectra, Baevsky index & SpO2 desaturations...'), 1800);

      const result = await api.uploadSensorFile(selectedFile, selectedPersonnelCode);
      onAnalysisComplete(result);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }, message?: string };
      const detailMsg = axiosErr.response?.data?.detail || axiosErr.message || 'Analysis pipeline failed. Please check file format.';
      setErrorMessage(`Pipeline Error: ${detailMsg}`);
    } finally {
      setProcessing(false);
    }
  };

  const handleRunQuickScenario = async (scenario: SampleScenario) => {
    setProcessing(true);
    setErrorMessage(null);
    setProcessingStatus(`Loading scenario "${scenario.title}"...`);

    try {
      setTimeout(() => setProcessingStatus('Executing PyTorch sleep staging & multimodal fusion...'), 800);
      const result = await api.runSampleScenario(scenario.scenario_type);
      onAnalysisComplete(result);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }, message?: string };
      const detailMsg = axiosErr.response?.data?.detail || axiosErr.message || 'Failed to run scenario.';
      setErrorMessage(`Scenario Error: ${detailMsg}`);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Hero Title */}
      <div className="text-center space-y-2 pt-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/80 border border-indigo-800 text-indigo-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>CAPF Operational Welfare & Fatigue Monitoring System</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Multimodal Biosignal Sensor Ingestion
        </h1>
        <p className="text-sm text-slate-400 max-w-2xl mx-auto">
          Upload wearable/duty sensor recordings (ECG, EMG, EOG, SpO2, Accelerometer) to run deep learning sleep staging, autonomic stress scoring, and tactical readiness analytics.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 bg-rose-950/80 border border-rose-800 rounded-xl flex items-center gap-3 text-rose-200 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Personnel Profile Selection */}
        <div className="p-6 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Users className="w-4 h-4 text-indigo-400" />
              <span>Target Personnel</span>
            </h3>
            <button
              onClick={() => setIsCreatingPersonnel(!isCreatingPersonnel)}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              <UserPlus className="w-3.5 h-3.5" />
              <span>{isCreatingPersonnel ? 'Cancel' : 'New Profile'}</span>
            </button>
          </div>

          {isCreatingPersonnel ? (
            <form onSubmit={handleCreatePersonnel} className="space-y-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Personnel ID Code *</label>
                <input
                  type="text"
                  placeholder="e.g. CRPF-0231"
                  value={newPersonnelId}
                  onChange={(e) => setNewPersonnelId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                  required
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Force Branch</label>
                <select
                  value={newForceType}
                  onChange={(e) => setNewForceType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="CRPF">CRPF (Central Reserve Police Force)</option>
                  <option value="BSF">BSF (Border Security Force)</option>
                  <option value="ITBP">ITBP (Indo-Tibetan Border Police)</option>
                  <option value="CISF">CISF (Central Industrial Security Force)</option>
                  <option value="SSB">SSB (Sashastra Seema Bal)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Officer Name (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Sub-Inspector R. Sharma"
                  value={newPersonnelName}
                  onChange={(e) => setNewPersonnelName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <button
                type="submit"
                className="w-full py-2 px-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition-all shadow-md shadow-indigo-600/30"
              >
                Create & Select Profile
              </button>
            </form>
          ) : (
            <div className="space-y-2">
              <label className="block text-xs text-slate-400">Select Existing Officer Profile:</label>
              <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                {personnelList.map((p) => {
                  const isSelected = selectedPersonnelCode === p.personnel_id;
                  return (
                    <div
                      key={p.id}
                      onClick={() => setSelectedPersonnelCode(p.personnel_id)}
                      className={`p-2.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-indigo-950/60 border-indigo-500/80 shadow-sm'
                          : 'bg-slate-950/40 border-slate-800 hover:border-slate-700 text-slate-300'
                      }`}
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-xs text-white">{p.personnel_id}</span>
                          <span className="text-[10px] px-1.5 rounded bg-slate-800 text-slate-300">{p.force_type}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 truncate max-w-[160px]">{p.name}</div>
                      </div>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-indigo-400" />}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span>Anonymized UID for Privacy Compliance</span>
          </div>
        </div>

        {/* File Upload Dropzone */}
        <div className="lg:col-span-2 p-6 bg-slate-900/70 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-sm flex flex-col justify-between space-y-4">
          <div>
            <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-1">
              <UploadCloud className="w-4 h-4 text-indigo-400" />
              <span>Upload Physiological Sensor File</span>
            </h3>
            <p className="text-xs text-slate-400">
              Supports standard multi-channel CSV (ECG, EMG, EOG, SpO2, Accelerometer) and clinical EDF formats.
            </p>
          </div>

          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleFileDrop}
            className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer flex flex-col items-center justify-center min-h-[190px] ${
              isDragging
                ? 'border-indigo-400 bg-indigo-950/30'
                : selectedFile
                ? 'border-emerald-500/60 bg-emerald-950/10'
                : 'border-slate-700/80 bg-slate-950/40 hover:border-slate-600'
            }`}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".csv,.edf"
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  setSelectedFile(e.target.files[0]);
                }
              }}
              className="hidden"
            />

            {selectedFile ? (
              <div className="space-y-2">
                <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-700/60 flex items-center justify-center mx-auto">
                  <FileSpreadsheet className="w-6 h-6 text-emerald-400" />
                </div>
                <div className="text-sm font-semibold text-white">{selectedFile.name}</div>
                <div className="text-xs text-slate-400">
                  {(selectedFile.size / 1024).toFixed(1)} KB — Click or drop another file to replace
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto">
                  <UploadCloud className="w-6 h-6 text-slate-400" />
                </div>
                <div className="text-sm font-medium text-slate-200">
                  Drag and drop your sensor CSV / EDF file here
                </div>
                <div className="text-xs text-slate-400">
                  or <span className="text-indigo-400 underline font-semibold">browse files</span> on your device
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between gap-4 pt-2">
            <div className="text-xs text-slate-400">
              Selected Target: <span className="font-mono text-white font-bold">{selectedPersonnelCode}</span>
            </div>
            <button
              onClick={handleUploadSubmit}
              disabled={!selectedFile || processing}
              className={`px-6 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg ${
                !selectedFile || processing
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white shadow-indigo-600/30'
              }`}
            >
              {processing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Run Pipeline Analysis</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Quick 1-Click Operational Scenario Demo Cards */}
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <span>Instant Operational Scenarios (Demo Short-Cuts)</span>
          </h3>
          <p className="text-xs text-slate-400">
            Run pre-generated synthetic physiological telemetry for instant testing of diverse operational outcomes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scenarios.map((scen) => (
            <div
              key={scen.scenario_type}
              className="p-5 bg-slate-900/70 border border-slate-800 hover:border-slate-700 rounded-2xl shadow-xl backdrop-blur-sm flex flex-col justify-between space-y-4 transition-all group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono uppercase px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800">
                    {scen.personnel_id}
                  </span>
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                    scen.expected_risk.includes('LOW')
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      : scen.expected_risk.includes('MODERATE')
                      ? 'bg-amber-950 text-amber-400 border border-amber-800'
                      : 'bg-rose-950 text-rose-400 border border-rose-800'
                  }`}>
                    {scen.expected_risk}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
                  {scen.title}
                </h4>
                <p className="text-xs leading-relaxed text-slate-400">{scen.description}</p>
              </div>
              <button
                onClick={() => handleRunQuickScenario(scen)}
                disabled={processing}
                className="w-full py-2 px-3 bg-slate-950/80 hover:bg-indigo-600 text-slate-200 hover:text-white rounded-xl text-xs font-semibold border border-slate-800 hover:border-indigo-500 transition-all flex items-center justify-center gap-2 shadow-sm"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Simulate & Analyze</span>
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Processing Modal Overlay */}
      {processing && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl max-w-md w-full text-center space-y-5 shadow-2xl">
            <div className="w-16 h-16 rounded-2xl bg-indigo-950/80 border border-indigo-700/60 flex items-center justify-center mx-auto animate-pulse">
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-white">SentinelSense Pipeline Executing</h3>
              <p className="text-xs text-slate-300 font-mono animate-pulse">{processingStatus}</p>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full w-2/3 animate-pulse rounded-full" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
