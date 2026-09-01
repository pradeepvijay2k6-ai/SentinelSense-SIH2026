import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Personnel(Base):
    __tablename__ = "personnel"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. CRPF-0231, BSF-0512
    name = Column(String(128), nullable=True)
    unit = Column(String(128), nullable=True, default="12th Battalion, Delta Coy")
    force_type = Column(String(64), nullable=True, default="CRPF") # CRPF, BSF, CISF, ITBP, SSB, NSG
    age = Column(Integer, nullable=True, default=32)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    uploads = relationship("UploadSession", back_populates="personnel", cascade="all, delete-orphan")

class UploadSession(Base):
    __tablename__ = "upload_sessions"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), nullable=False)
    filename = Column(String(256), nullable=False)
    file_type = Column(String(32), default="csv") # csv, edf
    file_path = Column(String(512), nullable=True)
    scenario_tag = Column(String(64), nullable=True) # e.g., well_rested, high_stress
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Analysis outputs
    risk_score = Column(Float, nullable=True) # 0 to 100
    risk_level = Column(String(32), nullable=True) # LOW, MODERATE, HIGH
    readiness_verdict = Column(String(64), nullable=True) # Fit for Duty, Monitoring Required, Unfit for Duty
    
    # Key Summary Metrics
    sleep_efficiency = Column(Float, nullable=True) # %
    deep_sleep_pct = Column(Float, nullable=True) # N3 %
    rem_sleep_pct = Column(Float, nullable=True) # REM %
    light_sleep_pct = Column(Float, nullable=True) # N1+N2 %
    wake_pct = Column(Float, nullable=True) # Wake %
    total_sleep_time_min = Column(Float, nullable=True)
    
    avg_heart_rate = Column(Float, nullable=True) # bpm
    hrv_rmssd = Column(Float, nullable=True) # ms
    hrv_sdnn = Column(Float, nullable=True) # ms
    hrv_lf_hf_ratio = Column(Float, nullable=True)
    baevsky_stress_index = Column(Float, nullable=True)
    
    avg_spo2 = Column(Float, nullable=True) # %
    spo2_min = Column(Float, nullable=True) # %
    odi_dips_per_hour = Column(Float, nullable=True) # events/hr
    hypoxic_burden_pct = Column(Float, nullable=True) # % time < 90%
    
    restlessness_index = Column(Float, nullable=True) # % movement
    
    # Detailed serialized payloads
    hypnogram_data = Column(JSON, nullable=True) # List of epochs with stage & time
    signal_preview_data = Column(JSON, nullable=True) # Downsampled 1-2 min multi-channel waveform preview for Medical Officer
    clinical_explanation = Column(Text, nullable=True) # Plain-language medical officer explanation
    commander_summary = Column(Text, nullable=True) # Operational commander briefing
    recommendations = Column(JSON, nullable=True) # Tactical & clinical action points
    
    personnel = relationship("Personnel", back_populates="uploads")
