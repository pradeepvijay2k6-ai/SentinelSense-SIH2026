"""
Motion & Restlessness Analyzer for SentinelSense.
SIH 2026 Problem Statement 26186.

Computes:
- Resultant vector magnitude from 3-axis accelerometer
- Restlessness index (% of epochs with significant body movements)
- Dynamic motion energy
"""

import numpy as np

def compute_motion_metrics(acc_x, acc_y, acc_z, motion_mag_raw=None, fs=100.0, epoch_duration=30):
    """
    Analyzes physical body movements, position shifts, and motor restlessness.
    """
    total_samples = len(acc_x) if acc_x is not None else len(motion_mag_raw)
    num_epochs = max(1, total_samples // (epoch_duration * int(fs)))
    samples_per_epoch = epoch_duration * int(fs)
    
    if motion_mag_raw is not None and len(motion_mag_raw) > 0:
        motion = np.array(motion_mag_raw)
    elif acc_x is not None and acc_y is not None and acc_z is not None:
        gx = np.array(acc_x)
        gy = np.array(acc_y)
        gz = np.array(acc_z)
        # Dynamic acceleration residual
        norm = np.sqrt(gx**2 + gy**2 + gz**2)
        motion = np.abs(norm - 1.0)
    else:
        motion = np.zeros(total_samples)
        
    epoch_motion_levels = []
    restless_epoch_count = 0
    movement_threshold = 0.08 # Significant movement threshold in g
    
    for ep in range(num_epochs):
        start = ep * samples_per_epoch
        end = min(total_samples, (ep + 1) * samples_per_epoch)
        if start < end:
            ep_motion = motion[start:end]
            mean_motion = float(np.mean(ep_motion))
            max_motion = float(np.max(ep_motion))
            is_restless = bool(max_motion > movement_threshold or mean_motion > 0.03)
            if is_restless:
                restless_epoch_count += 1
            epoch_motion_levels.append({
                "epoch_index": ep,
                "mean_motion_g": round(mean_motion, 4),
                "max_motion_g": round(max_motion, 4),
                "is_restless": is_restless
            })
            
    restlessness_index = float((restless_epoch_count / num_epochs) * 100.0) if num_epochs > 0 else 0.0
    
    return {
        "restlessness_index": round(restlessness_index, 1),
        "mean_motion_g": round(float(np.mean(motion)), 4) if len(motion) > 0 else 0.0,
        "epoch_motion_details": epoch_motion_levels,
        "motion_array": motion
    }
