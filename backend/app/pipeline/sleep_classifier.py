"""
PyTorch Deep ConvNet Sleep Classifier Module for SentinelSense.
SIH 2026 Problem Statement 26186.

Extracts 30s epochs from cleaned multimodal signals, computes CWT scalograms,
and runs batch inference using SentinelSleepNet (ResNet-18 style CNN).
Calculates AASM sleep architecture:
- Sleep Efficiency (%)
- Deep Sleep N3 (%)
- REM Sleep (%)
- Light Sleep N1+N2 (%)
- Wake (%)
- Total Sleep Time (TST) & Total Recording Time (TRT)
"""

import os
import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, Any, List

from .cwt_transform import extract_multimodal_scalogram_tensor, IDX_TO_STAGE
from ..config import CHECKPOINT_PATH
from ml.model import SentinelSleepNet

# Global cached model
_MODEL = None
_DEVICE = "cpu"

def get_loaded_model():
    global _MODEL, _DEVICE
    if _MODEL is None:
        _DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        _MODEL = SentinelSleepNet(in_channels=4, num_classes=5)
        if os.path.exists(CHECKPOINT_PATH):
            try:
                state_dict = torch.load(CHECKPOINT_PATH, map_location=_DEVICE, weights_only=True)
                _MODEL.load_state_dict(state_dict)
                print(f"Loaded SentinelSleepNet weights from {CHECKPOINT_PATH} onto {_DEVICE}")
            except Exception as e:
                print(f"Warning: Could not load checkpoint ({e}). Running with default initialization.")
        _MODEL.to(_DEVICE)
        _MODEL.eval()
    return _MODEL, _DEVICE

def classify_sleep_epochs(
    channels_dict: Dict[str, np.ndarray],
    fs: float = 100.0,
    epoch_duration_sec: int = 30
) -> Dict[str, Any]:
    """
    Splits recording into 30s epochs, runs PyTorch inference, and computes hypnogram metrics.
    """
    model, device = get_loaded_model()
    
    ecg = channels_dict["ecg"]
    emg = channels_dict["emg"]
    eog = channels_dict["eog"]
    motion = channels_dict.get("motion", np.zeros_like(ecg))
    spo2 = channels_dict.get("spo2", np.full_like(ecg, 98.0))
    
    total_samples = len(ecg)
    samples_per_epoch = int(epoch_duration_sec * fs)
    num_epochs = max(1, total_samples // samples_per_epoch)
    
    epoch_tensors = []
    epoch_metadata = []
    
    for ep in range(num_epochs):
        start = ep * samples_per_epoch
        end = min(total_samples, (ep + 1) * samples_per_epoch)
        
        ep_ecg = ecg[start:end]
        ep_emg = emg[start:end]
        ep_eog = eog[start:end]
        ep_motion = motion[start:end] if motion is not None else np.zeros(len(ep_ecg))
        ep_spo2 = spo2[start:end] if spo2 is not None else np.full(len(ep_ecg), 98.0)
        
        # Pad if short
        if len(ep_ecg) < samples_per_epoch:
            pad_len = samples_per_epoch - len(ep_ecg)
            ep_ecg = np.pad(ep_ecg, (0, pad_len), 'edge')
            ep_emg = np.pad(ep_emg, (0, pad_len), 'edge')
            ep_eog = np.pad(ep_eog, (0, pad_len), 'edge')
            ep_motion = np.pad(ep_motion, (0, pad_len), 'edge')
            ep_spo2 = np.pad(ep_spo2, (0, pad_len), 'edge')
            
        epoch_dict = {
            "ecg": ep_ecg,
            "emg": ep_emg,
            "eog": ep_eog,
            "motion": ep_motion
        }
        
        tensor_4ch = extract_multimodal_scalogram_tensor(epoch_dict, fs=fs)
        epoch_tensors.append(tensor_4ch)
        
        # Check for apnea / hypoxia in this epoch (SpO2 drops < 92%)
        has_apnea = bool(np.min(ep_spo2) < 91.0)
        has_motion = bool(np.max(ep_motion) > 0.08 or np.mean(ep_motion) > 0.03)
        
        time_sec = ep * epoch_duration_sec
        mins = int(time_sec // 60)
        secs = int(time_sec % 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        epoch_metadata.append({
            "epoch_index": ep,
            "timestamp_sec": float(time_sec),
            "time_str": time_str,
            "is_apnea_event": has_apnea,
            "is_motion_event": has_motion
        })
        
    # Batch inference with PyTorch
    batch_tensors = torch.tensor(np.array(epoch_tensors, dtype=np.float32)).to(device)
    with torch.no_grad():
        logits = model(batch_tensors)
        probs = F.softmax(logits, dim=1).cpu().numpy()
        pred_indices = np.argmax(probs, axis=1)
        
    hypnogram = []
    stage_counts = {"W": 0, "N1": 0, "N2": 0, "N3": 0, "REM": 0}
    
    for i, meta in enumerate(epoch_metadata):
        stage_idx = int(pred_indices[i])
        stage_str = IDX_TO_STAGE[stage_idx]
        conf = float(probs[i, stage_idx])
        
        stage_counts[stage_str] += 1
        
        hypnogram.append({
            "epoch_index": meta["epoch_index"],
            "timestamp_sec": meta["timestamp_sec"],
            "time_str": meta["time_str"],
            "stage": stage_str,
            "confidence": round(conf, 3),
            "is_apnea_event": meta["is_apnea_event"],
            "is_motion_event": meta["is_motion_event"]
        })
        
    # Sleep Architecture Calculations
    total_epochs = len(hypnogram)
    total_recording_time_min = (total_epochs * epoch_duration_sec) / 60.0
    
    sleep_epochs = stage_counts["N1"] + stage_counts["N2"] + stage_counts["N3"] + stage_counts["REM"]
    total_sleep_time_min = (sleep_epochs * epoch_duration_sec) / 60.0
    
    sleep_efficiency = (sleep_epochs / total_epochs) * 100.0 if total_epochs > 0 else 0.0
    deep_sleep_pct = (stage_counts["N3"] / total_epochs) * 100.0 if total_epochs > 0 else 0.0
    rem_sleep_pct = (stage_counts["REM"] / total_epochs) * 100.0 if total_epochs > 0 else 0.0
    light_sleep_pct = ((stage_counts["N1"] + stage_counts["N2"]) / total_epochs) * 100.0 if total_epochs > 0 else 0.0
    wake_pct = (stage_counts["W"] / total_epochs) * 100.0 if total_epochs > 0 else 0.0
    
    return {
        "hypnogram": hypnogram,
        "total_recording_time_min": round(total_recording_time_min, 1),
        "total_sleep_time_min": round(total_sleep_time_min, 1),
        "sleep_efficiency": round(sleep_efficiency, 1),
        "deep_sleep_pct": round(deep_sleep_pct, 1),
        "rem_sleep_pct": round(rem_sleep_pct, 1),
        "light_sleep_pct": round(light_sleep_pct, 1),
        "wake_pct": round(wake_pct, 1),
        "stage_counts": stage_counts
    }
