"""
Synthetic Multimodal Physiological Sensor Dataset Generator for SentinelSense.
Generates labeled multi-channel CSVs:
- ECG (mV)
- EMG (uV)
- EOG (uV)
- EEG (uV) - Delta, Theta, Alpha, Beta rhythms mapped by AASM sleep stage
- SpO2 (%)
- acc_x, acc_y, acc_z (g) and motion_mag
- true_stage (W, N1, N2, N3, REM)
"""

import os
import argparse
import numpy as np
import pandas as pd

def generate_ecg_epoch(duration_sec=30, fs=100, hr_bpm=60, hrv_std_ms=50, stress_factor=0.2):
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    mean_rr = 60.0 / hr_bpm
    hrv_sec = (hrv_std_ms / 1000.0) * max(0.15, (1.0 - 0.85 * stress_factor))
    
    r_peaks = []
    current_time = np.random.uniform(0.1, mean_rr)
    while current_time < duration_sec:
        rsa = 0.04 * (1.0 - stress_factor) * np.sin(2 * np.pi * 0.25 * current_time)
        rr = mean_rr + np.random.normal(0, hrv_sec) + rsa
        rr = max(0.45, min(1.6, rr))
        r_peaks.append(current_time)
        current_time += rr
        
    ecg = np.zeros(num_samples)
    for rp in r_peaks:
        dt = t - rp
        ecg += 0.15 * np.exp(-((dt + 0.16) ** 2) / (2 * 0.025 ** 2))
        ecg -= 0.15 * np.exp(-((dt + 0.04) ** 2) / (2 * 0.01 ** 2))
        ecg += 1.25 * np.exp(-(dt ** 2) / (2 * 0.015 ** 2))
        ecg -= 0.30 * np.exp(-((dt - 0.05) ** 2) / (2 * 0.015 ** 2))
        ecg += 0.35 * np.exp(-((dt - 0.22) ** 2) / (2 * 0.045 ** 2))
        
    respiration_noise = 0.05 * np.sin(2 * np.pi * 0.28 * t)
    powerline_50hz = 0.015 * np.sin(2 * np.pi * 50.0 * t)
    emg_noise = np.random.normal(0, 0.02 * (1.0 + 2.0 * stress_factor), num_samples)
    return ecg + respiration_noise + powerline_50hz + emg_noise

def generate_emg_epoch(duration_sec=30, fs=100, stage="N2", stress_factor=0.2):
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    stage_tone_std = {
        "W": 35.0,
        "N1": 20.0,
        "N2": 12.0,
        "N3": 6.0,
        "REM": 2.5
    }.get(stage, 15.0)
    
    stage_tone_std *= (1.0 + 0.8 * stress_factor)
    base_emg = np.random.normal(0, stage_tone_std, num_samples)
    
    # Butterworth bandpass filter simulation
    b, a = [0.2, 0.4, 0.2], [1.0, -0.6, 0.1]
    raw_emg = np.convolve(base_emg, b, mode='same')
    
    if stage == "W" and np.random.rand() < 0.4:
        burst_start = np.random.randint(0, num_samples - int(fs * 2))
        burst_len = int(fs * np.random.uniform(0.5, 2.0))
        raw_emg[burst_start:burst_start+burst_len] += np.random.normal(0, 70.0, burst_len)
        
    return raw_emg

def generate_eog_epoch(duration_sec=30, fs=100, stage="N2"):
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    eog = np.random.normal(0, 5.0, num_samples)
    
    if stage == "W":
        num_blinks = np.random.randint(2, 6)
        for _ in range(num_blinks):
            bp = np.random.uniform(1.0, duration_sec - 1.0)
            dt = t - bp
            eog += 80.0 * np.exp(-(dt ** 2) / (2 * 0.15 ** 2)) * np.random.choice([-1, 1])
    elif stage == "N1":
        eog += 40.0 * np.sin(2 * np.pi * 0.3 * t + np.random.uniform(0, 2*np.pi))
    elif stage == "REM":
        num_bursts = np.random.randint(2, 5)
        for _ in range(num_bursts):
            bp = np.random.uniform(2.0, duration_sec - 2.0)
            burst_len_sec = np.random.uniform(1.5, 3.5)
            mask = (t >= bp) & (t <= bp + burst_len_sec)
            eog[mask] += 60.0 * np.sin(2 * np.pi * 2.2 * (t[mask] - bp)) * np.hanning(np.sum(mask))
    return eog

