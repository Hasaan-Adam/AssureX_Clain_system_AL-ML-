"""
AssureX Claim Engine - System Constants & Enumerations
"""

from enum import Enum
from typing import Optional


class RoleEnum(str, Enum):
    """Canonical role set for the whole application.

    ``STAFF`` is kept as an enum alias of ``SERVICE_STAFF`` so that older
    references (``RoleEnum.STAFF``) keep working while the persisted value is
    always the canonical ``service_staff`` string.
    """

    CUSTOMER = "customer"
    SERVICE_STAFF = "service_staff"
    STAFF = "service_staff"
    REVIEWER = "reviewer"
    ADMIN = "admin"


#: Alternative spellings accepted on input (registration payloads, legacy DB
#: rows, JWT claims) and mapped onto a canonical role value.
ROLE_ALIASES = {
    "staff": RoleEnum.SERVICE_STAFF.value,
    "service_staff": RoleEnum.SERVICE_STAFF.value,
    "service center": RoleEnum.SERVICE_STAFF.value,
    "service-center": RoleEnum.SERVICE_STAFF.value,
    "servicecenter": RoleEnum.SERVICE_STAFF.value,
    "support": RoleEnum.SERVICE_STAFF.value,
    "customer": RoleEnum.CUSTOMER.value,
    "user": RoleEnum.CUSTOMER.value,
    "reviewer": RoleEnum.REVIEWER.value,
    "adjudicator": RoleEnum.REVIEWER.value,
    "admin": RoleEnum.ADMIN.value,
    "administrator": RoleEnum.ADMIN.value,
}

#: Roles allowed to see claims/products/warranties that belong to other users.
PRIVILEGED_ROLES = (RoleEnum.SERVICE_STAFF.value, RoleEnum.REVIEWER.value, RoleEnum.ADMIN.value)

#: Roles allowed to adjudicate claims and override the automated decision.
ADJUDICATOR_ROLES = (RoleEnum.REVIEWER.value, RoleEnum.ADMIN.value)


def normalize_role(value: object, default: Optional[str] = None) -> Optional[str]:
    """Return the canonical role string for ``value`` (or ``default``)."""
    if value is None:
        return default
    raw = value.value if hasattr(value, "value") else str(value)
    raw = raw.lower().strip()
    if not raw:
        return default
    return ROLE_ALIASES.get(raw, raw if raw in {r.value for r in RoleEnum} else default)


class ClaimStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    AUTO_APPROVED = "auto_approved"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    APPEAL_REQUESTED = "appeal_requested"
    SETTLED = "settled"
    CLOSED = "closed"


class DecisionType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    ESCALATE = "ESCALATE"


class DocumentType(str, Enum):
    PURCHASE_INVOICE = "purchase_invoice"
    WARRANTY_CARD = "warranty_card"
    DIAGNOSTIC_REPORT = "diagnostic_report"
    DEVICE_PHOTO_FRONT = "device_photo_front"
    DEVICE_PHOTO_BACK = "device_photo_back"
    SERIAL_NUMBER_PHOTO = "serial_number_photo"
    DAMAGE_PHOTO = "damage_photo"
    TECHNICIAN_REPORT = "technician_report"
    INSTALLATION_CERTIFICATE = "installation_certificate"
    APPEAL_DOCUMENT = "appeal_document"
    OTHER = "other"


class ProductCategory(str, Enum):
    ELECTRONICS = "ELECTRONICS"
    HOME_APPLIANCES = "HOME_APPLIANCES"
    MOBILE_PHONES = "MOBILE_PHONES"
    OTHER = "OTHER"


class WarrantyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    VOIDED = "VOIDED"
    CLAIMED = "CLAIMED"


class NotificationType(str, Enum):
    WARRANTY_EXPIRY = "warranty_expiry"
    CLAIM_UPDATE = "claim_update"
    MANUAL_REVIEW_ASSIGNED = "manual_review_assigned"
    FRAUD_ALERT = "fraud_alert"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class NotificationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AuditAction(str, Enum):
    USER_REGISTER = "USER_REGISTER"
    USER_LOGIN = "USER_LOGIN"
    WARRANTY_CREATE = "WARRANTY_CREATE"
    WARRANTY_UPDATE = "WARRANTY_UPDATE"
    CLAIM_SUBMIT = "CLAIM_SUBMIT"
    CLAIM_AI_PREDICT = "CLAIM_AI_PREDICT"
    CLAIM_REVIEW = "CLAIM_REVIEW"
    CLAIM_APPROVE = "CLAIM_APPROVE"
    CLAIM_REJECT = "CLAIM_REJECT"
    CLAIM_ESCALATE = "CLAIM_ESCALATE"
    REPAIR_CREATE = "REPAIR_CREATE"
    REPAIR_UPDATE = "REPAIR_UPDATE"
    SETTING_UPDATE = "SETTING_UPDATE"