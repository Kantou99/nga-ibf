"""
Data Loader Module
Handles loading and initial processing of all datasets
"""

import pandas as pd
import numpy as np
import h5py
from pathlib import Path
from typing import Dict, Optional, Tuple
import geopandas as gpd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Load and manage all IBF datasets"""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_cache = {}
        
    def load_centroids(self, filepath: Optional[str] = None) -> Dict:
        """
        Load Nigeria centroids from HDF5 file (1.5M grid points)
        
        Returns:
            Dictionary containing lat, lon, and grid metadata
        """
        if filepath is None:
            filepath = self.data_dir / "nigeria_centroids_1km.hdf5"
        
        logger.info(f"Loading centroids from {filepath}")
        
        try:
            with h5py.File(filepath, 'r') as f:
                centroids = {
                    'lat': f['lat'][:] if 'lat' in f else None,
                    'lon': f['lon'][:] if 'lon' in f else None,
                    'metadata': dict(f.attrs) if f.attrs else {}
                }
                
                # Log available datasets
                logger.info(f"Available datasets: {list(f.keys())}")
                
            logger.info(f"Loaded {len(centroids.get('lat', []))} grid points")
            self.data_cache['centroids'] = centroids
            return centroids
            
        except Exception as e:
            logger.error(f"Error loading centroids: {e}")
            raise
    
    def load_exposure_data(self, filepath: Optional[str] = None) -> gpd.GeoDataFrame:
        """
        Load LGA-level population exposure data
        
        Returns:
            GeoDataFrame with LGA-level exposure information
        """
        if filepath is None:
            # Try multiple possible formats
            for ext in ['.shp', '.geojson', '.gpkg', '.csv']:
                potential_file = self.data_dir / f"exposure_nigeria_lga_aggregated{ext}"
                if potential_file.exists():
                    filepath = potential_file
                    break
        
        logger.info(f"Loading exposure data from {filepath}")
        
        try:
            if str(filepath).endswith('.csv'):
                df = pd.read_csv(filepath)
                logger.info(f"Loaded exposure data: {df.shape[0]} LGAs")
            else:
                df = gpd.read_file(filepath)
                logger.info(f"Loaded exposure geodata: {df.shape[0]} LGAs")
            
            self.data_cache['exposure'] = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading exposure data: {e}")
            raise
    
    def load_displacement_data(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load DTM displacement event data (8,883 events)
        
        Returns:
            DataFrame with displacement event records
        """
        if filepath is None:
            filepath = self.data_dir / "dtm_displacement_data_cleaned.csv"
        
        logger.info(f"Loading displacement data from {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            # Convert date columns if they exist
            date_columns = ['date', 'Date', 'event_date', 'report_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            logger.info(f"Loaded {len(df)} displacement events")
            self.data_cache['displacement'] = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading displacement data: {e}")
            raise
    
    def load_displacement_monthly(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load monthly displacement time-series (4,576 records)
        
        Returns:
            DataFrame with monthly aggregated displacement data
        """
        if filepath is None:
            filepath = self.data_dir / "displacement_events_monthly.csv"
        
        logger.info(f"Loading monthly displacement data from {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            # Convert date columns
            date_columns = ['month', 'date', 'period']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    break
            
            logger.info(f"Loaded {len(df)} monthly records")
            self.data_cache['displacement_monthly'] = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading monthly displacement data: {e}")
            raise
    
    def load_displacement_statistics(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load LGA-level displacement statistics (123 LGAs)
        
        Returns:
            DataFrame with vulnerability indicators by LGA
        """
        if filepath is None:
            filepath = self.data_dir / "displacement_statistics_by_lga.csv"
        
        logger.info(f"Loading displacement statistics from {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded statistics for {len(df)} LGAs")
            self.data_cache['displacement_stats'] = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading displacement statistics: {e}")
            raise
    
    def load_flood_events(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load NEMA flood event data (1,029 events)
        
        Returns:
            DataFrame with flood event records
        """
        if filepath is None:
            filepath = self.data_dir / "nema_flood_data_cleaned.csv"
        
        logger.info(f"Loading flood event data from {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            # Convert date columns
            date_columns = ['date', 'Date', 'event_date', 'report_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            logger.info(f"Loaded {len(df)} flood events")
            self.data_cache['flood_events'] = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading flood event data: {e}")
            raise
    
    def load_flood_risk(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load LGA-level flood risk data (470 LGAs)
        
        Returns:
            DataFrame with flood risk indicators by LGA
        """
        if filepath is None:
            filepath = self.data_dir / "nema_flood_risk_by_lga.csv"
        
        logger.info(f"Loading flood risk data from {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded flood risk for {len(df)} LGAs")
            self.data_cache['flood_risk'] = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading flood risk data: {e}")
            raise
    
    def load_all_data(self) -> Dict:
        """
        Load all available datasets
        
        Returns:
            Dictionary containing all loaded datasets
        """
        logger.info("Loading all datasets...")
        
        datasets = {}
        
        try:
            datasets['centroids'] = self.load_centroids()
        except Exception as e:
            logger.warning(f"Could not load centroids: {e}")
        
        try:
            datasets['exposure'] = self.load_exposure_data()
        except Exception as e:
            logger.warning(f"Could not load exposure data: {e}")
        
        try:
            datasets['displacement'] = self.load_displacement_data()
        except Exception as e:
            logger.warning(f"Could not load displacement data: {e}")
        
        try:
            datasets['displacement_monthly'] = self.load_displacement_monthly()
        except Exception as e:
            logger.warning(f"Could not load monthly displacement data: {e}")
        
        try:
            datasets['displacement_stats'] = self.load_displacement_statistics()
        except Exception as e:
            logger.warning(f"Could not load displacement statistics: {e}")
        
        try:
            datasets['flood_events'] = self.load_flood_events()
        except Exception as e:
            logger.warning(f"Could not load flood events: {e}")
        
        try:
            datasets['flood_risk'] = self.load_flood_risk()
        except Exception as e:
            logger.warning(f"Could not load flood risk data: {e}")
        
        logger.info(f"Successfully loaded {len(datasets)} datasets")
        return datasets
    
    def filter_bay_states(self, df: pd.DataFrame, state_column: str = 'State') -> pd.DataFrame:
        """
        Filter data for Borno, Adamawa, and Yobe (BAY) states
        
        Args:
            df: DataFrame to filter
            state_column: Name of the state column
            
        Returns:
            Filtered DataFrame
        """
        bay_states = ['Borno', 'Adamawa', 'Yobe']
        
        if state_column not in df.columns:
            # Try alternative column names
            for col in ['state', 'STATE', 'admin1', 'State_Name']:
                if col in df.columns:
                    state_column = col
                    break
            else:
                logger.warning(f"State column not found in DataFrame. Available columns: {df.columns.tolist()}")
                return df
        
        filtered = df[df[state_column].isin(bay_states)]
        logger.info(f"Filtered to BAY states: {len(filtered)} records from {len(df)}")
        
        return filtered
    
    def get_data_summary(self) -> pd.DataFrame:
        """
        Get summary statistics for all loaded datasets
        
        Returns:
            DataFrame with dataset summaries
        """
        summary_data = []
        
        for name, data in self.data_cache.items():
            if isinstance(data, pd.DataFrame):
                summary_data.append({
                    'Dataset': name,
                    'Records': len(data),
                    'Columns': len(data.columns),
                    'Memory (MB)': data.memory_usage(deep=True).sum() / 1e6
                })
            elif isinstance(data, dict):
                summary_data.append({
                    'Dataset': name,
                    'Records': len(data.get('lat', [])),
                    'Columns': len(data.keys()),
                    'Memory (MB)': 'N/A'
                })
        
        return pd.DataFrame(summary_data)


if __name__ == "__main__":
    # Example usage
    loader = DataLoader()
    data = loader.load_all_data()
    print(loader.get_data_summary())
