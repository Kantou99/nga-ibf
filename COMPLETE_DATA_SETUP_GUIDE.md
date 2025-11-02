# 🌍 COMPLETE DATA SETUP GUIDE - Nigeria IBF System

**Your Step-by-Step Guide to Get ALL Required Data Files**

---

## 📋 Overview

You already have:
- ✅ WSL + Python setup
- ✅ CLIMADA 6.x installed
- ✅ Centroids file (`nigeria_centroids_1km.hdf5`) - 1.5M points ✅

You still need:
- ⬜ Admin boundaries (states/LGAs)
- ⬜ Population/exposure data
- ⬜ Historical displacement events
- ⬜ Forecast data (GloFAS/ACLED)

---

## 🎯 Required Files Summary

```
data/
├── nigeria_centroids_1km.hdf5              ✅ YOU HAVE THIS!
├── nigeria_admin_boundaries.geojson        ⬜ SECTION 1
├── nigeria_exposure.csv                    ⬜ SECTION 2
├── historical_displacement_events.xlsx     ⬜ SECTION 3
├── flood_forecast_YYYYMMDD.nc             ⬜ SECTION 4 (Optional)
└── conflict_forecast_YYYYMMDD.csv         ⬜ SECTION 5 (Optional)
```

**Estimated Time:** 30-60 minutes to get all files

---

## 📁 SECTION 1: Admin Boundaries (10 minutes)

### What You Need
Administrative boundaries for Nigeria (states and LGAs)

### Option A: GeoBoundaries API (Recommended) ✅

```bash
cd /mnt/c/Users/YMOUNKAR1/OneDrive\ -\ United\ Nations/Private\ files/Documents/Projects/nigeria-ibf

# Create download script
cat > download_boundaries.py << 'EOF'
#!/usr/bin/env python3
"""Download Nigeria administrative boundaries"""

import geopandas as gpd
import requests

print("Downloading Nigeria boundaries from GeoBoundaries...")

# Get state-level boundaries (ADM1)
url = "https://www.geoboundaries.org/api/current/gbOpen/NGA/ADM1/"
response = requests.get(url)
data = response.json()

# Download GeoJSON
geojson_url = data['gjDownloadURL']
print(f"Downloading from: {geojson_url}")

gdf = gpd.read_file(geojson_url)

# Clean and prepare
gdf = gdf.rename(columns={
    'shapeName': 'state_name',
    'shapeISO': 'iso_code',
    'shapeID': 'state_id'
})

# Add region classification
regions = {
    'North_West': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'],
    'North_East': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
    'North_Central': ['Benue', 'Kogi', 'Kwara', 'Nasarawa', 'Niger', 'Plateau', 'FCT'],
    'South_West': ['Ekiti', 'Lagos', 'Ogun', 'Ondo', 'Osun', 'Oyo'],
    'South_East': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
    'South_South': ['Akwa Ibom', 'Bayelsa', 'Cross River', 'Delta', 'Edo', 'Rivers']
}

gdf['region'] = 'Unknown'
for region, states in regions.items():
    for state in states:
        mask = gdf['state_name'].str.contains(state, case=False, na=False)
        gdf.loc[mask, 'region'] = region

# Save
output_file = 'data/nigeria_admin_boundaries.geojson'
gdf.to_file(output_file, driver='GeoJSON')

print(f"\n✅ SUCCESS!")
print(f"Downloaded {len(gdf)} states/territories")
print(f"Saved to: {output_file}")
print(f"\nRegional breakdown:")
print(gdf['region'].value_counts().to_string())

# Also save as shapefile (backup)
gdf.to_file('data/nigeria_admin_boundaries.shp')
print(f"\nAlso saved as: data/nigeria_admin_boundaries.shp")
EOF

# Create data directory
mkdir -p data

# Run the script
python download_boundaries.py
```

### Option B: Manual Download

1. Go to: https://www.geoboundaries.org/
2. Search for "Nigeria"
3. Download ADM1 (State level) in GeoJSON format
4. Save as `data/nigeria_admin_boundaries.geojson`

### Verify

