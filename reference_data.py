"""
IS 10262 : 2019  &  IS 456 : 2000
Reference tables used in concrete mix design
"""

# Standard deviation (IS 10262 Table 1)
SD_TABLE = {
    20: 4.0,
    25: 4.0,
    30: 5.0,
    35: 5.0,
    40: 5.0,
}

# Exposure condition requirements (IS 456 Table 5)
EXPOSURE_TABLE = {
    "mild":       {"max_wc": 0.55, "min_cement": 300, "min_grade": "M20"},
    "moderate":   {"max_wc": 0.50, "min_cement": 300, "min_grade": "M25"},
    "severe":     {"max_wc": 0.45, "min_cement": 320, "min_grade": "M30"},
    "very_severe":{"max_wc": 0.40, "min_cement": 340, "min_grade": "M35"},
    "extreme":    {"max_wc": 0.35, "min_cement": 360, "min_grade": "M40"},
}

# Free water content liters/m³ (IS 10262 Table 2)
# Keys: aggregate size (mm) → slump (mm)
WATER_CONTENT_TABLE = {
    10: {25: 180, 75: 200, 125: 220},
    20: {25: 160, 75: 180, 125: 200},
    40: {25: 140, 75: 160, 125: 180},
}

# Volume of coarse aggregate per m³ of concrete (IS 10262 Table 3)
# Keys: aggregate size (mm) → FA zone (1–4)
CA_VOLUME_TABLE = {
    10: {1: 0.50, 2: 0.48, 3: 0.46, 4: 0.44},
    20: {1: 0.66, 2: 0.64, 3: 0.62, 4: 0.60},
    40: {1: 0.75, 2: 0.73, 3: 0.71, 4: 0.69},
}

# Cement types and typical specific gravity
CEMENT_TYPES = {
    "OPC 43 Grade": 3.15,
    "OPC 53 Grade": 3.15,
    "PPC":          3.10,
    "PSC":          2.90,
    "SRC":          3.15,
}

# Target mean strength formula (IS 10262 Cl. 3.2)
# f'ck = fck + 1.65 × s
# where s = standard deviation from table above

# Admixture water reduction factors
ADMIXTURE_REDUCTION = {
    "none":             1.00,
    "plasticizer":      0.90,
    "superplasticizer": 0.80,
}
