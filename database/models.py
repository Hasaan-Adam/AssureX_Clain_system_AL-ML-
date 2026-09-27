"""SQLAlchemy ORM Models - AssureX Claim Engine

Fully matches SQLite & PostgreSQL schema with property aliases.
"""

from __future__ import annotations

import json
from datetime import datetime, date
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    event,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    JSON,
    Float,
)
from sqlalchemy.orm import relationship, declarative_base

from database.connection import Base
from src.utils.constants import RoleEnum


# ---------------------------------------------------------
# Enums
# ---------------------------------------------------------
# Single source of truth: role values live in src/utils/constants.py so the
# database layer, the API schemas and the RBAC layer can never drift apart.
UserRole = RoleEnum


class ClaimStatus(str, PyEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    AUTO_APPROVED = "auto_approved"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    INFO_REQUIRED = "info_required"
    MANUAL_REVIEW = "manual_review"
    APPEAL_REQUESTED = "appeal_requested"
    SETTLED = "settled"
    CLOSED = "closed"
    # Legacy alias kept so historical rows and older clients keep working.
    UNDER_EVALUATION = "under_evaluation"


class WarrantyType(str, PyEnum):
    STANDARD = "standard"
    EXTENDED = "extended"
    PROMOTIONAL = "promotional"


class DocumentType(str, PyEnum):
    PURCHASE_RECEIPT = "purchase_receipt"
    WARRANTY_CARD = "warranty_card"
    PRODUCT_IMAGE = "product_image"
    SERIAL_NUMBER = "serial_number"
    FAULT_EVIDENCE = "fault_evidence"
    REPAIR_REPORT = "repair_report"
    OTHER = "other"


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="customer")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    products = relationship("Product", back_populates="owner")
    claims = relationship("Claim", back_populates="claimant", foreign_keys="Claim.claimant_id")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    @property
    def password_hash(self) -> str:
        return self.hashed_password

    @password_hash.setter
    def password_hash(self, val: str):
        self.hashed_password = val


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)
    model_number = Column(String(50), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False)
    purchase_date = Column(Date, nullable=False)
    purchase_price = Column(Integer, nullable=False, default=0)
    retailer = Column(String(100), nullable=True)
    warranty_duration_months = Column(Integer, nullable=False, default=12)
    warranty_type = Column(String(50), nullable=False, default="standard")
    warranty_start_date = Column(Date, nullable=False)
    warranty_expiry_date = Column(Date, nullable=False)
    custom_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="products")
    warranties = relationship("Warranty", back_populates="product")
    claims = relationship("Claim", back_populates="product")

    @property
    def model_name(self) -> str:
        return self.name or ""

    @model_name.setter
    def model_name(self, val: str):
        self.name = val

    @property
    def is_active(self) -> bool:
        return True

    @is_active.setter
    def is_active(self, val: bool):
        pass

    @property
    def serial_prefix(self) -> Optional[str]:
        return self.serial_number[:4] if self.serial_number else "SN"

    @serial_prefix.setter
    def serial_prefix(self, val: Optional[str]):
        pass

    @property
    def msrp(self) -> float:
        return float(self.purchase_price) if self.purchase_price is not None else 0.0

    @msrp.setter
    def msrp(self, val: float):
        self.purchase_price = int(val)

    @property
    def warranty_months(self) -> int:
        return self.warranty_duration_months if self.warranty_duration_months is not None else 12

    @warranty_months.setter
    def warranty_months(self, val: int):
        self.warranty_duration_months = val

    @property
    def description(self) -> Optional[str]:
        return f"{self.brand or ''} {self.name or ''}".strip()

    @description.setter
    def description(self, val: Optional[str]):
        pass

    @property
    def image_url(self) -> Optional[str]:
        if self.custom_image_url:
            return self.custom_image_url
        if hasattr(self, '_custom_image_url') and self._custom_image_url:
            return self._custom_image_url
        cat = (self.category or "").lower()
        br = (self.brand or "").lower()
        nm = (self.name or "").lower()
        if "iphone" in nm or "mobile" in cat or "phone" in cat or "apple" in br or "watch" in nm:
            if "watch" in nm:
                return "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80"
            if "ipad" in nm:
                return "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&auto=format&fit=crop&q=80"
            return "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=600&auto=format&fit=crop&q=80"
        elif "tv" in nm or "qled" in nm or "oled" in nm or "screen" in nm:
            return "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=600&auto=format&fit=crop&q=80"
        elif "laptop" in nm or "omen" in nm or "xps" in nm or "dell" in br or "hp" in br or "macbook" in nm:
            return "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80"
        elif "washer" in nm or "refrigerator" in nm or "microwave" in nm or "ac" in nm or "split" in nm or "appliance" in cat or "haier" in br or "gree" in br or "panasonic" in br:
            if "microwave" in nm:
                return "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=600&auto=format&fit=crop&q=80"
            if "washer" in nm:
                return "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600&auto=format&fit=crop&q=80"
            if "refrigerator" in nm:
                return "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop&q=80"
            return "https://images.unsplash.com/photo-1614633833026-0620459c3a37?w=600&auto=format&fit=crop&q=80"
        return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80"

    @image_url.setter
    def image_url(self, val: Optional[str]):
        self.custom_image_url = val
        self._custom_image_url = val

    @staticmethod
    def _generate_product_id(product: "Product") -> str:
        """Deterministic business key: PRD-<CATEGORY>-<BRAND>-<MODEL>-<SERIAL>."""
        parts = [
            str(product.category or "GEN").split("_")[0][:6].upper(),
            str(product.brand or "NA")[:4].upper(),
            str(product.model_number or product.name or "NA").replace(" ", "")[:10].upper(),
            str(product.serial_number or "")[-6:].upper(),
        ]
        return "PRD-" + "-".join(part for part in parts if part)