```bash
# Check file exists
ls -lh data/nigeria_admin_boundaries.geojson

# Quick test
python << 'EOF'
import geopandas as gpd
gdf = gpd.read_file('data/nigeria_admin_boundaries.geojson')
print(f"✅ Loaded {len(gdf)} administrative units")
print(f"Columns: {', '.join(gdf.columns)}")
print(f"\nFirst few states:")
print(gdf[['state_name', 'region']].head(10).to_string())
EOF
```

**✅ Done!** You now have admin boundaries.

---

## 📊 SECTION 2: Population/Exposure Data (15 minutes)

### What You Need
Population exposure data for impact calculations

### Option A: Use CLIMADA LitPop (Recommended) ✅

```bash
# Create exposure generation script
cat > generate_exposure.py << 'EOF'
#!/usr/bin/env python3
"""Generate Nigeria exposure data using CLIMADA LitPop"""

from climada.entity import LitPop
import numpy as np

print("Generating Nigeria exposure using LitPop...")
print("This may take 5-10 minutes...")

# Generate exposure
# res_arcsec: 30 = ~1km, 150 = ~5km, 300 = ~10km
exposure = LitPop.from_countries(
    countries=['NGA'],
    res_arcsec=30,  # 1km resolution
    fin_mode='gdp'   # Financial mode: GDP-based
)

print(f"\n✅ Generated exposure for {len(exposure.gdf):,} points")

# Save to CSV
output_file = 'data/nigeria_exposure.csv'
exposure.gdf.to_csv(output_file, index=False)

print(f"Saved to: {output_file}")
print(f"File size: {len(exposure.gdf):,} rows")

# Summary statistics
print("\nExposure Summary:")
print(f"Total value: ${exposure.gdf['value'].sum():,.0f}")
print(f"Mean value per point: ${exposure.gdf['value'].mean():,.0f}")
print(f"Max value: ${exposure.gdf['value'].max():,.0f}")
print(f"Min value: ${exposure.gdf['value'].min():,.0f}")

print("\n✅ Exposure data ready!")
EOF

python generate_exposure.py
```

### Option B: Download WorldPop Data (Alternative)

```bash
# Create WorldPop download script
cat > download_worldpop.py << 'EOF'
#!/usr/bin/env python3
"""Download population data from WorldPop"""

import requests
from pathlib import Path

year = 2020
filename = f"nga_ppp_{year}_1km_Aggregated.tif"
url = f"https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/{year}/NGA/{filename}"

print(f"Downloading Nigeria population data for {year}...")
print(f"URL: {url}")
print("This may take 5-10 minutes (file is ~50 MB)...")

response = requests.get(url, stream=True)

if response.status_code == 200:
    output_file = f"data/{filename}"
    
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            f.write(chunk)
    
    print(f"\n✅ Downloaded: {output_file}")
    
    # Verify with rasterio
    try:
        import rasterio
        with rasterio.open(output_file) as src:
            print(f"Shape: {src.shape}")
            print(f"CRS: {src.crs}")
            data = src.read(1)
            print(f"Total population: {data.sum():,.0f}")
    except:
        print("Install rasterio to see file details: pip install rasterio")
else:
    print(f"❌ Download failed: HTTP {response.status_code}")
EOF

python download_worldpop.py
```

### Verify

```bash
# Check file
ls -lh data/nigeria_exposure.csv

# Quick test
python << 'EOF'
import pandas as pd
df = pd.read_csv('data/nigeria_exposure.csv')
print(f"✅ Loaded exposure data: {len(df):,} points")
print(f"Columns: {', '.join(df.columns)}")
print(f"\nSample data:")
print(df.head())
EOF
```

**✅ Done!** You now have exposure data.

---

## 📝 SECTION 3: Historical Displacement Events (20 minutes)

### What You Need
Historical data on flood and conflict-related displacement

### Option A: Create Template (If No Real Data Available)

