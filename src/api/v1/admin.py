"""
AssureX Claim Engine - Administrator Operations API Router
Handles audit trail querying, system telemetry/anomaly monitoring, and administrative settings.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import require_role
from src.models.settings_admin import AdminSetting
from src.models.user import User
from src.services import alert_service, audit_service
from src.utils.constants import RoleEnum

router = APIRouter(prefix="/admin", tags=["Admin Operations"], dependencies=[Depends(require_role(RoleEnum.ADMIN))])


@router.get("/audit-logs")
def get_audit_logs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type (Claim, User, etc.)"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action code"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve filtered and paginated immutable audit logs."""
    logs, total = audit_service.list_audit_logs(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        action=action,
        skip=skip,
        limit=limit,
    )
    return {
        "total": total,
        "logs": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "old_values": l.old_values,
                "new_values": l.new_values,
                "ip_address": l.ip_address,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ],
    }


@router.get("/anomalies")
def check_system_anomalies(
    db: Session = Depends(get_db),
):
    """Scan current telemetry and report anomalies triggering thresholds in config/monitoring.yaml."""
    anomalies = alert_service.check_system_anomalies(db)
    return {
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }


@router.get("/settings")
def list_admin_settings(
    db: Session = Depends(get_db),
):
    """Retrieve all configurable administrative settings."""
    settings_records = db.query(AdminSetting).all()
    if not settings_records:
        defaults = [
            ("autoApprovalMinConfidence", 0.85, "Minimum confidence threshold for automatic claim approval"),
            ("maxFraudRiskScore", 0.15, "Maximum allowed fraud risk score for automated fast-track"),
            ("maxClaimAmountRatio", 0.75, "Maximum claim amount to MSRP ratio before flag"),
            ("ocrFuzzyMatchThreshold", 0.85, "OCR fuzzy string match similarity threshold"),
            ("inAppAlertsEnabled", True, "Enable in-app notification alerts"),
            ("emailAlertsEnabled", True, "Enable email notifications for claim events"),
        ]
        for key, val, desc in defaults:
            s = AdminSetting(key=key, value=val, description=desc)
            db.add(s)
        db.commit()
        settings_records = db.query(AdminSetting).all()

    return {
        "settings": [
            {
                "id": s.id,
                "key": s.key,
                "value": s.value,
                "description": s.description,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in settings_records
        ]
    }


@router.put("/settings/{key}")
def update_admin_setting(
    key: str,
    payload: Dict[str, Any],
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    """Update a specific administrative setting key-value pair."""
    setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
    if not setting:
        setting = AdminSetting(
            key=key,
            value=payload.get("value", {}),
            description=payload.get("description"),
            updated_by=current_user.id,
        )
        db.add(setting)
    else:
        setting.value = payload.get("value", setting.value)
        if "description" in payload:
            setting.description = payload["description"]
        setting.updated_by = current_user.id

    db.commit()
    db.refresh(setting)
    return {"success": True, "setting": {"key": setting.key, "value": setting.value}}


import os
import json
from pathlib import Path
from fastapi import HTTPException

POLICIES_DIR = Path(__file__).resolve().parents[3] / "policies"

@router.get("/policies")
def list_policies():
    """List all available JSON warranty policies."""
    policies = []
    if POLICIES_DIR.exists():
        for file in os.listdir(POLICIES_DIR):
            if file.endswith(".json"):
                with open(POLICIES_DIR / file, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        policies.append({"filename": file, "data": data})
                    except Exception:
                        pass
    return {"policies": policies}

@router.put("/policies/{filename}")
def update_policy(filename: str, payload: dict):
    """Update a specific JSON warranty policy."""
    if not filename.endswith(".json"):
        filename += ".json"
    file_path = POLICIES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Policy file not found")
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
        
    from src.services.rule_engine import _POLICY_CACHE
    if filename in _POLICY_CACHE:
        del _POLICY_CACHE[filename]
        
    return {"message": f"Policy {filename} updated successfully"}
