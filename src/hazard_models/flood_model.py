"""
Flood Hazard Model
Analyzes flood risk and generates forecasts
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FloodModel:
    """Flood hazard assessment and forecasting"""
    
    def __init__(self):
        self.historical_data = None
        self.risk_levels = {
            'Low': (0, 0.25),
            'Medium': (0.25, 0.5),
            'High': (0.5, 0.75),
            'Very High': (0.75, 1.0)
        }
    
    def load_historical_data(self, flood_events: pd.DataFrame,
                           flood_risk: pd.DataFrame):
        """
        Load historical flood data
        
        Args:
            flood_events: Historical flood event data
            flood_risk: LGA-level flood risk data
        """
        self.historical_data = {
            'events': flood_events,
            'risk': flood_risk
        }
        logger.info(f"Loaded {len(flood_events)} flood events")
    
    def calculate_flood_frequency(self, events_df: pd.DataFrame,
                                 group_by: str = 'lga',
                                 date_col: str = 'date') -> pd.DataFrame:
        """
        Calculate flood frequency by location
        
        Args:
            events_df: Flood events DataFrame
            group_by: Column to group by (e.g., 'lga', 'state')
            date_col: Date column name
            
        Returns:
            DataFrame with flood frequency metrics
        """
        logger.info(f"Calculating flood frequency by {group_by}...")
        
        if date_col in events_df.columns:
            events_df = events_df.copy()
            events_df[date_col] = pd.to_datetime(events_df[date_col], errors='coerce')
            events_df = events_df[events_df[date_col].notna()]
            
            # Calculate time span
            min_date = events_df[date_col].min()
            max_date = events_df[date_col].max()
            years = (max_date - min_date).days / 365.25
        else:
            years = None
        
        # Count events by location
        frequency = events_df.groupby(group_by).agg({
            group_by: 'count'
        }).rename(columns={group_by: 'event_count'})
        
        if years and years > 0:
            frequency['events_per_year'] = frequency['event_count'] / years
            frequency['return_period_years'] = 1 / frequency['events_per_year'].replace(0, np.nan)
        
        # Calculate impact metrics
        impact_cols = ['deaths', 'injured', 'people_affected', 'houses_destroyed']
        for col in impact_cols:
            if col in events_df.columns:
                frequency[f'total_{col}'] = events_df.groupby(group_by)[col].sum()
                frequency[f'avg_{col}_per_event'] = events_df.groupby(group_by)[col].mean()
        
        frequency = frequency.reset_index()
        
        logger.info(f"Calculated frequency for {len(frequency)} locations")
        
        return frequency
    
    def calculate_seasonal_pattern(self, events_df: pd.DataFrame,
                                  date_col: str = 'date') -> pd.DataFrame:
        """
        Analyze seasonal flood patterns
        
        Args:
            events_df: Flood events DataFrame
            date_col: Date column name
            
        Returns:
            DataFrame with seasonal patterns
        """
        logger.info("Analyzing seasonal flood patterns...")
        
        df = events_df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df[df[date_col].notna()]
        
        # Extract temporal features
        df['month'] = df[date_col].dt.month
        df['year'] = df[date_col].dt.year
        df['season'] = df['month'].apply(self._get_season)
        
        # Seasonal statistics
        seasonal = df.groupby('season').agg({
            'season': 'count',
        }).rename(columns={'season': 'event_count'})
        
        # Monthly statistics
        monthly = df.groupby('month').agg({
            'month': 'count',
        }).rename(columns={'month': 'event_count'})
        
        seasonal = seasonal.reset_index()
        monthly = monthly.reset_index()
        
        logger.info(f"Peak flood season: {seasonal.loc[seasonal['event_count'].idxmax(), 'season']}")
        
        return {'seasonal': seasonal, 'monthly': monthly}
    
    def _get_season(self, month: int) -> str:
        """
        Map month to season in Nigeria
        
        Seasons:
        - Dry season: November - March
        - Rainy season: April - October
        """
        if month in [11, 12, 1, 2, 3]:
            return 'Dry'
        else:
            return 'Rainy'
    
    def calculate_flood_risk_score(self, lga_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite flood risk score for each LGA
        
        Args:
            lga_data: DataFrame with LGA-level indicators
            
        Returns:
            DataFrame with risk scores
        """
        logger.info("Calculating flood risk scores...")
        
        df = lga_data.copy()
        
        # Identify risk indicators
        risk_indicators = []
        
        # Event frequency indicators
        freq_cols = ['event_count', 'events_per_year']
        risk_indicators.extend([col for col in freq_cols if col in df.columns])
        
        # Impact indicators
        impact_cols = ['total_deaths', 'total_people_affected', 'total_houses_destroyed']
        risk_indicators.extend([col for col in impact_cols if col in df.columns])
        
        if not risk_indicators:
            logger.warning("No risk indicators found")
            df['flood_risk_score'] = 0
            return df
        
        # Normalize indicators (0-1 scale)
        normalized = pd.DataFrame()
        for col in risk_indicators:
            if df[col].std() > 0:
                normalized[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            else:
                normalized[col] = 0
        
        # Calculate composite score (equal weights)
        df['flood_risk_score'] = normalized.mean(axis=1)
        
        # Classify risk level
        df['flood_risk_level'] = pd.cut(
            df['flood_risk_score'],
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low', 'Medium', 'High', 'Very High'],
            include_lowest=True
        )
        
        logger.info(f"Risk distribution:\n{df['flood_risk_level'].value_counts()}")
        
        return df
    
    def forecast_flood_probability(self, lga: str,
                                  forecast_month: int,
                                  historical_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Forecast flood probability for a specific LGA and month
        
        Args:
            lga: LGA name
            forecast_month: Month to forecast (1-12)
            historical_data: Historical flood events
            
        Returns:
            Dictionary with forecast information
        """
        if historical_data is None and self.historical_data is not None:
            historical_data = self.historical_data['events']
        
        if historical_data is None:
            logger.warning("No historical data available for forecasting")
            return {
                'lga': lga,
                'month': forecast_month,
                'probability': 0.5,
                'confidence': 'Low'
            }
        
        # Filter data for LGA
        lga_events = historical_data[historical_data['lga'] == lga].copy()
        
        if len(lga_events) == 0:
            return {
                'lga': lga,
                'month': forecast_month,
                'probability': 0.0,
                'confidence': 'No Data'
            }
        
        # Calculate historical probability for this month
        if 'date' in lga_events.columns:
            lga_events['date'] = pd.to_datetime(lga_events['date'], errors='coerce')
            lga_events = lga_events[lga_events['date'].notna()]
            lga_events['month'] = lga_events['date'].dt.month
            
            # Count events in target month
            month_events = len(lga_events[lga_events['month'] == forecast_month])
            
            # Total years of data
            years = (lga_events['date'].max() - lga_events['date'].min()).days / 365.25
            
            if years > 0:
                # Probability = events per year
                probability = month_events / years
                probability = min(probability, 1.0)  # Cap at 1.0
            else:
                probability = 0.0
            
            # Confidence based on sample size
            if len(lga_events) >= 10:
                confidence = 'High'
            elif len(lga_events) >= 5:
                confidence = 'Medium'
            else:
                confidence = 'Low'
        else:
            probability = len(lga_events) / 12  # Assume uniform distribution
            confidence = 'Low'
        
        return {
            'lga': lga,
            'month': forecast_month,
            'probability': probability,
            'confidence': confidence,
            'historical_events': len(lga_events)
        }
    
    def generate_forecast_bulletin(self, forecast_date: datetime,
                                  lga_list: List[str],
                                  historical_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Generate flood forecast bulletin for multiple LGAs
        
        Args:
            forecast_date: Date for forecast
            lga_list: List of LGAs to forecast
            historical_data: Historical flood events
            
        Returns:
            DataFrame with forecasts for all LGAs
        """
        logger.info(f"Generating flood forecast bulletin for {len(lga_list)} LGAs...")
        
        forecasts = []
        forecast_month = forecast_date.month
        
        for lga in lga_list:
            forecast = self.forecast_flood_probability(lga, forecast_month, historical_data)
            forecast['forecast_date'] = forecast_date
            forecasts.append(forecast)
        
        bulletin = pd.DataFrame(forecasts)
        
        # Add alert levels
        bulletin['alert_level'] = bulletin['probability'].apply(self._get_alert_level)
        
        logger.info(f"Forecast bulletin generated with {len(bulletin)} entries")
        
        return bulletin
    
    def _get_alert_level(self, probability: float) -> str:
        """Map probability to alert level"""
        if probability >= 0.7:
            return 'Red'  # High probability
        elif probability >= 0.4:
            return 'Orange'  # Medium probability
        elif probability >= 0.2:
            return 'Yellow'  # Low-medium probability
        else:
            return 'Green'  # Low probability


if __name__ == "__main__":
    # Example usage
    model = FloodModel()
    print("Flood model ready")
