# 📍 Complete Data Setup Guide for Nigeria IBF System

This guide shows you how to generate ALL required data files from scratch.

---

## 🎯 Required Files Overview

```
data/
├── nigeria_centroids_1km.hdf5        ⭐ THIS GUIDE
├── nigeria_admin_boundaries.geojson   ⭐ THIS GUIDE
├── nga_ppp_2020_1km_Aggregated.tif   ⭐ THIS GUIDE
├── 2017_2024_Nigeria_displacement_events.xlsx  ⭐ THIS GUIDE
├── flood_forecast_{date}.nc          (from GloFAS)
└── conflict_forecast_{date}.csv      (from ACLED)
```

---

## 1️⃣ Generate Nigeria Centroids (nigeria_centroids_1km.hdf5)

### Option A: Quick Method (30 seconds) ⚡ **RECOMMENDED FOR TESTING**

```bash
python generate_centroids.py --method bbox --resolution 1.0
```

**Output:** ~150,000 points covering Nigeria's bounding box

### Option B: Precise Method (2-3 minutes) 🎯 **RECOMMENDED FOR PRODUCTION**

```bash
python generate_centroids.py --method boundary --resolution 1.0
```

**Output:** ~120,000 points within Nigeria's exact boundaries

### Option C: Coarser Resolution (faster, for testing)

```bash
# 5 km resolution (much faster, ~5,000 points)
python generate_centroids.py --method bbox --resolution 5.0 --output nigeria_centroids_5km.hdf5

# 10 km resolution (very fast, ~1,200 points)
python generate_centroids.py --method bbox --resolution 10.0 --output nigeria_centroids_10km.hdf5
```

### Verify the File

```python
from climada.hazard import Centroids

# Load and inspect
centroids = Centroids.from_hdf5('nigeria_centroids_1km.hdf5')
print(f"Number of points: {len(centroids.lat):,}")
print(f"Latitude range: {centroids.lat.min():.2f}° to {centroids.lat.max():.2f}°")
print(f"Longitude range: {centroids.lon.min():.2f}° to {centroids.lon.max():.2f}°")

# Plot
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 8))
plt.scatter(centroids.lon, centroids.lat, s=0.1, alpha=0.5)
plt.title('Nigeria Centroids')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.savefig('centroids_map.png', dpi=150, bbox_inches='tight')
print("Map saved as centroids_map.png")
```

---

## 2️⃣ Generate Admin Boundaries (nigeria_admin_boundaries.geojson)

### Method 1: Using GeoBoundaries (Recommended)

```python
import geopandas as gpd
import requests
from pathlib import Path

def download_nigeria_boundaries():
    """Download Nigeria administrative boundaries"""
    
    # GeoBoundaries API - free, high quality
    # ADM0 = country level
    # ADM1 = state level (36 states + FCT)
    # ADM2 = LGA level (774 LGAs)
    
    print("Downloading Nigeria boundaries from GeoBoundaries...")
    
    # State level (ADM1)
    url = "https://www.geoboundaries.org/api/current/gbOpen/NGA/ADM1/"
    response = requests.get(url)
    data = response.json()
    
    # Download the actual geojson
    geojson_url = data['gjDownloadURL']
    gdf = gpd.read_file(geojson_url)
    
    # Clean column names
    gdf = gdf.rename(columns={
        'shapeName': 'state',
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
    
    # Add region column
    gdf['region'] = None
    for region, states in regions.items():
        for state in states:
            mask = gdf['state'].str.contains(state, case=False, na=False)
            gdf.loc[mask, 'region'] = region
    
    # Save
    output_file = 'nigeria_admin_boundaries.geojson'
    gdf.to_file(output_file, driver='GeoJSON')
    
    print(f"✅ Saved {len(gdf)} states to {output_file}")
    print(f"   Regions: {gdf['region'].value_counts().to_dict()}")
    
    return gdf

# Run it
boundaries = download_nigeria_boundaries()
```

### Method 2: Using Natural Earth (Alternative)

```python
import geopandas as gpd

# Download Nigeria from Natural Earth
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
nigeria = world[world.name == 'Nigeria']
nigeria.to_file('nigeria_country_boundary.geojson', driver='GeoJSON')
print("✅ Country boundary saved")
```

### Quick Script Version

