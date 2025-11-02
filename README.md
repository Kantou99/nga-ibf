# Nigeria Multi-Hazard Impact-Based Forecasting System

## ?? Overview

This Impact-Based Forecasting (IBF) system provides early warning and anticipatory action support for **Borno, Adamawa, and Yobe (BAY) States** in Nigeria. The system integrates multiple hazards (floods, displacement) with exposure and vulnerability data to generate actionable forecasts and risk assessments.

### Key Features

- **Multi-hazard analysis**: Flood and displacement risk modeling
- **Impact-based forecasts**: Estimates of people at risk and sectoral needs
- **LGA-level granularity**: 123+ LGAs with detailed risk profiles
- **Spatial analysis**: 1.5M grid points for high-resolution analysis
- **Automated reporting**: Generates forecast bulletins and visualizations
- **Prioritization framework**: Ranks LGAs for anticipatory action

---

## ?? Available Datasets

| Dataset | Records | Description |
|---------|---------|-------------|
| `nigeria_centroids_1km.hdf5` | 1.5M points | 1km resolution spatial grid |
| `exposure_nigeria_lga_aggregated.*` | LGA-level | Population exposure by LGA |
| `dtm_displacement_data_cleaned.csv` | 8,883 events | Displacement event records |
| `displacement_events_monthly.csv` | 4,576 months | Monthly displacement time-series |
| `displacement_statistics_by_lga.csv` | 123 LGAs | Vulnerability indicators |
| `nema_flood_data_cleaned.csv` | 1,029 events | Historical flood events |
| `nema_flood_risk_by_lga.csv` | 470 LGAs | Flood risk indicators |

---

## ?? Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd nga-ibf

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Setup

Place your data files in the `data/raw/` directory:

```bash
data/raw/
??? nigeria_centroids_1km.hdf5
??? exposure_nigeria_lga_aggregated.*
??? dtm_displacement_data_cleaned.csv
??? displacement_events_monthly.csv
??? displacement_statistics_by_lga.csv
??? nema_flood_data_cleaned.csv
??? nema_flood_risk_by_lga.csv
```

### 3. Run the Pipeline

```bash
# Run the complete IBF pipeline
python main.py
```

This will:
1. Load and preprocess all datasets
2. Analyze hazards (flood, displacement)
3. Calculate multi-hazard impacts
4. Generate forecasts and prioritization
5. Create visualizations and reports
6. Export results to `data/outputs/`

---

## ?? Project Structure

```
nga-ibf/
??? data/
?   ??? raw/              # Input datasets (place your data here)
?   ??? processed/        # Cleaned and processed data
?   ??? outputs/          # Generated forecasts, maps, reports
?
??? src/
?   ??? data_processing/
?   ?   ??? data_loader.py       # Load datasets
?   ?   ??? preprocessor.py      # Clean and validate data
?   ?   ??? spatial_processor.py # Spatial operations
?   ?
?   ??? hazard_models/
?   ?   ??? flood_model.py       # Flood hazard analysis
?   ?   ??? displacement_model.py # Displacement risk modeling
?   ?
?   ??? risk_assessment/
?   ?   ??? impact_calculator.py # Calculate impacts and prioritize
?   ?
?   ??? visualization/
?       ??? mapping.py           # Create maps and dashboards
?       ??? reporting.py         # Generate bulletins and reports
?
??? notebooks/
?   ??? 01_data_exploration.ipynb # Interactive data exploration
?
??? config/
?   ??? config.yaml              # Configuration settings
?
??? main.py                      # Main pipeline script
??? requirements.txt             # Python dependencies
??? README.md                    # This file
```

---

## ?? Usage Examples

### Running the Main Pipeline

```bash
python main.py
```

### Using Individual Modules

```python
from src.data_processing.data_loader import DataLoader
from src.hazard_models.flood_model import FloodModel

# Load data
loader = DataLoader(data_dir='data/raw')
flood_events = loader.load_flood_events()

# Analyze flood risk
flood_model = FloodModel()
flood_model.load_historical_data(flood_events, flood_risk)
forecasts = flood_model.generate_forecast_bulletin(
    forecast_date=datetime.now(),
    lga_list=['Maiduguri', 'Yola North', 'Damaturu']
)
```

### Interactive Analysis with Jupyter

```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

---

## ?? Outputs

The system generates the following outputs in `data/outputs/`:

### Reports
- **`forecast_bulletin.txt`**: Text bulletin with executive summary and recommendations
- **`impact_forecasts_*.csv`**: LGA-level impact forecasts
- **`flood_risk_scores_*.csv`**: Flood risk scores by LGA
- **`displacement_hotspots_*.csv`**: Displacement hotspot rankings

### Visualizations
- **`flood_risk_map.png`**: Choropleth map of flood risk
- **`impact_dashboard.png`**: Multi-panel dashboard with key metrics
- **`displacement_trends.png`**: Time series of displacement patterns

### Logs
- **`ibf_run_*.log`**: Detailed execution logs

---

## ?? Key Capabilities

### 1. Hazard Analysis

**Flood Model**
- Historical flood frequency analysis
- Seasonal pattern identification
- Probability-based forecasting
- Alert level generation (Green/Yellow/Orange/Red)

**Displacement Model**
- Hotspot identification
- Trend analysis
- Vulnerability assessment
- Early warning generation

### 2. Impact Assessment

- **People at Risk**: Estimates population exposure by LGA
- **Sectoral Needs**: Health, Shelter, WASH, Food, Protection
- **Multi-hazard Integration**: Combined risk from multiple hazards
- **Prioritization**: Ranks LGAs for response planning

### 3. Visualization & Reporting

- Interactive maps and dashboards
- Automated forecast bulletins
- LGA risk profiles
- Time series analysis

---

## ?? Configuration

Modify `config/config.yaml` to customize:

- Data file paths
- Geographic bounds
- Alert/risk thresholds
- Sectoral impact ratios
- Visualization settings
- Output formats

Example:

```yaml
hazards:
  flood:
    enabled: true
    forecast_horizon_days: 30
    alert_levels:
      green: [0.0, 0.2]
      yellow: [0.2, 0.4]
      orange: [0.4, 0.7]
      red: [0.7, 1.0]
