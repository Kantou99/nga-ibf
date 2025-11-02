# Quick Start Guide: Nigeria IBF System

## 🚀 Get Started in 5 Steps

### Step 1: Install Dependencies (10 minutes)

```bash
# Create environment
conda create -n nigeria_ibf python=3.9
conda activate nigeria_ibf

# Install CLIMADA
pip install climada

# Install additional packages
pip install xarray netCDF4 pandas numpy scipy matplotlib geopandas openpyxl
```

### Step 2: Prepare Data (1-2 hours)

```bash
# Create centroids
python nigeria_data_preparation.py --create-centroids

# Expected output: data/nigeria_centroids_1km.hdf5
# Size: ~50 MB, ~1 million grid points
```

**Download Required Data:**

1. **Historical displacement events** → `data/2017_2024_Nigeria_displacement_events.xlsx`
   - Sources: IOM DTM, IDMC, NEMA
   - Format: See README_Nigeria_IBF.md section "Data Requirements"

2. **Flood forecasts** → `data/flood_forecast_YYYYMMDD.nc`
   - Source: GloFAS (glofas.copernicus.eu)
   - Or local hydrological model outputs

3. **Conflict predictions** → `data/conflict_forecast_YYYYMMDD.csv`
   - Source: ACLED + prediction model
   - Or use template: `python nigeria_data_preparation.py --forecast-template`

### Step 3: Process Hazards (30 minutes per forecast)

```bash
# Process hazards for a specific forecast date
python nigeria_hazard_processing.py \
    --run-datetime "2025-01-15T00:00:00" \
    --leadtime-days 2

# This creates:
# - hazards/nigeria_flood_2025-01-15T00:00:00_lead2d.hdf5
# - hazards/nigeria_conflict_2025-01-15T00:00:00_lead2d.hdf5
```

### Step 4: Run Forecast (15-30 minutes)

```bash
# Edit forecast date in the script, then run:
python nigeria_conflict_floods_2d_leadtime.py

# Outputs:
# - results/nigeria_flood_displacement_2025-01-15.xlsx
# - results/nigeria_conflict_displacement_2025-01-15.xlsx
# - results/nigeria_flood_sensitivity_2025-01-15.xlsx
# - results/nigeria_conflict_sensitivity_2025-01-15.xlsx
```

### Step 5: Interpret Results

**Displacement Forecast Output:**

```
Expected Displacement: 45,000 people
95% Confidence Interval: 28,000 - 75,000 people

Breakdown by uncertainty:
- Hazard intensity: 45%
- Vulnerability: 30%
- Exposure: 25%
```

**Decision Support:**

| Displacement Range | Recommended Action |
|-------------------|-------------------|
| < 10,000 | Monitor situation, alert local authorities |
| 10,000 - 50,000 | Prepare emergency supplies, activate early warning |
| 50,000 - 100,000 | Pre-position resources, evacuate high-risk areas |
| > 100,000 | Full emergency response, request international support |

---

## 📊 Example Workflow

### Scenario: Benue State Flood Forecast

**Situation:** Heavy rainfall forecast for Benue State, 2-day lead time

**Step-by-step:**

```python
# 1. Load required modules
from nigeria_conflict_floods_2d_leadtime import *

# 2. Set parameters
FORECAST_DATE = '2025-01-15'
EVENT_DATE = '2025-01-17'
LEADTIME_DAYS = 2

# 3. Run main forecast
main()

# 4. Read results
df_flood = pd.read_excel('results/nigeria_flood_displacement_2025-01-15.xlsx')

# 5. Summarize
print(f"Mean forecast: {df_flood['forecasted_displacement'].mean():,.0f} people")
print(f"95% CI: {df_flood['forecasted_displacement'].quantile(0.025):,.0f} - "
      f"{df_flood['forecasted_displacement'].quantile(0.975):,.0f} people")
```

**Expected Output:**

```
Processing flood forecast...
Loading centroids and exposure data...
Running flood displacement uncertainty analysis...

Forecast Summary:
  Mean forecasted displacement: 42,500 people
  Median: 41,200 people
  5th-95th percentile: 26,800 - 68,900 people

Key Sensitivity Factors:
  1. Flood intensity (ensemble spread): 45%
  2. Regional vulnerability: 30%
  3. Population exposure: 25%

Flood analysis complete.
Total execution time: 24.3 seconds
```

