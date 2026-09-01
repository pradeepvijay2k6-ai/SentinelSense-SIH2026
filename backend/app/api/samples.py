import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Personnel, UploadSession
from ..schemas import SampleScenarioItem, AnalysisResultResponse
from ..config import SAMPLE_DATA_DIR
from ..pipeline.processor import process_biosignal_file

router = APIRouter(prefix="/api/samples", tags=["samples"])

SAMPLE_DEFINITIONS = [
    {
        "filename": "well_rested_crpf_0101.csv",
        "scenario_type": "well_rested",
        "personnel_id": "CRPF-0101",
        "title": "Scenario 1: Restorative Sleep (CRPF-0101)",
        "description": "High deep slow-wave sleep (N3), strong parasympathetic vagal recovery (high RMSSD), normal SpO2, low restlessness. Operational status: Fully Fit.",
        "expected_risk": "LOW (0-15)"
    },
    {
        "filename": "sleep_deprived_crpf_0234.csv",
        "scenario_type": "sleep_deprived",
        "personnel_id": "CRPF-0234",
        "title": "Scenario 2: Severe Sleep Deprivation (CRPF-0234)",
        "description": "Fragmented light sleep, zero deep sleep, severe wakefulness bouts, high motor restlessness post-consecutive night shifts. Operational status: High Fatigue Risk.",
        "expected_risk": "HIGH (65-80)"
    },
    {
        "filename": "high_stress_bsf_0512.csv",
        "scenario_type": "high_stress",
        "personnel_id": "BSF-0512",
        "title": "Scenario 3: Hyperarousal & High Stress (BSF-0512)",
        "description": "Border outpost hyperarousal, elevated heart rate (88-95 bpm), rigid autonomic RR intervals (low RMSSD), high Baevsky Stress Index. Operational status: High Stress Risk.",
        "expected_risk": "HIGH (65-85)"
    },
    {
        "filename": "hypoxic_event_itbp_0891.csv",
        "scenario_type": "hypoxic_event",
        "personnel_id": "ITBP-0891",
        "title": "Scenario 4: High Altitude Nocturnal Hypoxia (ITBP-0891)",
        "description": "Repeated SpO2 desaturation dips (<82-87%), high Oxygen Desaturation Index (ODI >60 dips/hr), tachycardia arousals. Operational status: Medical Alert.",
        "expected_risk": "HIGH (65-80)"
    },
    {
        "filename": "duty_exhaustion_cisf_0320.csv",
        "scenario_type": "duty_exhaustion",
        "personnel_id": "CISF-0320",
        "title": "Scenario 5: Post-Deployment Exhaustion (CISF-0320)",
        "description": "Heavy deep sleep rebound accompanied by autonomic recovery exhaustion following a 24-hour tactical duty rotation. Operational status: Moderate Risk.",
        "expected_risk": "MODERATE (35-50)"
    }
]

@router.get("", response_model=List[SampleScenarioItem])
def list_sample_scenarios():
    return [SampleScenarioItem(**s) for s in SAMPLE_DEFINITIONS]

