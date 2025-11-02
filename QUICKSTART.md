# Quick Start Guide - Nigeria IBF System

## ?? Get Started in 5 Minutes

### Step 1: Setup Environment (2 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Add Your Data (1 minute)

Place these files in `data/raw/`:

? `nigeria_centroids_1km.hdf5`
? `exposure_nigeria_lga_aggregated.*`
? `dtm_displacement_data_cleaned.csv`
? `displacement_events_monthly.csv`
? `displacement_statistics_by_lga.csv`
? `nema_flood_data_cleaned.csv`
? `nema_flood_risk_by_lga.csv`

### Step 3: Run the System (2 minutes)

```bash
python main.py
```

### Step 4: View Results

Check `data/outputs/` for:
- ?? `forecast_bulletin.txt` - Main forecast report
- ?? `*.csv` - Impact data tables
- ??? `*.png` - Maps and visualizations

---

## ?? What You'll Get

### Forecast Bulletin
```
NIGERIA MULTI-HAZARD IMPACT-BASED FORECAST
Borno, Adamawa, and Yobe (BAY) States

TOP PRIORITY LGAs:
1. Maiduguri
   - People at risk: 45,000
   - Impact level: High
   - Hazards: Flood, Displacement

2. Yola North
   - People at risk: 32,000
   - Impact level: High
   ...
```

### Impact Data (CSV)
```
lga,people_at_risk,impact_level,priority_rank
Maiduguri,45000,High,1
Yola North,32000,High,2
...
```

### Visualizations
- Risk maps by LGA
- Impact dashboards
- Trend charts

---

## ?? Common Tasks

### Generate Monthly Forecast
```bash
python main.py
```

### Explore Data Interactively
```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

### Customize Settings
Edit `config/config.yaml`:
```yaml
hazards:
  flood:
    forecast_horizon_days: 30  # Change to 60 for 2-month forecast
```

### Process Single State
```python
# In main.py or your script
from src.data_processing.data_loader import DataLoader

loader = DataLoader()
data = loader.load_flood_events()

# Filter for Borno only
borno_data = data[data['state'] == 'Borno']
```

---

## ?? Key Outputs Explained

### 1. Forecast Bulletin
**Location**: `data/outputs/forecast_bulletin.txt`

Contains:
- Executive summary
- Top priority LGAs
- Recommended actions
- Hazard-specific forecasts

### 2. Impact Forecasts
**Location**: `data/outputs/impact_forecasts_*.csv`

Columns:
- `lga`: LGA name
- `people_at_risk`: Population estimate
- `impact_level`: Low/Medium/High/Severe
- `priority_rank`: 1 = highest priority
- `hazards`: Types of hazards

### 3. Risk Maps
**Location**: `data/outputs/*.png`

Shows:
- Flood risk by LGA (color-coded)
- Impact levels
- Displacement trends

---

## ?? VS Code Quick Setup

1. **Open Folder**: `File > Open Folder > nga-ibf`
2. **Select Python**: `Ctrl+Shift+P > Python: Select Interpreter > venv`
3. **Run**: Right-click `main.py` > Run Python File

---

## ?? Quick Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "File not found"
Check your files are in `data/raw/` with correct names

### "Memory error"
Edit `main.py`, line ~75:
```python
lga_list[:50]  # Add [:50] to process only 50 LGAs
```

---

## ?? Learn More

- **Full Documentation**: See `README.md`
- **Detailed Setup**: See `docs/SETUP_GUIDE.md`
- **Code Examples**: Browse `src/` modules

---

## ? Next Steps

1. ? Run `python main.py`
2. ? Review `data/outputs/forecast_bulletin.txt`
3. ? Open Jupyter notebook for analysis
4. ? Customize `config/config.yaml` for your needs

**Questions?** Check `README.md` or open an issue on GitHub.

---

**?? That's it! You're ready to generate forecasts for Nigeria BAY states!**