---

## 🔧 Troubleshooting

### Common Issues

**1. "Centroids file not found"**
```bash
# Solution: Create centroids first
python nigeria_data_preparation.py --create-centroids
```

**2. "No module named 'climada'"**
```bash
# Solution: Install CLIMADA
pip install climada
```

**3. "Flood forecast file not found"**
```bash
# Solution: Check file path and naming convention
# Expected: data/flood_forecast_20250115.nc
# Your file: [check actual filename]
```

**4. "Memory Error"**
```bash
# Solution: Reduce sample size
# In script, change: N_SAMPLE = 1000 → N_SAMPLE = 500
```

**5. "Results seem unrealistic"**
```bash
# Solution: Calibrate with historical events
python nigeria_historical_uncertainty_analysis.py 2020 flood 2d
# Review and adjust vulnerability parameters
```

---

## 📈 Validation Workflow

### Test with Historical Event

```bash
# 1. Select a known event from 2020
# Example: Kogi State flood, October 2020

# 2. Run retrospective forecast
python nigeria_historical_uncertainty_analysis.py 2020 flood 2d

# 3. Compare forecast vs. actual
# Forecast: 35,000 ± 15,000 people
# Actual: 32,000 people (from DTM)
# Error: +9% ✓ Good forecast

# 4. If error >50%, adjust regional vulnerability parameters
```

---

## 🎯 Next Steps

### For Operational Use:

1. **Set up automated data pipeline**
   - Daily GloFAS downloads
   - ACLED data updates
   - Automatic forecast generation

2. **Create forecast distribution system**
   - Email alerts to stakeholders
   - Web dashboard
   - Integration with NEMA systems

3. **Establish validation protocol**
   - Compare forecasts to actual events
   - Monthly performance reports
   - Continuous parameter refinement

### For Research:

1. **Improve conflict predictions**
   - Machine learning models
   - Sentiment analysis
   - Social media monitoring

2. **Refine vulnerability curves**
   - Household surveys
   - Agent-based modeling
   - Integration with poverty data

3. **Add more hazards**
   - Droughts
   - Disease outbreaks
   - Market shocks

---

## 📚 Key Files Reference

| File | Purpose | Runtime |
|------|---------|---------|
| `nigeria_data_preparation.py` | One-time setup | 1-2 hours |
| `nigeria_hazard_processing.py` | Per forecast | 30 min |
| `nigeria_conflict_floods_2d_leadtime.py` | Per forecast | 15-30 min |
| `nigeria_historical_uncertainty_analysis.py` | Validation | Hours-days |

---

## 💡 Pro Tips

1. **Start Simple:** Begin with just flood forecasts before adding conflict

2. **Validate First:** Run historical analysis before operational use

3. **Document Everything:** Keep log of parameter changes and rationale

4. **Engage Users:** Work with NEMA, SEMA, and humanitarian actors from start

5. **Iterate Rapidly:** Don't wait for perfect data, improve incrementally

---

## ✅ Checklist for First Forecast

- [ ] CLIMADA installed and working
- [ ] Nigeria centroids created
- [ ] Historical events database prepared
- [ ] Flood forecast data available
- [ ] Conflict forecast data available (or template)
- [ ] Hazard processing script tested
- [ ] Main forecast script runs without errors
- [ ] Results are in reasonable range (compare to past events)
- [ ] Stakeholders briefed on outputs

---

## 🆘 Getting Help

**Script Issues:**
- Check error messages carefully
- Review README_Nigeria_IBF.md
- Verify data formats match examples

**Methodology Questions:**
- Refer to ADAPTATION_SUMMARY.md
- Original paper: Kropf et al. (2024) Nature Communications

**CLIMADA Issues:**
- Documentation: climada-python.readthedocs.io
- GitHub: github.com/CLIMADA-project/climada_python

---

**Time to first forecast: ~4 hours** (assuming data available)

Good luck! 🚀
