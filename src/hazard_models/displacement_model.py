"""
Displacement Hazard Model
Analyzes displacement risk and patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DisplacementModel:
    """Displacement risk assessment and forecasting"""
    
    def __init__(self):
        self.historical_data = None
        self.vulnerability_data = None
    
    def load_data(self, displacement_events: pd.DataFrame,
                 displacement_monthly: pd.DataFrame,
                 displacement_stats: pd.DataFrame):
        """
        Load displacement datasets
        
        Args:
            displacement_events: Event-level displacement data
            displacement_monthly: Monthly time-series data
            displacement_stats: LGA-level statistics
        """
        self.historical_data = {
            'events': displacement_events,
            'monthly': displacement_monthly,
            'stats': displacement_stats
        }
        logger.info(f"Loaded displacement data: {len(displacement_events)} events")
    
    def analyze_displacement_trends(self, monthly_df: pd.DataFrame,
                                   date_col: str = 'month') -> Dict:
        """
        Analyze displacement trends over time
        
        Args:
            monthly_df: Monthly displacement time-series
            date_col: Date column name
            
        Returns:
            Dictionary with trend analysis
        """
        logger.info("Analyzing displacement trends...")
        
        df = monthly_df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df[df[date_col].notna()].sort_values(date_col)
        
        # Identify displacement columns
        disp_cols = [col for col in df.columns if 'displaced' in col.lower() or 'individuals' in col.lower()]
        
        if not disp_cols:
            logger.warning("No displacement columns found")
            return {}
        
        disp_col = disp_cols[0]
        
        # Calculate statistics
        trends = {
            'total_displaced': df[disp_col].sum(),
            'mean_monthly': df[disp_col].mean(),
            'max_monthly': df[disp_col].max(),
            'std_monthly': df[disp_col].std(),
            'min_date': df[date_col].min(),
            'max_date': df[date_col].max()
        }
        
        # Calculate trend (simple linear)
        if len(df) > 2:
            x = np.arange(len(df))
            y = df[disp_col].values
            
            # Remove NaN values
            mask = ~np.isnan(y)
            if mask.sum() > 2:
                z = np.polyfit(x[mask], y[mask], 1)
                trends['trend_slope'] = z[0]
                trends['trend_direction'] = 'Increasing' if z[0] > 0 else 'Decreasing'
            else:
                trends['trend_slope'] = 0
                trends['trend_direction'] = 'Stable'
        
        logger.info(f"Total displaced: {trends['total_displaced']:,.0f}")
        
        return trends
    
    def calculate_displacement_hotspots(self, events_df: pd.DataFrame,
                                      group_by: str = 'lga') -> pd.DataFrame:
        """
        Identify displacement hotspots
        
        Args:
            events_df: Displacement events DataFrame
            group_by: Column to group by
            
        Returns:
            DataFrame with hotspot rankings
        """
        logger.info(f"Calculating displacement hotspots by {group_by}...")
        
        # Identify displacement column
        disp_cols = [col for col in events_df.columns if 'displaced' in col.lower() or 'individuals' in col.lower()]
        
        if not disp_cols:
            logger.warning("No displacement columns found")
            return pd.DataFrame()
        
        disp_col = disp_cols[0]
        
        # Aggregate by location
        hotspots = events_df.groupby(group_by).agg({
            disp_col: ['sum', 'count', 'mean', 'max'],
            group_by: 'first'
        })
        
        hotspots.columns = ['total_displaced', 'event_count', 'avg_per_event', 'max_event', group_by]
        hotspots = hotspots.reset_index(drop=True)
        
        # Calculate hotspot score (normalized composite)
        for col in ['total_displaced', 'event_count', 'max_event']:
            if hotspots[col].std() > 0:
                hotspots[f'{col}_norm'] = (hotspots[col] - hotspots[col].min()) / (hotspots[col].max() - hotspots[col].min())
            else:
                hotspots[f'{col}_norm'] = 0
        
        hotspots['hotspot_score'] = hotspots[['total_displaced_norm', 'event_count_norm', 'max_event_norm']].mean(axis=1)
        
        # Rank hotspots
        hotspots = hotspots.sort_values('hotspot_score', ascending=False)
        hotspots['rank'] = range(1, len(hotspots) + 1)
        
        # Classify hotspot level
        hotspots['hotspot_level'] = pd.cut(
            hotspots['hotspot_score'],
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low', 'Medium', 'High', 'Critical'],
            include_lowest=True
        )
        
        logger.info(f"Identified {len(hotspots)} hotspots")
        logger.info(f"Top 3: {hotspots.head(3)[group_by].tolist()}")
        
        return hotspots
    
    def analyze_displacement_causes(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze causes of displacement
        
        Args:
            events_df: Displacement events DataFrame
            
        Returns:
            DataFrame with cause analysis
        """
        logger.info("Analyzing displacement causes...")
        
        # Look for cause/reason column
        cause_cols = [col for col in events_df.columns if any(term in col.lower() for term in ['cause', 'reason', 'trigger', 'hazard'])]
        
        if not cause_cols:
            logger.warning("No cause column found")
            return pd.DataFrame()
        
        cause_col = cause_cols[0]
        
        # Find displacement amount column
        disp_cols = [col for col in events_df.columns if 'displaced' in col.lower() or 'individuals' in col.lower()]
        disp_col = disp_cols[0] if disp_cols else None
        
        if disp_col:
            causes = events_df.groupby(cause_col).agg({
                disp_col: ['sum', 'count', 'mean'],
                cause_col: 'first'
            })
            causes.columns = ['total_displaced', 'event_count', 'avg_per_event', 'cause']
        else:
            causes = events_df[cause_col].value_counts().reset_index()
            causes.columns = ['cause', 'event_count']
        
        causes = causes.reset_index(drop=True)
        causes = causes.sort_values('total_displaced' if disp_col else 'event_count', ascending=False)
        
        logger.info(f"Identified {len(causes)} displacement causes")
        
        return causes
    
    def calculate_vulnerability_index(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate displacement vulnerability index for LGAs
        
        Args:
            stats_df: LGA-level displacement statistics
            
        Returns:
            DataFrame with vulnerability indices
        """
        logger.info("Calculating displacement vulnerability index...")
        
        df = stats_df.copy()
        
        # Identify vulnerability indicators
        vuln_indicators = []
        
        # Displacement frequency indicators
        freq_indicators = [col for col in df.columns if any(term in col.lower() for term in ['event', 'count', 'frequency'])]
        vuln_indicators.extend([col for col in freq_indicators if df[col].dtype in [np.float64, np.int64]])
        
        # Displacement magnitude indicators
        mag_indicators = [col for col in df.columns if any(term in col.lower() for term in ['displaced', 'total', 'sum', 'avg', 'mean'])]
        vuln_indicators.extend([col for col in mag_indicators if df[col].dtype in [np.float64, np.int64]])
        
        # Remove duplicates
        vuln_indicators = list(set(vuln_indicators))
        
        if not vuln_indicators:
            logger.warning("No vulnerability indicators found")
            df['vulnerability_index'] = 0
            return df
        
        # Normalize indicators
        normalized = pd.DataFrame()
        for col in vuln_indicators:
            if df[col].std() > 0:
                normalized[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            else:
                normalized[col] = 0
        
        # Calculate composite vulnerability index
        df['displacement_vulnerability_index'] = normalized.mean(axis=1)
        
        # Classify vulnerability level
        df['vulnerability_level'] = pd.cut(
            df['displacement_vulnerability_index'],
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low', 'Medium', 'High', 'Very High'],
            include_lowest=True
        )
        
        logger.info(f"Vulnerability distribution:\n{df['vulnerability_level'].value_counts()}")
        
        return df
    
    def forecast_displacement_risk(self, lga: str,
                                  forecast_period: str,
                                  historical_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Forecast displacement risk for an LGA
        
        Args:
            lga: LGA name
            forecast_period: Forecast period (e.g., 'next_month', 'next_quarter')
            historical_data: Historical displacement data
            
        Returns:
            Dictionary with forecast
        """
        if historical_data is None and self.historical_data is not None:
            historical_data = self.historical_data['events']
        
        if historical_data is None:
            logger.warning("No historical data available")
            return {
                'lga': lga,
                'forecast_period': forecast_period,
                'risk_level': 'Unknown',
                'confidence': 'No Data'
            }
        
        # Filter for LGA
        lga_data = historical_data[historical_data['lga'] == lga]
        
        if len(lga_data) == 0:
            return {
                'lga': lga,
                'forecast_period': forecast_period,
                'risk_level': 'Low',
                'confidence': 'No Historical Data'
            }
        
        # Calculate historical risk indicators
        disp_cols = [col for col in lga_data.columns if 'displaced' in col.lower()]
        
        if disp_cols:
            disp_col = disp_cols[0]
            
            total_displaced = lga_data[disp_col].sum()
            event_count = len(lga_data)
            avg_displacement = lga_data[disp_col].mean()
            
            # Simple risk classification based on historical data
            if total_displaced > lga_data[disp_col].quantile(0.75):
                risk_level = 'High'
            elif total_displaced > lga_data[disp_col].quantile(0.5):
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            confidence = 'High' if event_count >= 10 else 'Medium' if event_count >= 5 else 'Low'
        else:
            risk_level = 'Low'
            confidence = 'Low'
            total_displaced = 0
            event_count = len(lga_data)
        
        return {
            'lga': lga,
            'forecast_period': forecast_period,
            'risk_level': risk_level,
            'confidence': confidence,
            'historical_events': event_count,
            'total_historical_displacement': total_displaced
        }
    
    def generate_early_warning(self, lga_list: List[str],
                             threshold: str = 'Medium') -> pd.DataFrame:
        """
        Generate early warning for high-risk LGAs
        
        Args:
            lga_list: List of LGAs to assess
            threshold: Minimum risk level for warning
            
        Returns:
            DataFrame with early warnings
        """
        logger.info(f"Generating early warnings for {len(lga_list)} LGAs...")
        
        warnings = []
        risk_levels = {'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}
        threshold_value = risk_levels.get(threshold, 2)
        
        for lga in lga_list:
            forecast = self.forecast_displacement_risk(lga, 'next_month')
            risk_value = risk_levels.get(forecast['risk_level'], 1)
            
            if risk_value >= threshold_value:
                forecast['warning_issued'] = True
                forecast['warning_date'] = datetime.now()
                warnings.append(forecast)
        
        warnings_df = pd.DataFrame(warnings)
        
        logger.info(f"Issued {len(warnings_df)} early warnings")
        
        return warnings_df


if __name__ == "__main__":
    # Example usage
    model = DisplacementModel()
    print("Displacement model ready")