```bash
# Create template events database
cat > create_events_template.py << 'EOF'
#!/usr/bin/env python3
"""Create historical events template"""

import pandas as pd
from datetime import datetime, timedelta

print("Creating historical events template...")

# Example events (replace with real data when available)
events = []

# Example flood events
flood_events = [
    {'date': '2020-09-15', 'state': 'Kogi', 'lga': 'Lokoja', 'type': 'flood',
     'affected_population': 45000, 'displaced': 32000, 'deaths': 12,
     'flood_depth_m': 2.5, 'duration_days': 12, 'source': 'NEMA'},
    
    {'date': '2021-08-22', 'state': 'Benue', 'lga': 'Makurdi', 'type': 'flood',
     'affected_population': 38000, 'displaced': 28000, 'deaths': 8,
     'flood_depth_m': 1.8, 'duration_days': 8, 'source': 'DTM'},
    
    {'date': '2022-10-10', 'state': 'Bayelsa', 'lga': 'Yenagoa', 'type': 'flood',
     'affected_population': 52000, 'displaced': 41000, 'deaths': 15,
     'flood_depth_m': 3.2, 'duration_days': 18, 'source': 'NEMA'},
    
    {'date': '2023-09-05', 'state': 'Adamawa', 'lga': 'Yola', 'type': 'flood',
     'affected_population': 29000, 'displaced': 21000, 'deaths': 6,
     'flood_depth_m': 1.5, 'duration_days': 7, 'source': 'NEMA'},
]

# Example conflict events
conflict_events = [
    {'date': '2021-06-10', 'state': 'Borno', 'lga': 'Maiduguri', 'type': 'conflict',
     'affected_population': 52000, 'displaced': 41000, 'deaths': 45,
     'flood_depth_m': None, 'duration_days': 5, 'source': 'ACLED'},
    
    {'date': '2022-03-20', 'state': 'Zamfara', 'lga': 'Gusau', 'type': 'conflict',
     'affected_population': 31000, 'displaced': 24000, 'deaths': 28,
     'flood_depth_m': None, 'duration_days': 3, 'source': 'ACLED'},
    
    {'date': '2023-01-15', 'state': 'Plateau', 'lga': 'Jos', 'type': 'conflict',
     'affected_population': 18000, 'displaced': 13000, 'deaths': 19,
     'flood_depth_m': None, 'duration_days': 2, 'source': 'ACLED'},
]

# Combine all events
events = flood_events + conflict_events

# Create DataFrame
df = pd.DataFrame(events)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Add calculated fields
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year
df['displacement_rate'] = (df['displaced'] / df['affected_population'] * 100).round(1)

# Save to Excel
output_file = 'data/historical_displacement_events.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Main events sheet
    df.to_excel(writer, sheet_name='Events', index=False)
    
    # Summary by type
    summary = df.groupby('type').agg({
        'affected_population': ['count', 'sum', 'mean'],
        'displaced': ['sum', 'mean'],
        'deaths': ['sum', 'mean']
    }).round(0)
    summary.to_excel(writer, sheet_name='Summary_by_Type')
    
    # Summary by state
    state_summary = df.groupby('state').agg({
        'affected_population': 'sum',
        'displaced': 'sum',
        'deaths': 'sum'
    }).round(0).sort_values('displaced', ascending=False)
    state_summary.to_excel(writer, sheet_name='Summary_by_State')

print(f"✅ Created template with {len(df)} events")
print(f"Saved to: {output_file}")
print(f"\nEvent breakdown:")
print(df['type'].value_counts().to_string())
print(f"\nTotal affected: {df['affected_population'].sum():,}")
print(f"Total displaced: {df['displaced'].sum():,}")
print(f"Total deaths: {df['deaths'].sum():,}")

print("\n⚠️  IMPORTANT: This is a TEMPLATE with example data!")
print("   Replace with real historical data from:")
print("   - DTM (Displacement Tracking Matrix)")
print("   - NEMA (National Emergency Management Agency)")
print("   - ACLED (Armed Conflict Location & Event Data)")
print("   - IOM displacement reports")
EOF

python create_events_template.py
```

### Option B: Real Data Sources

If you have access to real data, use these sources:

**For Flood Events:**
- NEMA reports: https://nema.gov.ng/
- DTM Nigeria: https://dtm.iom.int/nigeria
- OCHA humanitarian bulletins

