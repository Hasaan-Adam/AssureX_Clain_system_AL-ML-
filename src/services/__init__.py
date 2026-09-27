"""
AssureX Claim Engine - Services Package

Lazy imports to avoid circular dependencies.
"""

# Core services (no circular deps)
from src.services.user_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    list_users,
    update_profile,
    update_user_role,
    update_user_status,
    change_password,
    authenticate_user,
)

from src.services.auth_service import (
    register_user,
    authenticate_user,
    create_user_tokens,
    refresh_access_token,
    validate_token,
)

# Lazy-loaded services (import on demand)
def get_claim_service():
    from src.services.claim_service import (
        create_claim,
        get_claim_by_id,
        list_claims,
        transition_claim_status,
        appeal_claim,
    )
    return {
        "create_claim": create_claim,
        "get_claim_by_id": get_claim_by_id,
        "list_claims": list_claims,
        "transition_claim_status": transition_claim_status,
        "appeal_claim": appeal_claim,
    }

def get_product_service():
    from src.services.product_service import (
        create_product,
        get_product_by_id,
        list_products,
        update_product,
        get_categories,
        get_brands,
    )
    return {
        "create_product": create_product,
        "get_product_by_id": get_product_by_id,
        "list_products": list_products,
        "update_product": update_product,
        "get_categories": get_categories,
        "get_brands": get_brands,
    }

def get_warranty_service():
    from src.services.warranty_service import (
        create_warranty,
        get_warranty_by_id,
        get_warranty_by_serial,
        list_warranties,
        update_warranty,
        calculate_expiry_date,
        calculate_warranty_status,
        generate_expiry_alerts,
    )
    return {
        "create_warranty": create_warranty,
        "get_warranty_by_id": get_warranty_by_id,
        "get_warranty_by_serial": get_warranty_by_serial,
        "list_warranties": list_warranties,
        "update_warranty": update_warranty,
        "calculate_expiry_date": calculate_expiry_date,
        "calculate_warranty_status": calculate_warranty_status,
        "generate_expiry_alerts": generate_expiry_alerts,
    }

def get_document_service():
    from src.services.document_service import (
        store_document,
        get_document_by_id,
        list_documents_for_claim,
        list_documents_for_warranty,
        check_access_rights,
        check_document_hash_exists,
    )
    return {
        "store_document": store_document,
        "get_document_by_id": get_document_by_id,
        "list_documents_for_claim": list_documents_for_claim,
        "list_documents_for_warranty": list_documents_for_warranty,
        "check_access_rights": check_access_rights,
        "check_document_hash_exists": check_document_hash_exists,
    }

def get_prediction_service():
    from src.services.prediction_service import (
        adjudicate_claim,
        calculate_fraud_risk,
    )
    return {
        "adjudicate_claim": adjudicate_claim,
        "calculate_fraud_risk": calculate_fraud_risk,
    }

def get_rule_engine():
    from src.services.rule_engine import evaluate_claim_rules
    return {"evaluate_claim_rules": evaluate_claim_rules}

def get_comparison_service():
    from src.services.comparison_service import compare_models
    return {"compare_models": compare_models}

def get_decision_service():
    from src.services.decision_service import aggregate_decision
    return {"aggregate_decision": aggregate_decision}

def get_explanation_service():
    from src.services.explanation_service import generate_decision_explanation
    return {"generate_decision_explanation": generate_decision_explanation}

def get_review_service():
    from src.services.review_service import (
        get_review_queue,
        submit_review_decision,
        get_human_override_stats,
    )
    return {
        "get_review_queue": get_review_queue,
        "submit_review_decision": submit_review_decision,
        "get_human_override_stats": get_human_override_stats,
    }

def get_dashboard_service():
    from src.services.dashboard_service import get_user_dashboard, get_admin_dashboard
    return {"get_user_dashboard": get_user_dashboard, "get_admin_dashboard": get_admin_dashboard}

def get_analytics_service():
    from src.services.analytics_service import (
        get_analytics_overview,
        get_fault_distribution,
        get_brand_reliability_index,
        get_fraud_detection_stats,
        get_time_series_claims,
    )
    return {
        "get_analytics_overview": get_analytics_overview,
        "get_fault_distribution": get_fault_distribution,
        "get_brand_reliability_index": get_brand_reliability_index,
        "get_fraud_detection_stats": get_fraud_detection_stats,
        "get_time_series_claims": get_time_series_claims,
    }

