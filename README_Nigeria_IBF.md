# Impact-Based Forecasting for Displacement in Nigeria
## Adapted from Tropical Cyclone Framework for Conflict and Flood Events

This repository contains code adapted from the TC Yasa case study to implement impact-based forecasting for displacement caused by floods and conflict in Nigeria.

---

## Overview

Impact-based forecasting (IBF) shifts from predicting *what* a hazard will be to predicting *what* it will do. This adaptation applies the methodology to:

1. **Flood Events**: Riverine floods, flash floods, and urban flooding
2. **Conflict Events**: Armed conflict, communal violence, and insurgency

### Key Differences from TC Framework

| Aspect | TC Framework (Original) | Nigeria Adaptation |
|--------|------------------------|-------------------|
| **Hazard Type** | Tropical cyclones | Floods + Conflict |
| **Geographic Scope** | Fiji (island nation) | Nigeria (large country) |
| **Data Sources** | ECMWF TIGGE, IBTrACS | GloFAS, ACLED, local forecasts |
| **Vulnerability** | Wind-based (v_half parameter) | Context-specific (regional) |
| **Displacement Drivers** | Single hazard (wind) | Multi-hazard (water + violence) |
| **Lead Time Focus** | 0.5-3 days | 1-7 days (varies by hazard) |

---

## Repository Structure

```
nigeria_ibf/
├── README.md                                    # This file
├── data/                                        # Data directory (not included)
│   ├── nigeria_centroids_1km.hdf5
│   ├── 2017_2024_Nigeria_displacement_events.xlsx
│   ├── flood_forecast_{date}.nc
│   ├── conflict_forecast_{date}.csv
│   └── hazards/
│       ├── flood_*.hdf5
│       └── conflict_*.hdf5
├── scripts/
│   ├── nigeria_conflict_floods_2d_leadtime.py   # Main forecast script
│   ├── nigeria_hazard_processing.py             # Hazard data processing
│   ├── nigeria_historical_uncertainty_analysis.py # Historical calibration
│   ├── nigeria_data_preparation.py              # Data preparation utilities
│   └── nigeria_results_visualization.py         # Visualization tools
├── results/                                     # Output directory
│   ├── nigeria_flood_displacement_*.xlsx
│   ├── nigeria_conflict_displacement_*.xlsx
│   └── visualizations/
└── uncertainty_analysis/                        # Uncertainty outputs
    └── historical_events/
        ├── flood/
        └── conflict/
```

---

## Installation

### Requirements

```bash
# Create conda environment
conda create -n nigeria_ibf python=3.9
conda activate nigeria_ibf

# Install CLIMADA
pip install climada

# Additional dependencies
pip install xarray netCDF4 pandas numpy scipy matplotlib geopandas
```

### CLIMADA Installation

Follow the official CLIMADA installation guide: https://climada-python.readthedocs.io/

---

## Data Requirements

### 1. Centroids
- **File**: `nigeria_centroids_1km.hdf5`
- **Resolution**: 1km on land, coarser on water
- **Format**: CLIMADA Centroids HDF5
- **Generation**: Use `climada.hazard.Centroids.from_raster()` or global centroids

### 2. Historical Events
- **File**: `2017_2024_Nigeria_displacement_events.xlsx`
- **Required columns**:
  - `event_id`: Unique identifier
  - `event_name`: Event name
  - `event_date`: Date/time of event
  - `event_year`: Year
  - `event_type`: 'flood' or 'conflict'
  - `state`: Affected state(s)
  - `min_lon`, `max_lon`, `min_lat`, `max_lat`: Bounding box
  - `reported_displacement`: Actual displacement numbers
  
- **Data sources**:
  - IOM DTM (Displacement Tracking Matrix)
  - IDMC (Internal Displacement Monitoring Centre)
  - NEMA (National Emergency Management Agency)

### 3. Flood Forecasts
- **Format**: NetCDF with ensemble forecasts
- **Variables needed**:
  - `flood_depth` (m) or `discharge` (m³/s)
  - `longitude`, `latitude`
  - `time`, `ensemble`
  
