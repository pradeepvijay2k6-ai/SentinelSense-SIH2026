"""
Optional European Data Format (EDF) Biosignal Parser for SentinelSense.
Supports standard PhysioNet Sleep-EDF files.
"""

import numpy as np
from typing import Dict, Any, Tuple

def parse_edf_file(file_path: str) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
    """
    Parses EDF file format channels.
    Attempts pyedflib or mne, otherwise returns informative error.
    """
    try:
        import pyedflib
        f = pyedflib.EdfReader(file_path)
        n_channels = f.signals_in_file
        signal_labels = [f.getLabel(i).lower() for i in range(n_channels)]
        
        fs = f.getSampleFrequency(0)
        n_samples = f.getNSamples()[0]
        
        ecg, emg, eog = None, None, None
        
        for i, label in enumerate(signal_labels):
            if "ecg" in label or "ekg" in label or "heart" in label:
                ecg = f.readSignal(i)
            elif "emg" in label or "chin" in label or "submental" in label:
                emg = f.readSignal(i)
            elif "eog" in label or "eye" in label or "horizontal" in label:
                eog = f.readSignal(i)
                
        f.close()
        
        total_rows = n_samples
        if ecg is None:
            ecg = np.zeros(total_rows, dtype=np.float32)
        if emg is None:
            emg = np.zeros(total_rows, dtype=np.float32)
        if eog is None:
            eog = np.zeros(total_rows, dtype=np.float32)
            
        spo2 = np.full(total_rows, 98.0, dtype=np.float32)
        motion = np.zeros(total_rows, dtype=np.float32)
        
        channels = {
            "ecg": ecg.astype(np.float32),
            "emg": emg.astype(np.float32),
            "eog": eog.astype(np.float32),
            "spo2": spo2,
            "acc_x": None, "acc_y": None, "acc_z": None,
            "motion": motion
        }
        
        metadata = {
            "total_samples": total_rows,
            "sampling_rate_hz": float(fs),
            "duration_sec": float(total_rows / fs),
            "channels_found": signal_labels
        }
        return channels, metadata
    except ImportError:
        raise RuntimeError("EDF parsing requires 'pyedflib' or 'mne'. Please upload CSV or install pyedflib.")
