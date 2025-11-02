"""
Main Pipeline for Nigeria Multi-Hazard Impact-Based Forecasting
Run this script to execute the complete IBF workflow
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_processing.data_loader import DataLoader
from data_processing.preprocessor import DataPreprocessor
from data_processing.spatial_processor import SpatialProcessor
from hazard_models.flood_model import FloodModel
from hazard_models.displacement_model import DisplacementModel
from risk_assessment.impact_calculator import ImpactCalculator
from visualization.mapping import MapVisualizer
from visualization.reporting import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'data/outputs/ibf_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main IBF pipeline execution"""
    
    logger.info("=" * 80)
    logger.info("NIGERIA MULTI-HAZARD IMPACT-BASED FORECASTING SYSTEM")
    logger.info("=" * 80)
    
    # 1. Load Data
    logger.info("\n[STEP 1] Loading data...")
    loader = DataLoader(data_dir="data/raw")
    
    try:
        datasets = loader.load_all_data()
        logger.info(f"Successfully loaded {len(datasets)} datasets")
        print("\nData Summary:")
        print(loader.get_data_summary())
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        logger.info("Please ensure your data files are in the data/raw directory")
        return
    
    # 2. Preprocess Data
    logger.info("\n[STEP 2] Preprocessing data...")
    preprocessor = DataPreprocessor()
    
    # Filter for BAY states
    if 'exposure' in datasets:
        datasets['exposure_bay'] = loader.filter_bay_states(datasets['exposure'])
    
    if 'displacement' in datasets:
        datasets['displacement_clean'] = preprocessor.clean_displacement_data(
            loader.filter_bay_states(datasets['displacement'])
        )
    
    if 'flood_events' in datasets:
        datasets['flood_events_clean'] = preprocessor.clean_flood_data(
            loader.filter_bay_states(datasets['flood_events'])
        )
    
    # 3. Hazard Analysis
    logger.info("\n[STEP 3] Analyzing hazards...")
    
    # Flood Model
    if 'flood_events_clean' in datasets and 'flood_risk' in datasets:
        flood_model = FloodModel()
        flood_model.load_historical_data(
            datasets['flood_events_clean'],
            datasets['flood_risk']
        )
        
        # Calculate flood frequency
        flood_frequency = flood_model.calculate_flood_frequency(datasets['flood_events_clean'])
        
        # Calculate flood risk scores
        flood_risk_scores = flood_model.calculate_flood_risk_score(flood_frequency)
        
        # Generate forecasts for next month
        lga_list = flood_risk_scores['lga'].unique().tolist()
        forecast_date = datetime.now()
        flood_forecasts = flood_model.generate_forecast_bulletin(
            forecast_date, lga_list[:50], datasets['flood_events_clean']  # Limit to 50 for demo
        )
        
        logger.info(f"Generated flood forecasts for {len(flood_forecasts)} LGAs")
        datasets['flood_forecasts'] = flood_forecasts
        datasets['flood_risk_scores'] = flood_risk_scores
    
    # Displacement Model
    if all(k in datasets for k in ['displacement_clean', 'displacement_monthly', 'displacement_stats']):
        disp_model = DisplacementModel()
        disp_model.load_data(
            datasets['displacement_clean'],
            datasets['displacement_monthly'],
            datasets['displacement_stats']
        )
        
        # Analyze trends
        if 'displacement_monthly' in datasets:
            trends = disp_model.analyze_displacement_trends(datasets['displacement_monthly'])
            logger.info(f"Displacement trends: {trends.get('trend_direction', 'Unknown')}")
        
        # Calculate hotspots
        hotspots = disp_model.calculate_displacement_hotspots(datasets['displacement_clean'])
        
        # Calculate vulnerability
        vulnerability = disp_model.calculate_vulnerability_index(datasets['displacement_stats'])
        
        logger.info(f"Identified {len(hotspots)} displacement hotspots")
        datasets['displacement_hotspots'] = hotspots
        datasets['displacement_vulnerability'] = vulnerability
    
    # 4. Impact Assessment
    logger.info("\n[STEP 4] Calculating impacts...")
    
    impact_calculator = ImpactCalculator()
    
    if 'exposure_bay' in datasets:
        impact_calculator.load_data(
            exposure=datasets['exposure_bay'],
            vulnerability=datasets.get('displacement_vulnerability'),
            hazard=datasets.get('flood_forecasts')
        )
        
        # Generate impact forecasts
        if 'flood_forecasts' in datasets:
            impact_forecasts = impact_calculator.generate_impact_forecast(
                lga_list=datasets['flood_forecasts']['lga'].unique().tolist(),
                forecast_period='Next 30 days',
                hazard_forecasts=datasets['flood_forecasts'].rename(columns={'alert_level': 'hazard_type'})
            )
            
            # Prioritize LGAs
            prioritized = impact_calculator.prioritize_lgas(impact_forecasts)
            
            logger.info(f"Generated impact forecasts for {len(prioritized)} LGAs")
            datasets['impact_forecasts'] = prioritized
    
    # 5. Visualization
    logger.info("\n[STEP 5] Creating visualizations...")
    
    visualizer = MapVisualizer()
    
    if 'flood_risk_scores' in datasets:
        try:
            visualizer.create_risk_map(
                datasets['flood_risk_scores'],
                risk_column='flood_risk_score',
                title='Nigeria Flood Risk Map (BAY States)',
                output_file='data/outputs/flood_risk_map.png'
            )
        except Exception as e:
            logger.warning(f"Could not create risk map: {e}")
    
    if 'impact_forecasts' in datasets:
        try:
            visualizer.create_impact_dashboard(
                datasets['impact_forecasts'],
                output_file='data/outputs/impact_dashboard.png'
            )
        except Exception as e:
            logger.warning(f"Could not create dashboard: {e}")
    
    if 'displacement_monthly' in datasets:
        try:
            date_col = 'month' if 'month' in datasets['displacement_monthly'].columns else 'date'
            disp_cols = [col for col in datasets['displacement_monthly'].columns 
                        if 'displaced' in col.lower() or 'individuals' in col.lower()]
            
            if disp_cols:
                visualizer.create_time_series_plot(
                    datasets['displacement_monthly'],
                    date_col=date_col,
                    value_col=disp_cols[0],
                    title='Displacement Trends Over Time (BAY States)',
                    output_file='data/outputs/displacement_trends.png'
                )
        except Exception as e:
            logger.warning(f"Could not create time series plot: {e}")
    
    # 6. Generate Reports
    logger.info("\n[STEP 6] Generating reports...")
    
    reporter = ReportGenerator()
    
    if 'impact_forecasts' in datasets and 'flood_forecasts' in datasets:
        bulletin = reporter.generate_forecast_bulletin(
            impact_forecasts=datasets['impact_forecasts'],
            hazard_forecasts=datasets['flood_forecasts'],
            forecast_date=datetime.now(),
            output_file='data/outputs/forecast_bulletin.txt'
        )
        
        print("\n" + "=" * 80)
        print("FORECAST BULLETIN PREVIEW")
        print("=" * 80)
        print(bulletin[:1000] + "\n... (see full bulletin in data/outputs/forecast_bulletin.txt)")
    
    # Export processed data
    if 'impact_forecasts' in datasets:
        reporter.export_to_csv(datasets['impact_forecasts'], 'impact_forecasts')
    
    if 'flood_risk_scores' in datasets:
        reporter.export_to_csv(datasets['flood_risk_scores'], 'flood_risk_scores')
    
    if 'displacement_hotspots' in datasets:
        reporter.export_to_csv(datasets['displacement_hotspots'], 'displacement_hotspots')
    
    logger.info("\n" + "=" * 80)
    logger.info("IBF PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info("\nOutputs saved to: data/outputs/")
    logger.info("Check the following files:")
    logger.info("  - forecast_bulletin.txt")
    logger.info("  - impact_forecasts_*.csv")
    logger.info("  - flood_risk_scores_*.csv")
    logger.info("  - *.png (visualizations)")


if __name__ == "__main__":
    main()
