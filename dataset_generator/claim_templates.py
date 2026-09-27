"""Raw material for warranty claim records: products, brands, faults, retailers."""

PRODUCT_CATALOG = [
    {
        "category": "electronics",
        "name": "LED Television",
        "brands": ["Samsung", "LG", "Sony", "Hisense"],
        "price_range": (45000, 220000),
        "warranty_months_options": [12, 24, 36],
    },
    {
        "category": "electronics",
        "name": "Laptop",
        "brands": ["Dell", "HP", "Lenovo", "Asus"],
        "price_range": (65000, 400000),
        "warranty_months_options": [12, 24, 36],
    },
    {
        "category": "electronics",
        "name": "Desktop Computer",
        "brands": ["Dell", "HP", "Lenovo"],
        "price_range": (50000, 300000),
        "warranty_months_options": [12, 24],
    },
    {
        "category": "electronics",
        "name": "Wireless Headphones",
        "brands": ["Sony", "JBL", "Bose", "Samsung"],
        "price_range": (8000, 60000),
        "warranty_months_options": [6, 12, 24],
    },
    {
        "category": "electronics",
        "name": "Printer",
        "brands": ["HP", "Canon", "Epson"],
        "price_range": (15000, 90000),
        "warranty_months_options": [12, 24],
    },
    {
        "category": "home_appliances",
        "name": "Refrigerator",
        "brands": ["Samsung", "LG", "Haier", "Dawlance"],
        "price_range": (55000, 350000),
        "warranty_months_options": [12, 24, 36],
    },
    {
        "category": "home_appliances",
        "name": "Washing Machine",
        "brands": ["Samsung", "LG", "Haier", "Dawlance"],
        "price_range": (40000, 250000),
        "warranty_months_options": [12, 24],
    },
    {
        "category": "home_appliances",
        "name": "Microwave Oven",
        "brands": ["Samsung", "LG", "Panasonic"],
        "price_range": (18000, 80000),
        "warranty_months_options": [12, 24],
    },
    {
        "category": "home_appliances",
        "name": "Air Conditioner",
        "brands": ["Samsung", "LG", "Haier", "Gree"],
        "price_range": (70000, 400000),
        "warranty_months_options": [12, 24, 36],
    },
    {
        "category": "home_appliances",
        "name": "Vacuum Cleaner",
        "brands": ["Dyson", "Samsung", "LG"],
        "price_range": (12000, 120000),
        "warranty_months_options": [12, 24],
    },
    {
        "category": "mobile_phones",
        "name": "Smartphone",
        "brands": ["Samsung", "Apple", "Xiaomi", "OnePlus", "Vivo"],
        "price_range": (25000, 450000),
        "warranty_months_options": [6, 12, 24],
    },
    {
        "category": "mobile_phones",
        "name": "Tablet",
        "brands": ["Samsung", "Apple", "Lenovo", "Xiaomi"],
        "price_range": (30000, 250000),
        "warranty_months_options": [12, 24],
    },
    {
        "category": "mobile_phones",
        "name": "Smartwatch",
        "brands": ["Samsung", "Apple", "Huawei", "Xiaomi"],
        "price_range": (8000, 120000),
        "warranty_months_options": [6, 12],
    },
]

RETAILERS = [
    "Metro Electronics",
    "City Mart Stores",
    "Online - ShopPak",
    "Online - PriceOye",
    "United Mobile Mall",
    "HomeStyle Appliances",
    "TechBazaar Official",
    "Brand Outlet Center",
    "QuickCommerce Store",
    "National Distributors",
]

COVERED_FAULTS = [
    "hardware_failure",
    "battery_degradation",
    "display_issue",
    "compressor_failure",
    "motor_failure",
    "charging_port_fault",
    "software_defect",
    "power_supply_failure",
    "overheating_issue",
    "keyboard_or_button_failure",
    "fan_or_cooling_failure",
    "audio_output_failure",
]

EXCLUDED_FAULTS = [
    "physical_drop_damage",
    "liquid_spill_damage",
    "unauthorized_modification",
    "normal_wear_and_tear",
    "theft_or_loss",
    "electrical_surge_misuse",
    "pest_or_environment_damage",
]

DAMAGE_TYPES = [
    "manufacturing_defect",
    "performance_degradation",
    "component_failure",
    "accidental_damage",
    "environmental_damage",
    "wear_and_tear",
]

FAULT_DESCRIPTIONS = {
    "covered": [
        "Device stopped working during normal use",
        "Component failed without external damage",
        "Performance dropped significantly within warranty period",
        "Unit does not power on under normal conditions",
        "Intermittent fault observed during regular operation",
        "Part replacement required due to internal failure",
    ],
    "excluded": [
        "Visible cracks after accidental drop",
        "Water damage found inside the unit",
        "Modified firmware detected on the device",
        "Physical wear consistent with long-term misuse",
        "Damage caused by power surge from external source",
    ],
}

CONTRADICTION_TYPES = [
    "claim_before_purchase",
    "repair_before_purchase",
    "model_mismatch",
    "serial_conflict",
    "fault_after_claim",
]

SERIAL_PREFIXES = {
    "electronics": "ELC",
    "home_appliances": "HAP",
    "mobile_phones": "MPH",
}
