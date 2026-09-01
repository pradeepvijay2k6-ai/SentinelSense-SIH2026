from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Personnel, UploadSession
from ..schemas import PersonnelCreate, PersonnelResponse, PersonnelHistoryResponse, AnalysisResultResponse

router = APIRouter(prefix="/api/personnel", tags=["personnel"])

@router.get("", response_model=List[PersonnelResponse])
def get_all_personnel(db: Session = Depends(get_db)):
    personnel_list = db.query(Personnel).order_by(Personnel.id.desc()).all()
    results = []
    for p in personnel_list:
        latest_upload = db.query(UploadSession).filter(UploadSession.personnel_id == p.id).order_by(UploadSession.uploaded_at.desc()).first()
        total_uploads = db.query(UploadSession).filter(UploadSession.personnel_id == p.id).count()
        
        results.append(PersonnelResponse(
            id=p.id,
            personnel_id=p.personnel_id,
            name=p.name or p.personnel_id,
            unit=p.unit or "12th Battalion, Delta Coy",
            force_type=p.force_type or "CRPF",
            age=p.age or 32,
            created_at=p.created_at,
            latest_risk_score=latest_upload.risk_score if latest_upload else None,
            latest_risk_level=latest_upload.risk_level if latest_upload else None,
            latest_readiness=latest_upload.readiness_verdict if latest_upload else None,
            total_uploads=total_uploads
        ))
    return results

@router.post("", response_model=PersonnelResponse)
def create_personnel(payload: PersonnelCreate, db: Session = Depends(get_db)):
    existing = db.query(Personnel).filter(Personnel.personnel_id == payload.personnel_id.strip()).first()
    if existing:
        return PersonnelResponse(
            id=existing.id,
            personnel_id=existing.personnel_id,
            name=existing.name,
            unit=existing.unit,
            force_type=existing.force_type,
            age=existing.age,
            created_at=existing.created_at,
            latest_risk_score=None,
            latest_risk_level=None,
            latest_readiness=None,
            total_uploads=db.query(UploadSession).filter(UploadSession.personnel_id == existing.id).count()
        )
        
    personnel = Personnel(
        personnel_id=payload.personnel_id.strip().upper(),
        name=payload.name or payload.personnel_id.strip().upper(),
        unit=payload.unit or "12th Battalion, Delta Coy",
        force_type=payload.force_type or "CRPF",
        age=payload.age or 32
    )
    db.add(personnel)
    db.commit()
    db.refresh(personnel)
    
    return PersonnelResponse(
        id=personnel.id,
        personnel_id=personnel.personnel_id,
        name=personnel.name,
        unit=personnel.unit,
        force_type=personnel.force_type,
        age=personnel.age,
        created_at=personnel.created_at,
        latest_risk_score=None,
        latest_risk_level=None,
        latest_readiness=None,
        total_uploads=0
    )

@router.get("/{id}/history", response_model=PersonnelHistoryResponse)
def get_personnel_history(id: int, db: Session = Depends(get_db)):
    personnel = db.query(Personnel).filter(Personnel.id == id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
        
    uploads = db.query(UploadSession).filter(UploadSession.personnel_id == id).order_by(UploadSession.uploaded_at.asc()).all()
    
    latest_upload = uploads[-1] if uploads else None
    p_resp = PersonnelResponse(
        id=personnel.id,
        personnel_id=personnel.personnel_id,
        name=personnel.name,
        unit=personnel.unit,
        force_type=personnel.force_type,
        age=personnel.age,
        created_at=personnel.created_at,
        latest_risk_score=latest_upload.risk_score if latest_upload else None,
        latest_risk_level=latest_upload.risk_level if latest_upload else None,
        latest_readiness=latest_upload.readiness_verdict if latest_upload else None,
        total_uploads=len(uploads)
    )
    
    history_items = []
    for u in uploads:
        history_items.append(AnalysisResultResponse(
            id=u.id,
            personnel_id=u.personnel_id,
            personnel_code=personnel.personnel_id,
            filename=u.filename,
            scenario_tag=u.scenario_tag,
            uploaded_at=u.uploaded_at,
            risk_score=u.risk_score or 0.0,
            risk_level=u.risk_level or "LOW",
            readiness_verdict=u.readiness_verdict or "Fit for Duty",
            sleep_score=max(0.0, 100.0 - (u.sleep_efficiency or 85.0)),
            stress_score=round((u.baevsky_stress_index or 50.0) / 4.0, 1),
            fatigue_score=round((u.restlessness_index or 10.0) * 1.5, 1),
            hypoxia_score=round((u.odi_dips_per_hour or 0.0) * 4.0, 1),
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
            key_drivers=[],
            recommendations=u.recommendations or [],
            hypnogram=u.hypnogram_data or [],
            waveform_preview=u.signal_preview_data or []
        ))
        
    return PersonnelHistoryResponse(personnel=p_resp, history=history_items)
