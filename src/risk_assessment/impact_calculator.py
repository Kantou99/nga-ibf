"""
Impact Calculator
Calculates potential impacts and generates impact-based forecasts
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImpactCalculator:
    """Calculate and forecast multi-hazard impacts"""
    
    def __init__(self):
        self.exposure_data = None
        self.vulnerability_data = None
        self.hazard_data = None
    
    def load_data(self, exposure: pd.DataFrame,
                 vulnerability: Optional[pd.DataFrame] = None,
                 hazard: Optional[pd.DataFrame] = None):
        """
        Load exposure, vulnerability, and hazard data
        
        Args:
            exposure: Population exposure data
            vulnerability: Vulnerability indicators
            hazard: Hazard forecasts
        """
        self.exposure_data = exposure
        self.vulnerability_data = vulnerability
        self.hazard_data = hazard
        
        logger.info("Impact calculator data loaded")
    
    def calculate_people_at_risk(self, lga: str,
                                hazard_probability: float,
                                hazard_type: str = 'flood') -> Dict:
        """
        Calculate number of people at risk
        
        Args:
            lga: LGA name
            hazard_probability: Probability of hazard occurrence (0-1)
            hazard_type: Type of hazard
            
        Returns:
            Dictionary with impact estimates
        """
        if self.exposure_data is None:
            logger.warning("No exposure data loaded")
            return {'error': 'No exposure data'}
        
        # Find LGA in exposure data
        lga_col = 'lga' if 'lga' in self.exposure_data.columns else 'LGA'
        lga_exposure = self.exposure_data[self.exposure_data[lga_col] == lga]
        
        if len(lga_exposure) == 0:
            logger.warning(f"LGA {lga} not found in exposure data")
            return {'lga': lga, 'people_at_risk': 0, 'error': 'LGA not found'}
        
        # Get population
        pop_cols = [col for col in lga_exposure.columns if 'pop' in col.lower() or 'people' in col.lower()]
        
        if not pop_cols:
            logger.warning("No population column found")
            return {'lga': lga, 'people_at_risk': 0, 'error': 'No population data'}
        
        population = lga_exposure[pop_cols[0]].values[0]
        
        # Get vulnerability factor if available
        vulnerability_factor = 1.0
        if self.vulnerability_data is not None:
            lga_vuln = self.vulnerability_data[self.vulnerability_data[lga_col] == lga]
            if len(lga_vuln) > 0:
                vuln_cols = [col for col in lga_vuln.columns if 'vulnerability' in col.lower() or 'index' in col.lower()]
                if vuln_cols:
                    vulnerability_factor = lga_vuln[vuln_cols[0]].values[0]
        
        # Calculate people at risk
        # Risk = Population ? Hazard Probability ? Vulnerability
        people_at_risk = population * hazard_probability * vulnerability_factor
        
        return {
            'lga': lga,
            'hazard_type': hazard_type,
            'population': population,
            'hazard_probability': hazard_probability,
            'vulnerability_factor': vulnerability_factor,
            'people_at_risk': int(people_at_risk),
            'percentage_at_risk': (people_at_risk / population * 100) if population > 0 else 0
        }
    
    def calculate_expected_displacement(self, lga: str,
                                       hazard_probability: float,
                                       historical_displacement_rate: Optional[float] = None) -> Dict:
        """
        Calculate expected displacement
        
        Args:
            lga: LGA name
            hazard_probability: Probability of hazard
            historical_displacement_rate: Historical displacement rate (people displaced per event)
            
        Returns:
            Dictionary with displacement estimates
        """
        # Get people at risk
        impact = self.calculate_people_at_risk(lga, hazard_probability)
        
        if 'error' in impact:
            return impact
        
        people_at_risk = impact['people_at_risk']
        
        # Estimate displacement
        # If historical rate provided, use it; otherwise assume 10% of people at risk
        if historical_displacement_rate is not None:
            expected_displacement = hazard_probability * historical_displacement_rate
        else:
            displacement_rate = 0.1  # Default: 10% of people at risk get displaced
            expected_displacement = people_at_risk * displacement_rate
        
        return {
            'lga': lga,
            'people_at_risk': people_at_risk,
            'expected_displacement': int(expected_displacement),
            'displacement_rate': historical_displacement_rate or 0.1,
            'confidence': 'Medium' if historical_displacement_rate else 'Low'
        }
    
    def calculate_multi_hazard_impact(self, lga: str,
                                     hazard_forecasts: Dict[str, float]) -> Dict:
        """
        Calculate combined impact from multiple hazards
        
        Args:
            lga: LGA name
            hazard_forecasts: Dictionary of {hazard_type: probability}
            
        Returns:
            Dictionary with combined impact estimates
        """
        logger.info(f"Calculating multi-hazard impact for {lga}...")
        
        total_impact = {
            'lga': lga,
            'hazards': hazard_forecasts,
            'impacts_by_hazard': {}
        }
        
        total_people_at_risk = 0
        max_people_at_risk = 0
        
        for hazard_type, probability in hazard_forecasts.items():
            impact = self.calculate_people_at_risk(lga, probability, hazard_type)
            total_impact['impacts_by_hazard'][hazard_type] = impact
            
            if 'people_at_risk' in impact:
                # Simple addition (may overestimate if hazards overlap)
                total_people_at_risk += impact['people_at_risk']
                max_people_at_risk = max(max_people_at_risk, impact['people_at_risk'])
        
        # Use average of sum and max to account for potential overlap
        total_impact['total_people_at_risk'] = int((total_people_at_risk + max_people_at_risk) / 2)
        total_impact['combined_hazard_probability'] = 1 - np.prod([1 - p for p in hazard_forecasts.values()])
        
        return total_impact
    
    def generate_impact_forecast(self, lga_list: List[str],
                                forecast_period: str,
                                hazard_forecasts: pd.DataFrame) -> pd.DataFrame:
        """
        Generate impact-based forecast for multiple LGAs
        
        Args:
            lga_list: List of LGAs
            forecast_period: Forecast period description
            hazard_forecasts: DataFrame with hazard forecasts (columns: lga, hazard_type, probability)
            
        Returns:
            DataFrame with impact forecasts
        """
        logger.info(f"Generating impact forecasts for {len(lga_list)} LGAs...")
        
        forecasts = []
        
        for lga in lga_list:
            # Get hazard forecasts for this LGA
            lga_hazards = hazard_forecasts[hazard_forecasts['lga'] == lga]
            
            if len(lga_hazards) == 0:
                continue
            
            # Create hazard dictionary
            hazard_dict = {}
            for _, row in lga_hazards.iterrows():
                hazard_type = row.get('hazard_type', 'unknown')
                probability = row.get('probability', 0)
                hazard_dict[hazard_type] = probability
            
            # Calculate multi-hazard impact
            impact = self.calculate_multi_hazard_impact(lga, hazard_dict)
            
            # Create forecast record
            forecast = {
                'lga': lga,
                'forecast_period': forecast_period,
                'people_at_risk': impact.get('total_people_at_risk', 0),
                'combined_probability': impact.get('combined_hazard_probability', 0),
                'hazards': ', '.join(hazard_dict.keys())
            }
            
            # Add individual hazard impacts
            for hazard_type, hazard_impact in impact.get('impacts_by_hazard', {}).items():
                forecast[f'{hazard_type}_probability'] = hazard_impact.get('hazard_probability', 0)
                forecast[f'{hazard_type}_people_at_risk'] = hazard_impact.get('people_at_risk', 0)
            
            forecasts.append(forecast)
        
        forecast_df = pd.DataFrame(forecasts)
        
        # Add impact level classification
        if 'people_at_risk' in forecast_df.columns:
            forecast_df['impact_level'] = pd.cut(
                forecast_df['people_at_risk'],
                bins=[0, 1000, 5000, 20000, np.inf],
                labels=['Low', 'Medium', 'High', 'Severe']
            )
        
        logger.info(f"Generated {len(forecast_df)} impact forecasts")
        
        return forecast_df
    
    def calculate_sectoral_impact(self, lga: str,
                                 people_at_risk: int,
                                 hazard_type: str) -> Dict:
        """
        Estimate impacts on different sectors (health, shelter, WASH, etc.)
        
        Args:
            lga: LGA name
            people_at_risk: Number of people at risk
            hazard_type: Type of hazard
            
        Returns:
            Dictionary with sectoral impact estimates
        """
        # Default impact ratios (can be calibrated with historical data)
        impact_ratios = {
            'flood': {
                'health_needs': 0.3,  # 30% may need health services
                'shelter_needs': 0.5,  # 50% may need shelter
                'wash_needs': 0.8,  # 80% may need WASH services
                'food_needs': 0.6,  # 60% may need food assistance
                'protection_needs': 0.2  # 20% may need protection services
            },
            'displacement': {
                'health_needs': 0.4,
                'shelter_needs': 0.9,
                'wash_needs': 0.9,
                'food_needs': 0.8,
                'protection_needs': 0.3
            },
            'default': {
                'health_needs': 0.3,
                'shelter_needs': 0.5,
                'wash_needs': 0.6,
                'food_needs': 0.5,
                'protection_needs': 0.2
            }
        }
        
        ratios = impact_ratios.get(hazard_type, impact_ratios['default'])
        
        sectoral_impact = {
            'lga': lga,
            'people_at_risk': people_at_risk,
            'hazard_type': hazard_type
        }
        
        for sector, ratio in ratios.items():
            sectoral_impact[f'{sector}_people'] = int(people_at_risk * ratio)
        
        return sectoral_impact
    
    def prioritize_lgas(self, impact_forecasts: pd.DataFrame,
                       criteria: List[str] = None) -> pd.DataFrame:
        """
        Prioritize LGAs for response based on impact forecasts
        
        Args:
            impact_forecasts: DataFrame with impact forecasts
            criteria: List of columns to use for prioritization
            
        Returns:
            DataFrame with priority rankings
        """
        logger.info("Prioritizing LGAs for response...")
        
        df = impact_forecasts.copy()
        
        # Default criteria
        if criteria is None:
            criteria = ['people_at_risk', 'combined_probability']
            # Add any vulnerability or impact level columns
            criteria.extend([col for col in df.columns if 'vulnerability' in col.lower() or 'impact' in col.lower()])
            criteria = [col for col in criteria if col in df.columns]
        
        if not criteria:
            logger.warning("No criteria available for prioritization")
            return df
        
        # Normalize criteria (0-1 scale)
        normalized = pd.DataFrame()
        for col in criteria:
            if df[col].dtype in [np.float64, np.int64]:
                if df[col].std() > 0:
                    normalized[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
                else:
                    normalized[col] = 0
        
        # Calculate priority score (equal weights)
        if len(normalized.columns) > 0:
            df['priority_score'] = normalized.mean(axis=1)
            df = df.sort_values('priority_score', ascending=False)
            df['priority_rank'] = range(1, len(df) + 1)
            
            # Classify priority level
            df['priority_level'] = pd.cut(
                df['priority_score'],
                bins=[0, 0.25, 0.5, 0.75, 1.0],
                labels=['Low', 'Medium', 'High', 'Critical'],
                include_lowest=True
            )
        
        logger.info(f"Prioritized {len(df)} LGAs")
        
        return df


if __name__ == "__main__":
    # Example usage
    calculator = ImpactCalculator()
    print("Impact calculator ready")
