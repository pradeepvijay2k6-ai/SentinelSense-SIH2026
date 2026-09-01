"""
Synthetic Multimodal Physiological Sensor Dataset Generator for SentinelSense.
SIH 2026 Problem Statement 26186 (CAPF Stress & Sleep Monitoring).

Generates labeled multi-channel CSVs:
- ecg (mV)
- emg (uV)
- eog (uV)
- spo2 (%)
- acc_x, acc_y, acc_z (g) and motion_mag
- true_stage (W, N1, N2, N3, REM)
"""

import os
import argparse
import numpy as np
import pandas as pd

def generate_ecg_epoch(duration_sec=30, fs=100, hr_bpm=60, hrv_std_ms=50, stress_factor=0.2):
    """
    Generate synthetic ECG with realistic P-Q-R-S-T waveforms and HRV dynamics.
    - Low stress / Deep sleep: Lower HR, high HRV (high RMSSD / RSA).
    - High stress: High HR, low HRV (low RMSSD, high sympathetic tone).
    """
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    # Modulate mean RR interval (seconds)
    mean_rr = 60.0 / hr_bpm
    hrv_sec = (hrv_std_ms / 1000.0) * max(0.15, (1.0 - 0.85 * stress_factor))
    
    # Generate R-peak timings
    r_peaks = []
    current_time = np.random.uniform(0.1, mean_rr)
    while current_time < duration_sec:
        # Add Respiratory Sinus Arrhythmia (0.25 Hz oscillation)
        rsa = 0.04 * (1.0 - stress_factor) * np.sin(2 * np.pi * 0.25 * current_time)
        rr = mean_rr + np.random.normal(0, hrv_sec) + rsa
        rr = max(0.45, min(1.6, rr))
        r_peaks.append(current_time)
        current_time += rr
        
    ecg = np.zeros(num_samples)
    
    # Gaussian P-Q-R-S-T template
    for rp in r_peaks:
        dt = t - rp
        # P wave (at dt = -0.16s, width=0.03s, amp=0.15mV)
        ecg += 0.15 * np.exp(-((dt + 0.16) ** 2) / (2 * 0.025 ** 2))
        # Q wave (at dt = -0.04s, width=0.015s, amp=-0.15mV)
        ecg -= 0.15 * np.exp(-((dt + 0.04) ** 2) / (2 * 0.01 ** 2))
        # R wave (at dt = 0.0s, width=0.018s, amp=1.2mV)
        ecg += 1.25 * np.exp(-(dt ** 2) / (2 * 0.015 ** 2))
        # S wave (at dt = +0.05s, width=0.015s, amp=-0.3mV)
        ecg -= 0.30 * np.exp(-((dt - 0.05) ** 2) / (2 * 0.015 ** 2))
        # T wave (at dt = +0.22s, width=0.05s, amp=0.35mV)
        ecg += 0.35 * np.exp(-((dt - 0.22) ** 2) / (2 * 0.045 ** 2))
        
    # Add baseline wander (respiration) + low amplitude 50Hz electrical noise + EMG artifact
    respiration_noise = 0.05 * np.sin(2 * np.pi * 0.28 * t)
    mains_noise = 0.01 * np.sin(2 * np.pi * 50.0 * t)
    white_noise = np.random.normal(0, 0.02, num_samples)
    
    ecg += respiration_noise + mains_noise + white_noise
    return ecg

def generate_emg_epoch(duration_sec=30, fs=100, stage="N2", stress_factor=0.2):
    """
    Generate submental EMG signal:
    - Wake: High tonic activity (20-60 uV) with frequent motor bursts.
    - N1/N2: Moderate tonic activity (10-25 uV).
    - N3: Low tonic activity (5-15 uV).
    - REM: Muscle atonia (very low baseline, 2-6 uV) with occasional transient micro-twitches.
    """
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    if stage == "W":
        base_amp = 35.0 + 15.0 * stress_factor
        raw_emg = np.random.normal(0, base_amp, num_samples)
        # Add movement bursts
        if np.random.rand() > 0.4:
            burst_start = np.random.randint(0, num_samples - 200)
            raw_emg[burst_start:burst_start+200] *= 3.0
    elif stage in ("N1", "N2"):
        base_amp = 15.0 + 5.0 * stress_factor
        raw_emg = np.random.normal(0, base_amp, num_samples)
    elif stage == "N3":
        base_amp = 8.0 + 2.0 * stress_factor
        raw_emg = np.random.normal(0, base_amp, num_samples)
    elif stage == "REM":
        base_amp = 4.0 # Muscle atonia
        raw_emg = np.random.normal(0, base_amp, num_samples)
        # Phasic muscle twitch
        if np.random.rand() > 0.6:
            tw_start = np.random.randint(0, num_samples - 50)
            raw_emg[tw_start:tw_start+50] += np.random.normal(0, 20.0, 50)
    else:
        raw_emg = np.random.normal(0, 15.0, num_samples)
        
    return raw_emg