def generate_eeg_epoch(duration_sec=30, fs=100, stage="N2"):
    """
    Generate electroencephalogram (EEG) signal according to AASM staging criteria:
    - Wake: High Alpha (8-12 Hz) with posterior eye closure + Beta (>13 Hz) activation
    - N1: Low voltage mixed frequency (Theta 4-7 Hz), Vertex sharp waves
    - N2: Sleep Spindles (12-14 Hz waxing/waning) + K-complexes (high-amplitude slow wave)
    - N3: High-amplitude Slow Wave Activity (Delta 0.5-2.0 Hz, >75 uV)
    - REM: Low-amplitude mixed frequency (sawtooth waves ~2-6 Hz)
    """
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    noise = np.random.normal(0, 4.0, num_samples)
    
    if stage == "W":
        # Alpha rhythm (9.5 Hz) + Beta activity (18 Hz)
        eeg = 25.0 * np.sin(2 * np.pi * 9.5 * t) + 12.0 * np.sin(2 * np.pi * 18.0 * t) + noise
    elif stage == "N1":
        # Theta background (5.2 Hz)
        eeg = 20.0 * np.sin(2 * np.pi * 5.2 * t + 0.3) + 10.0 * np.sin(2 * np.pi * 7.0 * t) + noise
    elif stage == "N2":
        # Theta background + Sleep Spindles (13 Hz) + K-complex
        eeg = 15.0 * np.sin(2 * np.pi * 5.5 * t) + noise
        # Sleep spindle burst
        spindle_t = np.random.uniform(3.0, duration_sec - 3.0)
        sp_mask = (t >= spindle_t) & (t <= spindle_t + 1.2)
        if np.sum(sp_mask) > 0:
            eeg[sp_mask] += 35.0 * np.sin(2 * np.pi * 13.0 * (t[sp_mask] - spindle_t)) * np.hanning(np.sum(sp_mask))
        # K-Complex (sharp negative deflection followed by slower positive wave)
        kc_t = np.random.uniform(10.0, duration_sec - 5.0)
        kc_mask = (t >= kc_t) & (t <= kc_t + 1.0)
        if np.sum(kc_mask) > 0:
            dt_kc = t[kc_mask] - kc_t
            eeg[kc_mask] += -80.0 * np.exp(-((dt_kc - 0.2)**2) / 0.02) + 60.0 * np.exp(-((dt_kc - 0.6)**2) / 0.04)
    elif stage == "N3":
        # Slow Wave Activity / Delta rhythm (0.8 - 1.5 Hz, high amplitude >85 uV)
        eeg = 75.0 * np.sin(2 * np.pi * 1.0 * t) + 40.0 * np.sin(2 * np.pi * 1.8 * t + 1.2) + noise
    elif stage == "REM":
        # Desynchronized low voltage mixed frequency + Sawtooth waves (3.5 Hz)
        eeg = 12.0 * np.sin(2 * np.pi * 5.0 * t) + 10.0 * np.sin(2 * np.pi * 3.5 * t) + noise
    else:
        eeg = 20.0 * np.sin(2 * np.pi * 8.0 * t) + noise
        
    return eeg

def generate_spo2_epoch(duration_sec=30, fs=100, base_spo2=98.0, has_apnea=False, dip_nadir=84.0):
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    if not has_apnea:
        spo2 = base_spo2 + 0.3 * np.sin(2 * np.pi * 0.05 * t) + np.random.normal(0, 0.15, num_samples)
        spo2 = np.clip(spo2, 94.0, 100.0)
    else:
        dip_profile = (base_spo2 - dip_nadir) * (np.sin(np.pi * t / duration_sec) ** 2)
        spo2 = base_spo2 - dip_profile + np.random.normal(0, 0.2, num_samples)
        spo2 = np.clip(spo2, 70.0, 100.0)
    return spo2

def generate_motion_epoch(duration_sec=30, fs=100, stage="N2", is_restless=False):
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    gx = 0.08 + np.random.normal(0, 0.003, num_samples)
    gy = 0.15 + np.random.normal(0, 0.003, num_samples)
    gz = 0.98 + np.random.normal(0, 0.003, num_samples)
    
    if is_restless or stage == "W":
        num_shifts = np.random.randint(1, 4)
        for _ in range(num_shifts):
            st = np.random.uniform(1.0, duration_sec - 3.0)
            slen = np.random.uniform(0.8, 2.5)
            mask = (t >= st) & (t <= st + slen)
            shift_amp = np.random.uniform(0.15, 0.6)
            gx[mask] += shift_amp * np.sin(2 * np.pi * 3.0 * (t[mask] - st))
            gy[mask] += shift_amp * np.cos(2 * np.pi * 2.5 * (t[mask] - st))
            gz[mask] += shift_amp * 0.5 * np.sin(2 * np.pi * 4.0 * (t[mask] - st))
            
    motion_mag = np.abs(np.sqrt(gx**2 + gy**2 + gz**2) - 1.0)
    return gx, gy, gz, motion_mag

