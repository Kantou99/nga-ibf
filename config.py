#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nigeria IBF System Configuration
Central configuration for Impact-Based Forecasting system
"""

from pathlib import Path
from datetime import datetime

# ============================================================================
# SYSTEM INFORMATION
# ============================================================================

SYSTEM_NAME = "Nigeria IBF System"
SYSTEM_VERSION = "1.0.0"
SYSTEM_DESCRIPTION = "Impact-Based Forecasting for Conflict and Flood Displacement"
ORGANIZATION = "United Nations - Nigeria"
LAST_UPDATED = datetime.now().strftime("%Y-%m-%d")

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, OUTPUTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# ============================================================================
# DATA FILES
# ============================================================================

DATA_FILES = {
    'dtm_monthly': DATA_DIR / 'displacement_events_monthly.csv',
    'dtm_lga_stats': DATA_DIR / 'displacement_statistics_by_lga.csv',
    'nema_lga_risk': DATA_DIR / 'nema_flood_risk_by_lga.csv',
    'nema_full': DATA_DIR / 'nema_flood_data_cleaned.csv',
    'exposure_csv': DATA_DIR / 'exposure_nigeria_lga_aggregated.csv',
}

# ============================================================================
# FORECAST PARAMETERS
# ============================================================================

CONFLICT_FORECAST_HORIZON = 4  # 4 weeks
FLOOD_FORECAST_HORIZON = 2     # 2 weeks

RISK_THRESHOLDS = {
    'very_high': 0.80,
    'high': 0.60,
    'moderate': 0.40,
    'low': 0.20,
}

BAY_STATES = ['Borno', 'Adamawa', 'Yobe']

# Seasonal patterns
RAINY_SEASON_MONTHS = [6, 7, 8, 9, 10]  # June-October
DRY_SEASON_MONTHS = [11, 12, 1, 2, 3]   # November-March

def validate_config():
    print(f"✅ {SYSTEM_NAME} v{SYSTEM_VERSION}")
    for key, path in DATA_FILES.items():
        status = "✅" if path.exists() else "❌"
        print(f"{status} {key}: {path.name}")

if __name__ == "__main__":
    validate_config()