**For Conflict Events:**
- ACLED: https://acleddata.com/ (requires free registration)
- UNOCHA situation reports
- DTM emergency tracking

### Verify

```bash
# Check file
ls -lh data/historical_displacement_events.xlsx

# Quick test
python << 'EOF'
import pandas as pd
df = pd.read_excel('data/historical_displacement_events.xlsx', sheet_name='Events')
print(f"✅ Loaded {len(df)} historical events")
print(f"\nEvent types:")
print(df['type'].value_counts().to_string())
print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
EOF
```

**✅ Done!** You now have historical events data.

---

## 🌊 SECTION 4: Flood Forecast Data (Optional)

### What You Need
GloFAS (Global Flood Awareness System) forecast data

### How to Get It

**Option A: GloFAS FTP (Requires Account)**

1. Register at: https://www.globalfloods.eu/
2. Get FTP credentials
3. Download forecast NetCDF files

**Option B: Manual Download**

```python
# Example script (requires credentials)
cat > download_glofas.py << 'EOF'
#!/usr/bin/env python3
"""Download GloFAS forecast data"""

import cdsapi
from datetime import datetime

# You need to register at: https://cds.climate.copernicus.eu/
# And set up your API key in ~/.cdsapirc

c = cdsapi.Client()

today = datetime.now().strftime('%Y%m%d')

c.retrieve(
    'cems-glofas-forecast',
    {
        'system_version': 'operational',
        'hydrological_model': 'lisflood',
        'product_type': 'control_forecast',
        'variable': 'river_discharge_in_the_last_24_hours',
        'hyear': '2024',
        'hmonth': '10',
        'hday': '19',
        'leadtime_hour': ['24', '48', '72'],
        'area': [14, 3, 4, 15],  # Nigeria bounding box
        'format': 'netcdf',
    },
    f'data/flood_forecast_{today}.nc'
)

print(f"✅ Downloaded GloFAS forecast: flood_forecast_{today}.nc")
EOF
```

**Option C: Use Sample Data (For Testing)**

For now, you can work without real forecast data and use historical data instead.

---

## ⚔️ SECTION 5: Conflict Forecast Data (Optional)

### What You Need
ACLED conflict event data

### How to Get It

**Option A: ACLED API (Free with Registration)**

1. Register at: https://acleddata.com/
2. Get API key
3. Download recent events

```python
cat > download_acled.py << 'EOF'
#!/usr/bin/env python3
"""Download ACLED conflict data"""

import requests
import pandas as pd
from datetime import datetime, timedelta

# Get your API key from: https://acleddata.com/
API_KEY = "YOUR_API_KEY_HERE"
EMAIL = "your.email@example.com"

# Get last 90 days of data for Nigeria
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

url = "https://api.acleddata.com/acled/read"
params = {
    'key': API_KEY,
    'email': EMAIL,
    'country': 'Nigeria',
    'event_date': f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}",
    'event_date_where': 'BETWEEN'
}

response = requests.get(url, params=params)
data = response.json()['data']

df = pd.DataFrame(data)
output_file = f'data/conflict_events_{datetime.now().strftime("%Y%m%d")}.csv'
df.to_csv(output_file, index=False)

print(f"✅ Downloaded {len(df)} conflict events")
print(f"Saved to: {output_file}")
EOF
```

**Note:** You need to register and get an API key from ACLED first.

---

## ✅ VERIFICATION CHECKLIST

Run this to check all your data files:

