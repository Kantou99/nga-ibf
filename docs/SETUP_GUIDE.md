# Setup Guide for Nigeria IBF System

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended for large datasets)
- **Disk Space**: At least 5GB free space

### Required Software
1. **Python 3.8+**: [Download here](https://www.python.org/downloads/)
2. **Git**: [Download here](https://git-scm.com/downloads)
3. **Text Editor/IDE**: VS Code (recommended), PyCharm, or Jupyter

---

## Step-by-Step Installation

### 1. Clone or Download the Repository

**Option A: Using Git**
```bash
git clone <repository-url>
cd nga-ibf
```

**Option B: Download ZIP**
1. Download the ZIP file
2. Extract to your desired location
3. Open terminal/command prompt in the extracted folder

### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: This may take 5-10 minutes depending on your internet connection.

### 4. Verify Installation

```bash
python -c "import pandas, numpy, geopandas, matplotlib; print('All dependencies installed successfully!')"
```

If you see "All dependencies installed successfully!", you're ready to proceed.

---

## Data Setup

### 1. Create Data Directory Structure

The directories are already created, but verify they exist:

```bash
ls data/raw
ls data/processed
ls data/outputs
```

### 2. Place Your Data Files

Copy your data files to `data/raw/`:

```
data/raw/
??? nigeria_centroids_1km.hdf5
??? exposure_nigeria_lga_aggregated.shp (or .csv, .geojson, .gpkg)
??? dtm_displacement_data_cleaned.csv
??? displacement_events_monthly.csv
??? displacement_statistics_by_lga.csv
??? nema_flood_data_cleaned.csv
??? nema_flood_risk_by_lga.csv
```

### 3. Verify Data Files

```bash
python -c "import os; print('Files:', os.listdir('data/raw'))"
```

---

## Configuration

### 1. Review Configuration File

Open `config/config.yaml` and review the settings:

```yaml
data:
  raw_dir: "data/raw"
  processed_dir: "data/processed"
  output_dir: "data/outputs"
```

### 2. Customize Settings (Optional)

You can modify:
- Alert thresholds
- Risk level boundaries
- Color schemes
- Output formats

**Example**: Change flood alert levels:
```yaml
hazards:
  flood:
    alert_levels:
      green: [0.0, 0.3]    # Changed from 0.2
      yellow: [0.3, 0.5]   # Changed from 0.4
      orange: [0.5, 0.8]   # Changed from 0.7
      red: [0.8, 1.0]
```

---

## Running Your First Forecast

### 1. Test Run

```bash
python main.py
```

This will:
1. Load your data
2. Process and analyze
3. Generate forecasts
4. Create visualizations
5. Save outputs to `data/outputs/`

### 2. Check Outputs

Look in `data/outputs/` for:
- `forecast_bulletin.txt`
- `impact_forecasts_*.csv`
- `*.png` (maps and charts)
- `*.log` (execution logs)

### 3. Review the Bulletin

```bash
# On Windows
type data\outputs\forecast_bulletin.txt

# On macOS/Linux
cat data/outputs/forecast_bulletin.txt
```

---

## Working with Jupyter Notebooks

### 1. Start Jupyter

```bash
jupyter notebook
```

This will open Jupyter in your web browser.

### 2. Open Data Exploration Notebook

Navigate to:
```
notebooks/01_data_exploration.ipynb
```

### 3. Run Cells

Press `Shift + Enter` to run each cell sequentially.

---

## VS Code Setup (Recommended)

### 1. Install VS Code

Download from: https://code.visualstudio.com/

### 2. Install Python Extension

1. Open VS Code
2. Click Extensions icon (or `Ctrl+Shift+X`)
3. Search for "Python"
4. Install the official Python extension by Microsoft

### 3. Open Project

```
File > Open Folder > Select nga-ibf folder
```

### 4. Select Python Interpreter

1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose the virtual environment (`venv`)

### 5. Run Code

- Open `main.py`
- Right-click and select "Run Python File in Terminal"
- Or press `F5` to run in debug mode

---

## Troubleshooting

### Issue: Module Not Found Error

**Error**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**:
```bash
# Make sure venv is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Data File Not Found

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'data/raw/...'`

**Solution**:
1. Check file is in `data/raw/` directory
2. Check filename matches exactly (case-sensitive)
3. Verify file permissions

### Issue: HDF5 File Error

**Error**: `OSError: Unable to open file`

**Solution**:
```bash
# Reinstall h5py
pip install --upgrade h5py

# Test HDF5 file
python -c "import h5py; f = h5py.File('data/raw/nigeria_centroids_1km.hdf5', 'r'); print(list(f.keys()))"
```

### Issue: Memory Error

**Error**: `MemoryError`

**Solution**:
1. Close other applications
2. Process one state at a time
3. Reduce data in memory:
   ```python
   # In your code
   loader = DataLoader()
   datasets = loader.load_all_data()
   
   # Process each dataset separately
   del datasets['centroids']  # Free up memory
   ```

### Issue: Geopandas Installation Fails

**Windows Users**:
```bash
# Install from conda-forge
conda install -c conda-forge geopandas

# Or use pre-built wheels
pip install pipwin
pipwin install gdal
pipwin install fiona
pipwin install geopandas
```

---

## Performance Optimization

### 1. For Large Datasets

Edit `main.py` to process fewer LGAs:
```python
# Limit to top 50 LGAs
lga_list = flood_risk_scores['lga'].unique().tolist()[:50]
```

### 2. Disable Visualization

If visualization is slow:
```python
# Comment out visualization section
# visualizer.create_risk_map(...)
```

### 3. Use Multiprocessing

For advanced users, enable parallel processing:
```python
from multiprocessing import Pool

with Pool(processes=4) as pool:
    results = pool.map(process_lga, lga_list)
```

---

## Next Steps

1. ? **Verify installation** - Run `python main.py`
2. ? **Explore data** - Open Jupyter notebook
3. ? **Review outputs** - Check `data/outputs/`
4. ? **Customize** - Modify `config/config.yaml`
5. ? **Learn more** - Read main README.md

---

## Getting Help

### Documentation
- **Main README**: Project overview and usage
- **Code Comments**: Detailed in each module
- **Jupyter Notebooks**: Interactive tutorials

### Support Channels
- Open an issue on GitHub
- Email: [Your contact]
- Join discussion forum

### Common Resources
- **Pandas Tutorial**: https://pandas.pydata.org/docs/
- **Geopandas Guide**: https://geopandas.org/
- **Matplotlib Examples**: https://matplotlib.org/stable/gallery/

---

## Checklist

Before running the system, ensure:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Data files in `data/raw/` directory
- [ ] Configuration reviewed (`config/config.yaml`)
- [ ] Test run successful (`python main.py`)

**All checked? You're ready to generate forecasts! ??**
