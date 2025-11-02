"""
Reporting Module
Generates reports and bulletins
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate forecast bulletins and reports"""
    
    def __init__(self):
        self.report_template = None
    
    def generate_forecast_bulletin(self, impact_forecasts: pd.DataFrame,
                                  hazard_forecasts: pd.DataFrame,
                                  forecast_date: datetime,
                                  output_file: Optional[str] = None) -> str:
        """
        Generate forecast bulletin text
        
        Args:
            impact_forecasts: DataFrame with impact forecasts
            hazard_forecasts: DataFrame with hazard forecasts
            forecast_date: Date of forecast
            output_file: Path to save bulletin
            
        Returns:
            Bulletin text
        """
        logger.info("Generating forecast bulletin...")
        
        bulletin = []
        bulletin.append("=" * 80)
        bulletin.append("NIGERIA MULTI-HAZARD IMPACT-BASED FORECAST")
        bulletin.append("Borno, Adamawa, and Yobe (BAY) States")
        bulletin.append("=" * 80)
        bulletin.append(f"\nIssued: {forecast_date.strftime('%Y-%m-%d %H:%M')}")
        bulletin.append(f"Valid for: Next 30 days\n")
        
        # Executive Summary
        bulletin.append("\n" + "=" * 80)
        bulletin.append("EXECUTIVE SUMMARY")
        bulletin.append("=" * 80)
        
        # Count high-risk areas
        high_risk = impact_forecasts[impact_forecasts['impact_level'].isin(['High', 'Severe'])]
        critical_priority = impact_forecasts[impact_forecasts.get('priority_level', 'Low') == 'Critical']
        
        total_at_risk = impact_forecasts['people_at_risk'].sum() if 'people_at_risk' in impact_forecasts.columns else 0
        
        bulletin.append(f"\n? Total LGAs analyzed: {len(impact_forecasts)}")
        bulletin.append(f"? LGAs with HIGH/SEVERE impact forecast: {len(high_risk)}")
        bulletin.append(f"? LGAs requiring CRITICAL priority response: {len(critical_priority)}")
        bulletin.append(f"? Total estimated people at risk: {total_at_risk:,.0f}")
        
        # Top priority LGAs
        bulletin.append("\n" + "=" * 80)
        bulletin.append("TOP PRIORITY LGAs FOR EARLY ACTION")
        bulletin.append("=" * 80 + "\n")
        
        # Sort by priority
        if 'priority_rank' in impact_forecasts.columns:
            top_lgas = impact_forecasts.nsmallest(10, 'priority_rank')
        else:
            top_lgas = impact_forecasts.nlargest(10, 'people_at_risk')
        
        for idx, row in top_lgas.iterrows():
            lga = row.get('lga', 'Unknown')
            people = row.get('people_at_risk', 0)
            impact = row.get('impact_level', 'Unknown')
            hazards = row.get('hazards', 'Multiple')
            
            bulletin.append(f"{idx+1}. {lga}")
            bulletin.append(f"   - People at risk: {people:,.0f}")
            bulletin.append(f"   - Impact level: {impact}")
            bulletin.append(f"   - Hazards: {hazards}")
            bulletin.append("")
        
        # Hazard-specific forecasts
        bulletin.append("\n" + "=" * 80)
        bulletin.append("HAZARD-SPECIFIC FORECASTS")
        bulletin.append("=" * 80 + "\n")
        
        # Flood forecast
        flood_forecasts = hazard_forecasts[hazard_forecasts.get('hazard_type', '') == 'flood']
        if len(flood_forecasts) > 0:
            bulletin.append("FLOOD HAZARD")
            bulletin.append("-" * 40)
            
            high_prob = flood_forecasts[flood_forecasts['probability'] >= 0.5]
            bulletin.append(f"? LGAs with high flood probability (?50%): {len(high_prob)}")
            
            if len(high_prob) > 0:
                bulletin.append(f"? Highest risk LGAs:")
                for _, row in high_prob.nlargest(5, 'probability').iterrows():
                    bulletin.append(f"  - {row['lga']}: {row['probability']*100:.0f}% probability")
            bulletin.append("")
        
        # Displacement forecast
        displacement_forecasts = hazard_forecasts[hazard_forecasts.get('hazard_type', '') == 'displacement']
        if len(displacement_forecasts) > 0:
            bulletin.append("DISPLACEMENT RISK")
            bulletin.append("-" * 40)
            
            high_risk_disp = displacement_forecasts[displacement_forecasts.get('risk_level', 'Low') == 'High']
            bulletin.append(f"? LGAs with high displacement risk: {len(high_risk_disp)}")
            bulletin.append("")
        
        # Recommended actions
        bulletin.append("\n" + "=" * 80)
        bulletin.append("RECOMMENDED EARLY ACTIONS")
        bulletin.append("=" * 80 + "\n")
        
        bulletin.append("Based on the forecast, the following early actions are recommended:\n")
        
        if len(critical_priority) > 0:
            bulletin.append("IMMEDIATE ACTIONS (Critical Priority LGAs):")
            bulletin.append("? Activate emergency operations centers")
            bulletin.append("? Pre-position emergency supplies and personnel")
            bulletin.append("? Conduct community early warning dissemination")
            bulletin.append("? Prepare evacuation plans and shelters")
            bulletin.append("")
        
        if len(high_risk) > 0:
            bulletin.append("PREPAREDNESS ACTIONS (High Risk LGAs):")
            bulletin.append("? Monitor situation closely")
            bulletin.append("? Ensure communication systems operational")
            bulletin.append("? Brief response teams")
            bulletin.append("? Review contingency plans")
            bulletin.append("")
        
        bulletin.append("GENERAL ACTIONS:")
        bulletin.append("? Continue monitoring meteorological and hydrological conditions")
        bulletin.append("? Coordinate with sectoral partners (Health, WASH, Shelter, Protection)")
        bulletin.append("? Prepare assessment teams")
        bulletin.append("? Ensure funding mechanisms are ready for activation")
        
        # Footer
        bulletin.append("\n" + "=" * 80)
        bulletin.append("For more information, contact: [Contact details]")
        bulletin.append("Next bulletin: [Date]")
        bulletin.append("=" * 80)
        
        bulletin_text = "\n".join(bulletin)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(bulletin_text)
            logger.info(f"Bulletin saved to {output_file}")
        
        return bulletin_text
    
    def generate_lga_profile(self, lga: str,
                           impact_data: pd.DataFrame,
                           historical_data: Optional[Dict] = None) -> str:
        """
        Generate detailed LGA risk profile
        
        Args:
            lga: LGA name
            impact_data: Impact forecast data
            historical_data: Historical event data
            
        Returns:
            LGA profile text
        """
        logger.info(f"Generating profile for {lga}...")
        
        profile = []
        profile.append("=" * 80)
        profile.append(f"LGA RISK PROFILE: {lga}")
        profile.append("=" * 80 + "\n")
        
        # Current forecast
        lga_forecast = impact_data[impact_data['lga'] == lga]
        
        if len(lga_forecast) > 0:
            row = lga_forecast.iloc[0]
            
            profile.append("CURRENT FORECAST")
            profile.append("-" * 40)
            profile.append(f"People at risk: {row.get('people_at_risk', 0):,.0f}")
            profile.append(f"Impact level: {row.get('impact_level', 'Unknown')}")
            profile.append(f"Priority level: {row.get('priority_level', 'Unknown')}")
            profile.append(f"Hazards: {row.get('hazards', 'Multiple')}")
            profile.append("")
        
        # Historical context
        if historical_data:
            profile.append("HISTORICAL CONTEXT")
            profile.append("-" * 40)
            
            if 'flood_events' in historical_data:
                flood_events = historical_data['flood_events']
                lga_floods = flood_events[flood_events['lga'] == lga]
                profile.append(f"Historical flood events: {len(lga_floods)}")
            
            if 'displacement_events' in historical_data:
                disp_events = historical_data['displacement_events']
                lga_disp = disp_events[disp_events['lga'] == lga]
                profile.append(f"Historical displacement events: {len(lga_disp)}")
            
            profile.append("")
        
        profile_text = "\n".join(profile)
        
        return profile_text
    
    def export_to_csv(self, data: pd.DataFrame, filename: str,
                     output_dir: str = "data/outputs"):
        """
        Export data to CSV with timestamp
        
        Args:
            data: DataFrame to export
            filename: Base filename
            output_dir: Output directory
        """
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_path / f"{filename}_{timestamp}.csv"
        
        data.to_csv(output_file, index=False)
        logger.info(f"Data exported to {output_file}")
    
    def create_summary_table(self, impact_forecasts: pd.DataFrame) -> pd.DataFrame:
        """
        Create summary table for reporting
        
        Args:
            impact_forecasts: Impact forecast data
            
        Returns:
            Summary DataFrame
        """
        summary = impact_forecasts.groupby('impact_level').agg({
            'lga': 'count',
            'people_at_risk': 'sum'
        }).reset_index()
        
        summary.columns = ['Impact Level', 'Number of LGAs', 'Total People at Risk']
        
        return summary


if __name__ == "__main__":
    # Example usage
    reporter = ReportGenerator()
    print("Report generator ready")