```bash
cd /mnt/c/Users/YMOUNKAR1/OneDrive\ -\ United\ Nations/Private\ files/Documents/Projects/nigeria-ibf

# Create verification script
cat > verify_data.py << 'EOF'
#!/usr/bin/env python3
"""Verify all required data files"""

from pathlib import Path
import sys

print("="*70)
print("NIGERIA IBF DATA VERIFICATION")
print("="*70)

required_files = {
    'data/nigeria_centroids_1km.hdf5': 'Centroids grid',
    'data/nigeria_admin_boundaries.geojson': 'Admin boundaries',
    'data/nigeria_exposure.csv': 'Population exposure',
    'data/historical_displacement_events.xlsx': 'Historical events',
}

optional_files = {
    'data/flood_forecast_*.nc': 'Flood forecasts (GloFAS)',
    'data/conflict_events_*.csv': 'Conflict data (ACLED)',
}

print("\n✓ REQUIRED FILES:")
all_required_present = True
for filepath, description in required_files.items():
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size / (1024*1024)
        print(f"  ✅ {description:30s} {filepath:50s} ({size:.1f} MB)")
    else:
        print(f"  ❌ {description:30s} {filepath:50s} MISSING")
        all_required_present = False

print("\n⭐ OPTIONAL FILES:")
for pattern, description in optional_files.items():
    files = list(Path('data').glob(pattern.replace('data/', '')))
    if files:
        print(f"  ✅ {description:30s} {len(files)} file(s) found")
    else:
        print(f"  ⚠️  {description:30s} Not present (optional)")

print("\n" + "="*70)
if all_required_present:
    print("✅ ALL REQUIRED FILES PRESENT - READY FOR FORECASTING!")
else:
    print("❌ SOME REQUIRED FILES MISSING - Follow guide to get them")
print("="*70)

sys.exit(0 if all_required_present else 1)
EOF

python verify_data.py
```

---

## 📦 COMPLETE SETUP SCRIPT (All-in-One)

If you want to run everything at once:

```bash
cat > setup_all_data.sh << 'BASH_EOF'
#!/bin/bash
set -e

echo "========================================="
echo "NIGERIA IBF COMPLETE DATA SETUP"
echo "========================================="

cd /mnt/c/Users/YMOUNKAR1/OneDrive\ -\ United\ Nations/Private\ files/Documents/Projects/nigeria-ibf

# Create directories
mkdir -p data logs outputs

echo ""
echo "1️⃣  Centroids..."
if [ -f "nigeria_centroids_1km.hdf5" ]; then
    cp nigeria_centroids_1km.hdf5 data/
    echo "✅ Centroids copied to data/"
else
    echo "⚠️  Generate centroids first: python generate_centroids.py"
fi

echo ""
echo "2️⃣  Downloading admin boundaries..."
python download_boundaries.py

echo ""
echo "3️⃣  Generating exposure data..."
python generate_exposure.py

echo ""
echo "4️⃣  Creating events template..."
python create_events_template.py

echo ""
echo "========================================="
echo "✅ DATA SETUP COMPLETE!"
echo "========================================="
echo ""
echo "Run verification:"
echo "python verify_data.py"
BASH_EOF

chmod +x setup_all_data.sh
./setup_all_data.sh
```

---

## 🎯 NEXT STEPS

After getting all data files:

1. **Verify everything:**
   ```bash
   python verify_data.py
   ```

2. **Download the other system files** (config.py, etc.)

3. **Run your first forecast!**

---

## 🆘 TROUBLESHOOTING

### Issue: "ModuleNotFoundError"
```bash
pip install geopandas requests openpyxl
```

### Issue: "Permission denied"
```bash
# Make sure you're in your virtual environment
source venv/bin/activate
# Or: conda activate nigeria-ibf
```

### Issue: "Can't download from GeoBoundaries"
Try the manual download option or use a VPN if network is restricted.

---

## 📞 DATA SOURCES QUICK REFERENCE

| Data Type | Source | URL |
|-----------|--------|-----|
| Admin Boundaries | GeoBoundaries | https://www.geoboundaries.org/ |
| Population | WorldPop | https://www.worldpop.org/ |
| Population | CLIMADA LitPop | Built-in |
| Flood Forecast | GloFAS | https://www.globalfloods.eu/ |
| Conflict Data | ACLED | https://acleddata.com/ |
| Displacement | DTM Nigeria | https://dtm.iom.int/nigeria |
| Emergency Data | NEMA | https://nema.gov.ng/ |

---

**🎉 You're now ready to get all the data you need!**

Start with Sections 1-3 (required), then add Sections 4-5 when available.