Save this as `download_boundaries.py`:

```python
#!/usr/bin/env python3
import geopandas as gpd
import requests

url = "https://www.geoboundaries.org/api/current/gbOpen/NGA/ADM1/"
response = requests.get(url)
geojson_url = response.json()['gjDownloadURL']

gdf = gpd.read_file(geojson_url)
gdf.to_file('nigeria_admin_boundaries.geojson', driver='GeoJSON')
print(f"✅ Downloaded {len(gdf)} states")
```

Run with: `python download_boundaries.py`

---

## 3️⃣ Generate Population Data (nga_ppp_2020_1km_Aggregated.tif)

### Option A: Use CLIMADA's LitPop (Easiest)

```python
from climada.entity import LitPop

# Generate exposure for Nigeria
print("Generating exposure from LitPop...")
exposure = LitPop.from_countries(['NGA'], res_arcsec=30)  # 30 arcsec ≈ 1 km

# Save as CSV for inspection
exposure.gdf.to_csv('nigeria_population_exposure.csv', index=False)
print(f"✅ Generated exposure for {len(exposure.gdf):,} points")

# LitPop already provides population and asset values
# No need for separate population raster
```

### Option B: Download from WorldPop (Most Accurate)

```python
#!/usr/bin/env python3
"""
Download population data from WorldPop
"""
import requests
from pathlib import Path

def download_worldpop_nigeria(year=2020):
    """
    Download Nigeria population from WorldPop
    
    WorldPop provides free, high-resolution population data
    https://www.worldpop.org/
    """
    
    # WorldPop FTP URLs
    # Unconstrained population count (people per pixel)
    base_url = "https://data.worldpop.org/GIS/Population/Global_2000_2020_1km"
    filename = f"NGA_ppp_{year}_1km_Aggregated.tif"
    url = f"{base_url}/{year}/NGA/{filename}"
    
    print(f"Downloading {filename} from WorldPop...")
    print(f"URL: {url}")
    print("This may take a few minutes (file is ~50 MB)...")
    
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        output_file = f"nga_ppp_{year}_1km_Aggregated.tif"
        
        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024  # 1 MB
        
        with open(output_file, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(block_size):
                downloaded += len(data)
                f.write(data)
                if total_size:
                    progress = (downloaded / total_size) * 100
                    print(f"Progress: {progress:.1f}% ({downloaded/(1024*1024):.1f} MB)", end='\r')
        
        print(f"\n✅ Downloaded: {output_file}")
        
        # Verify
        import rasterio
        with rasterio.open(output_file) as src:
            print(f"   Shape: {src.shape}")
            print(f"   CRS: {src.crs}")
            print(f"   Bounds: {src.bounds}")
            data = src.read(1)
            print(f"   Total population: {data.sum():,.0f}")
        
        return output_file
    else:
        print(f"❌ Failed to download: HTTP {response.status_code}")
        return None

if __name__ == "__main__":
    download_worldpop_nigeria(2020)
```

Save as `download_population.py` and run: `python download_population.py`

### Option C: Use LitPop + Save as Raster (For Compatibility)

```python
from climada.entity import LitPop
import rasterio
from rasterio.transform import from_bounds
import numpy as np

# Generate LitPop
exposure = LitPop.from_countries(['NGA'], res_arcsec=30)

# Convert to raster
bounds = (exposure.gdf.longitude.min(), exposure.gdf.latitude.min(),
          exposure.gdf.longitude.max(), exposure.gdf.latitude.max())

# Create grid
resolution = 0.00833333  # 30 arcsec in degrees
width = int((bounds[2] - bounds[0]) / resolution)
height = int((bounds[3] - bounds[1]) / resolution)

# Create transform
transform = from_bounds(*bounds, width, height)

# Rasterize
from rasterio.features import rasterize
shapes = [(geom, value) for geom, value in zip(exposure.gdf.geometry, exposure.gdf.value)]
raster = rasterize(shapes, out_shape=(height, width), transform=transform, fill=0)

# Save
with rasterio.open(
    'nga_ppp_2020_1km_Aggregated.tif',
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype=raster.dtype,
    crs='EPSG:4326',
    transform=transform,
    compress='lzw'
) as dst:
    dst.write(raster, 1)

print("✅ Population raster created")
```

