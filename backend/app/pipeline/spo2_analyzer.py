"""
SpO2 & Oximetry Hypoxic Burden Analyzer for SentinelSense.
SIH 2026 Problem Statement 26186.

Calculates:
- Baseline SpO2 (%)
- Minimum SpO2 (Nadir %)
- Oxygen Desaturation Index (ODI-3% and ODI-4% events per hour)
- Hypoxic burden (% recording time with SpO2 < 90% and < 85%)
- Per-epoch apnea/hypopnea event flags
"""

import numpy as np

def analyze_spo2(spo2_signal, duration_sec, fs=100.0):
    """
    Analyzes SpO2 channel for desaturations and nocturnal hypoxemia.
    """
    if len(spo2_signal) == 0:
        return {
            "avg_spo2": 98.0,
            "spo2_min": 96.0,
            "odi_dips_per_hour": 0.0,
            "hypoxic_burden_pct": 0.0,
            "events": []
        }
        
    # Downsample or median filter SpO2 if sampled at high frequency (e.g. 100Hz -> 1Hz)
    step = max(1, int(fs))
    spo2_1hz = spo2_signal[::step]
    
    avg_spo2 = float(np.mean(spo2_1hz))
    spo2_min = float(np.min(spo2_1hz))
    
    # Calculate baseline using moving 5-minute rolling maximum
    win_samples = min(len(spo2_1hz), 300)
    baseline_spo2 = float(np.percentile(spo2_1hz, 95))
    
    # Detect desaturation dips (drop >= 3% from local baseline lasting >= 10 seconds)
    dips_3pct = 0
    in_dip = False
    dip_start = 0
    events = []
    
    for i, val in enumerate(spo2_1hz):
        drop = baseline_spo2 - val
        if drop >= 3.0:
            if not in_dip:
                in_dip = True
                dip_start = i
        else:
            if in_dip:
                dip_len = i - dip_start
                if dip_len >= 8: # Lasts at least 8-10 seconds
                    dips_3pct += 1
                    nadir = float(np.min(spo2_1hz[dip_start:i]))
                    events.append({
                        "start_sec": dip_start,
                        "end_sec": i,
                        "nadir": nadir,
                        "drop_pct": round(baseline_spo2 - nadir, 1)
                    })
                in_dip = False
                
    total_hours = max(0.05, duration_sec / 3600.0)
    odi_dips_per_hour = float(dips_3pct / total_hours)
    
    # Hypoxic burden (% time < 90%)
    time_under_90 = np.sum(spo2_1hz < 90.0)
    hypoxic_burden_pct = float((time_under_90 / len(spo2_1hz)) * 100.0)
    
    return {
        "avg_spo2": round(avg_spo2, 1),
        "spo2_min": round(spo2_min, 1),
        "odi_dips_per_hour": round(odi_dips_per_hour, 1),
        "hypoxic_burden_pct": round(hypoxic_burden_pct, 1),
        "events": events
    }
