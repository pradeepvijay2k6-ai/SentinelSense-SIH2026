from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UploadSession, Personnel
from ..schemas import AnalysisResultResponse

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.get("/{id}", response_model=AnalysisResultResponse)
def get_analysis_by_id(id: int, db: Session = Depends(get_db)):
    u = db.query(UploadSession).filter(UploadSession.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Analysis session not found")
        
    personnel = db.query(Personnel).filter(Personnel.id == u.personnel_id).first()
    personnel_code = personnel.personnel_id if personnel else "UNKNOWN"
    
    # Reconstruct drivers based on metrics
    key_drivers = []
    if (u.hrv_rmssd or 45.0) < 28.0:
        key_drivers.append(f"Vagal suppression with low HRV RMSSD ({u.hrv_rmssd:.1f} ms, normal >45 ms)")
    if (u.baevsky_stress_index or 90.0) > 200.0:
        key_drivers.append(f"Sympathetic autonomic strain: Baevsky Stress Index ({u.baevsky_stress_index:.0f}, normal <120)")
    if (u.deep_sleep_pct or 20.0) < 12.0:
        key_drivers.append(f"Deep Slow-Wave sleep deficit (N3: {u.deep_sleep_pct:.1f}%, recommended 15-25%)")
    if (u.sleep_efficiency or 85.0) < 75.0:
        key_drivers.append(f"Severely fragmented sleep architecture (Efficiency: {u.sleep_efficiency:.1f}%)")
    if (u.odi_dips_per_hour or 0.0) >= 12.0:
        key_drivers.append(f"Frequent nocturnal oxygen desaturations (ODI: {u.odi_dips_per_hour:.1f} dips/hr, nadir {u.spo2_min:.0f}%)")
    if (u.restlessness_index or 5.0) > 35.0:
        key_drivers.append(f"High motor restlessness & positional instability ({u.restlessness_index:.1f}% restless epochs)")
    if not key_drivers:
        key_drivers.append("Optimal restorative sleep architecture and balanced autonomic tone.")
        
    return AnalysisResultResponse(
        id=u.id,
        personnel_id=u.personnel_id,
        personnel_code=personnel_code,
        filename=u.filename,
        scenario_tag=u.scenario_tag,
        uploaded_at=u.uploaded_at,
        risk_score=u.risk_score or 0.0,
        risk_level=u.risk_level or "LOW",
        readiness_verdict=u.readiness_verdict or "Fit for Duty",
        sleep_score=round(max(0.0, 100.0 - (u.sleep_efficiency or 85.0)), 1),
        stress_score=round(min(100.0, (u.baevsky_stress_index or 50.0) / 3.0), 1),
        fatigue_score=round(min(100.0, (u.restlessness_index or 10.0) * 1.5), 1),
        hypoxia_score=round(min(100.0, (u.odi_dips_per_hour or 0.0) * 4.5), 1),
        sleep_efficiency=u.sleep_efficiency or 0.0,
        deep_sleep_pct=u.deep_sleep_pct or 0.0,
        rem_sleep_pct=u.rem_sleep_pct or 0.0,
        light_sleep_pct=u.light_sleep_pct or 0.0,
        wake_pct=u.wake_pct or 0.0,
        total_sleep_time_min=u.total_sleep_time_min or 0.0,
        total_recording_time_min=u.total_sleep_time_min or 0.0,
        avg_heart_rate=u.avg_heart_rate or 0.0,
        hrv_rmssd=u.hrv_rmssd or 0.0,
        hrv_sdnn=u.hrv_sdnn or 0.0,
        hrv_lf_hf_ratio=u.hrv_lf_hf_ratio or 1.0,
        baevsky_stress_index=u.baevsky_stress_index or 0.0,
        avg_spo2=u.avg_spo2 or 98.0,
        spo2_min=u.spo2_min or 96.0,
        odi_dips_per_hour=u.odi_dips_per_hour or 0.0,
        hypoxic_burden_pct=u.hypoxic_burden_pct or 0.0,
        restlessness_index=u.restlessness_index or 0.0,
        clinical_explanation=u.clinical_explanation or "",
        commander_summary=u.commander_summary or "",
        key_drivers=key_drivers,
        recommendations=u.recommendations or [],
        hypnogram=u.hypnogram_data or [],
        waveform_preview=u.signal_preview_data or []
    )

@router.delete("/{id}")
def delete_analysis(id: int, db: Session = Depends(get_db)):
    u = db.query(UploadSession).filter(UploadSession.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(u)
    db.commit()
    return {"status": "deleted", "id": id}