def generate_scenario(scenario_type="well_rested", num_epochs=20, fs=100):
    epoch_duration = 30
    
    if scenario_type == "well_rested":
        stages = ["W", "N1", "N2", "N2", "N3", "N3", "N3", "N3", "N3", "N2", "N2", "REM", "REM", "N2", "N3", "N3", "N3", "N2", "REM", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 58
        hrv_std = 55
        stress_fac = 0.05
        apnea_prob = 0.0
        restless_prob = 0.05
        
    elif scenario_type == "sleep_deprived":
        stages = ["W", "W", "N1", "W", "N1", "N1", "W", "N1", "W", "N2", "W", "W", "N1", "W", "W", "N1", "W", "N1", "W", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 78
        hrv_std = 25
        stress_fac = 0.78
        apnea_prob = 0.0
        restless_prob = 0.75
        
    elif scenario_type == "high_stress":
        stages = ["W", "N1", "W", "N1", "N2", "W", "N1", "W", "N1", "W", "N2", "W", "N1", "W", "N1", "W", "N2", "W", "N1", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 88
        hrv_std = 15
        stress_fac = 0.95
        apnea_prob = 0.05
        restless_prob = 0.60
        
    elif scenario_type == "hypoxic_event":
        stages = ["W", "N1", "N2", "N2", "W", "N2", "N2", "W", "N2", "N1", "W", "N2", "N2", "W", "N2", "N2", "W", "N2", "N1", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 75
        hrv_std = 32
        stress_fac = 0.65
        apnea_prob = 0.75
        restless_prob = 0.50
        
    elif scenario_type == "duty_exhaustion":
        stages = ["W", "N1", "N2", "N3", "N3", "N3", "N3", "N2", "N3", "N3", "N2", "REM", "N3", "N3", "N2", "N3", "N2", "REM", "N2", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 68
        hrv_std = 26
        stress_fac = 0.70
        apnea_prob = 0.1
        restless_prob = 0.35
    else:
        raise ValueError(f"Unknown scenario: {scenario_type}")
        
    all_ecg, all_emg, all_eog, all_eeg, all_spo2 = [], [], [], [], []
    all_gx, all_gy, all_gz, all_motion = [], [], [], []
    all_stage_labels = []
    
    for ep_idx, stage in enumerate(stages):
        is_apnea = (np.random.rand() < apnea_prob)
        is_restless = (np.random.rand() < restless_prob)
        
        st_hr = base_hr
        if stage == "N3":
            st_hr -= 6
        elif stage == "REM":
            st_hr += 5
        elif stage == "W":
            st_hr += 8
            
        ecg = generate_ecg_epoch(epoch_duration, fs, hr_bpm=st_hr, hrv_std_ms=hrv_std, stress_factor=stress_fac)
        emg = generate_emg_epoch(epoch_duration, fs, stage=stage, stress_factor=stress_fac)
        eog = generate_eog_epoch(epoch_duration, fs, stage=stage)
        eeg = generate_eeg_epoch(epoch_duration, fs, stage=stage)
        
        nadir = np.random.uniform(81.0, 87.0) if is_apnea else 97.0
        spo2 = generate_spo2_epoch(epoch_duration, fs, base_spo2=98.0, has_apnea=is_apnea, dip_nadir=nadir)
        gx, gy, gz, motion = generate_motion_epoch(epoch_duration, fs, stage=stage, is_restless=is_restless)
        
        all_ecg.extend(ecg)
        all_emg.extend(emg)
        all_eog.extend(eog)
        all_eeg.extend(eeg)
        all_spo2.extend(spo2)
        all_gx.extend(gx)
        all_gy.extend(gy)
        all_gz.extend(gz)
        all_motion.extend(motion)
        all_stage_labels.extend([stage] * len(ecg))
        
    timestamps = np.round(np.arange(len(all_ecg)) / fs, 3)
    
    df = pd.DataFrame({
        "timestamp_sec": timestamps,
        "ecg_mv": np.round(all_ecg, 4),
        "emg_uv": np.round(all_emg, 2),
        "eog_uv": np.round(all_eog, 2),
        "eeg_uv": np.round(all_eeg, 2),
        "spo2_pct": np.round(all_spo2, 1),
        "acc_x": np.round(all_gx, 3),
        "acc_y": np.round(all_gy, 3),
        "acc_z": np.round(all_gz, 3),
        "motion_mag": np.round(all_motion, 4),
        "sleep_stage": all_stage_labels
    })
    return df

def generate_all_sample_files(output_dir="sample_data/scenarios", num_epochs=20):
    os.makedirs(output_dir, exist_ok=True)
    scenarios = [
        ("well_rested_crpf_0101.csv", "well_rested", "CRPF-0101"),
        ("sleep_deprived_crpf_0234.csv", "sleep_deprived", "CRPF-0234"),
        ("high_stress_bsf_0512.csv", "high_stress", "BSF-0512"),
        ("hypoxic_event_itbp_0891.csv", "hypoxic_event", "ITBP-0891"),
        ("duty_exhaustion_cisf_0320.csv", "duty_exhaustion", "CISF-0320")
    ]
    
    created_files = []
    for filename, scen_type, officer_id in scenarios:
        filepath = os.path.join(output_dir, filename)
        df = generate_scenario(scenario_type=scen_type, num_epochs=num_epochs, fs=100)
        df.to_csv(filepath, index=False)
        print(f"Generated {filename} ({len(df)} rows, {num_epochs} epochs, officer={officer_id})")
        created_files.append(filepath)
    return created_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic biosignal datasets for SentinelSense")
    parser.add_argument("--output_dir", type=str, default="sample_data/scenarios", help="Output directory")
    parser.add_argument("--num_epochs", type=int, default=20, help="Number of 30-second epochs (default: 20 -> 10 mins)")
    args = parser.parse_args()
    generate_all_sample_files(args.output_dir, args.num_epochs)