---

## 4️⃣ Create Historical Events Database

### Generate from DTM Reports (If Available)

```python
#!/usr/bin/env python3
"""
Parse DTM displacement reports and create events database
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

def create_events_database(dtm_files=None, acled_files=None):
    """
    Create historical events database
    
    If you don't have real data, this creates a template with example data
    """
    
    # Template structure
    events = []
    
    # Example flood events (replace with real data)
    flood_events = [
        {
            'date': '2020-09-15',
            'state': 'Kogi',
            'type': 'flood',
            'affected_population': 45000,
            'displaced': 32000,
            'flood_depth_m': 2.5,
            'duration_days': 12,
            'source': 'NEMA Report'
        },
        {
            'date': '2021-08-22',
            'state': 'Benue',
            'type': 'flood',
            'affected_population': 38000,
            'displaced': 28000,
            'flood_depth_m': 1.8,
            'duration_days': 8,
            'source': 'DTM Round 10'
        },
        # Add more events...
    ]
    
    # Example conflict events (replace with real data)
    conflict_events = [
        {
            'date': '2021-06-10',
            'state': 'Borno',
            'type': 'conflict',
            'affected_population': 52000,
            'displaced': 41000,
            'fatalities': 45,
            'duration_days': 5,
            'source': 'ACLED + DTM'
        },
        # Add more events...
    ]
    
    events = flood_events + conflict_events
    
    # Create DataFrame
    df = pd.DataFrame(events)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Save
    output_file = '2017_2024_Nigeria_displacement_events.xlsx'
    df.to_excel(output_file, index=False, sheet_name='Events')
    
    print(f"✅ Created events database: {output_file}")
    print(f"   Total events: {len(df)}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Event types: {df['type'].value_counts().to_dict()}")
    
    # Create summary sheet
    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
        summary = df.groupby(['type', 'state']).agg({
            'displaced': ['count', 'sum', 'mean'],
            'affected_population': 'sum'
        }).round(0)
        summary.to_excel(writer, sheet_name='Summary')
    
    return df

if __name__ == "__main__":
    events = create_events_database()
    
    # If you have real DTM files, you can parse them:
    # dtm_dir = Path('data/raw/dtm')
    # dtm_files = list(dtm_dir.glob('*.xlsx'))
    # events = create_events_database(dtm_files=dtm_files)
```

### Template Excel File

Create `2017_2024_Nigeria_displacement_events.xlsx` with these columns:

| date | state | type | affected_population | displaced | flood_depth_m | fatalities | duration_days | source |
|------|-------|------|-------------------|-----------|---------------|------------|---------------|---------|
| 2020-09-15 | Kogi | flood | 45000 | 32000 | 2.5 | - | 12 | NEMA |
| 2021-06-10 | Borno | conflict | 52000 | 41000 | - | 45 | 5 | ACLED+DTM |

---

## 5️⃣ Quick Setup Script (All-in-One)

Save this as `setup_data.py`:

```python
#!/usr/bin/env python3
"""
One-click data setup for Nigeria IBF System
Generates all required files
"""

import sys
from pathlib import Path

def setup_all_data():
    """Generate all required data files"""
    
    print("="*70)
    print("NIGERIA IBF DATA SETUP")
    print("="*70)
    
    # Create directories
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    print("\n1️⃣ Generating centroids...")
    try:
        from generate_centroids import generate_nigeria_centroids
        centroids = generate_nigeria_centroids(
            resolution_km=1.0,
            output_file='data/nigeria_centroids_1km.hdf5',
            method='bbox'  # Use fast method
        )
        print("   ✅ Centroids generated")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n2️⃣ Downloading admin boundaries...")
    try:
        import geopandas as gpd
        import requests
        
        url = "https://www.geoboundaries.org/api/current/gbOpen/NGA/ADM1/"
        response = requests.get(url)
        geojson_url = response.json()['gjDownloadURL']
        gdf = gpd.read_file(geojson_url)
        gdf.to_file('data/nigeria_admin_boundaries.geojson', driver='GeoJSON')
        print(f"   ✅ Downloaded {len(gdf)} states")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n3️⃣ Generating exposure data...")
    try:
        from climada.entity import LitPop
        exposure = LitPop.from_countries(['NGA'], res_arcsec=30)
        exposure.gdf.to_csv('data/nigeria_exposure.csv', index=False)
        print(f"   ✅ Generated exposure ({len(exposure.gdf):,} points)")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n4️⃣ Creating events database template...")
    try:
        import pandas as pd
        template = pd.DataFrame({
            'date': ['2020-09-15'],
            'state': ['Kogi'],
            'type': ['flood'],
            'affected_population': [45000],
            'displaced': [32000],
            'flood_depth_m': [2.5],
            'fatalities': [None],
            'duration_days': [12],
            'source': ['Template']
        })
        template.to_excel('data/2017_2024_Nigeria_displacement_events.xlsx', index=False)
        print("   ✅ Template created (replace with real data)")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n" + "="*70)
    print("DATA SETUP COMPLETE!")
    print("="*70)
    print("\nGenerated files:")
    for f in Path('data').glob('*'):
        size = f.stat().st_size / (1024*1024)
        print(f"  ✓ {f.name} ({size:.1f} MB)")
    
    print("\nNext steps:")
    print("1. Update config paths if needed")
    print("2. Replace template events with real historical data")
    print("3. Add forecast data (GloFAS, ACLED)")
    print("4. Run your first forecast!")

if __name__ == "__main__":
    setup_all_data()
```

