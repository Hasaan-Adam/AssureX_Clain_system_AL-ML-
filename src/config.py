"""
AssureX Claim Engine - Central Application Configuration
Loads YAML settings with environment variable overrides.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_yaml(file_path: Path) -> Dict[str, Any]:
    """Safely load a YAML file or return an empty dict if not found."""
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}



class AppInfo(BaseModel):
    name: str = "AssureX Claim Engine"
    version: str = "1.0.0"
    description: str = "Enterprise Warranty Lifecycle and AI-Powered Claim Adjudication Engine"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = True


class ServerInfo(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class DatabaseInfo(BaseModel):
    url: str = "sqlite:///./assurex.db"
    echo: bool = False
    pool_pre_ping: bool = True


class SecurityInfo(BaseModel):
    secret_key: str = "assurex-super-secret-production-encryption-key-change-in-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    password_reset_token_expire_minutes: int = 15


class CorsInfo(BaseModel):
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = False
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class LoggingInfo(BaseModel):
    level: str = "INFO"
    format: str = "json"
    log_file: str = "logs/assurex.log"
    max_bytes: int = 10485760
    backup_count: int = 5


class UploadsInfo(BaseModel):
    upload_dir: str = "./uploads"
    max_file_size_bytes: int = 10485760
    allowed_extensions: List[str] = [".pdf", ".png", ".jpg", ".jpeg", ".webp"]
    allowed_mime_types: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/webp",
    ]


class EmailInfo(BaseModel):
    enabled: bool = False
    smtp_host: str = "smtp.mailtrap.io"
    smtp_port: int = 2525
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = "no-reply@assurex.com"
    from_name: str = "AssureX Claims Support"



class AIComparisonThresholds(BaseModel):
    strong_match_delta: float = 0.10
    acceptable_delta: float = 0.20
    weak_match_delta: float = 0.35
    disagreement_delta: float = 0.35


class ConfidenceThresholds(BaseModel):
    high_confidence: float = 0.80
    medium_confidence_min: float = 0.60
    low_confidence: float = 0.60


class AutoApprovalRules(BaseModel):
    min_confidence: float = 0.85
    max_fraud_score: float = 0.15
    max_claim_amount_ratio: float = 0.75
    require_verified_warranty: bool = True
    require_all_docs_valid: bool = True


class AutoRejectionRules(BaseModel):
    min_confidence: float = 0.85
    min_fraud_score: float = 0.80
    direct_policy_exclusion_rejection: bool = True


class ManualReviewRules(BaseModel):
    trigger_confidence_range: Dict[str, float] = {"min": 0.60, "max": 0.85}
    trigger_fraud_score_range: Dict[str, float] = {"min": 0.30, "max": 0.80}
    trigger_on_ai_disagreement: bool = True
    trigger_on_missing_receipt: bool = True


class DecisionRules(BaseModel):
    auto_approval: AutoApprovalRules = Field(default_factory=AutoApprovalRules)
    auto_rejection: AutoRejectionRules = Field(default_factory=AutoRejectionRules)
    manual_review: ManualReviewRules = Field(default_factory=ManualReviewRules)


class OCRMatchingRules(BaseModel):
    model_config = {"protected_namespaces": ()}
    serial_number_fuzzy_threshold: float = 0.85
    model_number_fuzzy_threshold: float = 0.85
    date_match_tolerance_days: int = 7
    price_tolerance_percentage: float = 0.05


class ThresholdConfig(BaseModel):
    ai_comparison: AIComparisonThresholds = Field(default_factory=AIComparisonThresholds)
    confidence_thresholds: ConfidenceThresholds = Field(default_factory=ConfidenceThresholds)
    decision_rules: DecisionRules = Field(default_factory=DecisionRules)
    ocr_matching: OCRMatchingRules = Field(default_factory=OCRMatchingRules)



class WarrantyExpiryAlertConfig(BaseModel):
    alert_days: List[int] = [30, 15, 7, 0]
    post_expiry_grace_reminder_days: List[int] = [-3]
    frequency: str = "daily"
    cooldown_hours_between_same_alert: int = 24


class ClaimStatusAlertConfig(BaseModel):
    notify_customer_on_status_change: bool = True
    notify_reviewer_on_new_manual_review: bool = True
    notify_admin_on_fraud_escalation: bool = True
    sla_warning_hours: int = 48
    sla_breach_hours: int = 72


class ChannelsConfig(BaseModel):
    in_app: Dict[str, Any] = {"enabled": True, "retention_days": 90}
    email: Dict[str, Any] = {"enabled": False, "digest_enabled": True}
    sms: Dict[str, Any] = {"enabled": False}


class AlertSettingsConfig(BaseModel):
    warranty_expiry: WarrantyExpiryAlertConfig = Field(default_factory=WarrantyExpiryAlertConfig)
    claim_status_alerts: ClaimStatusAlertConfig = Field(default_factory=ClaimStatusAlertConfig)
    channels: ChannelsConfig = Field(default_factory=ChannelsConfig)



class MonitoringConfig(BaseModel):
    anomaly_thresholds: Dict[str, Any] = Field(default_factory=dict)
    system_health: Dict[str, Any] = Field(default_factory=dict)



class Settings(BaseSettings):
    """
    Primary Application Settings loaded from config files and environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    app: AppInfo = Field(default_factory=AppInfo)
    server: ServerInfo = Field(default_factory=ServerInfo)
    database: DatabaseInfo = Field(default_factory=DatabaseInfo)
    security: SecurityInfo = Field(default_factory=SecurityInfo)
    cors: CorsInfo = Field(default_factory=CorsInfo)
    logging: LoggingInfo = Field(default_factory=LoggingInfo)
    uploads: UploadsInfo = Field(default_factory=UploadsInfo)
    email: EmailInfo = Field(default_factory=EmailInfo)

    thresholds: ThresholdConfig = Field(default_factory=ThresholdConfig)
    alerts: AlertSettingsConfig = Field(default_factory=AlertSettingsConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ENVIRONMENT: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """
    Load settings singleton with YAML parsing and env var merging.
    """
    config_dir = Path("config")
    settings_yaml = _load_yaml(config_dir / "settings.yaml")
    thresholds_yaml = _load_yaml(config_dir / "thresholds.yaml")
    alerts_yaml = _load_yaml(config_dir / "alert_settings.yaml")
    monitoring_yaml = _load_yaml(config_dir / "monitoring.yaml")

    merged_data: Dict[str, Any] = {
        **settings_yaml,
        "thresholds": thresholds_yaml,
        "alerts": alerts_yaml,
        "monitoring": monitoring_yaml,
    }

    if db_url := os.getenv("DATABASE_URL"):
        merged_data.setdefault("database", {})["url"] = db_url
        merged_data["DATABASE_URL"] = db_url

    if secret := os.getenv("SECRET_KEY"):
        merged_data.setdefault("security", {})["secret_key"] = secret
        merged_data["SECRET_KEY"] = secret

    if env_name := os.getenv("ENVIRONMENT"):
        merged_data.setdefault("app", {})["environment"] = env_name
        merged_data["ENVIRONMENT"] = env_name

    return Settings(**merged_data)


settings = get_settings()