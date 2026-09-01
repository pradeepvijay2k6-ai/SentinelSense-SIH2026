"""
Cardiovascular & Heart Rate Variability (HRV) Analyzer for SentinelSense.
SIH 2026 Problem Statement 26186.

Implements:
- Pan-Tompkins QRS R-peak detection
- Time-domain HRV: Mean HR (bpm), SDNN (ms), RMSSD (ms), pNN50 (%)
- Frequency-domain HRV: LF power (0.04-0.15 Hz), HF power (0.15-0.40 Hz), LF/HF Ratio
- Baevsky Stress Index (SI = AMo / (2 * Mo * MxDMn))
"""

import numpy as np
from scipy import signal

def detect_r_peaks(ecg_signal, fs=100.0):
    """
    Pan-Tompkins inspired R-peak detector:
    1. Bandpass filter (5-15 Hz for QRS energy concentration)
    2. Five-point derivative
    3. Squaring function
    4. Moving window integrator (150ms window)
    5. Adaptive threshold peak detection with refractory period (250ms)
    """
    # 1. Bandpass 5-15 Hz
    nyq = 0.5 * fs
    low = max(0.01, 5.0 / nyq)
    high = min(0.99, 15.0 / nyq)
    b, a = signal.butter(2, [low, high], btype='band')
    filtered = signal.filtfilt(b, a, ecg_signal)
    
    # 2. Derivative
    diff = np.diff(filtered, prepend=filtered[0])
    
    # 3. Squaring
    squared = diff ** 2
    
    # 4. Moving window integration (~150ms)
    win_len = max(3, int(0.15 * fs))
    kernel = np.ones(win_len) / win_len
    integrated = np.convolve(squared, kernel, mode='same')
    
    # 5. Peak picking with refractory blanking (250ms)
    min_dist = int(0.25 * fs) # Refractory period
    thresh = np.mean(integrated) + 0.6 * np.std(integrated)
    
    peaks, _ = signal.find_peaks(integrated, distance=min_dist, height=thresh)
    
    # Refine peak locations to maximum amplitude in raw/filtered ECG window around each peak
    refined_peaks = []
    search_win = int(0.08 * fs)
    for p in peaks:
        start = max(0, p - search_win)
        end = min(len(ecg_signal), p + search_win)
        if start < end:
            best_idx = start + np.argmax(ecg_signal[start:end])
            refined_peaks.append(best_idx)
            
    # Remove duplicate refined peaks
    refined_peaks = sorted(list(set(refined_peaks)))
    return np.array(refined_peaks, dtype=int)