@event.listens_for(Product, "before_insert")
def _assign_product_id(mapper, connection, target: Product) -> None:
    """Fill the business key when a caller (scripts/seeds) omits it."""
    if not target.product_id:
        target.product_id = target._generate_product_id(target)


class Warranty(Base):
    """Warranty registration.

    Columns mirror the SRS data dictionary (warranty_number, user_id,
    serial_number, purchase_date, status, purchase_price, ...). Ownership is
    stored directly on the warranty so warranty queries never depend on a join
    through the product row.
    """

    __tablename__ = "warranties"

    id = Column(Integer, primary_key=True, index=True)
    warranty_number = Column(String(100), nullable=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    serial_number = Column(String(100), nullable=False, index=True)
    provider = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    purchase_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="ACTIVE", index=True)
    purchase_price = Column(Float, default=0.0)
    invoice_number = Column(String(100), nullable=True)
    store_name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    warranty_duration_months = Column(Integer, nullable=True)
    coverage_conditions = Column(Text, nullable=True)
    exclusions = Column(Text, nullable=True)
    service_centers = Column(Text, nullable=True)
    custom_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="warranties")
    claims = relationship("Claim", back_populates="warranty")
    owner = relationship("User", foreign_keys=[user_id])

    @property
    def image_url(self) -> Optional[str]:
        if self.custom_image_url:
            return self.custom_image_url
        return self.product.image_url if self.product else None

    @image_url.setter
    def image_url(self, val: Optional[str]):
        self.custom_image_url = val

    @property
    def is_expired(self) -> bool:
        return bool(self.expiry_date and self.expiry_date < date.today())

    @property
    def days_until_expiry(self) -> Optional[int]:
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days

    @property
    def effective_status(self) -> str:
        """Status honouring the expiry date even if the stored value is stale."""
        if self.status and self.status.upper() == "VOIDED":
            return "VOIDED"
        return "EXPIRED" if self.is_expired else "ACTIVE"


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), unique=True, index=True, nullable=False)
    claimant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warranty_id = Column(Integer, ForeignKey("warranties.id"), nullable=True)

    fault_occurrence_date = Column(Date, nullable=False)
    fault_type = Column(String(100), nullable=False)
    fault_description = Column(Text, nullable=True)
    damage_type = Column(String(50), nullable=True)
    claim_amount = Column(Float, default=0.0, nullable=False)
    claim_submission_date = Column(Date, default=lambda: datetime.utcnow().date(), nullable=False)
    status = Column(String(50), default="draft", nullable=False)

    # Who physically filed the claim (differs from the claimant when a
    # service-centre employee submits on behalf of a customer).
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    filing_channel = Column(String(30), default="self_service", nullable=False)
    service_center = Column(String(120), nullable=True)

    rejection_reason = Column(Text, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    appeal_notes = Column(Text, nullable=True)

    python_prediction = Column(String(50), nullable=True)
    python_confidence = Column(String(500), nullable=True)
    tm_prediction = Column(String(50), nullable=True)
    tm_confidence = Column(String(500), nullable=True)
    comparison_result = Column(Text, nullable=True)
    rule_engine_result = Column(Text, nullable=True)
    final_decision = Column(String(50), nullable=True)
    python_model_version = Column(String(50), nullable=True)
    tm_model_version = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    claimant = relationship("User", back_populates="claims", foreign_keys=[claimant_id])
    filed_by = relationship("User", foreign_keys=[created_by])
    product = relationship("Product", back_populates="claims")
    warranty = relationship("Warranty", back_populates="claims")
    documents = relationship("Document", back_populates="claim")
    predictions = relationship("Prediction", back_populates="claim")
    reviews = relationship("Review", back_populates="claim")

    @property
    def user(self) -> Optional[User]:
        return self.claimant

    @user.setter
    def user(self, val: Optional[User]):
        self.claimant = val

    @property
    def user_id(self) -> int:
        return self.claimant_id

    @user_id.setter
    def user_id(self, val: int):
        self.claimant_id = val

    @property
    def claim_number(self) -> str:
        return self.claim_id

    @claim_number.setter
    def claim_number(self, val: str):
        self.claim_id = val

    @property
    def description(self) -> Optional[str]:
        return self.fault_description

    @description.setter
    def description(self, val: Optional[str]):
        self.fault_description = val

    @property
    def ai_decision(self) -> Optional[str]:
        return self.python_prediction or self.final_decision or "PENDING"

    @property
    def ai_confidence(self) -> float:
        if self.python_confidence:
            try:
                import json
                import ast
                try:
                    c = json.loads(self.python_confidence)
                except Exception:
                    c = ast.literal_eval(self.python_confidence)
                if isinstance(c, dict) and c:
                    return round(float(max(c.values())), 3)
                elif isinstance(c, (int, float)):
                    return round(float(c), 3)
            except Exception:
                pass
        if self.predictions:
            for p in reversed(self.predictions):
                if p.python_probabilities:
                    try:
                        import json
                        import ast
                        try:
                            c = json.loads(p.python_probabilities)
                        except Exception:
                            c = ast.literal_eval(p.python_probabilities)
                        if isinstance(c, dict) and c:
                            return round(float(max(c.values())), 3)
                        elif isinstance(c, (int, float)):
                            return round(float(c), 3)
                    except Exception:
                        pass
        return None

    @property
    def tm_confidence_score(self) -> Optional[float]:
        if self.tm_confidence:
            try:
                import json
                import ast
                try:
                    c = json.loads(self.tm_confidence)
                except Exception:
                    c = ast.literal_eval(self.tm_confidence)
                if isinstance(c, dict) and c:
                    return round(float(max(c.values())), 3)
                elif isinstance(c, (int, float)):
                    return round(float(c), 3)
            except Exception:
                pass
        if self.predictions:
            for p in reversed(self.predictions):
                if p.tm_probabilities:
                    try:
                        import json
                        import ast
                        try:
                            c = json.loads(p.tm_probabilities)
                        except Exception:
                            c = ast.literal_eval(p.tm_probabilities)
                        if isinstance(c, dict) and c:
                            return round(float(max(c.values())), 3)
                    except Exception:
                        pass
        return None

    @property
    def fraud_score(self) -> float:
        score = 0.0
        if self.rule_engine_result:
            try:
                import json, ast
                try:
                    r = json.loads(self.rule_engine_result)
                except Exception:
                    r = ast.literal_eval(self.rule_engine_result)
                if isinstance(r, dict):
                    violations = r.get("violations", [])
                    if any("serial" in str(v).lower() for v in violations):
                        score += 0.40
                    if any("duplicate" in str(v).lower() for v in violations):
                        score += 0.50
                    if any("contradiction" in str(v).lower() for v in violations):
                        score += 0.30
            except Exception:
                pass
        return round(min(score, 1.0), 2)

    @property
    def model_agreement_score(self) -> Optional[float]:
        if self.comparison_result:
            try:
                import json, ast
                try:
                    c = json.loads(self.comparison_result)
                except Exception:
                    c = ast.literal_eval(self.comparison_result)
                if isinstance(c, dict) and "max_delta" in c:
                    return round(max(0.0, 1.0 - float(c["max_delta"])), 3)
                if isinstance(c, dict) and "agreement_score" in c:
                    return round(float(c["agreement_score"]), 3)
            except Exception:
                pass
        return None

    @property
    def is_filed_on_behalf(self) -> bool:
        """True when a service-centre employee filed this claim for the customer."""
        return bool(self.created_by) and self.created_by != self.claimant_id


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=True)
    extracted_data = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    claim = relationship("Claim", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploader_id])
    verifier = relationship("User", foreign_keys=[verified_by])

    @property
    def file_name(self) -> str:
        import os
        return os.path.basename(self.file_path) if self.file_path else "document"

    @property
    def uploaded_at(self) -> datetime:
        return self.created_at or datetime.utcnow()

    @property
    def warranty_id(self) -> Optional[int]:
        return self.claim.warranty_id if self.claim else None

    @property
    def ocr_extracted_text(self) -> Optional[str]:
        """Raw OCR text, whether stored as an OCR payload or as plain text."""
        payload = self.ocr_payload
        if payload:
            return payload.get("text")
        return self.extracted_data

    @ocr_extracted_text.setter
    def ocr_extracted_text(self, val: Optional[str]):
        self.extracted_data = val

    def apply_ocr_result(
        self,
        text: Optional[str],
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None,
        entities: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist a real OCR result (text + engine confidence + metadata)."""
        self.extracted_data = json.dumps(
            {
                "text": text or "",
                "confidence": round(float(confidence or 0.0), 3),
                "metadata": metadata or {},
                "entities": entities or {},
            },
            default=str,
        )

    @property
    def ocr_payload(self) -> Dict[str, Any]:
        """Structured OCR payload stored in `extracted_data` (empty if absent)."""
        if not self.extracted_data:
            return {}
        try:
            parsed = json.loads(self.extracted_data)
        except (ValueError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}

    @property
    def ocr_confidence(self) -> float:
        payload = self.ocr_payload
        if payload and payload.get("confidence") is not None:
            try:
                return round(float(payload["confidence"]), 3)
            except (TypeError, ValueError):
                return 0.0
        return 0.0

    @ocr_confidence.setter
    def ocr_confidence(self, val: float):
        payload = self.ocr_payload
        payload["confidence"] = round(float(val or 0.0), 3)
        payload.setdefault("text", "")
        payload.setdefault("metadata", {})
        self.extracted_data = json.dumps(payload, default=str)

    @property
    def ocr_metadata(self) -> Dict[str, Any]:
        return self.ocr_payload.get("metadata") or {}

    @ocr_metadata.setter
    def ocr_metadata(self, val: Dict[str, Any]):
        payload = self.ocr_payload
        payload["metadata"] = val or {}
        payload.setdefault("text", "")
        payload.setdefault("confidence", 0.0)
        self.extracted_data = json.dumps(payload, default=str)

    @property
    def ocr_entities(self) -> Dict[str, Any]:
        return self.ocr_payload.get("entities") or {}


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    python_predicted_class = Column(String(50), nullable=True)
    python_probabilities = Column(Text, nullable=True)
    tm_predicted_class = Column(String(50), nullable=True)
    tm_probabilities = Column(Text, nullable=True)
    comparison_result = Column(Text, nullable=True)
    model_consistency_status = Column(String(50), nullable=True)
    rule_decision = Column(String(50), nullable=True)
    rule_breakdown = Column(Text, nullable=True)
    final_decision = Column(String(50), nullable=True)
    model_versions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    claim = relationship("Claim", back_populates="predictions")

    @property
    def model_name(self) -> str:
        return "Dual AI Ensemble (XGBoost + Teachable Machine)"

    @property
    def prediction_result(self) -> str:
        return self.final_decision or self.python_predicted_class or self.tm_predicted_class or "Likely Valid"

    @property
    def confidence_score(self) -> float:
        if self.python_probabilities:
            try:
                import json
                p = json.loads(self.python_probabilities)
                if isinstance(p, dict):
                    return round(max(float(v) for v in p.values()), 3)
            except Exception:
                pass
        return 0.95

    @property
    def fraud_risk_score(self) -> float:
        return self.claim.fraud_score if self.claim else 0.0

    @property
    def feature_importance(self) -> Optional[Dict[str, Any]]:
        return None

    @property
    def raw_output(self) -> Optional[Dict[str, Any]]:
        return {
            "python_predicted_class": self.python_predicted_class,
            "tm_predicted_class": self.tm_predicted_class,
            "consistency_status": self.model_consistency_status,
            "rule_decision": self.rule_decision,
            "final_decision": self.final_decision,
        }


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String(50), nullable=False)
    comments = Column(Text, nullable=True)
    override_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    claim = relationship("Claim", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    @property
    def previous_status(self) -> str:
        return "under_review"

    @property
    def new_status(self) -> str:
        d = (self.decision or "").lower()
        if "appr" in d:
            return "approved"
        elif "rej" in d:
            return "rejected"
        elif "esc" in d:
            return "escalated"
        return "under_review"

    @property
    def reasoning(self) -> str:
        return self.override_reason or self.comments or "Reviewer decision recorded"

    @reasoning.setter
    def reasoning(self, val: str):
        self.override_reason = val

    @property
    def notes(self) -> Optional[str]:
        return self.comments

    @notes.setter
    def notes(self, val: Optional[str]):
        self.comments = val

    @property
    def reviewed_at(self) -> datetime:
        return self.updated_at or self.created_at or datetime.utcnow()


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="notifications")

    @property
    def notification_type(self) -> str:
        return self.type or "system_alert"

    @notification_type.setter
    def notification_type(self, val: str):
        self.type = val

    @property
    def channel(self) -> str:
        return "in_app"

    @channel.setter
    def channel(self, val: str):
        pass

    @property
    def severity(self) -> str:
        return "INFO"

    @severity.setter
    def severity(self, val: str):
        pass

    @property
    def metadata_json(self) -> Optional[dict]:
        return {"related_entity_type": self.related_entity_type, "related_entity_id": self.related_entity_id}


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(100), nullable=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="audit_logs")


class AdminSetting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RepairHistory(Base):
    __tablename__ = "repair_history"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    repair_date = Column(Date, nullable=False)
    repair_center = Column(String(200), nullable=True)
    parts_replaced = Column(Text, nullable=True)
    repair_outcome = Column(String(100), nullable=True)
    repair_cost = Column(Integer, nullable=True)
    authorized_status = Column(String(50), nullable=False, default="yes")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False)
    algorithm = Column(String(100), nullable=False)
    framework = Column(String(50), nullable=False)
    hyperparameters = Column(Text, nullable=True)
    metrics = Column(Text, nullable=True)
    artifacts = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    registered_by = Column(Integer, ForeignKey("users.id"), nullable=True)