- **Sources**:
  - GloFAS (Global Flood Awareness System)
  - Local hydrological models
  - ECMWF precipitation forecasts

### 4. Conflict Forecasts
- **Format**: CSV with predicted events
- **Required columns**:
  - `latitude`, `longitude`
  - `predicted_fatalities`
  - `event_type`
  - `probability` (optional)
  - `scenario_id` (for ensembles)
  
- **Sources**:
  - ACLED (Armed Conflict Location & Event Data)
  - Conflict prediction models
  - Early warning systems

---

## Usage

### 1. Data Preparation

First, prepare your data:

```bash
python scripts/nigeria_data_preparation.py \
    --flood-data path/to/flood_forecast.nc \
    --conflict-data path/to/conflict_data.csv \
    --output-dir data/
```

### 2. Process Hazards

Convert forecast data into CLIMADA hazard objects:

```bash
python scripts/nigeria_hazard_processing.py \
    --run-datetime "2025-01-15T00:00:00" \
    --leadtime-days 2
```

This generates:
- `hazards/nigeria_flood_{datetime}_lead2d.hdf5`
- `hazards/nigeria_conflict_{datetime}_lead2d.hdf5`

### 3. Run Impact-Based Forecast

Execute the main forecasting script:

```bash
python scripts/nigeria_conflict_floods_2d_leadtime.py
```

This produces:
- Displacement forecasts with uncertainty ranges
- Sensitivity analysis showing key uncertainty drivers
- Regional breakdown of expected impacts

### 4. Historical Calibration

Validate the system using past events:

```bash
# Single year, single event type
python scripts/nigeria_historical_uncertainty_analysis.py 2020 flood 2d

# All years and event types
python scripts/nigeria_historical_uncertainty_analysis.py
```

### 5. Visualization

Generate visualizations:

```bash
python scripts/nigeria_results_visualization.py \
    --forecast-date 2025-01-15 \
    --output-dir results/visualizations/
```

---

## Configuration

### Regional Vulnerability Parameters

Vulnerability parameters are calibrated for six Nigerian geo-political zones:

**Flood Vulnerability** (intensity_half parameter in meters):
- **North West**: 0.12 - 0.42 m
- **North East**: 0.18 - 0.60 m (highest vulnerability)
- **North Central**: 0.10 - 0.42 m
- **South West**: 0.08 - 0.36 m (lowest vulnerability)
- **South East**: 0.11 - 0.44 m
- **South South**: 0.15 - 0.53 m

**Conflict Vulnerability** (intensity_half in fatalities):
- **North West**: 20 - 65
- **North East**: 30 - 75 (highest vulnerability)
- **North Central**: 15 - 60
- **South West**: 8 - 52 (lowest vulnerability)
- **South East**: 12 - 57
- **South South**: 18 - 63

These parameters represent the 10th to 90th percentile of observed vulnerability in each region based on 2017-2024 historical data.

### Uncertainty Parameters

```python
N_SAMPLE = 1000           # Monte Carlo samples
n_ev_haz = 1              # Hazard sub-sampling
bounds_totval = [0.8, 1.2]  # Exposure uncertainty (±20%)
```

---

## Outputs

### 1. Displacement Forecasts

Excel files with columns:
- `forecast_date`: When forecast was issued
- `event_date`: Expected event date
- `hazard_type`: 'flood' or 'conflict'
- `leadtime_days`: Lead time
- `forecasted_displacement`: Number of people (distribution)

### 2. Sensitivity Analysis

Excel files showing which parameters drive uncertainty:
- `param`: Parameter name (hazard, exposure, vulnerability)
- `S1`: First-order sensitivity index
- `S1_conf`: Confidence interval

### 3. Visualizations

- Spatial maps of displacement risk
- Uncertainty distributions
- Time series of forecast evolution
- Sensitivity tornado diagrams