@router.post("/run/{scenario_type}", response_model=AnalysisResultResponse)
def run_sample_scenario(scenario_type: str, db: Session = Depends(get_db)):
    matching = next((s for s in SAMPLE_DEFINITIONS if s["scenario_type"] == scenario_type), None)
    if not matching:
        raise HTTPException(status_code=404, detail=f"Unknown scenario type: {scenario_type}")
        
    csv_path = SAMPLE_DATA_DIR / matching["filename"]
    if not os.path.exists(csv_path):
        # Generate on the fly
        from sample_data.generate_synthetic import generate_scenario
        os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)
        df = generate_scenario(scenario_type=scenario_type, num_epochs=20, fs=100)
        df.to_csv(csv_path, index=False)
        
    code_clean = matching["personnel_id"]
    personnel = db.query(Personnel).filter(Personnel.personnel_id == code_clean).first()
    if not personnel:
        force = "CRPF"
        if "BSF" in code_clean: force = "BSF"
        elif "CISF" in code_clean: force = "CISF"
        elif "ITBP" in code_clean: force = "ITBP"
        
        personnel = Personnel(
            personnel_id=code_clean,
            name=f"Officer {code_clean}",
            force_type=force,
            unit=f"Sector HQ, {force} Ops Unit",
            age=32
        )
        db.add(personnel)
        db.commit()
        db.refresh(personnel)
        
    res = process_biosignal_file(str(csv_path), scenario_tag=scenario_type)
    risk_r = res["risk_results"]
    sleep_r = res["sleep_results"]
    hrv_r = res["hrv_results"]
    spo2_r = res["spo2_results"]
    motion_r = res["motion_results"]
    
    upload_record = UploadSession(
        personnel_id=personnel.id,
        filename=matching["filename"],
        file_type="csv",
        file_path=str(csv_path),
        scenario_tag=scenario_type,
        risk_score=risk_r["risk_score"],
        risk_level=risk_r["risk_level"],
        readiness_verdict=risk_r["readiness_verdict"],
        sleep_efficiency=sleep_r["sleep_efficiency"],
        deep_sleep_pct=sleep_r["deep_sleep_pct"],
        rem_sleep_pct=sleep_r["rem_sleep_pct"],
        light_sleep_pct=sleep_r["light_sleep_pct"],
        wake_pct=sleep_r["wake_pct"],
        total_sleep_time_min=sleep_r["total_sleep_time_min"],
        avg_heart_rate=hrv_r["avg_heart_rate"],
        hrv_rmssd=hrv_r["hrv_rmssd"],
        hrv_sdnn=hrv_r["hrv_sdnn"],
        hrv_lf_hf_ratio=hrv_r["hrv_lf_hf_ratio"],
        baevsky_stress_index=hrv_r["baevsky_stress_index"],
        avg_spo2=spo2_r["avg_spo2"],
        spo2_min=spo2_r["spo2_min"],
        odi_dips_per_hour=spo2_r["odi_dips_per_hour"],
        hypoxic_burden_pct=spo2_r["hypoxic_burden_pct"],
        restlessness_index=motion_r["restlessness_index"],
        hypnogram_data=sleep_r["hypnogram"],
        signal_preview_data=res["waveform_preview"],
        clinical_explanation=risk_r["clinical_explanation"],
        commander_summary=risk_r["commander_summary"],
        recommendations=risk_r["recommendations"]
    )
    db.add(upload_record)
    db.commit()
    db.refresh(upload_record)
    
    return AnalysisResultResponse(
        id=upload_record.id,
        personnel_id=personnel.id,
        personnel_code=personnel.personnel_id,
        filename=upload_record.filename,
        scenario_tag=upload_record.scenario_tag,
        uploaded_at=upload_record.uploaded_at,
        risk_score=risk_r["risk_score"],
        risk_level=risk_r["risk_level"],
        readiness_verdict=risk_r["readiness_verdict"],
        sleep_score=risk_r["sleep_score"],
        stress_score=risk_r["stress_score"],
        fatigue_score=risk_r["fatigue_score"],
        hypoxia_score=risk_r["hypoxia_score"],
        sleep_efficiency=sleep_r["sleep_efficiency"],
        deep_sleep_pct=sleep_r["deep_sleep_pct"],
        rem_sleep_pct=sleep_r["rem_sleep_pct"],
        light_sleep_pct=sleep_r["light_sleep_pct"],
        wake_pct=sleep_r["wake_pct"],
        total_sleep_time_min=sleep_r["total_sleep_time_min"],
        total_recording_time_min=sleep_r["total_recording_time_min"],
        avg_heart_rate=hrv_r["avg_heart_rate"],
        hrv_rmssd=hrv_r["hrv_rmssd"],
        hrv_sdnn=hrv_r["hrv_sdnn"],
        hrv_lf_hf_ratio=hrv_r["hrv_lf_hf_ratio"],
        baevsky_stress_index=hrv_r["baevsky_stress_index"],
        avg_spo2=spo2_r["avg_spo2"],
        spo2_min=spo2_r["spo2_min"],
        odi_dips_per_hour=spo2_r["odi_dips_per_hour"],
        hypoxic_burden_pct=spo2_r["hypoxic_burden_pct"],
        restlessness_index=motion_r["restlessness_index"],
        clinical_explanation=risk_r["clinical_explanation"],
        commander_summary=risk_r["commander_summary"],
        key_drivers=risk_r["key_drivers"],
        recommendations=risk_r["recommendations"],
        hypnogram=sleep_r["hypnogram"],
        waveform_preview=res["waveform_preview"]
    )
