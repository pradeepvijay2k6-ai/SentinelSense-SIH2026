from typing import List, Optional, Any, Dict
from pydantic import BaseModel
import datetime

class PersonnelBase(BaseModel):
    personnel_id: str
    name: Optional[str] = None
    unit: Optional[str] = "12th Battalion, Delta Coy"
    force_type: Optional[str] = "CRPF"
    age: Optional[int] = 32

class PersonnelCreate(PersonnelBase):
    pass

class PersonnelResponse(PersonnelBase):
    id: int
    created_at: datetime.datetime
    latest_risk_score: Optional[float] = None
    latest_risk_level: Optional[str] = None
    latest_readiness: Optional[str] = None
    total_uploads: int = 0

    class Config:
        from_attributes = True

class HypnogramEpoch(BaseModel):
    epoch_index: int
    timestamp_sec: float
    time_str: str
    stage: str # W, N1, N2, N3, REM
    confidence: float
    is_apnea_event: bool = False
    is_motion_event: bool = False

class SignalChannelPoint(BaseModel):
    time_sec: float
    ecg_raw: float
    ecg_clean: float
    emg: float
    eog: float
    eeg: Optional[float] = 0.0
    spo2: float
    motion: float

class AnalysisResultResponse(BaseModel):
    id: int
    personnel_id: int
    personnel_code: str
    filename: str
    scenario_tag: Optional[str] = None
    uploaded_at: datetime.datetime
    
    # Primary Risk Scores
    risk_score: float
    risk_level: str # LOW, MODERATE, HIGH
    readiness_verdict: str # Fit for Duty, Monitoring Required, Rest Recommended, Unfit
    
    # Sub-scores (0-100)
    sleep_score: float
    stress_score: float
    fatigue_score: float
    hypoxia_score: float
    
    # Sleep Architecture
    sleep_efficiency: float
    deep_sleep_pct: float
    rem_sleep_pct: float
    light_sleep_pct: float
    wake_pct: float
    total_sleep_time_min: float
    total_recording_time_min: float
    
    # Cardiovascular & Autonomic HRV
    avg_heart_rate: float
    hrv_rmssd: float
    hrv_sdnn: float
    hrv_lf_hf_ratio: float
    baevsky_stress_index: float
    
    # Oximetry & Respiratory
    avg_spo2: float
    spo2_min: float
    odi_dips_per_hour: float
    hypoxic_burden_pct: float
    
    # Activity & Restlessness
    restlessness_index: float
    
    # Narratives & Summaries
    clinical_explanation: str
    commander_summary: str
    key_drivers: List[str]
    recommendations: List[str]
    
    # Visualizations
    hypnogram: List[HypnogramEpoch]
    waveform_preview: List[Dict[str, Any]]

class PersonnelHistoryResponse(BaseModel):
    personnel: PersonnelResponse
    history: List[AnalysisResultResponse]

class RosterOverviewItem(BaseModel):
    id: int
    personnel_id: str
    name: Optional[str]
    unit: str
    force_type: str
    latest_upload_id: Optional[int] = None
    latest_upload_time: Optional[datetime.datetime] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None # LOW, MODERATE, HIGH
    readiness_verdict: Optional[str] = None
    sleep_efficiency: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2_min: Optional[float] = None

class SampleScenarioItem(BaseModel):
    filename: str
    scenario_type: str
    personnel_id: str
    title: str
    description: str
    expected_risk: str