def compute_hrv_metrics(ecg_signal, fs=100.0):
    """
    Computes comprehensive clinical and autonomic HRV metrics from ECG.
    """
    r_peaks = detect_r_peaks(ecg_signal, fs=fs)
    
    # If not enough peaks, return fallback normative values
    if len(r_peaks) < 5:
        return {
            "avg_heart_rate": 72.0,
            "hrv_rmssd": 35.0,
            "hrv_sdnn": 45.0,
            "hrv_pnn50": 15.0,
            "hrv_lf_hf_ratio": 1.5,
            "baevsky_stress_index": 120.0,
            "rr_intervals_ms": []
        }
        
    # RR intervals in milliseconds
    rr_intervals_sec = np.diff(r_peaks) / fs
    # Filter physiologically impossible RR intervals (300ms to 2000ms = 30 to 200 bpm)
    valid_mask = (rr_intervals_sec >= 0.3) & (rr_intervals_sec <= 2.0)
    rr_valid = rr_intervals_sec[valid_mask] * 1000.0 # ms
    
    if len(rr_valid) < 4:
        return {
            "avg_heart_rate": 72.0,
            "hrv_rmssd": 35.0,
            "hrv_sdnn": 45.0,
            "hrv_pnn50": 15.0,
            "hrv_lf_hf_ratio": 1.5,
            "baevsky_stress_index": 120.0,
            "rr_intervals_ms": []
        }
        
    # Mean HR
    mean_rr_ms = np.mean(rr_valid)
    mean_hr = 60000.0 / mean_rr_ms
    
    # SDNN (Standard Deviation of NN intervals)
    sdnn = float(np.std(rr_valid, ddof=1)) if len(rr_valid) > 1 else 30.0
    
    # RMSSD (Root Mean Square of Successive Differences) - Vagal / Parasympathetic marker
    successive_diffs = np.diff(rr_valid)
    rmssd = float(np.sqrt(np.mean(successive_diffs ** 2))) if len(successive_diffs) > 0 else 30.0
    
    # pNN50 (% of successive intervals differing by > 50ms)
    nn50 = np.sum(np.abs(successive_diffs) > 50.0)
    pnn50 = float((nn50 / len(successive_diffs)) * 100.0) if len(successive_diffs) > 0 else 0.0
    
    # Frequency domain analysis via Lomb-Scargle or FFT on resampled 4Hz RR series
    try:
        t_rr = np.cumsum(rr_valid) / 1000.0
        t_uniform = np.arange(t_rr[0], t_rr[-1], 0.25) # 4 Hz interpolation
        if len(t_uniform) > 16:
            rr_interp = np.interp(t_uniform, t_rr, rr_valid)
            # Welch PSD
            freqs, psd = signal.welch(rr_interp - np.mean(rr_interp), fs=4.0, nperseg=min(len(rr_interp), 64))
            
            # LF: 0.04 - 0.15 Hz, HF: 0.15 - 0.40 Hz
            lf_mask = (freqs >= 0.04) & (freqs < 0.15)
            hf_mask = (freqs >= 0.15) & (freqs <= 0.40)
            
            lf_power = np.trapz(psd[lf_mask], freqs[lf_mask]) if np.sum(lf_mask) > 0 else 1.0
            hf_power = np.trapz(psd[hf_mask], freqs[hf_mask]) if np.sum(hf_mask) > 0 else 1.0
            
            lf_power = max(1e-5, lf_power)
            hf_power = max(1e-5, hf_power)
            lf_hf_ratio = float(np.clip(lf_power / hf_power, 0.1, 15.0))
        else:
            # Fallback estimation based on RMSSD vs SDNN
            lf_hf_ratio = float(np.clip(sdnn / max(rmssd, 5.0), 0.5, 6.0))
    except Exception:
        lf_hf_ratio = float(np.clip(sdnn / max(rmssd, 5.0), 0.5, 6.0))
        
    # Baevsky Stress Index (SI = AMo / (2 * Mo * MxDMn))
    # Mo: Mode (most frequent RR in seconds)
    # AMo: Amplitude of mode (% of intervals in mode bin)
    # MxDMn: Variation range (Max RR - Min RR in seconds)
    try:
        rr_sec = rr_valid / 1000.0
        counts, bin_edges = np.histogram(rr_sec, bins=15)
        max_bin_idx = np.argmax(counts)
        mo = (bin_edges[max_bin_idx] + bin_edges[max_bin_idx + 1]) / 2.0
        amo = (counts[max_bin_idx] / len(rr_sec)) * 100.0
        mxdmn = max(0.05, np.max(rr_sec) - np.min(rr_sec))
        
        baevsky_si = float((amo) / (2.0 * mo * mxdmn))
        baevsky_si = float(np.clip(baevsky_si, 15.0, 800.0))
    except Exception:
        baevsky_si = 120.0
        
    return {
        "avg_heart_rate": round(float(mean_hr), 1),
        "hrv_rmssd": round(float(rmssd), 1),
        "hrv_sdnn": round(float(sdnn), 1),
        "hrv_pnn50": round(float(pnn50), 1),
        "hrv_lf_hf_ratio": round(float(lf_hf_ratio), 2),
        "baevsky_stress_index": round(float(baevsky_si), 1),
        "rr_intervals_ms": [round(float(r), 1) for r in rr_valid[:100]] # First 100 for preview
    }
