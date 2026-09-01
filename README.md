# SentinelSense (SIH 2026 - Problem Statement 26186)
### AI-Powered Multimodal Biosignal Analytics for CAPF Operational Stress & Fatigue Monitoring

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-teal.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.0-61dafb.svg)](https://react.dev/)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind-CSS-38bdf8.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SentinelSense** is an end-to-end intelligent physiological monitoring and tactical readiness platform built for the **Ministry of Home Affairs (MHA)** and **Central Armed Police Forces (CRPF, BSF, ITBP, CISF, SSB)**. It ingests multimodal biosignal telemetry (ECG, EMG, EOG, SpO2, and 3-axis Accelerometer) from wearable sensors to deliver:
- Continuous **AASM 5-stage sleep staging** via PyTorch Continuous Wavelet Transform (CWT) CNNs (`SentinelSleepNet`).
- Real-time **Autonomic Heart Rate Variability (HRV)** & **Baevsky Stress Index** extraction.
- **Hypoxic burden & nocturnal desaturation index (ODI-3%)** detection.
- **Dual-role explainable intelligence:** A detailed clinical diagnostic workbench for **Medical Officers** and privacy-preserved operational duty readiness rosters for **Field Commanders**.

---

## 🚀 Key Features

1. **Multimodal Biosignal Ingestion:**
   - Supports flexible multi-channel **CSV** telemetry and clinical **EDF** (European Data Format).
   - Automated sampling rate estimation, baseline wander removal, 50Hz powerline notch filtering, and Butterworth bandpass filtering.

2. **Continuous Wavelet Transform (CWT) Deep Learning Staging:**
   - Converts multi-channel time-series epochs into multi-frequency spectrogram scalograms.
   - ResNet-18-style convolutional backbone classifies 30-second epochs into AASM stages: **Wake (W)**, **N1**, **N2**, **N3 (Deep SWS)**, and **REM**.

3. **Composite Autonomic & Fatigue Risk Engine (0–100 Scale):**
   - Fuses sleep architecture (efficiency, N3/REM deficit), HRV vagal tone ($RMSSD$, $SDNN$, $LF/HF$, Baevsky Index), respiratory oxygen desaturation ($ODI$, $SpO_2$ nadir), and physical restlessness.
   - Classified into distinct operational risk bands:
     - 🟢 **LOW (0–30):** *Fit for Tactical Duty*
     - 🟡 **MODERATE (31–60):** *Elevated Fatigue / Routine Shift Rotation*
     - 🔴 **HIGH (61–100):** *Critical Stress & Sleep Deprivation / Medical Review*

4. **Privacy-Preserved Role-Based Access Control (RBAC):**
   - **Medical Officer Mode:** Unrestricted access to raw 5-channel interactive oscilloscopes, epoch-level hypnograms, PSD frequency spectra, and clinical differential narratives.
   - **Commander Mode:** Anonymized officer UID, high-level readiness verdicts, battalion risk rosters, and operational directives without exposing intimate biometric records.

5. **Simulated Operational Scenarios (Instant Testing):**
   - Built-in physiologically realistic scenario generators for:
     1. Well-Rested Patrol Officer
     2. Acute Sleep-Deprived Night Sentry
     3. High-Stress Tactical Operation
     4. High-Altitude Hypoxic Sleep Apnea (ITBP Sector)
     5. Cumulative Multi-Day Duty Exhaustion

---

## 📂 Project Architecture

```
SentinelSense-SIH2026/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI endpoint routers (personnel, upload, analysis, roster, samples)
│   │   ├── pipeline/        # Signal cleaning, Pan-Tompkins HRV, SpO2 ODI, Sleep Classifier, Risk Engine
│   │   ├── config.py        # Environment & filesystem paths
│   │   ├── database.py      # SQLite / SQLAlchemy session
│   │   ├── models.py        # Personnel & UploadSession ORM models
│   │   ├── schemas.py       # Pydantic v2 schemas
│   │   └── main.py          # FastAPI application entrypoint
│   └── requirements.txt
├── ml/
│   ├── model.py             # SentinelSleepNet (ResNet-18 4-channel CNN)
│   ├── cwt_utils.py         # SciPy spectrogram & scalogram transformation
│   ├── train_synthetic.py   # Training script for PyTorch classifier
│   └── checkpoint.pt        # Pre-trained deep learning weights (99.6% acc)
├── sample_data/
│   ├── generate_synthetic.py # 5-scenario physiological multi-channel generator
│   └── scenarios/           # Pre-built benchmark CSV datasets
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API client
│   │   ├── components/      # RiskGauge, HypnogramChart, SignalViewer, MetricsGrid, etc.
│   │   ├── pages/           # UploadPage, ResultPage, PersonnelHistoryPage, RosterPage
│   │   └── types/           # TypeScript interfaces & definitions
│   ├── vite.config.ts
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Quickstart & Local Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Git**

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/pradeep/SentinelSense-SIH2026.git
cd SentinelSense-SIH2026

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies & PyTorch
pip install -r backend/requirements.txt

# Start FastAPI backend server (port 8000)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
# In a new terminal window:
cd frontend

# Install frontend dependencies
npm install

# Start Vite dev server (port 5173 with proxy to 8000)
npm run dev
```

Open your browser at **`http://localhost:5173`**.

---

## 🧪 CSV Telemetry Schema

The pipeline automatically parses CSV files matching standard wearable exports. Timestamp column can be ISO format or relative seconds:

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `timestamp` / `time` | float / str | Sampling timestamps (100 Hz nominal) |
| `ecg` / `ecg_raw` | float (mV) | Single or multi-lead electrocardiogram |
| `emg` | float (uV) | Electromyogram (submental / chin tone) |
| `eog` | float (uV) | Electrooculogram (saccades / REM tracking) |
| `spo2` | float (%) | Pulse oximetry blood oxygen saturation |
| `acc_x`, `acc_y`, `acc_z` | float (g) | 3-axis tri-axial accelerometer |
| `motion_mag` | float (g) | Vector magnitude $\sqrt{x^2+y^2+z^2}$ |

---

## 🐳 Running with Docker Compose

```bash
docker-compose up --build
```
The application will be accessible at `http://localhost:5173` with the backend API at `http://localhost:8000/docs`.

---

## 👥 Contributors & SIH 2026 Team
Built for **Smart India Hackathon 2026**, **Problem Statement 26186** (*Predictive Stress, Fatigue & Welfare Monitoring for CAPF Personnel*).
