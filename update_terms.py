import os
import re

def replace_in_file(filepath, replacements):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        for old, new in replacements:
            content = content.replace(old, new)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    except Exception as e:
        print(f"Error in {filepath}: {e}")

replacements_comp = [
    ('Model 1: Python XGBoost', 'Python Classification Model'),
    ('Model 2: Google GTM', 'Google Teachable Machine Model'),
    ('Ensemble Delta (Δ)', 'Confidence Difference'),
    ('Ensemble Delta', 'Confidence Difference'),
    ('Tabular Data Confidence', 'Confidence Score'),
    ('Visual Defect Confidence', 'Confidence Score'),
    ('Agreement:', 'Model Consistency Status:')
]
replace_in_file('frontend/src/components/claim/ComparisonPanel.jsx', replacements_comp)

replacements_pred = [
    ('Model 1: Python ML (XGBoost / Random Forest)', 'Python Classification Model'),
    ('Model 2: Google Teachable Machine / Vision', 'Google Teachable Machine Model'),
    ('Teachable Machine (Vision)', 'Google Teachable Machine Model'),
    ('Python ML Model', 'Python Classification Model')
]
replace_in_file('frontend/src/components/claim/PredictionPanel.jsx', replacements_pred)

replacements_rule = [
    ('Warranty Policy Verification', 'Warranty Rule Validation'),
    ('Policy Rule Evaluation Engine', 'Warranty Rule Validation'),
    ('Chronological Contradiction Detected', 'Contradiction Detection'),
    ('Possible Contradictions', 'Contradiction Detection')
]
replace_in_file('frontend/src/components/claim/RuleResultPanel.jsx', replacements_rule)

replacements_prep = [
    ('Missing Documents', 'Missing Document Detection')
]
replace_in_file('frontend/src/components/claim/PreparationAssistancePanel.jsx', replacements_prep)

replacements_dup = [
    ('Duplicate Claim Velocity Alert Detected', 'Duplicate Claim Detection')
]
replace_in_file('frontend/src/components/claim/DuplicateAlert.jsx', replacements_dup)

replacements_repair = [
    ('Log Repair History', 'Repair History Management'),
    ('Log Repair', 'Repair History Management')
]
replace_in_file('frontend/src/components/claim/RepairModal.jsx', replacements_repair)

replacements_dash_admin = [
    ('Admin Dashboard', 'Administrator Dashboard'),
    ('Claim Distribution by Status', 'Claim Status Tracking')
]
replace_in_file('frontend/src/pages/AdminDashboardPage.jsx', replacements_dash_admin)
replace_in_file('frontend/src/components/dashboard/AdminDashboard.jsx', replacements_dash_admin)

replacements_sidebar = [
    ("name: 'Dashboard'", "name: 'Claim Dashboard'")
]
replace_in_file('frontend/src/components/common/Sidebar.jsx', replacements_sidebar)

replacements_nav = [
    ('My Profile', 'User Profile Management')
]
replace_in_file('frontend/src/components/common/Navbar.jsx', replacements_nav)

replace_in_file('frontend/src/components/claim/SummaryCardView.jsx', [
    ('Claim Summary Card (Teachable Machine Input)', 'Claim Summary Card')
])

replace_in_file('frontend/src/components/claim/GTMPredictor.jsx', [
    ('Google Teachable Machine - Visual Claim Analysis', 'Google Teachable Machine Model'),
    ('AssureX Claim Summary Card', 'Claim Summary Card')
])
