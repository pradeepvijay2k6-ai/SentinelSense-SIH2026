"""
CWT Transformation Pipeline wrapper for SentinelSense.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from ml.cwt_utils import compute_channel_scalogram, extract_multimodal_scalogram_tensor, STAGE_TO_IDX, IDX_TO_STAGE, STAGE_NAMES
