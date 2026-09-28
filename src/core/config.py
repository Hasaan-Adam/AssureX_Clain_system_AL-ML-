"""Application Configuration Settings.

Loads configuration from YAML files and environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    url: str = "sqlite:///./assurex.db"
    echo: bool = False


class SecuritySettings(BaseModel):
    secret_key: str = "assurex-super-secret-production-encryption-key-change-in-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 30


class TMModelSettings(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_dir: str = "model/teachable_machine"
    input_size: tuple = (224, 224, 3)
    classes: List[str] = ["Invalid Claim", "Manual Review", "Valid Claim"]


class MLModelSettings(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_dir: str = "model/python"
    feature_columns_path: str = "model/python/feature_columns.json"
    confidence_threshold: float = 0.85


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=(),
    )

    app_name: str = "AssureX Claim Engine"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    database: DatabaseSettings = DatabaseSettings()

    security: SecuritySettings = SecuritySettings()

    tm_model: TMModelSettings = TMModelSettings()

    ml_model: MLModelSettings = MLModelSettings()

    cors_origins: List[str] = ["*"]

    @classmethod
    def load_from_yaml(cls, config_path: str = "AssureX-Claim-Engine/config/settings.yaml") -> "Settings":
        """Load settings from YAML file, overriding with env vars."""
        path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}
            return cls(**yaml_data)
        return cls()


settings = Settings.load_from_yaml()


def get_settings() -> Settings:
    return settings

