"""
Signal Cleaning and Filtering Module for SentinelSense.
Multimodal physiological biosignal processing:
- ECG (Electrocardiogram)
- EMG (Electromyogram)
- EOG (Electrooculogram)
- EEG (Electroencephalogram - Delta, Theta, Alpha, Beta band preservation)
- SpO2 (Pulse Oximetry)
- 50 Hz powerline notch filter & baseline wander removal
"""

import numpy as np
from scipy import signal

def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    """Zero-phase Butterworth bandpass filter using filtfilt."""
    nyq = 0.5 * fs
    low = max(0.01, lowcut / nyq)
    high = min(0.99, highcut / nyq)
    
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.filtfilt(b, a, data)
    return y

def notch_filter(data, freq=50.0, fs=100.0, quality_factor=30.0):
    """50 Hz / 60 Hz mains powerline notch filter."""
    if fs <= 2 * freq:
        return data # Nyquist violation safeguard
    w0 = freq / (fs / 2)
    b, a = signal.iirnotch(w0, quality_factor)
    return signal.filtfilt(b, a, data)

def remove_baseline_wander(data, fs=100.0, cutoff=0.5):
    """High-pass filter to remove respiratory baseline wander and motion artifacts."""
    nyq = 0.5 * fs
    normal_cutoff = max(0.01, min(0.99, cutoff / nyq))
    b, a = signal.butter(2, normal_cutoff, btype='high', analog=False)
    return signal.filtfilt(b, a, data)

def clean_ecg_signal(ecg_raw, fs=100.0):
    """
    Complete cleaning chain for ECG:
    1. Baseline wander removal (>0.5 Hz)
    2. Powerline 50Hz notch filter
    3. Bandpass filter 0.5 - 45.0 Hz
    """
    if len(ecg_raw) < int(fs * 2):
        return ecg_raw
    ecg_clean = remove_baseline_wander(ecg_raw, fs=fs, cutoff=0.5)
    ecg_clean = notch_filter(ecg_clean, freq=50.0, fs=fs, quality_factor=30.0)
    ecg_clean = butter_bandpass_filter(ecg_clean, lowcut=0.5, highcut=45.0, fs=fs, order=3)
    return ecg_clean

def clean_emg_signal(emg_raw, fs=100.0):
    """
    Cleaning chain for submental EMG:
    Bandpass 10.0 - 45.0 Hz + 50Hz notch.
    """
    if len(emg_raw) < int(fs * 2):
        return emg_raw
    emg_clean = notch_filter(emg_raw, freq=50.0, fs=fs, quality_factor=25.0)
    emg_clean = butter_bandpass_filter(emg_clean, lowcut=10.0, highcut=45.0, fs=fs, order=3)
    return emg_clean

def clean_eog_signal(eog_raw, fs=100.0):
    """
    Cleaning chain for EOG:
    Bandpass 0.2 - 15.0 Hz (retains slow rolling and rapid saccades while attenuating EMG crosstalk).
    """
    if len(eog_raw) < int(fs * 2):
        return eog_raw
    eog_clean = butter_bandpass_filter(eog_raw, lowcut=0.2, highcut=15.0, fs=fs, order=2)
    return eog_clean

def clean_eeg_signal(eeg_raw, fs=100.0):
    """
    Cleaning chain for EEG (C3/C4 / Fpz-Cz):
    Bandpass 0.5 - 35.0 Hz + 50Hz powerline notch.
    Preserves Delta (0.5-4Hz), Theta (4-8Hz), Alpha (8-12Hz), and Beta (12-30Hz) rhythms.
    """
    if len(eeg_raw) < int(fs * 2):
        return eeg_raw
    eeg_clean = notch_filter(eeg_raw, freq=50.0, fs=fs, quality_factor=30.0)
    eeg_clean = butter_bandpass_filter(eeg_clean, lowcut=0.5, highcut=35.0, fs=fs, order=3)
    return eeg_clean