Run with: `python setup_data.py`

---

## 6️⃣ Data Sources Reference

### Free Data Sources

| Data | Source | URL | Resolution |
|------|--------|-----|------------|
| **Admin Boundaries** | GeoBoundaries | https://www.geoboundaries.org/ | State/LGA level |
| **Population** | WorldPop | https://www.worldpop.org/ | 1 km |
| **Population** | LitPop (CLIMADA) | Built-in | 30 arcsec |
| **Elevation** | SRTM | https://earthexplorer.usgs.gov/ | 30 m |
| **Flood Forecasts** | GloFAS | https://www.globalfloods.eu/ | 0.1° (~11 km) |
| **Conflict Data** | ACLED | https://acleddata.com/ | Event-based |
| **Basemaps** | Natural Earth | https://www.naturalearthdata.com/ | Multiple |

---

## 7️⃣ Verification Checklist

```bash
# Check all files exist
ls -lh data/

# Should see:
# ✓ nigeria_centroids_1km.hdf5
# ✓ nigeria_admin_boundaries.geojson
# ✓ nga_ppp_2020_1km_Aggregated.tif (or use LitPop)
# ✓ 2017_2024_Nigeria_displacement_events.xlsx
```

```python
# Verify centroids
from climada.hazard import Centroids
centroids = Centroids.from_hdf5('data/nigeria_centroids_1km.hdf5')
print(f"✓ Centroids: {len(centroids.lat):,} points")

# Verify boundaries
import geopandas as gpd
boundaries = gpd.read_file('data/nigeria_admin_boundaries.geojson')
print(f"✓ Boundaries: {len(boundaries)} states")

# Verify exposure
from climada.entity import LitPop
exposure = LitPop.from_countries(['NGA'], res_arcsec=30)
print(f"✓ Exposure: {len(exposure.gdf):,} points")

# Verify events
import pandas as pd
events = pd.read_excel('data/2017_2024_Nigeria_displacement_events.xlsx')
print(f"✓ Events: {len(events)} records")

print("\n✅ ALL DATA FILES VERIFIED!")
```

---

## 🎉 You're Ready!

Once you have these files, you can run the IBF system:

```bash
python -m production_forecast_engine \
    --environment development \
    --forecast-date 2025-01-20 \
    --lead-time 2.0
```

---

## 🆘 Troubleshooting

**Problem:** "ModuleNotFoundError: No module named 'climada'"
```bash
pip install climada
```

**Problem:** "No such file or directory: nigeria_centroids_1km.hdf5"
```bash
python generate_centroids.py --method bbox
mv nigeria_centroids_1km.hdf5 data/
```

**Problem:** Centroids generation is too slow
```bash
# Use coarser resolution for testing
python generate_centroids.py --method bbox --resolution 5.0
```

**Problem:** Can't download WorldPop data
- Use CLIMADA's built-in LitPop instead
- It's already population-weighted and works well

---

**Need help?** Check the DEPLOYMENT_OPERATIONS.md for more details!
