import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Personnel, UploadSession
from ..schemas import AnalysisResultResponse
from ..config import STORAGE_DIR
from ..pipeline.processor import process_biosignal_file

router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("", response_model=AnalysisResultResponse)
async def upload_and_analyze_file(
    file: UploadFile = File(...),
    personnel_code: str = Form(...),
    scenario_tag: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    code_clean = personnel_code.strip().upper()
    if not code_clean:
        raise HTTPException(status_code=400, detail="Personnel code is required")
        
    personnel = db.query(Personnel).filter(Personnel.personnel_id == code_clean).first()
    if not personnel:
        # Determine force type from prefix
        force = "CRPF"
        if "BSF" in code_clean: force = "BSF"
        elif "CISF" in code_clean: force = "CISF"
        elif "ITBP" in code_clean: force = "ITBP"
        elif "SSB" in code_clean: force = "SSB"
        
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
        
    # Save uploaded file to storage
    upload_dir = STORAGE_DIR / "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    saved_filename = f"{personnel.personnel_id}_{file.filename}"
    file_path = upload_dir / saved_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Execute Multimodal Pipeline
        res = process_biosignal_file(str(file_path), scenario_tag=scenario_tag)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Pipeline processing failed: {str(e)}")
        
    risk_r = res["risk_results"]
    sleep_r = res["sleep_results"]
    hrv_r = res["hrv_results"]
    spo2_r = res["spo2_results"]
    motion_r = res["motion_results"]
    
    # Save to database
    upload_record = UploadSession(
        personnel_id=personnel.id,
        filename=file.filename,
        file_type="csv" if file.filename.endswith(".csv") else "edf",
        file_path=str(file_path),
        scenario_tag=scenario_tag,
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
