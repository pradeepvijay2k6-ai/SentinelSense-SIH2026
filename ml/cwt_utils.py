"""
Continuous Wavelet Transform (CWT) & Time-Frequency Utilities for SentinelSense.
Computes scalograms/spectrograms from 30s epochs of ECG, EMG, EOG, and Motion.
"""

import numpy as np
from scipy import signal

# Sleep stage class mapping per AASM standards
STAGE_TO_IDX = {"W": 0, "N1": 1, "N2": 2, "N3": 3, "REM": 4}
IDX_TO_STAGE = {0: "W", 1: "N1", 2: "N2", 3: "N3", 4: "REM"}
STAGE_NAMES = {
    "W": "Wake",
    "N1": "Stage 1 (Light Sleep)",
    "N2": "Stage 2 (Core Sleep)",
    "N3": "Stage 3 (Deep / Slow-Wave Sleep)",
    "REM": "REM Sleep"
}

def compute_channel_scalogram(sig, fs=100, n_freqs=32, target_time_bins=64):
    """
    Computes a normalized time-frequency scalogram/spectrogram representation
    for a single 30s biosignal epoch.
    
    Uses SciPy's Continuous Wavelet / Morlet or Spectrogram transform.
    Returns: (n_freqs, target_time_bins) 2D numpy array normalized in [0, 1].
    """
    # Use short-time Fourier transform / Morlet-equivalent bank with logarithmic frequency spacing
    # Frequency range 0.5 Hz to 35 Hz is critical for sleep EEG/EOG/EMG/ECG rhythms
    nperseg = int(fs * 2.0) # 2-second sliding window
    noverlap = int(fs * 1.5) # 75% overlap
    
    freqs, times, Sxx = signal.spectrogram(
        sig,
        fs=fs,
        window='hann',
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=256
    )
    
    # Restrict to 0.5 - 35 Hz
    freq_mask = (freqs >= 0.5) & (freqs <= 35.0)
    if np.sum(freq_mask) < 4:
        freq_mask = freqs <= 35.0
        
    Sxx_sub = Sxx[freq_mask, :]
    
    # Log-power transform
    log_power = np.log1p(Sxx_sub)
    
    # Resample or interpolate to fixed shape (n_freqs, target_time_bins)
    from scipy.ndimage import zoom
    zoom_f = n_freqs / log_power.shape[0]
    zoom_t = target_time_bins / log_power.shape[1]
    
    scalogram = zoom(log_power, (zoom_f, zoom_t), order=1)
    
    # Min-max normalize per epoch
    min_val, max_val = np.min(scalogram), np.max(scalogram)
    if max_val > min_val:
        scalogram = (scalogram - min_val) / (max_val - min_val)
    else:
        scalogram = np.zeros((n_freqs, target_time_bins))
        
    return scalogram.astype(np.float32)

def extract_multimodal_scalogram_tensor(epoch_dict, fs=100):
    """
    Takes a 30s epoch dictionary containing channels:
    - ecg (mV)
    - emg (uV)
    - eog (uV)
    - motion (g/magnitude)
    
    Returns: (4, 32, 64) tensor combining 4 scalogram channels.
    """
    ecg_scalo = compute_channel_scalogram(epoch_dict["ecg"], fs=fs)
    emg_scalo = compute_channel_scalogram(epoch_dict["emg"], fs=fs)
    eog_scalo = compute_channel_scalogram(epoch_dict["eog"], fs=fs)
    motion_scalo = compute_channel_scalogram(epoch_dict.get("motion", np.zeros_like(epoch_dict["ecg"])), fs=fs)
    
    # Stack into 4-channel representation [C, F, T]
    tensor_4ch = np.stack([ecg_scalo, emg_scalo, eog_scalo, motion_scalo], axis=0)
    return tensor_4ch