def get_notification_service():
    from src.services.notification_service import (
        create_notification,
        get_user_notifications,
        mark_notification_as_read,
        mark_all_notifications_as_read,
        notify_all_reviewers,
    )
    return {
        "create_notification": create_notification,
        "get_user_notifications": get_user_notifications,
        "mark_notification_as_read": mark_notification_as_read,
        "mark_all_notifications_as_read": mark_all_notifications_as_read,
        "notify_all_reviewers": notify_all_reviewers,
    }

def get_document_service_full():
    from src.services.document_service import (
        store_document,
        get_document_by_id,
        list_documents_for_claim,
        list_documents_for_warranty,
        check_access_rights,
        check_document_hash_exists,
        perform_ocr_on_image,
        process_document_ocr,
    )
    return {
        "store_document": store_document,
        "get_document_by_id": get_document_by_id,
        "list_documents_for_claim": list_documents_for_claim,
        "list_documents_for_warranty": list_documents_for_warranty,
        "check_access_rights": check_access_rights,
        "check_document_hash_exists": check_document_hash_exists,
        "perform_ocr_on_image": perform_ocr_on_image,
        "process_document_ocr": process_document_ocr,
    }

def get_export_service():
    from src.services.export_service import (
        export_claims_csv,
        export_claims_excel,
        export_reviews_csv,
        export_audit_logs_csv,
    )
    return {
        "export_claims_csv": export_claims_csv,
        "export_claims_excel": export_claims_excel,
        "export_reviews_csv": export_reviews_csv,
        "export_audit_logs_csv": export_audit_logs_csv,
    }

def get_report_service():
    from src.services.report_service import generate_claim_pdf_report
    return {"generate_claim_pdf_report": generate_claim_pdf_report}

def get_audit_service():
    from src.services.audit_service import list_audit_logs, log_action
    return {"list_audit_logs": list_audit_logs, "log_action": log_action}

def get_model_version_service():
    from src.services.model_version_service import get_current_active_model, list_model_versions
    return {"get_current_active_model": get_current_active_model, "list_model_versions": list_model_versions}

def get_tm_service():
    from src.services.tm_service import predict_visual_claim, accept_frontend_tm_result
    return {"predict_visual_claim": predict_visual_claim, "accept_frontend_tm_result": accept_frontend_tm_result}

def get_prep_assist_service():
    from src.services.prep_assist_service import analyze_claim_readiness
    return {"analyze_claim_readiness": analyze_claim_readiness}

def get_preprocessing_service():
    from src.services.preprocessing_service import compute_derived_fields
    return {"compute_derived_fields": compute_derived_fields}

def get_validation_service():
    from src.services.validation_service import (
        validate_claim_amount,
        validate_claim_dates,
        validate_claim_payload,
    )
    return {
        "validate_claim_amount": validate_claim_amount,
        "validate_claim_dates": validate_claim_dates,
        "validate_claim_payload": validate_claim_payload,
    }

def get_duplicate_service():
    from src.services.duplicate_service import check_duplicate_claim, check_duplicate_document
    return {"check_duplicate_claim": check_duplicate_claim, "check_duplicate_document": check_duplicate_document}

def get_contradiction_service():
    from src.services.contradiction_service import detect_contradictions
    return {"detect_contradictions": detect_contradictions}

def get_missing_doc_service():
    from src.services.missing_doc_service import check_missing_documents
    return {"check_missing_documents": check_missing_documents}

def get_serial_service():
    from src.services.serial_service import verify_serial_number
    return {"verify_serial_number": verify_serial_number}

def get_ai_summary_service():
    from src.services.ai_summary_service import summarize_claim
    return {"summarize_claim": summarize_claim}

def get_alert_service():
    from src.services.alert_service import check_system_anomalies
    return {"check_system_anomalies": check_system_anomalies}

# Export commonly used functions directly
__all__ = [
    # User/Auth
    "create_user", "get_user_by_email", "get_user_by_id", "list_users",
    "update_profile", "update_user_role", "update_user_status", "change_password",
    "register_user", "authenticate_user", "create_user_tokens",
    "refresh_access_token", "validate_token",
    # Lazy loaders
    "get_claim_service", "get_product_service", "get_warranty_service",
    "get_document_service", "get_prediction_service", "get_rule_engine",
    "get_comparison_service", "get_decision_service", "get_explanation_service",
    "get_review_service", "get_dashboard_service", "get_analytics_service",
    "get_notification_service", "get_document_service_full",
    "get_export_service", "get_report_service", "get_audit_service",
    "get_model_version_service", "get_tm_service", "get_prep_assist_service",
    "get_preprocessing_service", "get_validation_service", "get_duplicate_service",
    "get_contradiction_service", "get_missing_doc_service", "get_serial_service",
    "get_ai_summary_service", "get_alert_service",
]