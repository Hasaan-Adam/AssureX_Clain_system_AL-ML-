"""Generate all 11 Demo Claim Scenarios for AssureX Claim Engine.

Creates rich structured claim.json and high-fidelity receipt.jpg for each scenario.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def generate_sample_claims():
    scenarios = [
        {
            "dir": "01_valid_claim",
            "claim_id": "CLM-DEMO-001",
            "label": "Valid Claim",
            "scenario": "complete_active_warranty",
            "product_id": "PRD-ELE-27927",
            "user_id": "USR-92345",
            "product_name": 'Samsung 65" 4K Neo QLED TV',
            "product_category": "electronics",
            "brand": "Samsung",
            "model_number": "QN65QN90C",
            "serial_number": "ELC-SAM-904751",
            "serial_status": "match",
            "purchase_date": "2024-03-10",
            "purchase_price": 218000,
            "retailer": "Samsung Official Flagship Store",
            "retailer_address": "Plot 14-C, Main Boulevard, Gulberg III, Lahore",
            "warranty_duration_months": 24,
            "warranty_type": "standard",
            "warranty_start_date": "2024-03-10",
            "warranty_expiry_date": "2026-03-10",
            "warranty_active": "yes",
            "remaining_warranty_days": 572,
            "claim_submission_date": "2024-08-15",
            "product_age_days": 158,
            "fault_occurrence_date": "2024-08-05",
            "fault_type": "hardware_failure",
            "fault_description": "Vertical colored distortion lines appeared across right LED matrix panel during standard operation. No external impact or power surge.",
            "damage_type": "manufacturing_defect",
            "covered_fault": "yes",
            "claim_reporting_days": 10,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 0,
            "last_repair_date": "",
            "repair_authorized": "none",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "no",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "PASS",
                "hard_stop": False,
                "violations": [],
            },
            "expected_python_prediction": {
                "label": "Valid Claim",
                "confidence": 0.985,
            },
            "expected_tm_prediction": {
                "label": "Valid Claim",
                "confidence": 0.962,
            },
            "expected_final_decision": "AUTO_APPROVE",
            "demo_notes": "Golden standard valid claim. Active 24-month OEM warranty, covered display matrix failure, 100% document completeness, valid receipt and serial match.",
        },
        {
            "dir": "02_invalid_claim",
            "claim_id": "CLM-DEMO-002",
            "label": "Invalid Claim",
            "scenario": "excluded_damage_type",
            "product_id": "PRD-MOB-88412",
            "user_id": "USR-61955",
            "product_name": "iPhone 15 Pro Max 256GB",
            "product_category": "mobile_phones",
            "brand": "Apple",
            "model_number": "A3106",
            "serial_number": "MPH-APP-884129",
            "serial_status": "match",
            "purchase_date": "2024-01-10",
            "purchase_price": 465000,
            "retailer": "iStore Pakistan Authorized Reseller",
            "retailer_address": "Dolmen Mall Clifton, Karachi",
            "warranty_duration_months": 12,
            "warranty_type": "standard",
            "warranty_start_date": "2024-01-10",
            "warranty_expiry_date": "2025-01-10",
            "warranty_active": "yes",
            "remaining_warranty_days": 243,
            "claim_submission_date": "2024-05-12",
            "product_age_days": 123,
            "fault_occurrence_date": "2024-05-08",
            "fault_type": "liquid_spill_damage",
            "fault_description": "Device dropped in water basin; red Liquid Contact Indicator (LCI) tripped inside SIM tray, device will not boot.",
            "damage_type": "accidental_damage",
            "covered_fault": "no",
            "claim_reporting_days": 4,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 0,
            "last_repair_date": "",
            "repair_authorized": "none",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "yes",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FAIL",
                "hard_stop": True,
                "violations": [
                    "POLICY_EXCLUSION: Liquid/Submersion Damage (Clause 4.1)"
                ],
            },
            "expected_python_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.992,
            },
            "expected_tm_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.978,
            },
            "expected_final_decision": "AUTO_REJECT",
            "demo_notes": "Explicit policy exclusion scenario. Claim clearly describes liquid immersion and corrosion which is excluded under Section 4.1 of the warranty agreement.",
        },
        {
            "dir": "03_manual_review_claim",
            "claim_id": "CLM-DEMO-003",
            "label": "Manual Review",
            "scenario": "missing_mandatory_documents",
            "product_id": "PRD-ELE-55193",
            "user_id": "USR-48201",
            "product_name": "Dell XPS 15 9530 Core i7",
            "product_category": "electronics",
            "brand": "Dell",
            "model_number": "XPS-9530-OLED",
            "serial_number": "ELC-DEL-551930",
            "serial_status": "match",
            "purchase_date": "2024-02-14",
            "purchase_price": 345000,
            "retailer": "MegaTech Computers",
            "retailer_address": "Hafeez Centre, Ground Floor, Lahore",
            "warranty_duration_months": 12,
            "warranty_type": "standard",
            "warranty_start_date": "2024-02-14",
            "warranty_expiry_date": "2025-02-14",
            "warranty_active": "yes",
            "remaining_warranty_days": 209,
            "claim_submission_date": "2024-07-20",
            "product_age_days": 157,
            "fault_occurrence_date": "2024-07-10",
            "fault_type": "power_supply_failure",
            "fault_description": "Internal power management chip failure. Laptop suddenly shuts off when plugged into charger.",
            "damage_type": "component_failure",
            "covered_fault": "yes",
            "claim_reporting_days": 10,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 0,
            "last_repair_date": "",
            "repair_authorized": "none",
            "previous_replacement": "no",
            "receipt_available": "no",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 1,
            "mandatory_docs_complete": "no",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "no",
            "proof_of_purchase": "no",
            "excluded_damage": "no",
            "ocr_quality": "medium",
            "expected_rule_result": {
                "status": "FLAG_REVIEW",
                "hard_stop": False,
                "violations": [
                    "MISSING_DOC: Mandatory Proof of Purchase Receipt Missing"
                ],
            },
            "expected_python_prediction": {
                "label": "Manual Review",
                "confidence": 0.924,
            },
            "expected_tm_prediction": {
                "label": "Manual Review",
                "confidence": 0.896,
            },
            "expected_final_decision": "MANUAL_REVIEW",
            "demo_notes": "Document defect scenario. Claimant provided warranty card and diagnostic photos but omitted the commercial purchase invoice.",
        },
        {
            "dir": "04_expired_warranty",
            "claim_id": "CLM-DEMO-004",
            "label": "Invalid Claim",
            "scenario": "warranty_expired_hard",
            "product_id": "PRD-HOM-44102",
            "user_id": "USR-80928",
            "product_name": "Panasonic Inverter Microwave 32L",
            "product_category": "home_appliances",
            "brand": "Panasonic",
            "model_number": "NN-ST65JB",
            "serial_number": "HAP-PAN-441029",
            "serial_status": "match",
            "purchase_date": "2022-11-15",
            "purchase_price": 42000,
            "retailer": "Al-Fatah Electronics Hub",
            "retailer_address": "Mall of Lahore, Cantt, Lahore",
            "warranty_duration_months": 12,
            "warranty_type": "standard",
            "warranty_start_date": "2022-11-15",
            "warranty_expiry_date": "2023-11-15",
            "warranty_active": "no",
            "remaining_warranty_days": -90,
            "claim_submission_date": "2024-02-13",
            "product_age_days": 455,
            "fault_occurrence_date": "2024-02-05",
            "fault_type": "hardware_failure",
            "fault_description": "Magnetron stopped heating food; turntable turns but no microwave radiation generated.",
            "damage_type": "component_failure",
            "covered_fault": "yes",
            "claim_reporting_days": 8,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 0,
            "last_repair_date": "",
            "repair_authorized": "none",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "no",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FAIL",
                "hard_stop": True,
                "violations": [
                    "WARRANTY_EXPIRED: Policy expired 90 days prior to claim date"
                ],
            },
            "expected_python_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.995,
            },
            "expected_tm_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.981,
            },
            "expected_final_decision": "AUTO_REJECT",
            "demo_notes": "Hard warranty expiration scenario. Policy expired 90 days before claim filing, well beyond the allowable 15-day grace threshold.",
        },
        {
            "dir": "05_missing_document",
            "claim_id": "CLM-DEMO-005",
            "label": "Manual Review",
            "scenario": "missing_mandatory_documents",
            "product_id": "PRD-HOM-77291",
            "user_id": "USR-99983",
            "product_name": "Haier Inverter Refrigerator 438L",
            "product_category": "home_appliances",
            "brand": "Haier",
            "model_number": "HRF-438IDRA",
            "serial_number": "HAP-HAI-772910",
            "serial_status": "match",
            "purchase_date": "2023-09-01",
            "purchase_price": 148000,
            "retailer": "Metro Cash & Carry",
            "retailer_address": "Thokar Niaz Baig, Lahore",
            "warranty_duration_months": 36,
            "warranty_type": "standard",
            "warranty_start_date": "2023-09-01",
            "warranty_expiry_date": "2026-09-01",
            "warranty_active": "yes",
            "remaining_warranty_days": 760,
            "claim_submission_date": "2024-08-02",
            "product_age_days": 336,
            "fault_occurrence_date": "2024-07-28",
            "fault_type": "compressor_failure",
            "fault_description": "Cooling stopped in freezer section; compressor makes clicking noise without starting.",
            "damage_type": "component_failure",
            "covered_fault": "yes",
            "claim_reporting_days": 5,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 2,
            "last_repair_date": "2024-03-15",
            "repair_authorized": "yes",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 1,
            "mandatory_docs_complete": "no",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "no",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FLAG_REVIEW",
                "hard_stop": False,
                "violations": [
                    "MISSING_DOC: Prior Authorized Service Center Repair Report Required"
                ],
            },
            "expected_python_prediction": {
                "label": "Manual Review",
                "confidence": 0.941,
            },
            "expected_tm_prediction": {
                "label": "Manual Review",
                "confidence": 0.912,
            },
            "expected_final_decision": "MANUAL_REVIEW",
            "demo_notes": "Repair history verification scenario. The claim indicates 2 prior repairs, requiring official repair service sheets to verify OEM parts integrity.",
        },
        {
            "dir": "06_duplicate_claim",
            "claim_id": "CLM-DEMO-006",
            "label": "Invalid Claim",
            "scenario": "duplicate_claim",
            "product_id": "PRD-HOM-33910",
            "user_id": "USR-13400",
            "product_name": "Samsung Front Load EcoBubble Washer 9kg",
            "product_category": "home_appliances",
            "brand": "Samsung",
            "model_number": "WW90T554DAX",
            "serial_number": "HAP-SAM-339102",
            "serial_status": "match",
            "purchase_date": "2023-11-20",
            "purchase_price": 195000,
            "retailer": "Hyperstar Packages Mall",
            "retailer_address": "Walton Road, Lahore",
            "warranty_duration_months": 24,
            "warranty_type": "standard",
            "warranty_start_date": "2023-11-20",
            "warranty_expiry_date": "2025-11-20",
            "warranty_active": "yes",
            "remaining_warranty_days": 468,
            "claim_submission_date": "2024-08-09",
            "product_age_days": 263,
            "fault_occurrence_date": "2024-07-25",
            "fault_type": "motor_failure",
            "fault_description": "Digital Inverter motor shaking violently during spin cycle with error code 3E.",
            "damage_type": "component_failure",
            "covered_fault": "yes",
            "claim_reporting_days": 15,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 1,
            "last_repair_date": "2024-06-10",
            "repair_authorized": "yes",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "yes",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "yes",
            "duplicate_of_claim_id": "CLM-00042",
            "document_hash_match": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "proof_of_purchase": "yes",
            "excluded_damage": "no",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FAIL",
                "hard_stop": True,
                "violations": [
                    "FRAUD_TRIGGER: Exact Duplicate Claim & Document Hash Detected (Original CLM-00042)"
                ],
            },
            "expected_python_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.987,
            },
            "expected_tm_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.965,
            },
            "expected_final_decision": "AUTO_REJECT",
            "demo_notes": "Duplicate submission attack. System detects matching SHA-256 receipt image hash and identical active claim CLM-00042 in database.",
        },
        {
            "dir": "07_contradictory_claim",
            "claim_id": "CLM-DEMO-007",
            "label": "Invalid Claim",
            "scenario": "minor_data_contradiction",
            "product_id": "PRD-ELE-66231",
            "user_id": "USR-77508",
            "product_name": 'Sony Bravia XR 55" OLED TV',
            "product_category": "electronics",
            "brand": "Sony",
            "model_number": "XR-55A80L",
            "serial_number": "ELC-SON-662319",
            "serial_status": "match",
            "purchase_date": "2024-06-15",
            "purchase_price": 380000,
            "retailer": "Sony World Official Outlet",
            "retailer_address": "Blue Area, Islamabad",
            "warranty_duration_months": 24,
            "warranty_type": "standard",
            "warranty_start_date": "2024-06-15",
            "warranty_expiry_date": "2026-06-15",
            "warranty_active": "yes",
            "remaining_warranty_days": 700,
            "claim_submission_date": "2024-02-10",
            "product_age_days": -126,
            "fault_occurrence_date": "2024-02-01",
            "fault_type": "hardware_failure",
            "fault_description": "HDMI arc port audio handshake failed.",
            "damage_type": "component_failure",
            "covered_fault": "yes",
            "claim_reporting_days": 9,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 0,
            "last_repair_date": "",
            "repair_authorized": "none",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "yes",
            "contradiction_type": "claim_before_purchase",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "no",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FAIL",
                "hard_stop": True,
                "violations": [
                    "CHRONOLOGY_CONTRADICTION: Claim date 2024-02-10 precedes Purchase date 2024-06-15"
                ],
            },
            "expected_python_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.976,
            },
            "expected_tm_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.945,
            },
            "expected_final_decision": "AUTO_REJECT",
            "demo_notes": "Temporal contradiction detection. Claim and fault dates are recorded in February 2024, whereas purchase receipt states June 2024.",
        },
        {
            "dir": "08_serial_number_mismatch",
            "claim_id": "CLM-DEMO-008",
            "label": "Invalid Claim",
            "scenario": "serial_mismatch_confirmed",
            "product_id": "PRD-ELE-98214",
            "user_id": "USR-41686",
            "product_name": "HP Omen 16 Gaming Laptop",
            "product_category": "electronics",
            "brand": "HP",
            "model_number": "16-wf0033dx",
            "serial_number": "ELC-HP-869046",
            "serial_status": "mismatch",
            "detected_ocr_serial": "ELC-HP-998877",
            "purchase_date": "2024-04-10",
            "purchase_price": 410000,
            "retailer": "Shing Technologies",
            "retailer_address": "Techno City Mall, Karachi",
            "warranty_duration_months": 12,
            "warranty_type": "standard",
            "warranty_start_date": "2024-04-10",
            "warranty_expiry_date": "2025-04-10",
            "warranty_active": "yes",
            "remaining_warranty_days": 239,
            "claim_submission_date": "2024-08-14",
            "product_age_days": 126,
            "fault_occurrence_date": "2024-08-01",
            "fault_type": "overheating_issue",
            "fault_description": "GPU thermal throttling and shutdown under moderate load.",
            "damage_type": "manufacturing_defect",
            "covered_fault": "yes",
            "claim_reporting_days": 13,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 0,
            "last_repair_date": "",
            "repair_authorized": "none",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "yes",
            "contradiction_type": "serial_conflict",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "no",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FAIL",
                "hard_stop": True,
                "violations": [
                    "SERIAL_MISMATCH: Physical device serial ELC-HP-998877 conflicts with registered ELC-HP-869046"
                ],
            },
            "expected_python_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.991,
            },
            "expected_tm_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.982,
            },
            "expected_final_decision": "AUTO_REJECT",
            "demo_notes": "Serial swap / unit spoofing scenario. OCR inspection extracts serial number ELC-HP-998877 which does not match warranty registration ELC-HP-869046.",
        },
        {
            "dir": "09_unauthorized_repair",
            "claim_id": "CLM-DEMO-009",
            "label": "Invalid Claim",
            "scenario": "excluded_damage_type",
            "product_id": "PRD-HOM-41829",
            "user_id": "USR-66160",
            "product_name": "Gree Inverter Split AC 1.5 Ton",
            "product_category": "home_appliances",
            "brand": "Gree",
            "model_number": "GS-18FITH",
            "serial_number": "HAP-GRE-418290",
            "serial_status": "match",
            "purchase_date": "2023-08-10",
            "purchase_price": 165000,
            "retailer": "Carrefour LuckyOne",
            "retailer_address": "Federal B Area, Karachi",
            "warranty_duration_months": 36,
            "warranty_type": "standard",
            "warranty_start_date": "2023-08-10",
            "warranty_expiry_date": "2026-08-10",
            "warranty_active": "yes",
            "remaining_warranty_days": 725,
            "claim_submission_date": "2024-08-15",
            "product_age_days": 371,
            "fault_occurrence_date": "2024-08-05",
            "fault_type": "hardware_failure",
            "fault_description": "Outdoor PCB board burnt out following local unauthorized electrician wiring modification.",
            "damage_type": "unauthorized_modification",
            "covered_fault": "no",
            "claim_reporting_days": 10,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 1,
            "last_repair_date": "2024-07-20",
            "repair_authorized": "no",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "yes",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FAIL",
                "hard_stop": True,
                "violations": [
                    "POLICY_EXCLUSION: Third-party unauthorized tampering/repair voids warranty coverage (Clause 4.2)"
                ],
            },
            "expected_python_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.968,
            },
            "expected_tm_prediction": {
                "label": "Invalid Claim",
                "confidence": 0.938,
            },
            "expected_final_decision": "AUTO_REJECT",
            "demo_notes": "Unauthorized modification policy exclusion. Tamper seal breached and third-party wiring altered unit circuitry.",
        },
        {
            "dir": "10_boundary_date_claim",
            "claim_id": "CLM-DEMO-010",
            "label": "Manual Review",
            "scenario": "grace_period_boundary",
            "product_id": "PRD-MOB-55420",
            "user_id": "USR-56483",
            "product_name": "Samsung Galaxy Watch 6 Classic",
            "product_category": "mobile_phones",
            "brand": "Samsung",
            "model_number": "SM-R960",
            "serial_number": "MPH-SAM-554201",
            "serial_status": "match",
            "purchase_date": "2023-08-01",
            "purchase_price": 72000,
            "retailer": "Samsung Experience Center",
            "retailer_address": "Centaurus Mall, Islamabad",
            "warranty_duration_months": 12,
            "warranty_type": "standard",
            "warranty_start_date": "2023-08-01",
            "warranty_expiry_date": "2024-08-01",
            "warranty_active": "yes",
            "remaining_warranty_days": -12,
            "claim_submission_date": "2024-08-13",
            "product_age_days": 378,
            "fault_occurrence_date": "2024-07-28",
            "fault_type": "keyboard_or_button_failure",
            "fault_description": "Rotating bezel sensor unresponsive and back key stuck. Fault occurred 3 days before warranty expiry.",
            "damage_type": "component_failure",
            "covered_fault": "yes",
            "claim_reporting_days": 16,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 0,
            "last_repair_date": "",
            "repair_authorized": "none",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "no",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FLAG_REVIEW",
                "hard_stop": False,
                "violations": [
                    "BOUNDARY_CONDITION: Claim filed on Day 12 of 15-day Grace Period following Expiration"
                ],
            },
            "expected_python_prediction": {
                "label": "Manual Review",
                "confidence": 0.865,
            },
            "expected_tm_prediction": {
                "label": "Manual Review",
                "confidence": 0.832,
            },
            "expected_final_decision": "MANUAL_REVIEW",
            "demo_notes": "15-day grace period boundary condition. Warranty officially expired 12 days prior, but fault occurred during active coverage, requiring reviewer discretion.",
        },
        {
            "dir": "11_model_disagreement",
            "claim_id": "CLM-DEMO-011",
            "label": "Manual Review",
            "scenario": "grace_period_boundary",
            "product_id": "PRD-MOB-99014",
            "user_id": "USR-89499",
            "product_name": 'Apple iPad Air M2 11" 128GB',
            "product_category": "mobile_phones",
            "brand": "Apple",
            "model_number": "A2902",
            "serial_number": "MPH-APP-990145",
            "serial_status": "match",
            "purchase_date": "2023-09-15",
            "purchase_price": 175000,
            "retailer": "Future Tech Apple Premium Reseller",
            "retailer_address": "Kohinoor City, Faisalabad",
            "warranty_duration_months": 12,
            "warranty_type": "standard",
            "warranty_start_date": "2023-09-15",
            "warranty_expiry_date": "2024-09-15",
            "warranty_active": "yes",
            "remaining_warranty_days": 28,
            "claim_submission_date": "2024-08-18",
            "product_age_days": 338,
            "fault_occurrence_date": "2024-07-20",
            "fault_type": "charging_port_fault",
            "fault_description": "USB-C charging intermittent. Minor cosmetic scuffs on casing, port pins look oxidized.",
            "damage_type": "wear_and_tear",
            "covered_fault": "yes",
            "claim_reporting_days": 29,
            "within_reporting_period": "yes",
            "reporting_deadline_days": 30,
            "repair_history_count": 0,
            "last_repair_date": "",
            "repair_authorized": "none",
            "previous_replacement": "no",
            "receipt_available": "yes",
            "warranty_card_available": "yes",
            "product_image_available": "yes",
            "serial_evidence_available": "yes",
            "fault_evidence_available": "yes",
            "repair_report_available": "no",
            "missing_document_count": 0,
            "mandatory_docs_complete": "yes",
            "has_contradiction": "no",
            "contradiction_type": "none",
            "is_duplicate": "no",
            "proof_of_purchase": "yes",
            "excluded_damage": "no",
            "ocr_quality": "high",
            "expected_rule_result": {
                "status": "FLAG_REVIEW",
                "hard_stop": False,
                "violations": [
                    "MODEL_DIVERGENCE: Tabular ML (Valid Claim: 0.63) vs Vision TM (Manual Review: 0.78), Delta = 0.38"
                ],
            },
            "expected_python_prediction": {
                "label": "Valid Claim",
                "confidence": 0.635,
            },
            "expected_tm_prediction": {
                "label": "Manual Review",
                "confidence": 0.782,
            },
            "expected_final_decision": "MANUAL_REVIEW",
            "demo_notes": "AI Model Disagreement case. Tabular features lean Valid (active warranty, full docs), but Vision model detects borderline wear and tear / reporting threshold on card.",
        },
    ]

    base_dir = Path("sample_claims")
    base_dir.mkdir(exist_ok=True)

    for sc in scenarios:
        s_dir = base_dir / sc["dir"]
        s_dir.mkdir(exist_ok=True, parents=True)

        # 1. Write rich claim.json
        claim_file = s_dir / "claim.json"
        with open(claim_file, "w", encoding="utf-8") as f:
            json.dump(sc, f, indent=2)
        print(f"Wrote {claim_file}")

        # 2. Draw photorealistic receipt.jpg
        img_w, img_h = 750, 1050
        img = Image.new("RGB", (img_w, img_h), color=(252, 252, 250))
        draw = ImageDraw.Draw(img)

        # Receipt borders and aesthetic header
        draw.rectangle(
            [(20, 20), (img_w - 20, img_h - 20)],
            outline=(180, 180, 180),
            width=2,
        )
        draw.rectangle(
            [(25, 25), (img_w - 25, img_h - 25)],
            outline=(220, 220, 220),
            width=1,
        )

        # Header banner
        draw.rectangle([(30, 30), (img_w - 30, 110)], fill=(30, 41, 59))
        draw.text((50, 45), sc["retailer"].upper(), fill=(255, 255, 255))
        draw.text(
            (50, 75),
            "TAX INVOICE / SALES RECEIPT & WARRANTY CERTIFICATE",
            fill=(148, 163, 184),
        )

        # Meta info
        y = 125
        draw.text(
            (50, y),
            f'Store Location: {sc.get("retailer_address", "Commercial Avenue, Tech City")}',
            fill=(50, 50, 50),
        )
        y += 24
        draw.text(
            (50, y),
            "NTN/STRN: 7392104-8  |  POS Terminal ID: POS-PK-0921",
            fill=(80, 80, 80),
        )
        y += 24
        inv_id = sc["claim_id"].replace("CLM-", "")
        draw.text(
            (50, y),
            f'Invoice No: INV-{inv_id}-2024  |  Date: {sc["purchase_date"]} 14:32 PKT',
            fill=(80, 80, 80),
        )
        y += 24
        draw.text(
            (50, y),
            f'Customer ID: {sc["user_id"]}  |  Registered Name: Verified Customer',
            fill=(80, 80, 80),
        )

        y += 35
        draw.line([(40, y), (img_w - 40, y)], fill=(200, 200, 200), width=2)

        # Table Header
        y += 10
        draw.rectangle([(40, y), (img_w - 40, y + 30)], fill=(241, 245, 249))
        draw.text(
            (50, y + 7), "ITEM DESCRIPTION / SERIAL #", fill=(15, 23, 42)
        )
        draw.text((430, y + 7), "QTY", fill=(15, 23, 42))
        draw.text((510, y + 7), "UNIT (PKR)", fill=(15, 23, 42))
        draw.text((630, y + 7), "TOTAL", fill=(15, 23, 42))

        y += 40
        # Line item
        draw.text(
            (50, y), f'{sc["brand"]} {sc["product_name"]}', fill=(15, 23, 42)
        )
        y += 22
        draw.text(
            (60, y),
            f'Model: {sc["model_number"]} | S/N: {sc["serial_number"]}',
            fill=(100, 116, 139),
        )
        draw.text((440, y - 10), "1", fill=(15, 23, 42))
        price_str = f'{sc["purchase_price"]:,}'
        draw.text((510, y - 10), price_str, fill=(15, 23, 42))
        draw.text((620, y - 10), price_str, fill=(15, 23, 42))

        y += 30
        draw.text(
            (50, y),
            f'Warranty Tier: {sc["warranty_type"].capitalize()} OEM Coverage ({sc["warranty_duration_months"]} Months)',
            fill=(16, 149, 193),
        )
        draw.text((630, y), "INCLUDED", fill=(16, 149, 193))

        y += 40
        draw.line([(40, y), (img_w - 40, y)], fill=(226, 232, 240), width=1)

        # Summary totals
        y += 20
        subtotal = sc["purchase_price"]
        gst = int(subtotal * 0.18)
        grand_total = subtotal + gst

        draw.text((420, y), "Subtotal:", fill=(71, 85, 105))
        draw.text((600, y), f"PKR {subtotal:,}", fill=(15, 23, 42))
        y += 24
        draw.text((420, y), "Sales Tax (18% GST):", fill=(71, 85, 105))
        draw.text((600, y), f"PKR {gst:,}", fill=(15, 23, 42))
        y += 24
        draw.text((420, y), "Total Paid (Settled):", fill=(15, 23, 42))
        draw.text((580, y), f"PKR {grand_total:,}", fill=(15, 23, 42))

        y += 40
        draw.line([(40, y), (img_w - 40, y)], fill=(200, 200, 200), width=2)

        # Warranty terms & bar
        y += 20
        draw.text(
            (50, y),
            "OFFICIAL WARRANTY REGISTRATION & TERMS:",
            fill=(15, 23, 42),
        )
        y += 24
        terms = [
            f'1. Product Warranty is valid from {sc["warranty_start_date"]} until {sc["warranty_expiry_date"]}.',
            (
                "2. Covers internal hardware & manufacturing defects under"
                " normal operating usage."
            ),
            (
                "3. Excludes water/liquid ingress, physical casing impact, and"
                " unauthorized repairs."
            ),
            (
                "4. To submit a claim, retain this verified invoice and register"
                " on AssureX Portal."
            ),
        ]
        for t in terms:
            draw.text((50, y), t, fill=(100, 116, 139))
            y += 20

        y += 25
        # Barcode aesthetic simulation
        draw.rectangle([(50, y), (img_w - 50, y + 45)], fill=(245, 245, 245))
        for bx in range(60, img_w - 60, 6):
            if (bx % 12 == 0) or (bx % 18 == 0):
                draw.rectangle([(bx, y + 5), (bx + 3, y + 40)], fill=(0, 0, 0))
        y += 55
        draw.text(
            (img_w // 2 - 120, y),
            f'* {sc["serial_number"]} *',
            fill=(80, 80, 80),
        )

        y += 35
        draw.rectangle([(40, y), (img_w - 40, y + 40)], fill=(241, 245, 249))
        draw.text(
            (55, y + 12),
            "AUTHENTICATED DIGITAL RECEIPT — ASSUREX VERIFIED DOCUMENT ID",
            fill=(71, 85, 105),
        )

        receipt_path = s_dir / "receipt.jpg"
        img.save(receipt_path, "JPEG", quality=95)
        print(f"Generated receipt image: {receipt_path}")


if __name__ == "__main__":
    generate_sample_claims()