```

---

## ?? Methodology

### Risk Formula

```
Risk = Hazard ? Exposure ? Vulnerability
```

Where:
- **Hazard**: Probability of event occurrence (0-1)
- **Exposure**: Population in affected area
- **Vulnerability**: Susceptibility to impact (0-1)

### Impact Calculation

```
People at Risk = Population ? Hazard Probability ? Vulnerability Factor
```

### Prioritization Score

Combines:
- People at risk (normalized)
- Hazard probability (normalized)
- Vulnerability index (normalized)
- Historical impact (normalized)

---

## ?? Requirements

### Python Version
- Python 3.8 or higher

### Key Dependencies
- **pandas** (?1.5.0): Data manipulation
- **numpy** (?1.23.0): Numerical computing
- **geopandas** (?0.12.0): Geospatial operations
- **matplotlib** (?3.6.0): Visualization
- **h5py** (?3.7.0): HDF5 file handling
- **scipy** (?1.9.0): Scientific computing

See `requirements.txt` for complete list.

---

## ??? Focus Area: BAY States

The system focuses on three states in Northeast Nigeria:

- **Borno State**: 27 LGAs
- **Adamawa State**: 21 LGAs  
- **Yobe State**: 17 LGAs

These states face multiple humanitarian challenges including:
- Seasonal flooding (April-October)
- Conflict-induced displacement
- Food insecurity
- Limited infrastructure

---

## ?? Data Processing Workflow

```mermaid
graph LR
    A[Raw Data] --> B[Data Loading]
    B --> C[Preprocessing]
    C --> D[Hazard Analysis]
    D --> E[Impact Assessment]
    E --> F[Prioritization]
    F --> G[Reporting]
    G --> H[Outputs]
```

1. **Data Loading**: Import datasets from multiple sources
2. **Preprocessing**: Clean, validate, filter for BAY states
3. **Hazard Analysis**: Calculate flood and displacement risk
4. **Impact Assessment**: Estimate people at risk and sectoral needs
5. **Prioritization**: Rank LGAs for anticipatory action
6. **Reporting**: Generate bulletins, maps, and dashboards
7. **Outputs**: Save results for decision-makers

---

## ??? Troubleshooting

### Missing Data Files

If you get "File not found" errors:
1. Check that data files are in `data/raw/` directory
2. Verify file names match configuration in `config/config.yaml`
3. Ensure you have read permissions

### Import Errors

If modules can't be imported:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Python version
python --version  # Should be 3.8+
```

### Memory Issues

For large datasets:
1. Process one state at a time
2. Reduce grid resolution in config
3. Use data chunking for large files

---

## ?? Documentation

### For Analysts

- **Quick Reference**: See code comments in each module
- **Jupyter Notebooks**: Step-by-step analysis in `notebooks/`
- **Configuration Guide**: Modify `config/config.yaml`

### For Developers

- **Code Structure**: Modular design with clear separation of concerns
- **Adding Hazards**: Create new model in `src/hazard_models/`
- **Custom Indicators**: Extend `impact_calculator.py`
- **Testing**: Add tests in `tests/` directory

---

## ?? Contributing

To contribute to this project:

1. Create a feature branch
2. Make your changes
3. Add tests if applicable
4. Update documentation
5. Submit a pull request

---

## ?? Citation

If you use this system in your work, please cite:

```
Nigeria Multi-Hazard Impact-Based Forecasting System
Version 1.0.0
Focus: Borno, Adamawa, and Yobe States
Year: 2025
```

---

## ?? Contact & Support

For questions, issues, or collaboration:

- **Issues**: Open an issue on GitHub
- **Email**: [Your contact email]
- **Documentation**: See Wiki for detailed guides

---

## ?? Version History

### Version 1.0.0 (2025)
- Initial release
- Multi-hazard forecasting (flood, displacement)
- LGA-level impact assessment
- Automated reporting and visualization
- Support for BAY states

---

## ?? License

[Specify your license here]

---

## ?? Acknowledgments

This system integrates data from:
- **DTM (Displacement Tracking Matrix)**: Displacement data
- **NEMA (National Emergency Management Agency)**: Flood event data
- **GRID3**: Population and infrastructure data
- **Local partners**: Ground truth and validation

---

## ?? Training Resources

### Getting Started
1. Read this README
2. Review `config/config.yaml`
3. Run `python main.py` with sample data
4. Explore notebooks in `notebooks/`

### Advanced Usage
1. Customize hazard models
2. Integrate new data sources
3. Develop custom indicators
4. Create specialized reports

---

**Ready to start? Run `python main.py` to generate your first forecast!** ??