---

## Key Adaptations from TC Framework

### 1. Impact Functions

**Original (TC Wind)**:
```python
# Emanuel USA function for wind damage
impf = ImpfTropCyclone.from_emanuel_usa(v_thresh=25.7, v_half=42.0)
```

**Adapted (Flood)**:
```python
# Sigmoid function for flood displacement
mdd = 1 / (1 + exp(-5 * (depth - depth_half) / depth_half))
```

**Adapted (Conflict)**:
```python
# Sigmoid function for conflict displacement
mdd = 1 / (1 + exp(-3 * (fatalities - fatal_half) / fatal_half))
```

### 2. Hazard Processing

**Original**: ECMWF BUFR tracks → wind field calculation

**Adapted**:
- **Floods**: Hydrological forecasts → flood depth grids
- **Conflict**: Event predictions → spatially decayed intensity fields

### 3. Exposure

**Original**: Population data with single vulnerability curve

**Adapted**: Population data with regional vulnerability curves accounting for:
- Socio-economic conditions
- Infrastructure quality
- Historical displacement patterns
- Access to early warning

### 4. Multi-Hazard Integration

**New feature**: Combine flood and conflict forecasts:
```python
# Maximum approach (worst case)
combined_intensity = np.maximum(flood_norm, conflict_norm)

# Or additive (compounding effects)
combined_intensity = 0.5 * flood_norm + 0.5 * conflict_norm
```

---

## Validation Metrics

Evaluate forecast performance using:

1. **Bias**: Mean(forecast) - Actual
2. **Relative Error**: (Forecast - Actual) / Actual × 100%
3. **Hit Rate**: P(Forecast > threshold | Event occurred)
4. **False Alarm Rate**: P(Forecast > threshold | No event)
5. **ROC AUC**: Area under receiver operating characteristic curve

---

## Example Workflow

### Scenario: 2-day Flood Forecast for Benue State

```python
from climada.entity import LitPop
from climada.hazard import Hazard
from scripts.nigeria_conflict_floods_2d_leadtime import *

# 1. Load flood forecast
haz_flood = load_flood_forecast_hydrological(
    'data/flood_forecast_20250115.nc',
    centroids_nigeria,
    datetime(2025, 1, 15)
)

# 2. Load population exposure for Benue
exp_benue = LitPop.from_countries('NGA', res_arcsec=300)
exp_benue = exp_benue.gdf[exp_benue.gdf['region_id'] == 'Benue']
exp_benue.assign_centroids(haz_flood)

# 3. Get vulnerability for North Central region
impf_list = get_regional_vulnerability_distribution('North_Central', 'flood')

# 4. Run forecast
unc_output = run_uncertainty_analysis(exp_iv, impf_iv, haz_iv, 1000)

# 5. Get results
forecast = unc_output.get_uncertainty()['aai_agg'].values
print(f"Expected displacement: {np.mean(forecast):,.0f} people")
print(f"95% confidence: {np.percentile(forecast, 2.5):,.0f} - {np.percentile(forecast, 97.5):,.0f}")
```

---

## Citation

If you use this code, please cite:

1. **Original TC Framework**:
   ```
   Kropf, C. M., Riedel, L., et al. (2024). Impact-based forecasting of tropical 
   cyclone-related human displacement to support anticipatory action. 
   Nature Communications, 15, 8795.
   ```

2. **CLIMADA**:
   ```
   Aznar-Siguan, G., & Bresch, D. N. (2019). CLIMADA v1: A global weather and 
   climate risk assessment platform. Geoscientific Model Development, 12(7), 
   3085-3097.
   ```

---

## Contact & Support

For questions or issues:
- Open an issue on GitHub
- Contact: [your contact info]

## License

This adaptation maintains the original license terms of the TC displacement forecasting framework.

---

## Acknowledgments

- Original TC framework developers
- CLIMADA development team
- IOM DTM for displacement data
- ACLED for conflict data
- GloFAS for flood forecasts
