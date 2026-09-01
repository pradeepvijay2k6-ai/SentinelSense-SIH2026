import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
STORAGE_DIR = BACKEND_DIR / "storage"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data" / "scenarios"
CHECKPOINT_PATH = BASE_DIR / "ml" / "checkpoint.pt"

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR / "uploads", exist_ok=True)

DATABASE_URL = f"sqlite:///{STORAGE_DIR}/sentinelsense.db"
