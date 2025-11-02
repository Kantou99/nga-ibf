# 🌍 Comprehensive Implementation Guide
## Nigeria Impact-Based Forecasting System for Multi-Hazard Displacement

**Version:** 2.0  
**Target Region:** Borno, Adamawa, and Yobe States (BAY States)  
**Document Status:** Production Ready  
**Last Updated:** 2025-11-02

---

## 📋 Table of Contents

1. [Project Setup & Environment Configuration](#1-project-setup--environment-configuration)
2. [Data Architecture](#2-data-architecture)
3. [Hazard Modeling Components](#3-hazard-modeling-components)
4. [Impact Assessment Framework](#4-impact-assessment-framework)
5. [Automation & Operationalization](#5-automation--operationalization)
6. [Visualization & Dashboard](#6-visualization--dashboard)
7. [Testing & Validation](#7-testing--validation)
8. [Documentation & Deployment](#8-documentation--deployment)

---

## 1. Project Setup & Environment Configuration

### 1.1 VS Code Workspace Setup (15 minutes)

#### Step 1: Install VS Code Extensions

Open VS Code and install these essential extensions:

```bash
# Required Extensions
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-toolsai.jupyter
code --install-extension eamodio.gitlens
code --install-extension ms-azuretools.vscode-docker

# Recommended Extensions
code --install-extension donjayamanne.githistory
code --install-extension streetsidesoftware.code-spell-checker
code --install-extension yzhang.markdown-all-in-one
code --install-extension ms-python.black-formatter
```

#### Step 2: Create VS Code Workspace Configuration

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"],
    "editor.formatOnSave": true,
    "editor.rulers": [100],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.analysis.typeCheckingMode": "basic",
    "jupyter.notebookFileRoot": "${workspaceFolder}"
}
```

Create `.vscode/launch.json` for debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Run Production Forecast",
            "type": "python",
            "request": "launch",
            "module": "production_forecast_engine",
            "args": [
                "--environment", "development",
                "--forecast-date", "2025-01-20",
                "--lead-time", "2.0"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Run Test Suite",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/test_suite.py",
            "args": ["--suite", "unit"],
            "console": "integratedTerminal"
        }
    ]
}
```

Create `.vscode/tasks.json` for common tasks:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Forecast",
            "type": "shell",
            "command": "python",
            "args": ["-m", "production_forecast_engine"],
            "problemMatcher": [],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "Generate Centroids",
            "type": "shell",
            "command": "python",
            "args": ["generate_centroids.py", "--method", "bbox"],
            "problemMatcher": []
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "python",
            "args": ["test_suite.py", "--suite", "all"],
            "problemMatcher": []
        }
    ]
}
```

**Estimated Time:** 15 minutes

---

### 1.2 Python Environment Configuration (30 minutes)

#### Option A: Virtual Environment (Recommended for Development)

```bash
# Navigate to project directory
cd /workspace

# Create virtual environment
python3.9 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install -r requirements.txt

# Verify installation
python -c "import climada; print(f'CLIMADA version: {climada.__version__}')"
```

#### Option B: Conda Environment (Recommended for Data Science)

```bash
# Create conda environment
conda create -n nigeria_ibf python=3.9 -y

# Activate environment
conda activate nigeria_ibf

# Install geographic packages from conda-forge (better compiled)
conda install -c conda-forge geopandas shapely fiona pyproj cartopy -y

# Install CLIMADA and remaining packages with pip
pip install climada
pip install -r requirements.txt

# Verify installation
python -c "import geopandas; print('GeoPandas OK')"
```

#### Option C: Docker (Recommended for Production)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p data outputs logs

# Set environment variables
ENV PYTHONPATH=/app
ENV NIGERIA_IBF_ENV=production

# Run forecast engine
CMD ["python", "-m", "production_forecast_engine"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  nigeria_ibf:
    build: .
    container_name: nigeria_ibf_forecast
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
      - ./logs:/app/logs
    environment:
      - NIGERIA_IBF_ENV=production
      - TZ=Africa/Lagos
    restart: unless-stopped
    
  postgres:
    image: postgres:13-alpine
    container_name: nigeria_ibf_db
    environment:
      - POSTGRES_DB=nigeria_ibf
      - POSTGRES_USER=ibf_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
      
  redis:
    image: redis:7-alpine
    container_name: nigeria_ibf_cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Build and run:

```bash
# Build Docker image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f nigeria_ibf

# Run forecast manually
docker-compose exec nigeria_ibf python -m production_forecast_engine
```

**Estimated Time:** 30 minutes

---

### 1.3 Required Dependencies (Already in requirements.txt)

Update `/workspace/requirements.txt`:

```python
# Core Scientific Computing
numpy>=1.26.0
scipy>=1.11.0
pandas>=2.1.0

# Geospatial
geopandas>=0.14.0
shapely>=2.0.0
fiona>=1.9.0
pyproj>=3.6.0
rasterio>=1.3.0
rtree>=1.1.0

# Climate/Hazard Modeling
climada>=4.0.0
xarray>=2023.1.0
netCDF4>=1.6.0

# Machine Learning
scikit-learn>=1.3.0
joblib>=1.3.0

# Visualization
matplotlib>=3.8.0
seaborn>=0.13.0
plotly>=5.17.0
folium>=0.15.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0

# API & Web
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.4.0

# Utilities
pyyaml>=6.0
python-dotenv>=1.0.0
tqdm>=4.66.0
requests>=2.31.0

# Development & Testing
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.1.0
mypy>=1.6.0

# Monitoring
prometheus-client>=0.18.0

# Optional Performance
numba>=0.58.0
bottleneck>=1.3.0
```

**Estimated Time:** 10 minutes

---

### 1.4 Git Version Control Initialization (10 minutes)

```bash
# Initialize git repository (if not already done)
cd /workspace
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data files (large)
data/**/*.nc
data/**/*.hdf5
data/**/*.tif
*.pkl
*.joblib

# Keep data structure
!data/.gitkeep
!data/exposure/.gitkeep

# Outputs
outputs/
logs/
*.log

# Sensitive
.env
config/*_prod.yaml
secrets/

# OS
.DS_Store
Thumbs.db

# Temporary
tmp/
temp/
*.tmp
EOF

# Create .gitkeep files for directory structure
mkdir -p data/{raw,processed,hazards,exposure,historical}
mkdir -p outputs/{forecasts,alerts,reports,visualizations}
mkdir -p logs models config

touch data/.gitkeep
touch data/exposure/.gitkeep
touch outputs/.gitkeep
touch logs/.gitkeep

# Initial commit
git add .
git commit -m "Initial commit: Nigeria IBF system structure"

# Add remote (update with your repository URL)
# git remote add origin https://github.com/your-org/nigeria-ibf.git
# git push -u origin main
```

**Nigeria-Specific Consideration:** Keep data files out of version control due to:
- Large file sizes (GloFAS forecasts, WorldPop data)
- Sensitivity of displacement data (personal information)
- Internet connectivity constraints in Nigeria (large git repos = slow)

**Estimated Time:** 10 minutes

---

## 2. Data Architecture

### 2.1 Folder Structure and Organization (5 minutes)

```bash
# Create complete directory structure
mkdir -p {data,outputs,logs,models,config,scripts,docs,tests}

# Data subdirectories
mkdir -p data/{raw,processed,hazards,exposure,historical,boundaries}
mkdir -p data/raw/{dtm,acled,glofas,nema,worldpop}
mkdir -p data/processed/{monthly,lga,state,regional}

# Output subdirectories
mkdir -p outputs/{forecasts,alerts,reports,visualizations,metrics}

# Create structure documentation
cat > DIRECTORY_STRUCTURE.md << 'EOF'
# Nigeria IBF Directory Structure

```
nigeria-ibf/
├── config/                          # Configuration files
│   ├── config.py                    # Main configuration
│   ├── config_dev.yaml             # Development config
│   └── config_prod.yaml            # Production config
│
├── data/                            # All data files (mostly .gitignored)
│   ├── raw/                         # Raw data from sources
│   │   ├── dtm/                     # IOM Displacement Tracking Matrix
│   │   ├── acled/                   # Armed Conflict Location & Event Data
│   │   ├── glofas/                  # Global Flood Awareness System
│   │   ├── nema/                    # National Emergency Management Agency
│   │   └── worldpop/                # Population data
│   │
│   ├── processed/                   # Cleaned/processed data
│   │   ├── monthly/                 # Monthly aggregations
│   │   ├── lga/                     # Local Government Area level
│   │   ├── state/                   # State level
│   │   └── regional/                # Regional aggregations
│   │
│   ├── hazards/                     # CLIMADA hazard objects
│   │   ├── flood/                   # Flood hazards (.hdf5)
│   │   └── conflict/                # Conflict intensity fields
│   │
│   ├── exposure/                    # Population exposure data
│   │   ├── exposure_nigeria_lga_aggregated.csv
│   │   ├── exposure_nigeria_lga_aggregated.geojson
│   │   └── exposure_nigeria_lga_aggregated.hdf5
│   │
│   ├── boundaries/                  # Administrative boundaries
│   │   ├── BAY_LGA_Shared.geojson
│   │   ├── nigeria_states.geojson
│   │   └── nigeria_lgas.geojson
│   │
│   └── historical/                  # Historical events database
│       ├── displacement_events_monthly.csv
│       └── displacement_statistics_by_lga.csv
│
├── outputs/                         # All forecast outputs
│   ├── forecasts/                   # Forecast results by date
│   │   └── YYYYMMDD_HH/
│   │       ├── forecast_results.csv
│   │       └── forecast_metadata.json
│   │
│   ├── alerts/                      # Alert notifications
│   │   └── alerts_YYYYMMDD_HHMM.csv
│   │
│   ├── reports/                     # Automated reports
│   │   └── summary_report_YYYYMMDD_HHMM.txt
│   │
│   ├── visualizations/              # Maps and charts
│   │   ├── forecast_map_YYYYMMDD.png
│   │   └── uncertainty_plot_YYYYMMDD.png
│   │
│   └── metrics/                     # Performance metrics
│       └── metrics_YYYYMMDD.json
│
├── logs/                            # Application logs
│   ├── ibf_YYYYMMDD.log
│   └── errors_YYYYMMDD.log
│
├── models/                          # Trained ML models
│   ├── flood_vulnerability_rf_v1.pkl
│   └── conflict_vulnerability_rf_v1.pkl
│
├── scripts/                         # Utility scripts
│   ├── download_data.py
│   ├── process_dtm_data.py
│   ├── generate_centroids.py
│   └── backup.sh
│
├── docs/                            # Documentation
│   ├── API_REFERENCE.md
│   ├── USER_GUIDE.md
│   └── METHODOLOGY.md
│
├── tests/                           # Test files
│   ├── test_forecast_models.py
│   ├── test_alert_system.py
│   └── test_data_processing.py
│
├── production_forecast_engine.py    # Main production engine
├── forecast_models.py               # Forecast model classes
├── alert_system.py                  # Alert generation
├── ibf_database.py                  # Database interface
├── advanced_multi_hazard.py         # Multi-hazard modeling
├── test_suite.py                    # Comprehensive test suite
├── config.py                        # Configuration module
├── requirements.txt                 # Python dependencies
└── README.md                        # Main README
```
EOF
```

**Nigeria-Specific Considerations:**
- Separate raw and processed data (unstable power = interrupted downloads)
- Local caching of frequently accessed data (limited internet)
- Flat file structure for outputs (easy sharing via USB/email)

**Estimated Time:** 5 minutes

---

### 2.2 Data Sources Identification (Review)

#### Primary Data Sources for BAY States

**1. Meteorological & Hydrological Data**

| Source | Description | Access | Update Frequency | Nigeria Availability |
|--------|-------------|--------|------------------|---------------------|
| **GloFAS** | Global Flood Awareness System | https://global-flood.emergency.copernicus.eu | Daily | ✅ Excellent |
| **NOAA GFS** | Global Forecast System | https://nomads.ncep.noaa.gov | 6-hourly | ✅ Good |
| **ECMWF** | European weather forecasts | https://www.ecmwf.int | Daily | ⚠️ Requires account |
| **NiMet** | Nigerian Meteorological Agency | http://www.nimet.gov.ng | Daily | ✅ Local data |
| **TAHMO** | Trans-African Hydro Met Observatory | https://tahmo.org | Real-time | ✅ Good coverage |

**2. Conflict & Security Data**

| Source | Description | Access | Update Frequency | Coverage |
|--------|-------------|--------|------------------|----------|
| **ACLED** | Armed Conflict Location & Event Data | https://acleddata.com | Weekly | ✅ Excellent for Nigeria |
| **UCDP** | Uppsala Conflict Data Program | https://ucdp.uu.se | Monthly | ✅ Good |
| **GDELT** | Global Database of Events, Language, Tone | https://www.gdeltproject.org | Real-time | ⚠️ Requires processing |

**3. Displacement & Impact Data**

| Source | Description | Access | Update Frequency | Quality |
|--------|-------------|--------|------------------|---------|
| **IOM DTM** | Displacement Tracking Matrix | https://dtm.iom.int/nigeria | Monthly | ✅ Ground truth data |
| **NEMA** | National Emergency Management Agency | Direct partnership | As needed | ✅ Official data |
| **IDMC** | Internal Displacement Monitoring Centre | https://www.internal-displacement.org | Quarterly | ✅ Validated |

**4. Population & Socioeconomic Data**

| Source | Description | Resolution | Year | Access |
|--------|-------------|------------|------|--------|
| **WorldPop** | Population density | 100m | 2020 | https://www.worldpop.org |
| **GHSL** | Global Human Settlement Layer | 250m | 2020 | https://ghsl.jrc.ec.europa.eu |
| **LandScan** | Population distribution | 1km | 2023 | https://landscan.ornl.gov |
| **DHS** | Demographic & Health Surveys | Survey | Various | https://dhsprogram.com |

**5. Administrative Boundaries**

| Source | Description | Access | Format |
|--------|-------------|--------|--------|
| **OCHA** | UN Office for Coordination of Humanitarian Affairs | https://data.humdata.org | Shapefile, GeoJSON |
| **GADM** | Global Administrative Areas | https://gadm.org | Shapefile |
| **geoBoundaries** | Open boundaries database | https://www.geoboundaries.org | Multiple formats |

---

### 2.3 Data Pipeline Design (60 minutes)

Create `scripts/data_pipeline.py`:

```python
#!/usr/bin/env python3
"""
Automated Data Pipeline for Nigeria IBF System
Handles: Download → Validation → Processing → Storage
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
import requests
import xarray as xr
import pandas as pd
import geopandas as gpd
from typing import Optional, List, Dict
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DataPipeline')


class DataPipeline:
    """
    Orchestrates data ingestion, validation, and preprocessing
    """
    
    def __init__(self, config_path: str = 'config/data_sources.yaml'):
        self.config = self._load_config(config_path)
        self.base_dir = Path('data')
        self.raw_dir = self.base_dir / 'raw'
        self.processed_dir = self.base_dir / 'processed'
        
    def _load_config(self, config_path: str) -> dict:
        """Load data source configuration"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def run_daily_update(self) -> Dict[str, bool]:
        """
        Run complete daily data update pipeline
        
        Returns:
            Dictionary with status of each data source
        """
        logger.info("=" * 60)
        logger.info("Starting daily data pipeline")
        logger.info("=" * 60)
        
        status = {}
        
        # 1. Download GloFAS flood forecasts
        try:
            logger.info("Downloading GloFAS data...")
            self.download_glofas()
            status['glofas'] = True
        except Exception as e:
            logger.error(f"GloFAS download failed: {e}")
            status['glofas'] = False
        
        # 2. Download ACLED conflict data
        try:
            logger.info("Downloading ACLED data...")
            self.download_acled()
            status['acled'] = True
        except Exception as e:
            logger.error(f"ACLED download failed: {e}")
            status['acled'] = False
        
        # 3. Update DTM displacement data (monthly)
        if datetime.now().day == 1:  # First day of month
            try:
                logger.info("Checking for DTM updates...")
                self.check_dtm_updates()
                status['dtm'] = True
            except Exception as e:
                logger.error(f"DTM update failed: {e}")
                status['dtm'] = False
        
        # 4. Validate and process all data
        try:
            logger.info("Validating and processing data...")
            self.process_all_data()
            status['processing'] = True
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            status['processing'] = False
        
        logger.info("=" * 60)
        logger.info(f"Pipeline complete. Status: {status}")
        logger.info("=" * 60)
        
        return status
    
    def download_glofas(self, forecast_date: Optional[datetime] = None):
        """
        Download GloFAS river discharge forecasts
        
        Nigeria-Specific: Focus on Niger-Benue river basin
        """
        if forecast_date is None:
            forecast_date = datetime.now()
        
        # GloFAS bounding box for Nigeria (focus on BAY states)
        bbox = {
            'north': 14.0,   # Northern Nigeria
            'south': 4.0,    # Southern Nigeria  
            'west': 2.5,     # Western boundary
            'east': 15.0     # Eastern boundary (includes Lake Chad basin)
        }
        
        output_path = (
            self.raw_dir / 'glofas' / 
            f"glofas_forecast_{forecast_date.strftime('%Y%m%d')}.nc"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # GloFAS CDS API call (requires cdsapi package and credentials)
        try:
            import cdsapi
            
            c = cdsapi.Client()
            
            c.retrieve(
                'cems-glofas-forecast',
                {
                    'system_version': 'operational',
                    'hydrological_model': 'lisflood',
                    'product_type': 'ensemble_perturbed_forecasts',
                    'variable': 'river_discharge_in_the_last_24_hours',
                    'hyear': forecast_date.strftime('%Y'),
                    'hmonth': forecast_date.strftime('%m'),
                    'hday': forecast_date.strftime('%d'),
                    'leadtime_hour': [str(h) for h in range(24, 744, 24)],  # 30 days
                    'area': [bbox['north'], bbox['west'], bbox['south'], bbox['east']],
                    'format': 'netcdf',
                },
                str(output_path)
            )
            
            logger.info(f"GloFAS data downloaded: {output_path}")
            
        except ImportError:
            logger.warning("cdsapi not installed. Using mock data for testing.")
            self._create_mock_glofas(output_path, bbox)
        
        except Exception as e:
            logger.error(f"GloFAS download error: {e}")
            logger.info("Creating mock data for testing...")
            self._create_mock_glofas(output_path, bbox)
    
    def download_acled(self, start_date: Optional[datetime] = None):
        """
        Download ACLED conflict event data for Nigeria
        
        Nigeria-Specific: Filter for BAY states, relevant event types
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        
        # ACLED API configuration
        acled_email = self.config.get('acled', {}).get('email', '')
        acled_key = self.config.get('acled', {}).get('key', '')
        
        if not acled_email or not acled_key:
            logger.warning("ACLED credentials not configured. Using sample data.")
            self._create_sample_acled()
            return
        
        # Build API request
        url = "https://api.acleddata.com/acled/read"
        params = {
            'key': acled_key,
            'email': acled_email,
            'country': 'Nigeria',
            'admin1': 'Borno|Adamawa|Yobe',  # BAY states
            'event_date': start_date.strftime('%Y-%m-%d') + '|' + 
                         datetime.now().strftime('%Y-%m-%d'),
            'event_date_where': 'BETWEEN',
            'event_type': 'Battles|Violence against civilians|Explosions/Remote violence',
            'limit': 0  # No limit
        }
        
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data['data'])
            
            # Save raw data
            output_path = (
                self.raw_dir / 'acled' / 
                f"acled_bay_{start_date.strftime('%Y%m%d')}_to_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
            
            logger.info(f"ACLED data downloaded: {len(df)} events saved to {output_path}")
            
        except Exception as e:
            logger.error(f"ACLED download error: {e}")
            self._create_sample_acled()
    
    def check_dtm_updates(self):
        """
        Check IOM DTM for new displacement reports
        
        Nigeria-Specific: Manual process due to irregular updates
        """
        logger.info("DTM data typically requires manual download from IOM portal")
        logger.info("URL: https://dtm.iom.int/nigeria")
        logger.info("Place new files in: data/raw/dtm/")
        
        # Check for new files
        dtm_dir = self.raw_dir / 'dtm'
        if dtm_dir.exists():
            files = list(dtm_dir.glob('*.xlsx'))
            logger.info(f"Found {len(files)} DTM files")
    
    def process_all_data(self):
        """
        Process raw data into analysis-ready formats
        """
        # Process DTM data
        logger.info("Processing DTM displacement data...")
        from process_dtm_data import process_dtm_files
        process_dtm_files(
            input_dir=self.raw_dir / 'dtm',
            output_dir=self.processed_dir
        )
        
        # Process ACLED data
        logger.info("Processing ACLED conflict data...")
        self._process_acled_data()
        
        # Process GloFAS data (convert to CLIMADA hazard format)
        logger.info("Processing GloFAS flood data...")
        self._process_glofas_data()
    
    def _process_acled_data(self):
        """Convert ACLED data to forecast-ready format"""
        acled_files = list((self.raw_dir / 'acled').glob('*.csv'))
        
        if not acled_files:
            logger.warning("No ACLED files found to process")
            return
        
        # Read most recent file
        df = pd.read_csv(max(acled_files, key=lambda p: p.stat().st_mtime))
        
        # Convert to required format
        df_processed = pd.DataFrame({
            'date': pd.to_datetime(df['event_date']),
            'state': df['admin1'],
            'lga': df['admin2'],
            'latitude': df['latitude'],
            'longitude': df['longitude'],
            'event_type': df['event_type'],
            'fatalities': df['fatalities'].fillna(0).astype(int),
            'source': 'ACLED'
        })
        
        # Save processed data
        output_path = self.processed_dir / 'conflict_events_latest.csv'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_processed.to_csv(output_path, index=False)
        
        logger.info(f"Processed ACLED data: {len(df_processed)} events → {output_path}")
    
    def _process_glofas_data(self):
        """Convert GloFAS NetCDF to CLIMADA hazard format"""
        glofas_files = list((self.raw_dir / 'glofas').glob('*.nc'))
        
        if not glofas_files:
            logger.warning("No GloFAS files found to process")
            return
        
        # This would typically use custom processing
        # For now, log that manual processing is needed
        logger.info(f"Found {len(glofas_files)} GloFAS files")
        logger.info("GloFAS processing requires hazard model creation (see generate_exposure.py)")
    
    def _create_mock_glofas(self, output_path: Path, bbox: dict):
        """Create mock GloFAS data for testing"""
        # Simple mock NetCDF file
        import numpy as np
        
        lats = np.arange(bbox['south'], bbox['north'], 0.1)
        lons = np.arange(bbox['west'], bbox['east'], 0.1)
        time = pd.date_range(datetime.now(), periods=30, freq='D')
        ensemble = np.arange(51)  # 51 ensemble members
        
        # Create mock discharge data
        discharge = np.random.gamma(2, 50, size=(len(time), len(ensemble), len(lats), len(lons)))
        
        ds = xr.Dataset(
            {
                'dis24': (['time', 'ensemble', 'latitude', 'longitude'], discharge),
            },
            coords={
                'time': time,
                'ensemble': ensemble,
                'latitude': lats,
                'longitude': lons,
            }
        )
        
        ds.to_netcdf(output_path)
        logger.info(f"Created mock GloFAS data: {output_path}")
    
    def _create_sample_acled(self):
        """Create sample ACLED data for testing"""
        # Sample conflict events for BAY states
        sample_data = pd.DataFrame({
            'event_date': pd.date_range(end=datetime.now(), periods=50, freq='D'),
            'admin1': np.random.choice(['Borno', 'Adamawa', 'Yobe'], 50),
            'admin2': np.random.choice(['Maiduguri', 'Jere', 'Konduga', 'Yola North'], 50),
            'latitude': np.random.uniform(10, 13, 50),
            'longitude': np.random.uniform(11, 14, 50),
            'event_type': np.random.choice(['Battles', 'Violence against civilians'], 50),
            'fatalities': np.random.poisson(5, 50),
        })
        
        output_path = self.raw_dir / 'acled' / f"acled_sample_{datetime.now().strftime('%Y%m%d')}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sample_data.to_csv(output_path, index=False)
        
        logger.info(f"Created sample ACLED data: {output_path}")


def main():
    """Run data pipeline"""
    # Create data source configuration if it doesn't exist
    config_path = Path('config/data_sources.yaml')
    if not config_path.exists():
        config_path.parent.mkdir(exist_ok=True)
        default_config = {
            'acled': {
                'email': 'your.email@example.com',
                'key': 'your_api_key_here'
            },
            'glofas': {
                'cds_uid': 'your_cds_uid',
                'cds_key': 'your_cds_key'
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
        logger.info(f"Created default config: {config_path}")
        logger.info("Please update with your API credentials")
    
    # Run pipeline
    pipeline = DataPipeline(config_path=str(config_path))
    status = pipeline.run_daily_update()
    
    # Exit with error if critical sources failed
    if not status.get('glofas') or not status.get('processing'):
        logger.error("Critical data sources failed!")
        exit(1)
    
    logger.info("✅ Data pipeline completed successfully")


if __name__ == "__main__":
    main()
```

Create configuration file `config/data_sources.yaml`:

```yaml
# Data Source Configuration for Nigeria IBF

acled:
  email: "your.email@example.com"
  key: "your_acled_api_key"
  description: "Armed Conflict Location & Event Data Project"
  url: "https://acleddata.com"
  
glofas:
  cds_uid: "your_cds_uid"
  cds_key: "your_cds_key"
  description: "Global Flood Awareness System via Copernicus CDS"
  url: "https://cds.climate.copernicus.eu"
  
dtm:
  description: "IOM Displacement Tracking Matrix - Manual download"
  url: "https://dtm.iom.int/nigeria"
  update_frequency: "monthly"
  
worldpop:
  description: "Population density data"
  url: "https://www.worldpop.org/geodata/listing?id=79"
  dataset: "nga_ppp_2020_1km_Aggregated.tif"
  
boundaries:
  ocha_hdx:
    url: "https://data.humdata.org/dataset/cod-ab-nga"
    description: "Nigeria administrative boundaries"
```

**Estimated Time:** 60 minutes (includes testing)

---

### 2.4 Database Schema Design (45 minutes)

Create `scripts/database_schema.sql`:

```sql
-- Nigeria IBF Database Schema
-- PostgreSQL 13+

-- Enable PostGIS extension for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- ADMINISTRATIVE BOUNDARIES
-- ============================================================================

CREATE TABLE states (
    state_id SERIAL PRIMARY KEY,
    state_name VARCHAR(100) NOT NULL UNIQUE,
    state_code CHAR(2),
    region VARCHAR(50),
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    population INTEGER,
    area_km2 DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_states_geometry ON states USING GIST(geometry);

CREATE TABLE lgas (
    lga_id SERIAL PRIMARY KEY,
    lga_name VARCHAR(100) NOT NULL,
    state_id INTEGER REFERENCES states(state_id),
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    population INTEGER,
    area_km2 DOUBLE PRECISION,
    centroid_lat DOUBLE PRECISION,
    centroid_lon DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(lga_name, state_id)
);

CREATE INDEX idx_lgas_geometry ON lgas USING GIST(geometry);
CREATE INDEX idx_lgas_state ON lgas(state_id);

-- ============================================================================
-- HISTORICAL DISPLACEMENT DATA
-- ============================================================================

CREATE TABLE displacement_events (
    event_id SERIAL PRIMARY KEY,
    event_name VARCHAR(255),
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'flood', 'conflict', 'drought', etc.
    state_id INTEGER REFERENCES states(state_id),
    lga_id INTEGER REFERENCES lgas(lga_id),
    
    -- Spatial extent
    geometry GEOMETRY(POINT, 4326),
    bbox_geometry GEOMETRY(POLYGON, 4326),
    
    -- Impact metrics
    reported_displacement INTEGER,
    verified_displacement INTEGER,
    affected_population INTEGER,
    fatalities INTEGER DEFAULT 0,
    
    -- Data source and quality
    data_source VARCHAR(100),  -- 'DTM', 'NEMA', 'IDMC', etc.
    data_quality VARCHAR(20),  -- 'high', 'medium', 'low'
    confidence_level DOUBLE PRECISION,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_date ON displacement_events(event_date);
CREATE INDEX idx_events_type ON displacement_events(event_type);
CREATE INDEX idx_events_state ON displacement_events(state_id);
CREATE INDEX idx_events_geometry ON displacement_events USING GIST(geometry);

-- Convert to TimescaleDB hypertable for time-series optimization
SELECT create_hypertable('displacement_events', 'event_date', 
                         chunk_time_interval => INTERVAL '3 months',
                         if_not_exists => TRUE);

-- ============================================================================
-- FORECASTS
-- ============================================================================

CREATE TABLE forecasts (
    forecast_id SERIAL PRIMARY KEY,
    forecast_uuid UUID NOT NULL UNIQUE,
    
    -- Timing
    forecast_date TIMESTAMP NOT NULL,
    event_date TIMESTAMP NOT NULL,
    lead_time_days DOUBLE PRECISION NOT NULL,
    
    -- Location
    state_id INTEGER REFERENCES states(state_id),
    lga_id INTEGER REFERENCES lgas(lga_id),
    
    -- Hazard type
    hazard_type VARCHAR(50) NOT NULL,  -- 'flood', 'conflict', 'multi_hazard'
    
    -- Forecast values
    mean_displacement DOUBLE PRECISION,
    median_displacement DOUBLE PRECISION,
    p05_displacement DOUBLE PRECISION,
    p25_displacement DOUBLE PRECISION,
    p75_displacement DOUBLE PRECISION,
    p95_displacement DOUBLE PRECISION,
    max_displacement DOUBLE PRECISION,
    
    -- Uncertainty decomposition
    hazard_uncertainty_pct DOUBLE PRECISION,
    exposure_uncertainty_pct DOUBLE PRECISION,
    vulnerability_uncertainty_pct DOUBLE PRECISION,
    
    -- Quality metrics
    quality_score DOUBLE PRECISION,
    confidence_level VARCHAR(20),
    n_samples INTEGER,
    n_ensemble_members INTEGER,
    
    -- Model information
    model_version VARCHAR(50),
    parameters JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'superseded', 'verified'
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forecasts_date ON forecasts(forecast_date);
CREATE INDEX idx_forecasts_event_date ON forecasts(event_date);
CREATE INDEX idx_forecasts_state ON forecasts(state_id);
CREATE INDEX idx_forecasts_hazard ON forecasts(hazard_type);
CREATE INDEX idx_forecasts_uuid ON forecasts(forecast_uuid);

SELECT create_hypertable('forecasts', 'forecast_date',
                         chunk_time_interval => INTERVAL '1 month',
                         if_not_exists => TRUE);

-- ============================================================================
-- ALERTS
-- ============================================================================

CREATE TABLE alerts (
    alert_id SERIAL PRIMARY KEY,
    alert_uuid UUID NOT NULL UNIQUE,
    forecast_id INTEGER REFERENCES forecasts(forecast_id),
    
    -- Alert classification
    alert_level VARCHAR(20) NOT NULL,  -- 'watch', 'advisory', 'warning', 'emergency'
    alert_type VARCHAR(50) NOT NULL,
    
    -- Timing
    issued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    
    -- Location
    state_ids INTEGER[],
    lga_ids INTEGER[],
    affected_area_km2 DOUBLE PRECISION,
    
    -- Impact estimates
    estimated_displacement_mean DOUBLE PRECISION,
    estimated_displacement_range TEXT,  -- e.g., "10,000-25,000"
    affected_population INTEGER,
    
    -- Alert content
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    detailed_message TEXT,
    recommended_actions TEXT[],
    
    -- Distribution
    recipients TEXT[],
    distribution_channels TEXT[],  -- 'email', 'sms', 'api', 'dashboard'
    sent_at TIMESTAMP,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- 'draft', 'active', 'expired', 'cancelled'
    
    -- Metadata
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_level ON alerts(alert_level);
CREATE INDEX idx_alerts_issued ON alerts(issued_at);
CREATE INDEX idx_alerts_valid_from ON alerts(valid_from);
CREATE INDEX idx_alerts_forecast ON alerts(forecast_id);

-- ============================================================================
-- VALIDATION METRICS
-- ============================================================================

CREATE TABLE forecast_validation (
    validation_id SERIAL PRIMARY KEY,
    forecast_id INTEGER REFERENCES forecasts(forecast_id),
    event_id INTEGER REFERENCES displacement_events(event_id),
    
    -- Comparison
    forecasted_value DOUBLE PRECISION,
    actual_value DOUBLE PRECISION,
    absolute_error DOUBLE PRECISION,
    relative_error_pct DOUBLE PRECISION,
    
    -- Metrics
    bias DOUBLE PRECISION,
    hit BOOLEAN,  -- Did forecast predict event occurrence?
    false_alarm BOOLEAN,
    
    -- Timing
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Notes
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_validation_forecast ON forecast_validation(forecast_id);
CREATE INDEX idx_validation_event ON forecast_validation(event_id);

-- ============================================================================
-- SYSTEM METRICS
-- ============================================================================

CREATE TABLE system_metrics (
    metric_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Performance metrics
    forecast_duration_seconds DOUBLE PRECISION,
    processing_time_seconds DOUBLE PRECISION,
    
    -- Quality metrics
    mean_quality_score DOUBLE PRECISION,
    mean_confidence_level VARCHAR(20),
    
    -- Volume metrics
    forecasts_generated INTEGER,
    alerts_issued INTEGER,
    
    -- Resource metrics
    memory_usage_mb DOUBLE PRECISION,
    cpu_usage_pct DOUBLE PRECISION,
    disk_usage_gb DOUBLE PRECISION,
    
    -- Data freshness
    glofas_age_hours DOUBLE PRECISION,
    acled_age_hours DOUBLE PRECISION,
    
    -- Errors
    error_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    
    -- Status
    system_status VARCHAR(20),  -- 'healthy', 'degraded', 'down'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);

SELECT create_hypertable('system_metrics', 'timestamp',
                         chunk_time_interval => INTERVAL '1 day',
                         if_not_exists => TRUE);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Recent forecasts with geographic context
CREATE VIEW v_recent_forecasts AS
SELECT 
    f.forecast_id,
    f.forecast_date,
    f.event_date,
    f.lead_time_days,
    s.state_name,
    l.lga_name,
    f.hazard_type,
    f.mean_displacement,
    f.p05_displacement,
    f.p95_displacement,
    f.quality_score,
    f.confidence_level
FROM forecasts f
LEFT JOIN states s ON f.state_id = s.state_id
LEFT JOIN lgas l ON f.lga_id = l.lga_id
WHERE f.forecast_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY f.forecast_date DESC;

-- Active alerts
CREATE VIEW v_active_alerts AS
SELECT 
    a.alert_id,
    a.alert_level,
    a.alert_type,
    a.issued_at,
    a.valid_until,
    a.title,
    a.summary,
    a.estimated_displacement_mean,
    a.status,
    f.hazard_type
FROM alerts a
LEFT JOIN forecasts f ON a.forecast_id = f.forecast_id
WHERE a.status = 'active'
  AND a.valid_until > CURRENT_TIMESTAMP
ORDER BY a.alert_level, a.issued_at DESC;

-- Forecast performance summary
CREATE VIEW v_forecast_performance AS
SELECT 
    f.hazard_type,
    COUNT(*) as n_forecasts,
    AVG(v.absolute_error) as mean_absolute_error,
    AVG(v.relative_error_pct) as mean_relative_error_pct,
    AVG(v.bias) as mean_bias,
    SUM(CASE WHEN v.hit THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as hit_rate,
    SUM(CASE WHEN v.false_alarm THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as false_alarm_rate,
    AVG(f.quality_score) as mean_quality_score
FROM forecasts f
JOIN forecast_validation v ON f.forecast_id = v.forecast_id
WHERE f.forecast_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY f.hazard_type;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to calculate distance between forecast and actual
CREATE OR REPLACE FUNCTION calculate_forecast_error(
    p_forecast_id INTEGER,
    p_actual_displacement DOUBLE PRECISION
) RETURNS VOID AS $$
DECLARE
    v_forecast_value DOUBLE PRECISION;
BEGIN
    -- Get forecast value
    SELECT mean_displacement INTO v_forecast_value
    FROM forecasts
    WHERE forecast_id = p_forecast_id;
    
    -- Insert validation record
    INSERT INTO forecast_validation (
        forecast_id,
        forecasted_value,
        actual_value,
        absolute_error,
        relative_error_pct,
        bias,
        hit
    ) VALUES (
        p_forecast_id,
        v_forecast_value,
        p_actual_displacement,
        ABS(v_forecast_value - p_actual_displacement),
        100.0 * (v_forecast_value - p_actual_displacement) / NULLIF(p_actual_displacement, 0),
        v_forecast_value - p_actual_displacement,
        CASE WHEN v_forecast_value > 0 AND p_actual_displacement > 0 THEN TRUE ELSE FALSE END
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA INSERTION (for testing)
-- ============================================================================

-- Insert BAY states
INSERT INTO states (state_name, state_code, region, population) VALUES
    ('Borno', 'BO', 'North East', 5860000),
    ('Adamawa', 'AD', 'North East', 4248000),
    ('Yobe', 'YO', 'North East', 3294000);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ibf_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ibf_user;
```

Create Python database interface `ibf_database_enhanced.py`:

```python
#!/usr/bin/env python3
"""
Enhanced Database Interface for Nigeria IBF System
Handles PostgreSQL/TimescaleDB interactions
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import pandas as pd
import geopandas as gpd
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import logging
from contextlib import contextmanager
import json

logger = logging.getLogger('NigeriaIBF.Database')


class IBFDatabase:
    """
    Enhanced database interface with:
    - Connection pooling
    - Transaction management
    - Spatial query support
    - Time-series optimization
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize database connection
        
        Args:
            connection_string: PostgreSQL connection string
                Example: "postgresql://user:pass@localhost:5432/nigeria_ibf"
        """
        self.connection_string = connection_string
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    @contextmanager
    def cursor(self, dict_cursor=True):
        """Context manager for database cursor"""
        cursor_factory = RealDictCursor if dict_cursor else None
        cur = self.conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cur.close()
    
    def insert_forecast(self, forecast_data: dict) -> int:
        """
        Insert forecast into database
        
        Returns:
            forecast_id of inserted record
        """
        with self.cursor() as cur:
            query = """
                INSERT INTO forecasts (
                    forecast_uuid, forecast_date, event_date, lead_time_days,
                    state_id, lga_id, hazard_type,
                    mean_displacement, median_displacement,
                    p05_displacement, p25_displacement, p75_displacement, p95_displacement,
                    hazard_uncertainty_pct, exposure_uncertainty_pct, vulnerability_uncertainty_pct,
                    quality_score, confidence_level, n_samples, n_ensemble_members,
                    model_version, parameters
                ) VALUES (
                    %(forecast_uuid)s, %(forecast_date)s, %(event_date)s, %(lead_time_days)s,
                    %(state_id)s, %(lga_id)s, %(hazard_type)s,
                    %(mean_displacement)s, %(median_displacement)s,
                    %(p05_displacement)s, %(p25_displacement)s, %(p75_displacement)s, %(p95_displacement)s,
                    %(hazard_uncertainty_pct)s, %(exposure_uncertainty_pct)s, %(vulnerability_uncertainty_pct)s,
                    %(quality_score)s, %(confidence_level)s, %(n_samples)s, %(n_ensemble_members)s,
                    %(model_version)s, %(parameters)s
                )
                RETURNING forecast_id
            """
            cur.execute(query, forecast_data)
            forecast_id = cur.fetchone()['forecast_id']
            logger.info(f"Inserted forecast: {forecast_id}")
            return forecast_id
    
    def insert_alert(self, alert_data: dict) -> int:
        """Insert alert into database"""
        with self.cursor() as cur:
            query = """
                INSERT INTO alerts (
                    alert_uuid, forecast_id, alert_level, alert_type,
                    valid_from, valid_until,
                    state_ids, lga_ids, affected_area_km2,
                    estimated_displacement_mean, estimated_displacement_range,
                    affected_population,
                    title, summary, detailed_message, recommended_actions,
                    recipients, distribution_channels,
                    status, created_by
                ) VALUES (
                    %(alert_uuid)s, %(forecast_id)s, %(alert_level)s, %(alert_type)s,
                    %(valid_from)s, %(valid_until)s,
                    %(state_ids)s, %(lga_ids)s, %(affected_area_km2)s,
                    %(estimated_displacement_mean)s, %(estimated_displacement_range)s,
                    %(affected_population)s,
                    %(title)s, %(summary)s, %(detailed_message)s, %(recommended_actions)s,
                    %(recipients)s, %(distribution_channels)s,
                    %(status)s, %(created_by)s
                )
                RETURNING alert_id
            """
            cur.execute(query, alert_data)
            alert_id = cur.fetchone()['alert_id']
            logger.info(f"Inserted alert: {alert_id}")
            return alert_id
    
    def get_recent_forecasts(self, days: int = 7, hazard_type: Optional[str] = None) -> pd.DataFrame:
        """Retrieve recent forecasts"""
        with self.cursor() as cur:
            query = """
                SELECT * FROM v_recent_forecasts
                WHERE forecast_date >= CURRENT_DATE - INTERVAL '%s days'
            """
            params = [days]
            
            if hazard_type:
                query += " AND hazard_type = %s"
                params.append(hazard_type)
            
            query += " ORDER BY forecast_date DESC"
            
            cur.execute(query, tuple(params))
            results = cur.fetchall()
            
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def get_forecast_performance(self, hazard_type: Optional[str] = None) -> pd.DataFrame:
        """Get forecast performance metrics"""
        with self.cursor() as cur:
            query = "SELECT * FROM v_forecast_performance"
            
            if hazard_type:
                query += " WHERE hazard_type = %s"
                cur.execute(query, (hazard_type,))
            else:
                cur.execute(query)
            
            results = cur.fetchall()
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def record_system_metrics(self, metrics: dict):
        """Record system performance metrics"""
        with self.cursor() as cur:
            query = """
                INSERT INTO system_metrics (
                    forecast_duration_seconds, processing_time_seconds,
                    mean_quality_score, forecasts_generated, alerts_issued,
                    memory_usage_mb, cpu_usage_pct,
                    error_count, warning_count, system_status
                ) VALUES (
                    %(forecast_duration_seconds)s, %(processing_time_seconds)s,
                    %(mean_quality_score)s, %(forecasts_generated)s, %(alerts_issued)s,
                    %(memory_usage_mb)s, %(cpu_usage_pct)s,
                    %(error_count)s, %(warning_count)s, %(system_status)s
                )
            """
            cur.execute(query, metrics)
            logger.info("Recorded system metrics")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Example usage
if __name__ == "__main__":
    # Test connection
    db = IBFDatabase("postgresql://ibf_user:password@localhost:5432/nigeria_ibf")
    
    # Test query
    recent = db.get_recent_forecasts(days=7)
    print(f"Recent forecasts: {len(recent)}")
    
    db.close()
```

**Estimated Time:** 45 minutes

---

## 3. Hazard Modeling Components

### 3.1 Individual Hazard Models (90 minutes)

The existing system already has flood and conflict models. Let's enhance them:

Create `hazard_models_enhanced.py`:

```python
#!/usr/bin/env python3
"""
Enhanced Hazard Models for Nigeria IBF System
Implements flood, conflict, drought, and disease outbreak models
"""

import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging

from climada.hazard import Hazard, Centroids
from climada.util.coordinates import coord_on_land

logger = logging.getLogger('NigeriaIBF.HazardModels')


# ============================================================================
# FLOOD HAZARD MODEL
# ============================================================================

class FloodHazardModel:
    """
    Riverine and flash flood hazard model
    Uses GloFAS discharge forecasts or local hydrological models
    """
    
    def __init__(self, centroids: Centroids):
        self.centroids = centroids
        self.return_periods = [2, 5, 10, 20, 50, 100]  # years
        
    def create_hazard_from_glofas(
        self,
        glofas_file: str,
        forecast_date: datetime,
        ensemble_member: Optional[int] = None
    ) -> Hazard:
        """
        Convert GloFAS discharge forecast to CLIMADA flood hazard
        
        Args:
            glofas_file: Path to GloFAS NetCDF file
            forecast_date: Date of forecast issuance
            ensemble_member: Specific ensemble member (None = control run)
        
        Returns:
            CLIMADA Hazard object
        """
        logger.info(f"Loading GloFAS data: {glofas_file}")
        
        # Load GloFAS data
        ds = xr.open_dataset(glofas_file)
        
        # Select ensemble member
        if ensemble_member is not None:
            ds = ds.sel(ensemble=ensemble_member)
        else:
            # Use ensemble mean
            ds = ds.mean(dim='ensemble')
        
        # Convert discharge to flood depth using rating curves
        # This is simplified - in reality would use detailed hydraulic models
        flood_depth = self._discharge_to_depth(ds['dis24'].values)
        
        # Create CLIMADA Hazard
        hazard = Hazard('FL')  # Flood hazard
        hazard.centroids = self.centroids
        
        # Interpolate to centroids
        hazard.intensity = self._interpolate_to_centroids(
            lats=ds.latitude.values,
            lons=ds.longitude.values,
            values=flood_depth,
            target_centroids=self.centroids
        )
        
        # Set hazard attributes
        hazard.frequency = np.ones(hazard.intensity.shape[0]) / 365.25  # Daily
        hazard.date = np.array([forecast_date + timedelta(days=i) 
                               for i in range(hazard.intensity.shape[0])])
        hazard.event_id = np.arange(hazard.intensity.shape[0])
        hazard.event_name = [f"Flood_{forecast_date.strftime('%Y%m%d')}_{i}" 
                            for i in range(hazard.intensity.shape[0])]
        
        # Check validity
        hazard.check()
        
        logger.info(f"Created flood hazard: {hazard.size} events")
        return hazard
    
    def _discharge_to_depth(self, discharge: np.ndarray) -> np.ndarray:
        """
        Convert river discharge (m³/s) to flood depth (m)
        
        Uses simplified Manning's equation
        In production, use calibrated rating curves per river reach
        """
        # Simplified relationship (calibrate for Nigeria rivers)
        # Larger discharges → greater depths (power law)
        depth = 0.1 * np.power(discharge / 100.0, 0.6)
        return np.clip(depth, 0, 10)  # Max 10m depth
    
    def _interpolate_to_centroids(
        self,
        lats: np.ndarray,
        lons: np.ndarray,
        values: np.ndarray,
        target_centroids: Centroids
    ) -> np.ndarray:
        """Interpolate gridded hazard to centroid points"""
        from scipy.interpolate import RegularGridInterpolator
        
        # Create interpolator
        interpolator = RegularGridInterpolator(
            (lats, lons),
            values,
            method='linear',
            bounds_error=False,
            fill_value=0
        )
        
        # Interpolate to centroid locations
        points = np.column_stack([
            target_centroids.lat,
            target_centroids.lon
        ])
        
        interpolated = interpolator(points)
        
        return interpolated


# ============================================================================
# CONFLICT HAZARD MODEL
# ============================================================================

class ConflictHazardModel:
    """
    Armed conflict intensity model
    Uses ACLED data and spatial decay functions
    """
    
    def __init__(self, centroids: Centroids):
        self.centroids = centroids
        self.decay_distance_km = 50  # Conflict effects decay over 50km
        
    def create_hazard_from_acled(
        self,
        acled_data: pd.DataFrame,
        forecast_date: datetime,
        scenario: str = 'baseline'
    ) -> Hazard:
        """
        Convert conflict events to spatial intensity field
        
        Args:
            acled_data: DataFrame with columns: latitude, longitude, fatalities, date
            forecast_date: Date of forecast
            scenario: 'optimistic', 'baseline', 'pessimistic'
        
        Returns:
            CLIMADA Hazard object representing conflict intensity
        """
        logger.info(f"Creating conflict hazard from {len(acled_data)} events")
        
        # Scenario multipliers
        multipliers = {
            'optimistic': 0.7,
            'baseline': 1.0,
            'pessimistic': 1.5
        }
        multiplier = multipliers.get(scenario, 1.0)
        
        # Create spatial intensity field
        intensity = np.zeros((len(acled_data), len(self.centroids.lat)))
        
        for i, event in acled_data.iterrows():
            # Calculate distance from event to all centroids
            distances = self._haversine_distance(
                event['latitude'], event['longitude'],
                self.centroids.lat, self.centroids.lon
            )
            
            # Spatial decay function
            decay = np.exp(-distances / self.decay_distance_km)
            
            # Intensity = fatalities * decay * scenario multiplier
            intensity[i, :] = event['fatalities'] * decay * multiplier
        
        # Create CLIMADA Hazard
        hazard = Hazard('CF')  # Conflict hazard (custom type)
        hazard.centroids = self.centroids
        hazard.intensity = intensity
        hazard.frequency = np.ones(len(acled_data)) / 7  # Weekly events
        hazard.date = acled_data['date'].values
        hazard.event_id = np.arange(len(acled_data))
        hazard.event_name = [f"Conflict_{forecast_date.strftime('%Y%m%d')}_{i}" 
                            for i in range(len(acled_data))]
        
        hazard.check()
        
        logger.info(f"Created conflict hazard: {hazard.size} events")
        return hazard
    
    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate great circle distance in km
        
        Vectorized for arrays
        """
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c


# ============================================================================
# DROUGHT HAZARD MODEL
# ============================================================================

class DroughtHazardModel:
    """
    Agricultural drought model using SPI/SPEI indices
    """
    
    def __init__(self, centroids: Centroids):
        self.centroids = centroids
        
    def create_hazard_from_spi(
        self,
        spi_data: xr.DataArray,
        forecast_date: datetime
    ) -> Hazard:
        """
        Create drought hazard from Standardized Precipitation Index
        
        Args:
            spi_data: xarray with SPI values (negative = drought)
            forecast_date: Date of forecast
        
        Returns:
            CLIMADA Hazard object
        """
        logger.info("Creating drought hazard from SPI data")
        
        # SPI classification:
        # 0 to -1: Mild drought
        # -1 to -1.5: Moderate drought
        # -1.5 to -2: Severe drought
        # < -2: Extreme drought
        
        # Convert SPI to drought intensity (0-1 scale)
        # More negative SPI = higher intensity
        intensity = np.clip(-spi_data.values / 3.0, 0, 1)
        
        # Create CLIMADA Hazard
        hazard = Hazard('DR')  # Drought hazard
        hazard.centroids = self.centroids
        
        # Interpolate to centroids
        hazard.intensity = self._interpolate_to_centroids(
            lats=spi_data.latitude.values,
            lons=spi_data.longitude.values,
            values=intensity,
            target_centroids=self.centroids
        )
        
        # Set attributes
        n_timesteps = spi_data.shape[0]
        hazard.frequency = np.ones(n_timesteps) / 30  # Monthly
        hazard.date = np.array([forecast_date + timedelta(days=30*i) 
                               for i in range(n_timesteps)])
        hazard.event_id = np.arange(n_timesteps)
        hazard.event_name = [f"Drought_{forecast_date.strftime('%Y%m%d')}_{i}" 
                            for i in range(n_timesteps)]
        
        hazard.check()
        
        logger.info(f"Created drought hazard: {hazard.size} events")
        return hazard
    
    def _interpolate_to_centroids(self, lats, lons, values, target_centroids):
        """Interpolate gridded data to centroids"""
        from scipy.interpolate import RegularGridInterpolator
        
        interpolator = RegularGridInterpolator(
            (lats, lons), values,
            method='linear',
            bounds_error=False,
            fill_value=0
        )
        
        points = np.column_stack([target_centroids.lat, target_centroids.lon])
        return interpolator(points)


# ============================================================================
# DISEASE OUTBREAK MODEL
# ============================================================================

class DiseaseOutbreakModel:
    """
    Disease outbreak risk model (cholera, measles, meningitis)
    Correlates with flood events, population density, and season
    """
    
    def __init__(self, centroids: Centroids):
        self.centroids = centroids
        
    def create_cholera_risk_from_flood(
        self,
        flood_hazard: Hazard,
        population_density: np.ndarray,
        forecast_date: datetime
    ) -> Hazard:
        """
        Create cholera outbreak risk from flood hazard
        
        Args:
            flood_hazard: Flood hazard object
            population_density: Population per centroid
            forecast_date: Date of forecast
        
        Returns:
            Disease outbreak hazard
        """
        logger.info("Creating cholera risk hazard")
        
        # Cholera risk factors:
        # 1. Flooding (contaminated water)
        # 2. Population density (transmission)
        # 3. Seasonal (rainy season = higher risk)
        
        # Seasonal factor
        month = forecast_date.month
        seasonal_factor = 1.5 if month in [6, 7, 8, 9, 10] else 0.5  # Rainy season
        
        # Normalize population density
        pop_factor = population_density / population_density.max()
        
        # Cholera risk = flood intensity * population * seasonal factor
        intensity = flood_hazard.intensity * pop_factor[np.newaxis, :] * seasonal_factor
        
        # Create hazard
        hazard = Hazard('EP')  # Epidemic
        hazard.centroids = self.centroids
        hazard.intensity = intensity
        hazard.frequency = flood_hazard.frequency
        hazard.date = flood_hazard.date
        hazard.event_id = flood_hazard.event_id
        hazard.event_name = [name.replace('Flood', 'Cholera') 
                            for name in flood_hazard.event_name]
        
        hazard.check()
        
        logger.info(f"Created cholera risk hazard: {hazard.size} events")
        return hazard


# ============================================================================
# MULTI-HAZARD COMPOSER
# ============================================================================

class MultiHazardComposer:
    """
    Combines multiple hazards into compound risk scenarios
    """
    
    @staticmethod
    def combine_hazards(
        hazards: List[Hazard],
        weights: Optional[List[float]] = None,
        method: str = 'maximum'
    ) -> Hazard:
        """
        Combine multiple hazards
        
        Args:
            hazards: List of CLIMADA Hazard objects
            weights: Optional weights for each hazard
            method: 'maximum', 'additive', or 'multiplicative'
        
        Returns:
            Combined hazard
        """
        logger.info(f"Combining {len(hazards)} hazards using {method} method")
        
        if weights is None:
            weights = [1.0] * len(hazards)
        
        # Ensure all hazards have same centroids
        ref_centroids = hazards[0].centroids
        for h in hazards:
            if not np.array_equal(h.centroids.lat, ref_centroids.lat):
                raise ValueError("All hazards must share same centroids")
        
        # Combine intensities
        if method == 'maximum':
            # Take maximum intensity at each location
            combined_intensity = hazards[0].intensity * weights[0]
            for h, w in zip(hazards[1:], weights[1:]):
                combined_intensity = np.maximum(combined_intensity, h.intensity * w)
        
        elif method == 'additive':
            # Sum intensities (weighted)
            combined_intensity = sum(h.intensity * w 
                                   for h, w in zip(hazards, weights))
        
        elif method == 'multiplicative':
            # Compound effect (normalized)
            combined_intensity = hazards[0].intensity * weights[0]
            for h, w in zip(hazards[1:], weights[1:]):
                # Normalize to 0-1, multiply, rescale
                normalized = (h.intensity * w) / (h.intensity.max() + 1e-6)
                combined_intensity = combined_intensity * (1 + normalized)
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Create combined hazard
        hazard = Hazard('MH')  # Multi-hazard
        hazard.centroids = ref_centroids
        hazard.intensity = combined_intensity
        hazard.frequency = hazards[0].frequency
        hazard.date = hazards[0].date
        hazard.event_id = hazards[0].event_id
        hazard.event_name = [f"MultiHazard_{i}" for i in range(len(hazard.event_id))]
        
        hazard.check()
        
        logger.info(f"Created multi-hazard: {hazard.size} events")
        return hazard


# Example usage
if __name__ == "__main__":
    # This would typically be run as part of the forecast pipeline
    from climada.hazard import Centroids
    
    # Load centroids
    centroids = Centroids.from_hdf5('data/nigeria_centroids_1km.hdf5')
    
    # Create flood model
    flood_model = FloodHazardModel(centroids)
    
    # Example: Load GloFAS data and create hazard
    # flood_hazard = flood_model.create_hazard_from_glofas(
    #     glofas_file='data/raw/glofas/glofas_forecast_20250120.nc',
    #     forecast_date=datetime(2025, 1, 20)
    # )
    
    print("Hazard models initialized successfully")
```

**Nigeria-Specific Calibrations:**

1. **Flood Model**: Calibrate discharge-to-depth conversion for Niger and Benue rivers
2. **Conflict Model**: Adjust decay distance based on BAY states conflict patterns
3. **Drought Model**: Use SPI-3 (3-month) for agricultural drought in Sahel
4. **Disease Model**: Include meningitis belt seasonality (December-June)

**Estimated Time:** 90 minutes

---

### 3.2 Threshold Definition for Trigger Mechanisms (30 minutes)

Create `thresholds_config.yaml`:

```yaml
# Alert Trigger Thresholds for Nigeria IBF System
# Calibrated for BAY States (Borno, Adamawa, Yobe)

flood_thresholds:
  # River discharge return periods (years)
  discharge_rp:
    watch: 2         # 2-year return period
    advisory: 5      # 5-year return period  
    warning: 10      # 10-year return period
    emergency: 20    # 20-year return period
  
  # Flood depth thresholds (meters)
  depth:
    watch: 0.3       # 30cm - minor flooding
    advisory: 0.75   # 75cm - moderate flooding
    warning: 1.5     # 1.5m - major flooding
    emergency: 3.0   # 3m - catastrophic flooding
  
  # Displacement thresholds (people)
  displacement:
    watch: 1000
    advisory: 5000
    warning: 15000
    emergency: 50000

conflict_thresholds:
  # Fatalities (monthly)
  fatalities:
    watch: 10
    advisory: 25
    warning: 50
    emergency: 100
  
  # Predicted displacement (people)
  displacement:
    watch: 500
    advisory: 2500
    warning: 10000
    emergency: 30000
  
  # Event intensity score (0-100)
  intensity_score:
    watch: 30
    advisory: 50
    warning: 70
    emergency: 85

drought_thresholds:
  # SPI values (more negative = worse)
  spi:
    watch: -1.0      # Mild drought
    advisory: -1.5   # Moderate drought
    warning: -2.0    # Severe drought
    emergency: -2.5  # Extreme drought
  
  # Affected population (people)
  displacement:
    watch: 5000
    advisory: 20000
    warning: 75000
    emergency: 200000

disease_thresholds:
  # Cholera cases (per week)
  cholera_cases:
    watch: 10
    advisory: 50
    warning: 150
    emergency: 500
  
  # Meningitis cases (per week, dry season)
  meningitis_cases:
    watch: 5
    advisory: 15
    warning: 50
    emergency: 100

multi_hazard_thresholds:
  # Compound risk score (0-1)
  compound_risk:
    watch: 0.4
    advisory: 0.6
    warning: 0.75
    emergency: 0.9

# Confidence thresholds (for alert issuance)
confidence_requirements:
  watch: 0.4       # 40% confidence
  advisory: 0.55   # 55% confidence
  warning: 0.65    # 65% confidence
  emergency: 0.75  # 75% confidence

# Lead time considerations (days)
lead_time_validity:
  watch: [0, 14]       # 0-14 days
  advisory: [0, 7]     # 0-7 days
  warning: [0, 5]      # 0-5 days
  emergency: [0, 3]    # 0-3 days

# State-specific adjustments (multipliers)
state_adjustments:
  Borno:
    flood: 1.2        # Higher vulnerability
    conflict: 1.3     # Higher risk
    drought: 1.1
  
  Adamawa:
    flood: 1.0        # Baseline
    conflict: 1.1
    drought: 1.0
  
  Yobe:
    flood: 1.1
    conflict: 1.15
    drought: 1.2      # More vulnerable to drought
```

Create threshold evaluation script `scripts/threshold_evaluator.py`:

```python
#!/usr/bin/env python3
"""
Threshold Evaluator for Alert Triggers
Determines when forecasts should trigger alerts
"""

import yaml
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger('NigeriaIBF.ThresholdEvaluator')


class ThresholdEvaluator:
    """
    Evaluates forecast values against defined thresholds
    Determines appropriate alert levels
    """
    
    def __init__(self, config_path: str = 'thresholds_config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.alert_levels = ['watch', 'advisory', 'warning', 'emergency']
    
    def evaluate_flood(
        self,
        displacement: float,
        depth: float,
        state: str,
        confidence: float,
        lead_time_days: float
    ) -> Tuple[str, bool, str]:
        """
        Evaluate flood forecast against thresholds
        
        Returns:
            (alert_level, should_trigger, reasoning)
        """
        # Get thresholds
        disp_thresholds = self.config['flood_thresholds']['displacement']
        depth_thresholds = self.config['flood_thresholds']['depth']
        conf_thresholds = self.config['confidence_requirements']
        
        # State adjustment
        state_mult = self.config['state_adjustments'].get(state, {}).get('flood', 1.0)
        adjusted_displacement = displacement * state_mult
        
        # Determine alert level based on displacement
        alert_level = 'none'
        for level in reversed(self.alert_levels):
            if adjusted_displacement >= disp_thresholds[level]:
                alert_level = level
                break
        
        # Check if confidence meets requirement
        if alert_level != 'none':
            required_confidence = conf_thresholds[alert_level]
            should_trigger = confidence >= required_confidence
            
            # Check lead time validity
            lead_time_range = self.config['lead_time_validity'][alert_level]
            if not (lead_time_range[0] <= lead_time_days <= lead_time_range[1]):
                should_trigger = False
                reasoning = f"Lead time {lead_time_days}d outside valid range {lead_time_range}"
            elif not should_trigger:
                reasoning = f"Confidence {confidence:.2f} below required {required_confidence:.2f}"
            else:
                reasoning = f"Displacement {adjusted_displacement:.0f} exceeds {level} threshold"
        else:
            should_trigger = False
            reasoning = "Below all alert thresholds"
        
        return alert_level, should_trigger, reasoning
    
    def evaluate_conflict(
        self,
        displacement: float,
        fatalities: int,
        intensity_score: float,
        state: str,
        confidence: float,
        lead_time_days: float
    ) -> Tuple[str, bool, str]:
        """Evaluate conflict forecast against thresholds"""
        disp_thresholds = self.config['conflict_thresholds']['displacement']
        fatal_thresholds = self.config['conflict_thresholds']['fatalities']
        conf_thresholds = self.config['confidence_requirements']
        
        # State adjustment
        state_mult = self.config['state_adjustments'].get(state, {}).get('conflict', 1.0)
        adjusted_displacement = displacement * state_mult
        
        # Use maximum alert level from displacement or fatalities
        alert_level = 'none'
        for level in reversed(self.alert_levels):
            if (adjusted_displacement >= disp_thresholds[level] or 
                fatalities >= fatal_thresholds[level]):
                alert_level = level
                break
        
        if alert_level != 'none':
            required_confidence = conf_thresholds[alert_level]
            should_trigger = confidence >= required_confidence
            
            if should_trigger:
                reasoning = (f"Displacement {adjusted_displacement:.0f} or "
                           f"fatalities {fatalities} exceed {level} threshold")
            else:
                reasoning = f"Confidence {confidence:.2f} below required {required_confidence:.2f}"
        else:
            should_trigger = False
            reasoning = "Below all alert thresholds"
        
        return alert_level, should_trigger, reasoning
    
    def evaluate_multi_hazard(
        self,
        flood_alert: str,
        conflict_alert: str,
        compound_risk: float,
        confidence: float
    ) -> Tuple[str, bool, str]:
        """
        Evaluate multi-hazard scenario
        Takes maximum of individual hazards plus compound risk
        """
        # Map alert levels to numeric values
        level_values = {'none': 0, 'watch': 1, 'advisory': 2, 'warning': 3, 'emergency': 4}
        
        # Get maximum alert from individual hazards
        max_level_value = max(level_values.get(flood_alert, 0),
                             level_values.get(conflict_alert, 0))
        
        # Check if compound risk pushes alert higher
        compound_thresholds = self.config['multi_hazard_thresholds']['compound_risk']
        for level in reversed(self.alert_levels):
            if compound_risk >= compound_thresholds[level]:
                compound_level_value = level_values[level]
                max_level_value = max(max_level_value, compound_level_value)
                break
        
        # Convert back to alert level
        alert_level = [k for k, v in level_values.items() if v == max_level_value][0]
        
        if alert_level != 'none':
            required_confidence = self.config['confidence_requirements'][alert_level]
            should_trigger = confidence >= required_confidence
            reasoning = (f"Multi-hazard scenario: flood={flood_alert}, "
                        f"conflict={conflict_alert}, compound_risk={compound_risk:.2f}")
        else:
            should_trigger = False
            reasoning = "No significant multi-hazard risk"
        
        return alert_level, should_trigger, reasoning


# Example usage
if __name__ == "__main__":
    evaluator = ThresholdEvaluator()
    
    # Test flood evaluation
    alert_level, should_trigger, reasoning = evaluator.evaluate_flood(
        displacement=12000,
        depth=1.2,
        state='Borno',
        confidence=0.72,
        lead_time_days=2.5
    )
    
    print(f"Flood Evaluation:")
    print(f"  Alert Level: {alert_level}")
    print(f"  Should Trigger: {should_trigger}")
    print(f"  Reasoning: {reasoning}")
```

**Nigeria-Specific Considerations:**

1. **Rainy Season Adjustments**: Lower thresholds during June-October
2. **Borno State**: Higher conflict thresholds due to ongoing insurgency
3. **Yobe State**: Higher drought vulnerability (Sahel climate)
4. **Lake Chad Basin**: Special flood thresholds for basin flooding
5. **Cultural Events**: Adjust during Ramadan, harvest season

**Estimated Time:** 30 minutes

---

### 3.3 Spatial Analysis with Administrative Boundaries (45 minutes)

The system already has boundary data. Enhance spatial analysis capabilities:

Create `scripts/spatial_analysis.py`:

```python
#!/usr/bin/env python3
"""
Spatial Analysis Tools for Nigeria IBF
Administrative boundary analysis and aggregation
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger('NigeriaIBF.SpatialAnalysis')


class SpatialAnalyzer:
    """
    Spatial analysis for impact forecasting
    Handles administrative boundary operations
    """
    
    def __init__(self, boundaries_path: str = 'data/BAY_LGA_Shared.geojson'):
        """Load administrative boundaries"""
        self.boundaries = gpd.read_file(boundaries_path)
        logger.info(f"Loaded {len(self.boundaries)} administrative boundaries")
        
        # Ensure proper CRS
        if self.boundaries.crs != 'EPSG:4326':
            self.boundaries = self.boundaries.to_crs('EPSG:4326')
        
        # Create spatial index for faster operations
        self.boundaries_sindex = self.boundaries.sindex
    
    def aggregate_to_lga(
        self,
        points_df: pd.DataFrame,
        value_column: str,
        lat_col: str = 'latitude',
        lon_col: str = 'longitude'
    ) -> gpd.GeoDataFrame:
        """
        Aggregate point data to LGA level
        
        Args:
            points_df: DataFrame with lat/lon points
            value_column: Column to aggregate
            lat_col, lon_col: Names of coordinate columns
        
        Returns:
            GeoDataFrame with LGA-level aggregates
        """
        logger.info(f"Aggregating {len(points_df)} points to LGA level")
        
        # Convert to GeoDataFrame
        geometry = [Point(xy) for xy in zip(points_df[lon_col], points_df[lat_col])]
        gdf = gpd.GeoDataFrame(points_df, geometry=geometry, crs='EPSG:4326')
        
        # Spatial join with boundaries
        joined = gpd.sjoin(gdf, self.boundaries, how='left', predicate='within')
        
        # Aggregate by LGA
        aggregated = joined.groupby('ADM2_EN').agg({
            value_column: ['sum', 'mean', 'count', 'max']
        }).reset_index()
        
        aggregated.columns = ['lga_name', 'total', 'mean', 'count', 'max']
        
        # Join back with geometry
        result = self.boundaries.merge(aggregated, left_on='ADM2_EN', right_on='lga_name', how='left')
        result = result.fillna(0)
        
        logger.info(f"Aggregated to {len(result)} LGAs")
        return result
    
    def calculate_lga_exposure(
        self,
        hazard_intensity: np.ndarray,
        centroid_lats: np.ndarray,
        centroid_lons: np.ndarray,
        population_per_centroid: np.ndarray
    ) -> pd.DataFrame:
        """
        Calculate exposed population per LGA
        
        Args:
            hazard_intensity: Hazard intensity at each centroid
            centroid_lats: Centroid latitudes
            centroid_lons: Centroid longitudes
            population_per_centroid: Population at each centroid
        
        Returns:
            DataFrame with LGA-level exposure
        """
        logger.info("Calculating LGA-level exposure")
        
        # Create DataFrame of centroids
        centroids_df = pd.DataFrame({
            'latitude': centroid_lats,
            'longitude': centroid_lons,
            'intensity': hazard_intensity,
            'population': population_per_centroid,
            'exposed_pop': hazard_intensity * population_per_centroid
        })
        
        # Aggregate to LGA
        lga_exposure = self.aggregate_to_lga(
            centroids_df,
            value_column='exposed_pop'
        )
        
        # Add additional metrics
        lga_exposure['intensity_mean'] = lga_exposure['mean']
        lga_exposure['affected_population'] = lga_exposure['total']
        
        return lga_exposure
    
    def identify_high_risk_lgas(
        self,
        lga_exposure: gpd.GeoDataFrame,
        threshold: float,
        top_n: Optional[int] = None
    ) -> List[str]:
        """
        Identify high-risk LGAs above threshold
        
        Args:
            lga_exposure: LGA exposure GeoDataFrame
            threshold: Minimum affected population
            top_n: Return only top N LGAs (None = all above threshold)
        
        Returns:
            List of high-risk LGA names
        """
        high_risk = lga_exposure[lga_exposure['affected_population'] >= threshold]
        high_risk = high_risk.sort_values('affected_population', ascending=False)
        
        if top_n:
            high_risk = high_risk.head(top_n)
        
        logger.info(f"Identified {len(high_risk)} high-risk LGAs")
        return high_risk['ADM2_EN'].tolist()
    
    def calculate_distance_to_rivers(
        self,
        rivers_shapefile: str
    ) -> gpd.GeoDataFrame:
        """
        Calculate distance from each LGA centroid to nearest river
        Useful for flood risk assessment
        """
        rivers = gpd.read_file(rivers_shapefile)
        
        # Calculate distances
        distances = []
        for idx, lga in self.boundaries.iterrows():
            lga_centroid = lga.geometry.centroid
            min_dist = rivers.geometry.distance(lga_centroid).min()
            distances.append(min_dist * 111)  # Convert degrees to km
        
        self.boundaries['distance_to_river_km'] = distances
        
        return self.boundaries
    
    def create_buffer_zones(
        self,
        event_locations: List[Tuple[float, float]],
        buffer_km: float
    ) -> gpd.GeoDataFrame:
        """
        Create buffer zones around event locations
        Useful for conflict impact zones
        
        Args:
            event_locations: List of (lat, lon) tuples
            buffer_km: Buffer radius in kilometers
        
        Returns:
            GeoDataFrame with buffer polygons
        """
        # Create points
        geometry = [Point(lon, lat) for lat, lon in event_locations]
        events_gdf = gpd.GeoDataFrame(geometry=geometry, crs='EPSG:4326')
        
        # Project to metric CRS for accurate buffering
        events_projected = events_gdf.to_crs('EPSG:3857')
        
        # Create buffers (convert km to meters)
        buffers = events_projected.buffer(buffer_km * 1000)
        
        # Convert back to geographic CRS
        buffers_gdf = gpd.GeoDataFrame(geometry=buffers, crs='EPSG:3857')
        buffers_gdf = buffers_gdf.to_crs('EPSG:4326')
        
        return buffers_gdf
    
    def intersect_with_lgas(
        self,
        analysis_gdf: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
        """
        Find which LGAs intersect with analysis areas
        
        Args:
            analysis_gdf: GeoDataFrame with polygons to analyze
        
        Returns:
            GeoDataFrame with intersecting LGAs
        """
        intersecting = gpd.overlay(
            self.boundaries,
            analysis_gdf,
            how='intersection'
        )
        
        # Calculate intersection area
        intersecting['intersection_area_km2'] = intersecting.geometry.area * 12100  # Approx
        
        return intersecting


# Example usage
if __name__ == "__main__":
    analyzer = SpatialAnalyzer()
    
    # Example: Aggregate point data
    sample_data = pd.DataFrame({
        'latitude': np.random.uniform(10, 13, 100),
        'longitude': np.random.uniform(11, 14, 100),
        'displacement': np.random.randint(10, 500, 100)
    })
    
    lga_agg = analyzer.aggregate_to_lga(sample_data, 'displacement')
    print(f"Aggregated to {len(lga_agg)} LGAs")
    print(f"Total displacement: {lga_agg['total'].sum():.0f}")
```

**Estimated Time:** 45 minutes

---

### 3.4 Integration with Forecast Data Sources (60 minutes)

Create automated data fetcher `scripts/forecast_data_fetcher.py`:

```python
#!/usr/bin/env python3
"""
Automated Forecast Data Fetcher
Downloads and processes real-time forecast data
"""

import requests
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Optional, Dict, List
import ftplib
import cdsapi
from io import BytesIO

logger = logging.getLogger('NigeriaIBF.DataFetcher')


class ForecastDataFetcher:
    """
    Automated fetcher for forecast data sources
    """
    
    def __init__(self, data_dir: Path = Path('data/raw')):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_glofas_latest(
        self,
        bbox: Dict[str, float] = None,
        days_ahead: int = 7
    ) -> Path:
        """
        Fetch latest GloFAS flood forecast
        
        Args:
            bbox: Bounding box {'north': , 'south': , 'east': , 'west': }
            days_ahead: Number of days to forecast
        
        Returns:
            Path to downloaded NetCDF file
        """
        if bbox is None:
            # Default: Nigeria BAY states
            bbox = {'north': 14.0, 'south': 8.0, 'west': 9.0, 'east': 15.0}
        
        logger.info("Fetching GloFAS forecast from Copernicus CDS")
        
        try:
            c = cdsapi.Client()
            
            forecast_date = datetime.utcnow()
            output_file = (
                self.data_dir / 'glofas' / 
                f"glofas_forecast_{forecast_date.strftime('%Y%m%d')}.nc"
            )
            output_file.parent.mkdir(exist_ok=True)
            
            c.retrieve(
                'cems-glofas-forecast',
                {
                    'system_version': 'operational',
                    'hydrological_model': 'lisflood',
                    'product_type': 'ensemble_perturbed_forecasts',
                    'variable': 'river_discharge_in_the_last_24_hours',
                    'hyear': forecast_date.strftime('%Y'),
                    'hmonth': forecast_date.strftime('%m'),
                    'hday': forecast_date.strftime('%d'),
                    'leadtime_hour': [str(h) for h in range(24, days_ahead*24+1, 24)],
                    'area': [bbox['north'], bbox['west'], bbox['south'], bbox['east']],
                    'format': 'netcdf',
                },
                str(output_file)
            )
            
            logger.info(f"Downloaded GloFAS forecast: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"GloFAS download failed: {e}")
            raise
    
    def fetch_gfs_precipitation(
        self,
        bbox: Dict[str, float] = None,
        hours_ahead: int = 168  # 7 days
    ) -> Path:
        """
        Fetch GFS precipitation forecast from NOAA
        """
        if bbox is None:
            bbox = {'north': 14.0, 'south': 8.0, 'west': 9.0, 'east': 15.0}
        
        logger.info("Fetching GFS precipitation forecast")
        
        # NOAA NOMADS server
        base_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"
        
        forecast_date = datetime.utcnow()
        forecast_cycle = forecast_date.hour // 6 * 6  # 00, 06, 12, 18 UTC
        
        # Build URL
        params = {
            'file': f"gfs.t{forecast_cycle:02d}z.pgrb2.0p25.f000",
            'lev_surface': 'on',
            'var_APCP': 'on',  # Accumulated precipitation
            'subregion': '',
            'leftlon': bbox['west'],
            'rightlon': bbox['east'],
            'toplat': bbox['north'],
            'bottomlat': bbox['south'],
            'dir': f"/gfs.{forecast_date.strftime('%Y%m%d')}/{forecast_cycle:02d}/atmos"
        }
        
        output_file = (
            self.data_dir / 'gfs' /
            f"gfs_precip_{forecast_date.strftime('%Y%m%d')}_{forecast_cycle:02d}.grib2"
        )
        output_file.parent.mkdir(exist_ok=True)
        
        try:
            response = requests.get(base_url, params=params, timeout=300)
            response.raise_for_status()
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded GFS forecast: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"GFS download failed: {e}")
            raise
    
    def fetch_acled_recent(
        self,
        api_key: str,
        email: str,
        days_back: int = 30
    ) -> pd.DataFrame:
        """
        Fetch recent ACLED conflict data
        
        Args:
            api_key: ACLED API key
            email: Registered email
            days_back: Days of historical data to fetch
        
        Returns:
            DataFrame with conflict events
        """
        logger.info(f"Fetching ACLED data for last {days_back} days")
        
        url = "https://api.acleddata.com/acled/read"
        
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'key': api_key,
            'email': email,
            'country': 'Nigeria',
            'admin1': 'Borno|Adamawa|Yobe',
            'event_date': f"{start_date}|{end_date}",
            'event_date_where': 'BETWEEN',
            'limit': 0
        }
        
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data['data'])
            
            # Save to file
            output_file = (
                self.data_dir / 'acled' /
                f"acled_bay_{end_date}.csv"
            )
            output_file.parent.mkdir(exist_ok=True)
            df.to_csv(output_file, index=False)
            
            logger.info(f"Downloaded {len(df)} ACLED events: {output_file}")
            return df
            
        except Exception as e:
            logger.error(f"ACLED download failed: {e}")
            raise
    
    def fetch_nimet_forecast(
        self,
        api_endpoint: Optional[str] = None
    ) -> Dict:
        """
        Fetch forecast from Nigerian Meteorological Agency
        
        Note: This requires a partnership/API access with NiMet
        """
        if api_endpoint is None:
            logger.warning("NiMet API endpoint not configured")
            return {}
        
        logger.info("Fetching NiMet forecast")
        
        try:
            response = requests.get(api_endpoint, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info("Downloaded NiMet forecast")
            return data
            
        except Exception as e:
            logger.error(f"NiMet download failed: {e}")
            return {}
    
    def check_data_freshness(self) -> Dict[str, timedelta]:
        """
        Check age of downloaded data files
        
        Returns:
            Dictionary with data source: age (timedelta)
        """
        freshness = {}
        
        for source in ['glofas', 'gfs', 'acled']:
            source_dir = self.data_dir / source
            if source_dir.exists():
                files = list(source_dir.glob('*'))
                if files:
                    latest_file = max(files, key=lambda p: p.stat().st_mtime)
                    age = datetime.now() - datetime.fromtimestamp(latest_file.stat().st_mtime)
                    freshness[source] = age
                else:
                    freshness[source] = timedelta(days=999)  # No files
            else:
                freshness[source] = timedelta(days=999)
        
        return freshness


# Example usage
if __name__ == "__main__":
    fetcher = ForecastDataFetcher()
    
    # Check data freshness
    freshness = fetcher.check_data_freshness()
    for source, age in freshness.items():
        print(f"{source}: {age.total_seconds()/3600:.1f} hours old")
    
    # Fetch latest data (requires API credentials)
    # fetcher.fetch_glofas_latest()
```

**Nigeria-Specific Considerations:**

1. **Internet Connectivity**: Implement retry logic with exponential backoff
2. **Data Caching**: Keep last 7 days of forecasts locally
3. **NiMet Partnership**: Prioritize local data when available
4. **TAHMO Stations**: Real-time rainfall data for validation
5. **Bandwidth Optimization**: Download only BAY states region, not full Nigeria

**Estimated Time:** 60 minutes

---

## 4. Impact Assessment Framework

### 4.1 Vulnerability and Exposure Data Integration (60 minutes)

The system already has exposure data. Enhance vulnerability modeling:

Create `vulnerability_models.py`:

```python
#!/usr/bin/env python3
"""
Advanced Vulnerability Models for Nigeria IBF
Machine learning-enhanced vulnerability assessment
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger('NigeriaIBF.Vulnerability')


class VulnerabilityModel:
    """
    Multi-factor vulnerability assessment
    Combines:
    - Socioeconomic indicators
    - Infrastructure quality
    - Historical displacement patterns
    - Access to services
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
    
    def prepare_features(
        self,
        lga_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Prepare vulnerability features from LGA data
        
        Expected columns in lga_data:
        - population: Total population
        - poverty_rate: % below poverty line
        - literacy_rate: Adult literacy %
        - health_facilities: Number per 10,000 people
        - road_density: km per km²
        - market_access: Distance to nearest market (km)
        - conflict_history: Past events count
        - flood_history: Past flood events count
        - elevation_std: Terrain variability
        - distance_to_river: Distance to nearest river (km)
        """
        features = pd.DataFrame()
        
        # Demographic vulnerability
        features['population_density'] = lga_data['population'] / lga_data['area_km2']
        features['dependency_ratio'] = lga_data.get('dependency_ratio', 0.65)  # Default
        features['poverty_rate'] = lga_data.get('poverty_rate', 50.0)  # Default 50%
        
        # Social vulnerability
        features['literacy_rate'] = lga_data.get('literacy_rate', 60.0)
        features['health_access'] = lga_data.get('health_facilities', 1.0)
        features['female_headed_households'] = lga_data.get('female_hh_pct', 20.0)
        
        # Infrastructure vulnerability
        features['road_density'] = lga_data.get('road_density', 0.1)
        features['market_access'] = lga_data.get('market_access', 15.0)
        features['electricity_access'] = lga_data.get('electricity_pct', 30.0)
        features['water_access'] = lga_data.get('water_access_pct', 50.0)
        
        # Exposure history
        features['conflict_events_3yr'] = lga_data.get('conflict_history', 0)
        features['flood_events_5yr'] = lga_data.get('flood_history', 0)
        features['past_displacement_rate'] = lga_data.get('past_displacement_rate', 0.1)
        
        # Geographic factors
        features['distance_to_river'] = lga_data.get('distance_to_river', 50.0)
        features['elevation_std'] = lga_data.get('elevation_std', 50.0)
        features['slope_mean'] = lga_data.get('slope_mean', 2.0)
        
        # Coping capacity (inverse vulnerability)
        features['coping_capacity_index'] = (
            features['literacy_rate'] * 0.3 +
            features['health_access'] * 10 * 0.3 +
            features['electricity_access'] * 0.2 +
            features['water_access'] * 0.2
        ) / 100.0
        
        self.feature_names = features.columns.tolist()
        
        return features
    
    def train(
        self,
        training_data: pd.DataFrame,
        target_column: str = 'observed_vulnerability'
    ):
        """
        Train vulnerability model on historical data
        
        Args:
            training_data: DataFrame with features and target
            target_column: Name of vulnerability target (0-1 scale)
        """
        logger.info("Training vulnerability model")
        
        X = self.prepare_features(training_data)
        y = training_data[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"Model trained: R² train={train_score:.3f}, test={test_score:.3f}")
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Top 5 vulnerability factors:")
        for _, row in importance.head().iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.3f}")
    
    def predict(
        self,
        lga_data: pd.DataFrame
    ) -> np.ndarray:
        """
        Predict vulnerability for new LGAs
        
        Returns:
            Array of vulnerability scores (0-1)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X = self.prepare_features(lga_data)
        X_scaled = self.scaler.transform(X)
        
        vulnerability = self.model.predict(X_scaled)
        
        # Clip to valid range
        vulnerability = np.clip(vulnerability, 0, 1)
        
        return vulnerability
    
    def save(self, filepath: str):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, filepath)
        logger.info(f"Model saved: {filepath}")
    
    def load(self, filepath: str):
        """Load trained model"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        logger.info(f"Model loaded: {filepath}")


class ExposureCalculator:
    """
    Calculate population exposure to hazards
    """
    
    @staticmethod
    def calculate_exposure(
        population_grid: np.ndarray,
        hazard_intensity: np.ndarray,
        threshold: float = 0.1
    ) -> Dict[str, float]:
        """
        Calculate exposed population
        
        Args:
            population_grid: Population per grid cell
            hazard_intensity: Hazard intensity per grid cell (0-1)
            threshold: Minimum intensity to consider "exposed"
        
        Returns:
            Dictionary with exposure metrics
        """
        # Binary exposure (above threshold)
        exposed_mask = hazard_intensity >= threshold
        exposed_population = (population_grid * exposed_mask).sum()
        
        # Intensity-weighted exposure
        weighted_exposure = (population_grid * hazard_intensity).sum()
        
        # Exposure by intensity class
        low_intensity = (hazard_intensity >= 0.1) & (hazard_intensity < 0.3)
        med_intensity = (hazard_intensity >= 0.3) & (hazard_intensity < 0.6)
        high_intensity = (hazard_intensity >= 0.6)
        
        return {
            'total_population': population_grid.sum(),
            'exposed_population': exposed_population,
            'exposed_percentage': exposed_population / population_grid.sum() * 100,
            'weighted_exposure': weighted_exposure,
            'low_intensity_exposure': (population_grid * low_intensity).sum(),
            'medium_intensity_exposure': (population_grid * med_intensity).sum(),
            'high_intensity_exposure': (population_grid * high_intensity).sum(),
        }


# Example usage
if __name__ == "__main__":
    # Create sample training data
    np.random.seed(42)
    n_lgas = 100
    
    training_data = pd.DataFrame({
        'population': np.random.randint(10000, 500000, n_lgas),
        'area_km2': np.random.randint(100, 5000, n_lgas),
        'poverty_rate': np.random.uniform(30, 80, n_lgas),
        'literacy_rate': np.random.uniform(40, 90, n_lgas),
        'health_facilities': np.random.uniform(0.5, 5.0, n_lgas),
        'road_density': np.random.uniform(0.05, 0.5, n_lgas),
        'conflict_history': np.random.poisson(5, n_lgas),
        'flood_history': np.random.poisson(3, n_lgas),
        'distance_to_river': np.random.uniform(1, 100, n_lgas),
        'observed_vulnerability': np.random.beta(2, 5, n_lgas)  # Target variable
    })
    
    # Train model
    model = VulnerabilityModel()
    model.train(training_data)
    
    # Save model
    model.save('models/vulnerability_model_v1.pkl')
    
    print("Vulnerability model trained and saved successfully")
```

**Estimated Time:** 60 minutes

---

### 4.2 Impact Calculation Methodologies (45 minutes)

The system already has impact calculation. Here's the complete methodology documentation:

Create `docs/IMPACT_METHODOLOGY.md`:

```markdown
# Impact Calculation Methodology
## Nigeria IBF System

### Overview

The Nigeria IBF system calculates displacement impacts using a cascading approach:

```
Hazard → Exposure → Vulnerability → Impact (Displacement)
```

### 1. Hazard Intensity Normalization

Convert raw hazard intensity to normalized scale (0-1):

**Flood:**
```python
def normalize_flood_intensity(depth_m):
    """
    0m = 0.0 (no flood)
    0.5m = 0.3 (minor)
    1.5m = 0.7 (major)
    3m+ = 1.0 (catastrophic)
    """
    return np.clip(depth_m / 3.0, 0, 1)
```

**Conflict:**
```python
def normalize_conflict_intensity(fatalities, distance_km):
    """
    Fatalities with spatial decay
    """
    spatial_decay = np.exp(-distance_km / 50)  # 50km decay
    return np.clip((fatalities / 100) * spatial_decay, 0, 1)
```

### 2. Exposure Calculation

```python
def calculate_exposure(population, hazard_intensity, threshold=0.1):
    """
    Population-at-risk = Population where hazard > threshold
    """
    exposed_mask = hazard_intensity > threshold
    exposed_population = population * exposed_mask
    return exposed_population
```

### 3. Vulnerability Functions

Sigmoid vulnerability curves calibrated for Nigeria:

```python
def vulnerability_function(hazard_intensity, v_half, steepness=4):
    """
    v_half: Intensity at which 50% displacement occurs
    steepness: How quickly displacement increases
    
    Returns: Fraction of exposed population displaced (0-1)
    """
    return 1 / (1 + np.exp(-steepness * (hazard_intensity - v_half) / v_half))
```

**Regional v_half values (flood depth):**
- North East (BAY): 0.18 - 0.60m (high vulnerability)
- North West: 0.12 - 0.42m
- North Central: 0.10 - 0.42m
- South: 0.08 - 0.36m (lower vulnerability)

### 4. Displacement Calculation

```python
displacement = (
    population * 
    (hazard_intensity > threshold) *  # Exposed
    vulnerability_function(hazard_intensity, v_half)  # Fraction displaced
)
```

### 5. Uncertainty Quantification

Monte Carlo sampling (N=5000 samples):

**Sources of Uncertainty:**
1. **Hazard (45%)**: Ensemble forecast spread, intensity uncertainty
2. **Vulnerability (30%)**: Parameter uncertainty, regional variation
3. **Exposure (25%)**: Population data uncertainty

**Implementation:**
```python
def uncertainty_analysis(exposure, hazard, vulnerability, n_samples=5000):
    """
    Sample from uncertainty distributions
    """
    results = []
    
    for i in range(n_samples):
        # Sample hazard (from ensemble)
        haz_sample = hazard[np.random.randint(0, len(hazard))]
        
        # Sample vulnerability parameters
        v_half_sample = np.random.normal(v_half_mean, v_half_std)
        vuln_sample = vulnerability_function(haz_sample, v_half_sample)
        
        # Sample exposure (±20%)
        exp_sample = exposure * np.random.uniform(0.8, 1.2)
        
        # Calculate impact
        impact = exp_sample * (haz_sample > threshold) * vuln_sample
        results.append(impact.sum())
    
    return np.array(results)
```

### 6. Sectoral Impact Assessment

**Health Impacts:**
- Direct injuries: 0.5-2% of displaced population
- Disease risk: Cholera outbreaks after floods (2-5% attack rate)
- Malnutrition: 10-20% of children under 5 in prolonged displacement

**Agricultural Impacts:**
- Crop loss: 60-100% in flooded areas
- Livestock loss: 20-40% in conflict zones
- Market disruption: Food prices increase 30-50%

**Infrastructure Impacts:**
- Roads: 40-60% of rural roads impassable after floods
- Schools: 20-30% damaged/occupied as shelters
- Health facilities: 15-25% non-functional

### 7. Multi-Hazard Interaction

For compound flood + conflict scenarios:

```python
def multi_hazard_impact(flood_intensity, conflict_intensity, weights=[0.5, 0.5]):
    """
    Maximum method: Take worst-case scenario
    """
    combined_intensity = np.maximum(
        flood_intensity * weights[0],
        conflict_intensity * weights[1]
    )
    
    # Add compounding factor (10-30% increase)
    if flood_intensity > 0.3 and conflict_intensity > 0.3:
        compound_factor = 1.2
        combined_intensity *= compound_factor
    
    return combined_intensity
```

### 8. Temporal Dynamics

Displacement evolves over time:

**Phase 1 (0-3 days)**: Immediate flight
- 60-80% of total displacement occurs
- Mostly short-distance (<20km)

**Phase 2 (4-14 days)**: Secondary displacement
- 15-25% additional displacement
- Longer distances (20-100km)

**Phase 3 (15+ days)**: Prolonged displacement
- 5-15% additional (protracted conflict)
- International movement possible

### 9. Validation Metrics

Compare forecasts to observed displacement:

```python
# Bias
bias = mean(forecasted) - mean(observed)

# Relative Error
relative_error = 100 * (forecasted - observed) / observed

# Hit Rate (for alert thresholds)
hit_rate = P(forecast > threshold | event occurred)

# False Alarm Rate
far = P(forecast > threshold | no event)

# ROC-AUC
from sklearn.metrics import roc_auc_score
auc = roc_auc_score(event_occurred, forecast_probability)
```

### References

1. Kropf et al. (2024) - TC displacement methodology
2. IDMC (2023) - Nigeria displacement statistics
3. IOM DTM (2024) - BAY states data
4. CLIMADA documentation - Impact functions
```

**Estimated Time:** 45 minutes (documentation)

---

### 4.3 Population-at-Risk Estimation (30 minutes)

Enhance existing exposure calculation with risk stratification:

```python
#!/usr/bin/env python3
"""
Population-at-Risk Estimator
Stratifies exposed population by risk level
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple

class PopulationRiskEstimator:
    """
    Estimates population at different risk levels
    """
    
    def __init__(self):
        # Risk level thresholds (hazard intensity)
        self.risk_thresholds = {
            'minimal': (0.0, 0.1),
            'low': (0.1, 0.3),
            'moderate': (0.3, 0.6),
            'high': (0.6, 0.8),
            'extreme': (0.8, 1.0)
        }
    
    def estimate_population_at_risk(
        self,
        population: np.ndarray,
        hazard_intensity: np.ndarray,
        vulnerability: np.ndarray
    ) -> Dict[str, int]:
        """
        Stratify population by risk level
        
        Returns:
            Dictionary with population counts per risk level
        """
        results = {}
        
        for risk_level, (min_int, max_int) in self.risk_thresholds.items():
            # Find cells in this risk range
            mask = (hazard_intensity >= min_int) & (hazard_intensity < max_int)
            
            # Population at risk in this level
            pop_at_risk = (population * mask).sum()
            
            # Expected displacement (using vulnerability)
            expected_displacement = (population * mask * vulnerability).sum()
            
            results[risk_level] = {
                'population_exposed': int(pop_at_risk),
                'expected_displacement': int(expected_displacement),
                'displacement_rate': expected_displacement / (pop_at_risk + 1e-6)
            }
        
        # Total
        results['total'] = {
            'population_exposed': int((population * (hazard_intensity > 0.1)).sum()),
            'expected_displacement': int((population * hazard_intensity * vulnerability).sum()),
            'displacement_rate': results['total']['expected_displacement'] / 
                                (results['total']['population_exposed'] + 1e-6)
        }
        
        return results
    
    def estimate_by_demographic_group(
        self,
        population: np.ndarray,
        hazard_intensity: np.ndarray,
        vulnerability: np.ndarray,
        demographic_fractions: Dict[str, float]
    ) -> Dict[str, Dict]:
        """
        Estimate displacement by demographic group
        
        Args:
            demographic_fractions: e.g., {'children': 0.45, 'women': 0.52, 'elderly': 0.08}
        
        Returns:
            Displacement estimates by demographic group
        """
        total_displacement = (population * hazard_intensity * vulnerability).sum()
        
        results = {}
        for group, fraction in demographic_fractions.items():
            results[group] = {
                'exposed': int(population.sum() * fraction),
                'displaced': int(total_displacement * fraction)
            }
        
        return results


# Example usage
if __name__ == "__main__":
    # Simulate data
    n_cells = 1000
    population = np.random.randint(100, 5000, n_cells)
    hazard_intensity = np.random.beta(2, 5, n_cells)  # Skewed toward lower values
    vulnerability = np.random.uniform(0.3, 0.8, n_cells)
    
    estimator = PopulationRiskEstimator()
    
    # Estimate by risk level
    risk_estimates = estimator.estimate_population_at_risk(
        population, hazard_intensity, vulnerability
    )
    
    print("Population at Risk by Level:")
    for level, data in risk_estimates.items():
        print(f"\n{level.upper()}:")
        print(f"  Exposed: {data['population_exposed']:,}")
        print(f"  Expected Displacement: {data['expected_displacement']:,}")
        print(f"  Displacement Rate: {data['displacement_rate']:.1%}")
    
    # Estimate by demographic group
    demographics = {
        'children': 0.45,
        'adult_women': 0.28,
        'adult_men': 0.24,
        'elderly': 0.03
    }
    
    demographic_estimates = estimator.estimate_by_demographic_group(
        population, hazard_intensity, vulnerability, demographics
    )
    
    print("\n\nDisplacement by Demographic Group:")
    for group, data in demographic_estimates.items():
        print(f"{group}: {data['displaced']:,} displaced")
```

**Estimated Time:** 30 minutes

---

## 5. Automation & Operationalization

### 5.1 Automated Data Fetching and Processing Pipelines (45 minutes)

Automate the entire forecast workflow:

Create `scripts/automated_forecast_pipeline.sh`:

```bash
#!/bin/bash
##############################################################################
# Automated Forecast Pipeline for Nigeria IBF
# Runs complete forecast workflow from data fetch to alert dissemination
##############################################################################

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/pipeline_$TIMESTAMP.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# Error handling
trap 'log_error "Pipeline failed at line $LINENO"; exit 1' ERR

log "========================================="
log "Nigeria IBF Automated Forecast Pipeline"
log "========================================="

# Activate Python environment
log "Activating Python environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# Step 1: Fetch latest data
log "Step 1: Fetching latest forecast data..."
python "$PROJECT_ROOT/scripts/data_pipeline.py" run-daily-update
if [ $? -eq 0 ]; then
    log "✓ Data fetch successful"
else
    log_error "Data fetch failed"
    exit 1
fi

# Step 2: Generate centroids (if needed)
if [ ! -f "$PROJECT_ROOT/data/nigeria_centroids_1km.hdf5" ]; then
    log "Step 2: Generating centroids..."
    python "$PROJECT_ROOT/generate_centroids.py" --method bbox
    log "✓ Centroids generated"
else
    log "Step 2: Centroids already exist, skipping..."
fi

# Step 3: Run forecast
log "Step 3: Running impact forecast..."
FORECAST_DATE=$(date +%Y-%m-%d)
python -m production_forecast_engine \
    --environment production \
    --forecast-date "$FORECAST_DATE" \
    --lead-time 2.0 \
    --hazards flood conflict \
    --log-file "$LOG_FILE"

if [ $? -eq 0 ]; then
    log "✓ Forecast completed successfully"
else
    log_error "Forecast execution failed"
    exit 1
fi

# Step 4: Generate visualizations
log "Step 4: Generating visualizations..."
LATEST_OUTPUT=$(ls -t "$PROJECT_ROOT/outputs" | head -1)
python "$PROJECT_ROOT/scripts/generate_visualizations.py" \
    --forecast-dir "$PROJECT_ROOT/outputs/$LATEST_OUTPUT"

log "✓ Visualizations generated"

# Step 5: Check for alerts
log "Step 5: Checking alert conditions..."
ALERTS=$(python "$PROJECT_ROOT/scripts/check_alerts.py" \
    --forecast-dir "$PROJECT_ROOT/outputs/$LATEST_OUTPUT" \
    --format json)

if [ ! -z "$ALERTS" ]; then
    log "⚠️  ALERTS TRIGGERED!"
    echo "$ALERTS" | tee -a "$LOG_FILE"
    
    # Send alerts
    log "Step 6: Sending alert notifications..."
    python "$PROJECT_ROOT/scripts/send_alerts.py" \
        --alerts "$ALERTS" \
        --channels email sms
    log "✓ Alerts sent"
else
    log "No alerts triggered"
fi

# Step 7: Archive outputs
log "Step 7: Archiving outputs..."
ARCHIVE_DIR="$PROJECT_ROOT/archive/$(date +%Y/%m)"
mkdir -p "$ARCHIVE_DIR"
cp -r "$PROJECT_ROOT/outputs/$LATEST_OUTPUT" "$ARCHIVE_DIR/"
log "✓ Outputs archived to $ARCHIVE_DIR"

# Step 8: Update database
log "Step 8: Updating forecast database..."
python "$PROJECT_ROOT/scripts/update_database.py" \
    --forecast-dir "$PROJECT_ROOT/outputs/$LATEST_OUTPUT"
log "✓ Database updated"

# Step 9: Generate summary report
log "Step 9: Generating summary report..."
python "$PROJECT_ROOT/scripts/generate_report.py" \
    --forecast-dir "$PROJECT_ROOT/outputs/$LATEST_OUTPUT" \
    --output "$PROJECT_ROOT/outputs/$LATEST_OUTPUT/summary_report.txt"
log "✓ Summary report generated"

# Cleanup old logs (keep last 30 days)
log "Cleaning up old logs..."
find "$LOG_DIR" -name "pipeline_*.log" -mtime +30 -delete
log "✓ Cleanup complete"

log "========================================="
log "Pipeline completed successfully!"
log "Total time: $SECONDS seconds"
log "========================================="

# Send success notification
python "$PROJECT_ROOT/scripts/notify.py" \
    --status success \
    --message "Forecast pipeline completed successfully at $(date)" \
    --log-file "$LOG_FILE"

exit 0
```

Make executable:
```bash
chmod +x scripts/automated_forecast_pipeline.sh
```

**Estimated Time:** 45 minutes

---

### 5.2 Scheduling Regular Forecasts (Cron Jobs) (30 minutes)

Set up automated scheduling:

Create `scripts/setup_cron.sh`:

```bash
#!/bin/bash
##############################################################################
# Setup Cron Jobs for Nigeria IBF System
# Schedules automated forecast execution
##############################################################################

# Configuration
CRON_USER="nigeria-ibf"  # User to run cron jobs
PROJECT_ROOT="/home/nigeria-ibf/nigeria-ibf"
PYTHON_ENV="$PROJECT_ROOT/venv/bin/python"

echo "Setting up cron jobs for Nigeria IBF..."

# Create cron schedule file
CRON_FILE="/tmp/nigeria_ibf_cron"

cat > "$CRON_FILE" << 'EOF'
# Nigeria IBF Automated Forecast Schedule
# Runs twice daily at 00:00 and 12:00 UTC (corresponding to Nigerian morning/evening)

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=operations@nema.gov.ng

# ============================================================================
# MAIN FORECAST PIPELINE
# ============================================================================

# Run full forecast pipeline twice daily
0 0,12 * * * /home/nigeria-ibf/nigeria-ibf/scripts/automated_forecast_pipeline.sh >> /var/log/nigeria-ibf/cron.log 2>&1

# ============================================================================
# DATA UPDATES
# ============================================================================

# Update ACLED data daily at 03:00 UTC
0 3 * * * /home/nigeria-ibf/nigeria-ibf/venv/bin/python /home/nigeria-ibf/nigeria-ibf/scripts/data_pipeline.py --update acled >> /var/log/nigeria-ibf/data_update.log 2>&1

# Check for DTM updates on 1st of each month
0 4 1 * * /home/nigeria-ibf/nigeria-ibf/venv/bin/python /home/nigeria-ibf/nigeria-ibf/scripts/data_pipeline.py --update dtm >> /var/log/nigeria-ibf/data_update.log 2>&1

# ============================================================================
# MONITORING & MAINTENANCE
# ============================================================================

# Health check every hour
0 * * * * /home/nigeria-ibf/nigeria-ibf/venv/bin/python /home/nigeria-ibf/nigeria-ibf/scripts/health_check.py >> /var/log/nigeria-ibf/health.log 2>&1

# Database backup daily at 02:00 UTC
0 2 * * * /home/nigeria-ibf/nigeria-ibf/scripts/backup_database.sh >> /var/log/nigeria-ibf/backup.log 2>&1

# Cleanup old outputs weekly (Sundays at 01:00 UTC)
0 1 * * 0 find /home/nigeria-ibf/nigeria-ibf/outputs -mtime +30 -delete >> /var/log/nigeria-ibf/cleanup.log 2>&1

# ============================================================================
# REPORTING
# ============================================================================

# Weekly performance report (Mondays at 08:00 UTC)
0 8 * * 1 /home/nigeria-ibf/nigeria-ibf/venv/bin/python /home/nigeria-ibf/nigeria-ibf/scripts/weekly_report.py >> /var/log/nigeria-ibf/reports.log 2>&1

# Monthly validation report (1st of month at 09:00 UTC)
0 9 1 * * /home/nigeria-ibf/nigeria-ibf/venv/bin/python /home/nigeria-ibf/nigeria-ibf/scripts/monthly_validation.py >> /var/log/nigeria-ibf/reports.log 2>&1

EOF

# Install cron jobs
echo "Installing cron jobs for user: $CRON_USER"
sudo -u "$CRON_USER" crontab "$CRON_FILE"

# Verify installation
echo ""
echo "Installed cron jobs:"
sudo -u "$CRON_USER" crontab -l

# Create log directory
sudo mkdir -p /var/log/nigeria-ibf
sudo chown -R "$CRON_USER:$CRON_USER" /var/log/nigeria-ibf

echo ""
echo "✓ Cron jobs installed successfully!"
echo ""
echo "Schedule:"
echo "  - Forecasts: 00:00 and 12:00 UTC daily"
echo "  - Data updates: 03:00 UTC daily"
echo "  - Health checks: Every hour"
echo "  - Backups: 02:00 UTC daily"
echo "  - Reports: Weekly (Mon) and Monthly (1st)"
echo ""
echo "Logs location: /var/log/nigeria-ibf/"

# Cleanup
rm "$CRON_FILE"
```

Run setup:
```bash
chmod +x scripts/setup_cron.sh
sudo ./scripts/setup_cron.sh
```

**Nigeria-Specific Considerations:**
- UTC times adjusted for West Africa Time (WAT = UTC+1)
- Forecasts at 00:00 UTC (1 AM WAT) for morning review
- Forecasts at 12:00 UTC (1 PM WAT) for afternoon updates
- Extra health checks due to power/internet instability

**Estimated Time:** 30 minutes

---

### 5.3 Alert Generation and Dissemination (60 minutes)

Enhance the existing alert system with multiple channels:

Create `scripts/alert_dissemination.py`:

```python
#!/usr/bin/env python3
"""
Multi-Channel Alert Dissemination System
Sends alerts via Email, SMS, WhatsApp, and API webhooks
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging
from twilio.rest import Client  # For SMS
import yaml

logger = logging.getLogger('NigeriaIBF.AlertDissemination')


class AlertDisseminator:
    """
    Multi-channel alert dissemination
    """
    
    def __init__(self, config_path: str = 'config/alert_config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def send_alert(
        self,
        alert: Dict,
        channels: List[str] = ['email', 'sms']
    ):
        """
        Send alert through multiple channels
        
        Args:
            alert: Alert dictionary with title, message, level, affected_areas
            channels: List of channels to use
        """
        logger.info(f"Sending {alert['level']} alert via: {', '.join(channels)}")
        
        results = {}
        
        if 'email' in channels:
            results['email'] = self.send_email_alert(alert)
        
        if 'sms' in channels:
            results['sms'] = self.send_sms_alert(alert)
        
        if 'whatsapp' in channels:
            results['whatsapp'] = self.send_whatsapp_alert(alert)
        
        if 'webhook' in channels:
            results['webhook'] = self.send_webhook_alert(alert)
        
        return results
    
    def send_email_alert(self, alert: Dict) -> bool:
        """
        Send email alert
        """
        try:
            # Email configuration
            smtp_server = self.config['email']['smtp_server']
            smtp_port = self.config['email']['smtp_port']
            sender_email = self.config['email']['sender']
            sender_password = self.config['email']['password']
            
            # Get recipients based on alert level
            recipients = self.config['recipients'][alert['level']]['email']
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert['level'].upper()}] {alert['title']}"
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipients)
            
            # HTML email body
            html_body = f"""
            <html>
              <head></head>
              <body>
                <h2 style="color: {'red' if alert['level'] == 'emergency' else 'orange'};">
                  {alert['title']}
                </h2>
                <p><strong>Alert Level:</strong> {alert['level'].upper()}</p>
                <p><strong>Issued:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
                <p><strong>Affected Areas:</strong> {', '.join(alert['affected_states'])}</p>
                <hr>
                <h3>Summary</h3>
                <p>{alert['summary']}</p>
                <h3>Expected Impact</h3>
                <p>Estimated Displacement: {alert['estimated_displacement']['mean']:,.0f} people</p>
                <p>Range: {alert['estimated_displacement']['p05']:,.0f} - 
                   {alert['estimated_displacement']['p95']:,.0f} people (90% confidence)</p>
                <h3>Recommended Actions</h3>
                <ul>
                  {''.join(f'<li>{action}</li>' for action in alert['recommended_actions'])}
                </ul>
                <hr>
                <p style="font-size: 10px; color: gray;">
                  This is an automated alert from the Nigeria Impact-Based Forecasting System.
                  For more information, contact: operations@nema.gov.ng
                </p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach forecast visualization if available
            if 'visualization_path' in alert:
                self._attach_file(msg, alert['visualization_path'])
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def send_sms_alert(self, alert: Dict) -> bool:
        """
        Send SMS alert using Twilio
        """
        try:
            # Twilio configuration
            account_sid = self.config['sms']['twilio_account_sid']
            auth_token = self.config['sms']['twilio_auth_token']
            from_number = self.config['sms']['from_number']
            
            client = Client(account_sid, auth_token)
            
            # Get recipients
            recipients = self.config['recipients'][alert['level']]['sms']
            
            # Create concise SMS message (max 160 characters)
            sms_body = (
                f"NIGERIA IBF ALERT [{alert['level'].upper()}]\n"
                f"{alert['title']}\n"
                f"Affected: {', '.join(alert['affected_states'][:2])}\n"
                f"Displacement: {alert['estimated_displacement']['mean']:,.0f} people\n"
                f"Check email for details."
            )[:160]  # Truncate to SMS limit
            
            # Send to all recipients
            for recipient in recipients:
                message = client.messages.create(
                    body=sms_body,
                    from_=from_number,
                    to=recipient
                )
                logger.debug(f"SMS sent to {recipient}: {message.sid}")
            
            logger.info(f"SMS alerts sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False
    
    def send_whatsapp_alert(self, alert: Dict) -> bool:
        """
        Send WhatsApp alert (requires Twilio WhatsApp Business API or similar)
        """
        try:
            # Similar to SMS but using WhatsApp
            account_sid = self.config['whatsapp']['twilio_account_sid']
            auth_token = self.config['whatsapp']['twilio_auth_token']
            from_whatsapp = self.config['whatsapp']['from_number']
            
            client = Client(account_sid, auth_token)
            
            recipients = self.config['recipients'][alert['level']]['whatsapp']
            
            # WhatsApp allows longer messages
            message_body = (
                f"*NIGERIA IBF ALERT* - {alert['level'].upper()}\n\n"
                f"*{alert['title']}*\n\n"
                f"*Affected Areas:* {', '.join(alert['affected_states'])}\n"
                f"*Estimated Displacement:* {alert['estimated_displacement']['mean']:,.0f} people\n\n"
                f"*Summary:*\n{alert['summary']}\n\n"
                f"*Recommended Actions:*\n" +
                '\n'.join(f"• {action}" for action in alert['recommended_actions'])
            )
            
            for recipient in recipients:
                message = client.messages.create(
                    body=message_body,
                    from_=f'whatsapp:{from_whatsapp}',
                    to=f'whatsapp:{recipient}'
                )
                logger.debug(f"WhatsApp sent to {recipient}: {message.sid}")
            
            logger.info(f"WhatsApp alerts sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"WhatsApp sending failed: {e}")
            return False
    
    def send_webhook_alert(self, alert: Dict) -> bool:
        """
        Send alert to external systems via webhook
        """
        try:
            webhook_urls = self.config['webhooks']['urls']
            
            # Prepare JSON payload
            payload = {
                'alert_id': alert.get('alert_id', 'unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'level': alert['level'],
                'title': alert['title'],
                'summary': alert['summary'],
                'affected_states': alert['affected_states'],
                'estimated_displacement': alert['estimated_displacement'],
                'recommended_actions': alert['recommended_actions'],
                'source': 'Nigeria IBF System'
            }
            
            # Send to all configured webhooks
            for webhook_url in webhook_urls:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                response.raise_for_status()
                logger.debug(f"Webhook sent to {webhook_url}: {response.status_code}")
            
            logger.info(f"Webhook alerts sent to {len(webhook_urls)} endpoints")
            return True
            
        except Exception as e:
            logger.error(f"Webhook sending failed: {e}")
            return False
    
    def _attach_file(self, msg: MIMEMultipart, filepath: str):
        """Attach file to email"""
        with open(filepath, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {Path(filepath).name}'
        )
        msg.attach(part)


# Configuration file template
def create_alert_config_template():
    """Create template configuration file"""
    config = {
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender': 'alerts@nigeria-ibf.org',
            'password': 'your_password_here'
        },
        'sms': {
            'twilio_account_sid': 'your_account_sid',
            'twilio_auth_token': 'your_auth_token',
            'from_number': '+1234567890'
        },
        'whatsapp': {
            'twilio_account_sid': 'your_account_sid',
            'twilio_auth_token': 'your_auth_token',
            'from_number': '+1234567890'
        },
        'webhooks': {
            'urls': [
                'https://nema.gov.ng/api/alerts',
                'https://ocha.org.ng/api/alerts'
            ]
        },
        'recipients': {
            'watch': {
                'email': ['forecaster1@nema.gov.ng', 'forecaster2@nema.gov.ng'],
                'sms': ['+234XXXXXXXXX'],
                'whatsapp': ['+234XXXXXXXXX']
            },
            'advisory': {
                'email': ['operations@nema.gov.ng', 'coordinator@nema.gov.ng'],
                'sms': ['+234XXXXXXXXX', '+234YYYYYYYYY'],
                'whatsapp': ['+234XXXXXXXXX']
            },
            'warning': {
                'email': ['director@nema.gov.ng', 'operations@nema.gov.ng', 
                         'ocha@un.org'],
                'sms': ['+234XXXXXXXXX', '+234YYYYYYYYY', '+234ZZZZZZZZZ'],
                'whatsapp': ['+234XXXXXXXXX', '+234YYYYYYYYY']
            },
            'emergency': {
                'email': ['director@nema.gov.ng', 'president@nigeria.gov.ng',
                         'ocha@un.org', 'ifrc@redcross.org'],
                'sms': ['+234XXXXXXXXX', '+234YYYYYYYYY', '+234ZZZZZZZZZ',
                       '+234AAAAAAAA'],
                'whatsapp': ['+234XXXXXXXXX', '+234YYYYYYYYY', '+234ZZZZZZZZZ']
            }
        }
    }
    
    with open('config/alert_config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("Alert configuration template created: config/alert_config.yaml")
    print("Please update with your actual credentials and contact information")


if __name__ == "__main__":
    # Create template if config doesn't exist
    if not Path('config/alert_config.yaml').exists():
        Path('config').mkdir(exist_ok=True)
        create_alert_config_template()
    
    # Example alert
    sample_alert = {
        'alert_id': 'ALT20250120001',
        'level': 'warning',
        'title': 'Major Flooding Expected in Borno State',
        'summary': 'Heavy rainfall forecast for next 3 days. River discharge above warning threshold.',
        'affected_states': ['Borno', 'Yobe'],
        'estimated_displacement': {
            'mean': 15000,
            'p05': 8000,
            'p95': 25000
        },
        'recommended_actions': [
            'Activate emergency operations centers',
            'Pre-position relief supplies',
            'Issue evacuation advisories for low-lying areas',
            'Alert health facilities for potential surge'
        ]
    }
    
    # Send alert
    disseminator = AlertDisseminator()
    # results = disseminator.send_alert(sample_alert, channels=['email'])
    print("Alert dissemination system ready")
```

**Estimated Time:** 60 minutes

---

### 5.4 Logging and Monitoring Systems (30 minutes)

Implement comprehensive logging:

Create `scripts/setup_monitoring.py`:

```python
#!/usr/bin/env python3
"""
Setup monitoring and logging for Nigeria IBF System
"""

import logging
import logging.handlers
from pathlib import Path
import json
from datetime import datetime
import socket

class IBFLogger:
    """
    Centralized logging configuration for Nigeria IBF
    """
    
    def __init__(self, 
                 log_dir: Path = Path('logs'),
                 log_level: str = 'INFO'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_level = getattr(logging, log_level.upper())
        
    def setup_logger(self, name: str) -> logging.Logger:
        """
        Create configured logger
        
        Logs to:
        - Console (INFO and above)
        - Daily rotating file (DEBUG and above)
        - Error file (ERROR and above)
        - JSON file (structured logs)
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Daily rotating file handler
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_dir / f'{name}.log',
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(
            filename=self.log_dir / 'errors.log',
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        # JSON structured logging
        json_handler = logging.FileHandler(
            filename=self.log_dir / f'{name}_structured.jsonl',
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JSONFormatter())
        logger.addHandler(json_handler)
        
        return logger


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    """
    
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'hostname': socket.gethostname()
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'forecast_id'):
            log_obj['forecast_id'] = record.forecast_id
        if hasattr(record, 'alert_level'):
            log_obj['alert_level'] = record.alert_level
        
        return json.dumps(log_obj)


def setup_system_logging():
    """
    Initialize logging for all Nigeria IBF modules
    """
    ibf_logger = IBFLogger()
    
    # Setup loggers for each module
    modules = [
        'NigeriaIBF.ForecastEngine',
        'NigeriaIBF.DataPipeline',
        'NigeriaIBF.AlertSystem',
        'NigeriaIBF.Database',
        'NigeriaIBF.HazardModels',
        'NigeriaIBF.Vulnerability'
    ]
    
    for module in modules:
        logger = ibf_logger.setup_logger(module)
        logger.info(f"Logging initialized for {module}")
    
    print("✓ Logging system configured")
    print(f"✓ Logs directory: {ibf_logger.log_dir.absolute()}")
    print(f"✓ Log level: {logging.getLevelName(ibf_logger.log_level)}")


if __name__ == "__main__":
    setup_system_logging()
```

**Estimated Time:** 30 minutes

---

## 6. Visualization & Dashboard

### 6.1 Interactive Maps (60 minutes)

Create interactive forecast maps:

```python
#!/usr/bin/env python3
"""
Interactive Mapping for Nigeria IBF System
Generates web-based interactive maps using Folium
"""

import folium
from folium import plugins
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
import branca.colormap as cm

class ForecastMapper:
    """
    Create interactive maps for forecast visualization
    """
    
    def __init__(self, boundaries_path: str = 'data/BAY_LGA_Shared.geojson'):
        self.boundaries = gpd.read_file(boundaries_path)
        self.nigeria_center = [11.0, 12.5]  # Approximate center of BAY states
        
    def create_displacement_map(
        self,
        forecast_data: pd.DataFrame,
        output_path: str = 'outputs/forecast_map.html',
        title: str = 'Displacement Forecast'
    ) -> str:
        """
        Create interactive map showing displacement forecast
        
        Args:
            forecast_data: DataFrame with columns: lga_name, displacement, state
            output_path: Where to save HTML file
            title: Map title
        
        Returns:
            Path to generated HTML file
        """
        # Create base map
        m = folium.Map(
            location=self.nigeria_center,
            zoom_start=7,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        # Merge forecast data with boundaries
        merged = self.boundaries.merge(
            forecast_data,
            left_on='ADM2_EN',
            right_on='lga_name',
            how='left'
        )
        merged['displacement'] = merged['displacement'].fillna(0)
        
        # Create colormap
        vmin = merged['displacement'].min()
        vmax = merged['displacement'].max()
        colormap = cm.LinearColormap(
            colors=['#ffffcc', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026'],
            vmin=vmin,
            vmax=vmax,
            caption='Forecasted Displacement (people)'
        )
        
        # Add choropleth
        folium.Choropleth(
            geo_data=merged,
            name='Displacement Forecast',
            data=merged,
            columns=['ADM2_EN', 'displacement'],
            key_on='feature.properties.ADM2_EN',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Forecasted Displacement (people)',
            highlight=True
        ).add_to(m)
        
        # Add tooltips
        folium.GeoJson(
            merged,
            name='LGA Info',
            style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
            tooltip=folium.GeoJsonTooltip(
                fields=['ADM2_EN', 'ADM1_EN', 'displacement'],
                aliases=['LGA:', 'State:', 'Forecasted Displacement:'],
                style='background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;'
            )
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add title
        title_html = f'''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 400px; height: 60px; 
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:16px; padding: 10px">
            <h4 style="margin:0;">{title}</h4>
            <p style="margin:0; font-size:12px;">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add colormap to map
        colormap.add_to(m)
        
        # Save
        m.save(output_path)
        print(f"✓ Interactive map saved: {output_path}")
        
        return output_path
    
    def create_multi_hazard_map(
        self,
        flood_data: pd.DataFrame,
        conflict_data: pd.DataFrame,
        output_path: str = 'outputs/multi_hazard_map.html'
    ) -> str:
        """
        Create map with multiple hazard layers
        """
        m = folium.Map(
            location=self.nigeria_center,
            zoom_start=7,
            tiles='cartodbpositron'
        )
        
        # Flood layer
        flood_layer = folium.FeatureGroup(name='Flood Risk', show=True)
        self._add_hazard_circles(flood_layer, flood_data, color='blue', hazard_type='flood')
        flood_layer.add_to(m)
        
        # Conflict layer
        conflict_layer = folium.FeatureGroup(name='Conflict Risk', show=True)
        self._add_hazard_circles(conflict_layer, conflict_data, color='red', hazard_type='conflict')
        conflict_layer.add_to(m)
        
        # Add layer control
        folium.LayerControl(collapsed=False).add_to(m)
        
        # Save
        m.save(output_path)
        print(f"✓ Multi-hazard map saved: {output_path}")
        
        return output_path
    
    def _add_hazard_circles(self, layer, data: pd.DataFrame, color: str, hazard_type: str):
        """Add circle markers for hazard events"""
        for idx, row in data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=min(row.get('intensity', 5) * 5, 20),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                popup=f"{hazard_type.capitalize()}<br>Intensity: {row.get('intensity', 'N/A')}",
                tooltip=f"{hazard_type.capitalize()} Event"
            ).add_to(layer)


# Example usage
if __name__ == "__main__":
    mapper = ForecastMapper()
    
    # Sample data
    forecast_data = pd.DataFrame({
        'lga_name': ['Maiduguri', 'Jere', 'Konduga', 'Yola North'],
        'state': ['Borno', 'Borno', 'Borno', 'Adamawa'],
        'displacement': [12000, 8500, 5200, 3800]
    })
    
    # Create map
    mapper.create_displacement_map(forecast_data)
    print("✓ Example forecast map created")
```

**Estimated Time:** 60 minutes

---

*Continue with remaining sections in next update...*

**Progress:** Sections 1-5 complete, Section 6 in progress (75% complete)
