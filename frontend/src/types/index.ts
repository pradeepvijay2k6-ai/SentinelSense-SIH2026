export type RoleView = 'MEDICAL_OFFICER' | 'COMMANDER';

export interface Personnel {
  id: number;
  personnel_id: string;
  name: string;
  unit: string;
  force_type: string;
  age: number;
  created_at: string;
  latest_risk_score?: number | null;
  latest_risk_level?: 'LOW' | 'MODERATE' | 'HIGH' | null;
  latest_readiness?: string | null;
  total_uploads: number;
}

export interface HypnogramEpoch {
  epoch_index: number;
  timestamp_sec: number;
  time_str: string;
  stage: 'W' | 'N1' | 'N2' | 'N3' | 'REM';
  confidence: number;
  is_apnea_event: boolean;
  is_motion_event: boolean;
}

export interface WaveformPoint {
  time_sec: number;
  ecg_raw: number;
  ecg_clean: number;
  emg: number;
  eog: number;
  eeg?: number;
  spo2: number;
  motion: number;
}

export interface AnalysisResult {
  id: number;
  personnel_id: number;
  personnel_code: string;
  filename: string;
  scenario_tag?: string | null;
  uploaded_at: string;
  
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH';
  readiness_verdict: string;
  
  sleep_score: number;
  stress_score: number;
  fatigue_score: number;
  hypoxia_score: number;
  
  sleep_efficiency: number;
  deep_sleep_pct: number;
  rem_sleep_pct: number;
  light_sleep_pct: number;
  wake_pct: number;
  total_sleep_time_min: number;
  total_recording_time_min: number;
  
  avg_heart_rate: number;
  hrv_rmssd: number;
  hrv_sdnn: number;
  hrv_lf_hf_ratio: number;
  baevsky_stress_index: number;
  
  avg_spo2: number;
  spo2_min: number;
  odi_dips_per_hour: number;
  hypoxic_burden_pct: number;
  
  restlessness_index: number;
  
  clinical_explanation: string;
  commander_summary: string;
  key_drivers: string[];
  recommendations: string[];
  
  hypnogram: HypnogramEpoch[];
  waveform_preview: WaveformPoint[];
}

export interface PersonnelHistory {
  personnel: Personnel;
  history: AnalysisResult[];
}

export interface RosterItem {
  id: number;
  personnel_id: string;
  name: string;
  unit: string;
  force_type: string;
  latest_upload_id?: number | null;
  latest_upload_time?: string | null;
  risk_score?: number | null;
  risk_level?: 'LOW' | 'MODERATE' | 'HIGH' | null;
  readiness_verdict?: string | null;
  sleep_efficiency?: number | null;
  hrv_rmssd?: number | null;
  spo2_min?: number | null;
}

export interface RosterSummary {
  total_personnel: number;
  fit_for_duty: number;
  monitoring_required: number;
  critical_fatigue_stress: number;
  unscreened: number;
  average_unit_risk_score: number;
  roster: RosterItem[];
}

export interface SampleScenario {
  filename: string;
  scenario_type: string;
  personnel_id: string;
  title: string;
  description: string;
  expected_risk: string;
}
