from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import get_db
from ..models import Personnel, UploadSession
from ..schemas import RosterOverviewItem

router = APIRouter(prefix="/api/roster", tags=["roster"])

@router.get("", response_model=Dict[str, Any])
def get_commander_roster_summary(db: Session = Depends(get_db)):
    personnel_list = db.query(Personnel).all()
    
    roster_items = []
    total_count = len(personnel_list)
    fit_count = 0
    monitor_count = 0
    critical_count = 0
    unscreened_count = 0
    
    for p in personnel_list:
        latest = db.query(UploadSession).filter(UploadSession.personnel_id == p.id).order_by(UploadSession.uploaded_at.desc()).first()
        
        if latest and latest.risk_level:
            if latest.risk_level == "LOW":
                fit_count += 1
            elif latest.risk_level == "MODERATE":
                monitor_count += 1
            else:
                critical_count += 1
        else:
            unscreened_count += 1
            
        roster_items.append(RosterOverviewItem(
            id=p.id,
            personnel_id=p.personnel_id,
            name=p.name or p.personnel_id,
            unit=p.unit or "12th Battalion, Delta Coy",
            force_type=p.force_type or "CRPF",
            latest_upload_id=latest.id if latest else None,
            latest_upload_time=latest.uploaded_at if latest else None,
            risk_score=latest.risk_score if latest else None,
            risk_level=latest.risk_level if latest else None,
            readiness_verdict=latest.readiness_verdict if latest else "Not Screened",
            sleep_efficiency=latest.sleep_efficiency if latest else None,
            hrv_rmssd=latest.hrv_rmssd if latest else None,
            spo2_min=latest.spo2_min if latest else None
        ))
        
    avg_risk = round(sum(item.risk_score for item in roster_items if item.risk_score is not None) / max(1, total_count - unscreened_count), 1) if (total_count - unscreened_count) > 0 else 0.0
    
    return {
        "total_personnel": total_count,
        "fit_for_duty": fit_count,
        "monitoring_required": monitor_count,
        "critical_fatigue_stress": critical_count,
        "unscreened": unscreened_count,
        "average_unit_risk_score": avg_risk,
        "roster": roster_items
    }