def generate_eog_epoch(duration_sec=30, fs=100, stage="N2"):
    """
    Generate Electrooculogram (EOG):
    - Wake: Rapid saccades and blinks (high amplitude sharp deflections, 0.5-2 Hz).
    - N1: Slow rolling eye movements (SEMs, 0.2-0.5 Hz sinusoidal waves).
    - N2/N3: Minimal to no eye movements (flat low amplitude baseline).
    - REM: Rapid Eye Movements (sharp, conjugate episodic bursts of 1-3 Hz waves).
    """
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    eog = np.random.normal(0, 5.0, num_samples)
    
    if stage == "W":
        # Saccades & blinks
        num_blinks = np.random.randint(2, 6)
        for _ in range(num_blinks):
            bp = np.random.uniform(1.0, duration_sec - 1.0)
            dt = t - bp
            eog += 80.0 * np.exp(-(dt ** 2) / (2 * 0.15 ** 2)) * np.random.choice([-1, 1])
    elif stage == "N1":
        # Slow rolling eye movements (0.2 - 0.4 Hz)
        eog += 40.0 * np.sin(2 * np.pi * 0.3 * t + np.random.uniform(0, 2*np.pi))
    elif stage == "REM":
        # Bursts of rapid eye movements
        num_bursts = np.random.randint(2, 5)
        for _ in range(num_bursts):
            bp = np.random.uniform(2.0, duration_sec - 2.0)
            burst_len_sec = np.random.uniform(1.5, 3.5)
            mask = (t >= bp) & (t <= bp + burst_len_sec)
            eog[mask] += 60.0 * np.sin(2 * np.pi * 2.2 * (t[mask] - bp)) * np.hanning(np.sum(mask))
    return eog

def generate_spo2_epoch(duration_sec=30, fs=100, base_spo2=98.0, has_apnea=False, dip_nadir=84.0):
    """
    Generate SpO2 signal:
    - Normal: 96-99% with slight fluctuation.
    - Apnea / Hypoxic dip: Baseline drops over 20-30 seconds towards dip_nadir, then recovers.
    """
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    if not has_apnea:
        spo2 = base_spo2 + 0.3 * np.sin(2 * np.pi * 0.05 * t) + np.random.normal(0, 0.15, num_samples)
        spo2 = np.clip(spo2, 94.0, 100.0)
    else:
        # Desaturation event profile (U-shaped dip)
        dip_profile = (base_spo2 - dip_nadir) * (np.sin(np.pi * t / duration_sec) ** 2)
        spo2 = base_spo2 - dip_profile + np.random.normal(0, 0.2, num_samples)
        spo2 = np.clip(spo2, 70.0, 100.0)
    return spo2

def generate_motion_epoch(duration_sec=30, fs=100, stage="N2", is_restless=False):
    """
    Generate 3-axis Accelerometer (g) & Motion Magnitude:
    - Deep sleep: static gravity vector (e.g. 0.1, 0.2, 0.98), near-zero dynamic motion.
    - Restless / Wake: Significant acceleration spikes and shifts.
    """
    num_samples = int(duration_sec * fs)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    
    # Base orientation (lying on back or side)
    gx = 0.08 + np.random.normal(0, 0.005, num_samples)
    gy = 0.15 + np.random.normal(0, 0.005, num_samples)
    gz = 0.98 + np.random.normal(0, 0.005, num_samples)
    
    if stage == "W" or is_restless:
        # Movement spikes
        spikes = np.random.randint(1, 4)
        for _ in range(spikes):
            sp_time = np.random.uniform(1.0, duration_sec - 1.0)
            dt = t - sp_time
            spike_env = np.exp(-(dt ** 2) / (2 * 0.4 ** 2))
            gx += spike_env * np.random.uniform(-0.5, 0.5)
            gy += spike_env * np.random.uniform(-0.5, 0.5)
            gz += spike_env * np.random.uniform(-0.6, 0.6)
            
    motion_mag = np.sqrt(gx**2 + gy**2 + gz**2) - 1.0 # Dynamic residual
    motion_mag = np.abs(motion_mag)
    return gx, gy, gz, motion_mag

