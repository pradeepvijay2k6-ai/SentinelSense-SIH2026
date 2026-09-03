"""
End-to-End Multimodal Biosignal Processing Pipeline for SentinelSense.
Supports: ECG, EMG, EOG, EEG, SpO2, and Actigraphy.
"""

import os
import numpy as np
from typing import Dict, Any

from .csv_parser import parse_and_validate_csv
from .edf_parser import parse_edf_file
from .signal_cleaner import clean_ecg_signal, clean_emg_signal, clean_eog_signal, clean_eeg_signal
from .hrv_analyzer import compute_hrv_metrics
from .spo2_analyzer import analyze_spo2
from .motion_analyzer import compute_motion_metrics
from .sleep_classifier import classify_sleep_epochs
from .risk_scorer import compute_multimodal_risk_scores

def process_biosignal_file(file_path: str, scenario_tag: str = None) -> Dict[str, Any]:
    """
    Executes the full SentinelSense analysis pipeline on an uploaded file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = os.path.splitext(file_path)[1].lower()
    
    # 1. Parse File
    if ext == ".edf":
        channels, metadata = parse_edf_file(file_path)
    else:
        channels, metadata = parse_and_validate_csv(file_path)
        
    fs = metadata["sampling_rate_hz"]
    duration_sec = metadata["duration_sec"]
    
    # 2. Filter & Clean Signals
    ecg_raw = channels["ecg"]
    emg_raw = channels["emg"]
    eog_raw = channels["eog"]
    eeg_raw = channels.get("eeg", np.zeros_like(ecg_raw))
    spo2_raw = channels["spo2"]
    
    ecg_clean = clean_ecg_signal(ecg_raw, fs=fs)
    emg_clean = clean_emg_signal(emg_raw, fs=fs)
    eog_clean = clean_eog_signal(eog_raw, fs=fs)
    eeg_clean = clean_eeg_signal(eeg_raw, fs=fs)
    
    # 3. Motion & Restlessness
    motion_results = compute_motion_metrics(
        acc_x=channels.get("acc_x"),
        acc_y=channels.get("acc_y"),
        acc_z=channels.get("acc_z"),
        motion_mag_raw=channels.get("motion"),
        fs=fs
    )
    motion_arr = motion_results["motion_array"]
    
    # Cleaned channel dictionary for ML classifier
    cleaned_channels = {
        "ecg": ecg_clean,
        "emg": emg_clean,
        "eog": eog_clean,
        "eeg": eeg_clean,
        "spo2": spo2_raw,
        "motion": motion_arr
    }
    
    # 4. PyTorch Sleep Staging on CWT Scalograms
    sleep_results = classify_sleep_epochs(cleaned_channels, fs=fs, epoch_duration_sec=30)
    
    # 5. Cardiovascular & Autonomic HRV
    hrv_results = compute_hrv_metrics(ecg_clean, fs=fs)
    
    # 6. Nocturnal SpO2 Desaturations
    spo2_results = analyze_spo2(spo2_raw, duration_sec=duration_sec, fs=fs)
    
    # 7. Multimodal Fusion Risk Scoring & Explainability
    risk_results = compute_multimodal_risk_scores(
        sleep_metrics=sleep_results,
        hrv_metrics=hrv_results,
        spo2_metrics=spo2_results,
        motion_metrics=motion_results
    )
    
    # 8. Downsampled Waveform Preview for Medical Officer (approx 60-120 seconds, ~1200 points)
    preview_duration_sec = min(duration_sec, 60.0)
    preview_samples = int(preview_duration_sec * fs)
    downsample_factor = max(1, preview_samples // 1200)
    
    waveform_preview = []
    
    for idx in range(0, preview_samples, downsample_factor):
        t_val = round(float(idx / fs), 2)
        waveform_preview.append({
            "time_sec": t_val,
            "ecg_raw": round(float(ecg_raw[idx]), 3),
            "ecg_clean": round(float(ecg_clean[idx]), 3),
            "emg": round(float(emg_clean[idx]), 2),
            "eog": round(float(eog_clean[idx]), 2),
            "eeg": round(float(eeg_clean[idx]), 2),
            "spo2": round(float(spo2_raw[idx]), 1),
            "motion": round(float(motion_arr[idx]), 3)
        })
        
    return {
        "metadata": metadata,
        "scenario_tag": scenario_tag,
        "risk_results": risk_results,
        "sleep_results": sleep_results,
        "hrv_results": hrv_results,
        "spo2_results": spo2_results,
        "motion_results": motion_results,
        "waveform_preview": waveform_preview
    }
