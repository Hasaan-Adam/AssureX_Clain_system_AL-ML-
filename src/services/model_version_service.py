"""Model Version Service - Model Registry"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from database.models import ModelVersion


ACTIVE_VERSION = "v1.0.0"
MODEL_METADATA = {
    "version": "v1.0.0",
    "algorithm": "XGBoostClassifier",
    "framework": "xgboost / scikit-learn",
    "features_count": 23,
    "calibration": "isotonic",
    "status": "active",
}


def get_active_version() -> str:
    """Return active ML model version string."""
    return ACTIVE_VERSION


def get_version_metadata(version: Optional[str] = None) -> Dict[str, Any]:
    """Return model version metadata dictionary."""
    return MODEL_METADATA


def get_current_active_model(db: Optional[Session] = None) -> Optional[Any]:
    """Get the currently active model version."""
    if db:
        return db.query(ModelVersion).filter(ModelVersion.status == "active").first()
    return MODEL_METADATA


def list_model_versions(db: Optional[Session] = None) -> List[Any]:
    """List all model versions."""
    if db:
        return db.query(ModelVersion).order_by(ModelVersion.registered_at.desc()).all()
    return [MODEL_METADATA]



def register_model_version(
    db: Session,
    version: str,
    algorithm: str,
    framework: str,
    hyperparameters: Dict[str, Any],
    metrics: Dict[str, Any],
    artifacts: Dict[str, str],
    description: str = "",
    registered_by: Optional[int] = None,
) -> ModelVersion:
    """Register a new model version."""
    # Archive previous active
    db.query(ModelVersion).filter(ModelVersion.status == "active").update({"status": "archived"})
    
    mv = ModelVersion(
        version=version,
        algorithm=algorithm,
        framework=framework,
        hyperparameters=str(hyperparameters),
        metrics=str(metrics),
        artifacts=str(artifacts),
        description=description,
        status="active",
        registered_by=registered_by,
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return mv