def generate_scenario(scenario_type="well_rested", num_epochs=20, fs=100):
    """
    Generate a full multi-channel recording dataframe for a specific operational scenario:
    1. well_rested: Healthy sleep cycles, high N3 (Deep Sleep), high RMSSD HRV, 0 SpO2 dips.
    2. sleep_deprived: Prolonged Wake/N1, fragmented light sleep, low N3, high restlessness.
    3. high_stress: Hyperarousal, elevated HR (75-90 bpm), suppressed HRV (low RMSSD), high LF/HF.
    4. hypoxic_event: Repeated sleep apnea desaturations (<90% SpO2), tachycardia arousals.
    5. duty_exhaustion: Post-deployment acute fatigue profile.
    """
    epoch_duration = 30
    
    # Define sleep stage sequences and parameters per scenario
    if scenario_type == "well_rested":
        # Healthy progression: Wake -> N1 -> N2 -> N3 -> N3 -> N2 -> REM
        stages = ["W", "N1", "N2", "N3", "N3", "N3", "N2", "REM", "REM", "N2", "N3", "N3", "N2", "REM", "N2", "N3", "N2", "REM", "N2", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 54
        hrv_std = 55
        stress_fac = 0.05
        apnea_prob = 0.0
        restless_prob = 0.05
        
    elif scenario_type == "sleep_deprived":
        # Fragmented, light sleep, frequent wake bouts, zero deep sleep
        stages = ["W", "W", "N1", "W", "N1", "N1", "W", "N1", "W", "N2", "W", "W", "N1", "W", "W", "N1", "W", "N1", "W", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 78
        hrv_std = 25
        stress_fac = 0.78
        apnea_prob = 0.0
        restless_prob = 0.75
        
    elif scenario_type == "high_stress":
        # Sympathetic overdrive: high heart rate, suppressed HRV, hyperarousal
        stages = ["W", "N1", "W", "N1", "N2", "W", "N1", "W", "N1", "W", "N2", "W", "N1", "W", "N1", "W", "N2", "W", "N1", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 88
        hrv_std = 15 # Rigid RR intervals, severe vagal suppression
        stress_fac = 0.95
        apnea_prob = 0.05
        restless_prob = 0.60
        
    elif scenario_type == "hypoxic_event":
        # Sleep apnea pattern: N2/N3 with severe desaturation dips and arousal spikes
        stages = ["W", "N1", "N2", "N2", "W", "N2", "N2", "W", "N2", "N1", "W", "N2", "N2", "W", "N2", "N2", "W", "N2", "N1", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 75
        hrv_std = 32
        stress_fac = 0.65
        apnea_prob = 0.75 # Frequent dips (<88% SpO2)
        restless_prob = 0.50
        
    elif scenario_type == "duty_exhaustion":
        # Severe physical fatigue post-tactical operation
        stages = ["W", "N1", "N2", "N3", "N3", "N3", "N3", "N2", "N3", "N3", "N2", "REM", "N3", "N3", "N2", "N3", "N2", "REM", "N2", "W"]
        stages = (stages * ((num_epochs // len(stages)) + 1))[:num_epochs]
        base_hr = 68
        hrv_std = 26
        stress_fac = 0.70
        apnea_prob = 0.1
        restless_prob = 0.35
    else:
        raise ValueError(f"Unknown scenario: {scenario_type}")
        
    all_ecg, all_emg, all_eog, all_spo2 = [], [], [], []
    all_gx, all_gy, all_gz, all_motion = [], [], [], []
    all_stage_labels = []
    
    for ep_idx, stage in enumerate(stages):
        is_apnea = (np.random.rand() < apnea_prob)
        is_restless = (np.random.rand() < restless_prob)
        
        # Modulate HR slightly by stage (REM and Wake have higher HR than N3)
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
        
        nadir = np.random.uniform(81.0, 87.0) if is_apnea else 97.0
        spo2 = generate_spo2_epoch(epoch_duration, fs, base_spo2=98.0, has_apnea=is_apnea, dip_nadir=nadir)
        gx, gy, gz, motion = generate_motion_epoch(epoch_duration, fs, stage=stage, is_restless=is_restless)
        
        all_ecg.extend(ecg)
        all_emg.extend(emg)
        all_eog.extend(eog)
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
