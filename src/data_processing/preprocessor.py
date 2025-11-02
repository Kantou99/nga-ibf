"""
Data Preprocessing Module
Cleans, validates, and prepares data for analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocess and validate IBF datasets"""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_coordinates(self, df: pd.DataFrame, 
                           lat_col: str = 'latitude', 
                           lon_col: str = 'longitude') -> pd.DataFrame:
        """
        Validate and clean geographic coordinates
        
        Args:
            df: DataFrame with coordinate columns
            lat_col: Name of latitude column
            lon_col: Name of longitude column
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Validating coordinates...")
        
        initial_count = len(df)
        
        # Check if columns exist
        if lat_col not in df.columns or lon_col not in df.columns:
            logger.warning(f"Coordinate columns not found: {lat_col}, {lon_col}")
            return df
        
        # Remove invalid coordinates
        df = df.copy()
        df = df[df[lat_col].notna() & df[lon_col].notna()]
        df = df[(df[lat_col] >= -90) & (df[lat_col] <= 90)]
        df = df[(df[lon_col] >= -180) & (df[lon_col] <= 180)]
        
        # Nigeria bounding box filter (approximate)
        # Nigeria: lat 4-14?N, lon 3-15?E
        df = df[(df[lat_col] >= 4) & (df[lat_col] <= 14)]
        df = df[(df[lon_col] >= 3) & (df[lon_col] <= 15)]
        
        removed = initial_count - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} records with invalid coordinates")
        
        return df
    
    def clean_displacement_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize displacement event data
        
        Args:
            df: Raw displacement DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning displacement data...")
        
        df = df.copy()
        initial_count = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Standardize column names
        column_mapping = {
            'State': 'state',
            'LGA': 'lga',
            'Location': 'location',
            'Date': 'date',
            'Individuals': 'individuals_displaced',
            'Families': 'families_displaced',
            'Households': 'households_displaced'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Clean numeric columns
        numeric_cols = ['individuals_displaced', 'families_displaced', 'households_displaced']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        
        # Remove records with no displacement
        if 'individuals_displaced' in df.columns:
            df = df[df['individuals_displaced'] > 0]
        
        logger.info(f"Cleaned displacement data: {len(df)}/{initial_count} records retained")
        
        return df
    
    def clean_flood_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize flood event data
        
        Args:
            df: Raw flood DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning flood data...")
        
        df = df.copy()
        initial_count = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Standardize column names
        column_mapping = {
            'State': 'state',
            'LGA': 'lga',
            'Date': 'date',
            'Deaths': 'deaths',
            'Injured': 'injured',
            'Affected': 'people_affected',
            'Houses_Destroyed': 'houses_destroyed',
            'Houses_Damaged': 'houses_damaged'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Clean numeric columns
        numeric_cols = ['deaths', 'injured', 'people_affected', 'houses_destroyed', 'houses_damaged']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        
        logger.info(f"Cleaned flood data: {len(df)}/{initial_count} records retained")
        
        return df
    
    def aggregate_to_lga(self, df: pd.DataFrame, 
                        value_cols: List[str],
                        group_col: str = 'lga',
                        agg_func: str = 'sum') -> pd.DataFrame:
        """
        Aggregate data to LGA level
        
        Args:
            df: DataFrame to aggregate
            value_cols: Columns to aggregate
            group_col: Column to group by (default: 'lga')
            agg_func: Aggregation function ('sum', 'mean', 'max', etc.)
            
        Returns:
            Aggregated DataFrame
        """
        logger.info(f"Aggregating data to LGA level using {agg_func}...")
        
        if group_col not in df.columns:
            logger.error(f"Group column '{group_col}' not found")
            return df
        
        # Filter to valid value columns
        valid_cols = [col for col in value_cols if col in df.columns]
        
        if not valid_cols:
            logger.warning("No valid value columns found for aggregation")
            return df
        
        # Create aggregation dictionary
        agg_dict = {col: agg_func for col in valid_cols}
        
        # Add state if available
        group_cols = [group_col]
        if 'state' in df.columns:
            group_cols = ['state', group_col]
        
        aggregated = df.groupby(group_cols, as_index=False).agg(agg_dict)
        
        logger.info(f"Aggregated to {len(aggregated)} LGA records")
        
        return aggregated
    
    def create_time_series(self, df: pd.DataFrame,
                          date_col: str = 'date',
                          freq: str = 'M',
                          value_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create time series data at specified frequency
        
        Args:
            df: DataFrame with date column
            date_col: Name of date column
            freq: Frequency for resampling ('D', 'W', 'M', 'Y')
            value_cols: Columns to aggregate (if None, aggregates all numeric columns)
            
        Returns:
            Time series DataFrame
        """
        logger.info(f"Creating time series with frequency {freq}...")
        
        if date_col not in df.columns:
            logger.error(f"Date column '{date_col}' not found")
            return df
        
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df[df[date_col].notna()]
        
        # Set date as index
        df = df.set_index(date_col)
        
        # Select columns to aggregate
        if value_cols is None:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        else:
            value_cols = [col for col in value_cols if col in df.columns]
        
        # Resample
        ts = df[value_cols].resample(freq).sum()
        ts = ts.reset_index()
        
        logger.info(f"Created time series with {len(ts)} periods")
        
        return ts
    
    def calculate_vulnerability_index(self, 
                                     displacement_stats: pd.DataFrame,
                                     flood_risk: pd.DataFrame,
                                     exposure: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite vulnerability index for each LGA
        
        Args:
            displacement_stats: LGA-level displacement statistics
            flood_risk: LGA-level flood risk
            exposure: LGA-level population exposure
            
        Returns:
            DataFrame with vulnerability indices
        """
        logger.info("Calculating vulnerability index...")
        
        # Merge datasets
        vulnerability = displacement_stats.copy()
        
        # Merge with flood risk
        if 'lga' in flood_risk.columns and 'lga' in vulnerability.columns:
            vulnerability = vulnerability.merge(
                flood_risk, on='lga', how='left', suffixes=('', '_flood')
            )
        
        # Merge with exposure
        if 'lga' in exposure.columns and 'lga' in vulnerability.columns:
            vulnerability = vulnerability.merge(
                exposure, on='lga', how='left', suffixes=('', '_exposure')
            )
        
        # Normalize indicators (0-1 scale)
        def normalize(series):
            if series.std() == 0:
                return series
            return (series - series.min()) / (series.max() - series.min())
        
        # Calculate composite vulnerability (customize based on available columns)
        numeric_cols = vulnerability.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            normalized_data = vulnerability[numeric_cols].apply(normalize)
            vulnerability['vulnerability_index'] = normalized_data.mean(axis=1)
            
            # Classify vulnerability levels
            vulnerability['vulnerability_level'] = pd.cut(
                vulnerability['vulnerability_index'],
                bins=[0, 0.25, 0.5, 0.75, 1.0],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        
        logger.info(f"Calculated vulnerability index for {len(vulnerability)} LGAs")
        
        return vulnerability
    
    def merge_datasets(self, datasets: Dict[str, pd.DataFrame], 
                      join_key: str = 'lga') -> pd.DataFrame:
        """
        Merge multiple datasets on a common key
        
        Args:
            datasets: Dictionary of DataFrames to merge
            join_key: Column to join on
            
        Returns:
            Merged DataFrame
        """
        logger.info(f"Merging {len(datasets)} datasets on '{join_key}'...")
        
        merged = None
        
        for name, df in datasets.items():
            if join_key not in df.columns:
                logger.warning(f"Join key '{join_key}' not found in {name}, skipping")
                continue
            
            if merged is None:
                merged = df
            else:
                merged = merged.merge(df, on=join_key, how='outer', suffixes=('', f'_{name}'))
        
        if merged is not None:
            logger.info(f"Merged dataset has {len(merged)} records and {len(merged.columns)} columns")
        
        return merged
    
    def export_processed_data(self, df: pd.DataFrame, 
                            filename: str,
                            output_dir: str = "data/processed") -> None:
        """
        Export processed data to CSV
        
        Args:
            df: DataFrame to export
            filename: Output filename
            output_dir: Output directory
        """
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filepath = output_path / filename
        df.to_csv(filepath, index=False)
        
        logger.info(f"Exported {len(df)} records to {filepath}")


if __name__ == "__main__":
    # Example usage
    preprocessor = DataPreprocessor()
    print("Data preprocessor ready")
