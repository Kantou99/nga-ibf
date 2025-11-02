#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBF Forecast Models
Conflict displacement and flood impact forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

class ConflictForecastModel:
    """
    Forecast conflict-related displacement
    Based on historical patterns, trends, and seasonal factors
    """
    
    def __init__(self, database):
        """
        Args:
            database: IBFDatabase instance
        """
        self.db = database
        self.forecast_horizon = config.CONFLICT_FORECAST_HORIZON
        
    def forecast_lga(self, state, lga, weeks_ahead=4):
        """
        Forecast displacement for specific LGA
        
        Returns:
            dict with forecast results
        """
        # Get LGA profile
        profile = self.db.get_lga_profile(state, lga)
        
        if profile is None:
            return None
        
        # Get historical displacement data
        monthly_data = self.db.dtm_monthly[
            (self.db.dtm_monthly['state'] == state) &
            (self.db.dtm_monthly['lga'] == lga)
        ]
        
        if len(monthly_data) == 0:
            # No historical data - use vulnerability-based estimate
            return self._vulnerability_based_forecast(profile, weeks_ahead)
        
        # Calculate forecast
        forecast = self._calculate_forecast(profile, monthly_data, weeks_ahead)
        
        return forecast
    
    def _vulnerability_based_forecast(self, profile, weeks_ahead):
        """Forecast based on LGA vulnerability when no historical data"""
        
        risk_score = profile['conflict_risk'] / 100.0
        
        # Estimate based on regional averages
        baseline_displacement = 500  # Base estimate
        risk_multiplier = 1 + (risk_score * 3)  # 1x to 4x based on risk
        
        expected_displacement = baseline_displacement * risk_multiplier
        
        return {
            'lga': profile['lga'],
            'state': profile['state'],
            'forecast_week': weeks_ahead,
            'expected_displacement': int(expected_displacement),
            'probability': risk_score * 0.5,  # Lower confidence without history
            'confidence': 'low',
            'method': 'vulnerability_based',
            'risk_level': profile['risk_level']
        }
    
    def _calculate_forecast(self, profile, monthly_data, weeks_ahead):
        """Calculate forecast using historical data"""
        
        # Sort by date
        monthly_data = monthly_data.sort_values('date')
        
        # Get recent trend (last 6 months)
        recent = monthly_data.tail(6)
        trend = recent['total_idps'].diff().mean()
        
        # Historical average
        hist_mean = monthly_data['total_idps'].mean()
        hist_std = monthly_data['total_idps'].std()
        
        # Seasonal factor (current month)
        current_month = datetime.now().month
        seasonal_factor = self._get_seasonal_factor(current_month, state=profile['state'])
        
        # Base forecast
        base_forecast = hist_mean + (trend * 0.5)  # Partial trend contribution
        
        # Apply seasonal adjustment
        forecast_displacement = base_forecast * seasonal_factor
        
        # Adjust for recent activity
        if len(recent) > 0:
            recent_mean = recent['total_idps'].mean()
            if recent_mean > hist_mean * 1.5:
                # Recent escalation
                forecast_displacement = forecast_displacement * 1.3
        
        # Calculate probability and confidence
        risk_score = profile['conflict_risk'] / 100.0
        probability = min(0.95, risk_score * 0.8 + 0.1)
        
        if len(monthly_data) >= 12:
            confidence = 'high'
        elif len(monthly_data) >= 6:
            confidence = 'moderate'
        else:
            confidence = 'low'
        
        return {
            'lga': profile['lga'],
            'state': profile['state'],
            'forecast_week': weeks_ahead,
            'expected_displacement': int(max(0, forecast_displacement)),
            'lower_bound': int(max(0, forecast_displacement - hist_std)),
            'upper_bound': int(forecast_displacement + hist_std),
            'probability': round(probability, 2),
            'confidence': confidence,
            'method': 'historical_trend',
            'risk_level': profile['risk_level'],
            'historical_events': len(monthly_data),
            'trend': 'increasing' if trend > 0 else 'stable'
        }
    
    def _get_seasonal_factor(self, month, state):
        """Get seasonal adjustment factor"""
        
        # Dry season (potential increase in northern conflict)
        if month in config.DRY_SEASON_MONTHS:
            if state in config.BAY_STATES:
                return 1.2  # 20% increase
            else:
                return 1.0
        else:
            return 1.0
    
    def forecast_all_high_risk(self, risk_threshold=60):
        """Forecast all high-risk LGAs"""
        
        high_risk = self.db.get_high_risk_lgas(threshold=risk_threshold)
        
        forecasts = []
        for _, row in high_risk.iterrows():
            forecast = self.forecast_lga(row['state'], row['lga'])
            if forecast:
                forecasts.append(forecast)
        
        return pd.DataFrame(forecasts)


class FloodForecastModel:
    """
    Forecast flood impacts
    Based on historical flood patterns and risk scores
    """
    
    def __init__(self, database):
        """
        Args:
            database: IBFDatabase instance
        """
        self.db = database
        self.forecast_horizon = config.FLOOD_FORECAST_HORIZON
    
    def forecast_lga(self, state, lga, weeks_ahead=2):
        """Forecast flood impact for specific LGA"""
        
        profile = self.db.get_lga_profile(state, lga)
        
        if profile is None:
            return None
        
        # Check if currently in flood season
        current_month = datetime.now().month
        in_flood_season = current_month in config.RAINY_SEASON_MONTHS
        
        # Get flood risk
        flood_risk = profile['flood_risk'] / 100.0
        
        if flood_risk < 0.2 and not in_flood_season:
            # Low risk, not flood season - minimal forecast
            return {
                'lga': lga,
                'state': state,
                'forecast_week': weeks_ahead,
                'expected_affected': 0,
                'probability': 0.05,
                'confidence': 'moderate',
                'risk_level': 'low',
                'in_flood_season': False
            }
        
        # Calculate flood impact
        return self._calculate_flood_forecast(profile, weeks_ahead, in_flood_season)
    
    def _calculate_flood_forecast(self, profile, weeks_ahead, in_flood_season):
        """Calculate flood impact forecast"""
        
        flood_risk = profile['flood_risk'] / 100.0
        population = profile['population']
        
        # Historical flood data if available
        nema_events = profile.get('nema_flood_events', 0)
        nema_affected = profile.get('nema_flood_affected', 0)
        
        if nema_events > 0:
            # Use historical average
            avg_affected_per_event = nema_affected / nema_events
        else:
            # Estimate based on population and risk
            avg_affected_per_event = population * 0.05 * flood_risk
        
        # Seasonal adjustment
        if in_flood_season:
            seasonal_multiplier = 1.5
            probability_boost = 0.2
        else:
            seasonal_multiplier = 0.5
            probability_boost = 0.0
        
        # Expected impact
        expected_affected = int(avg_affected_per_event * seasonal_multiplier)
        
        # Probability
        base_probability = flood_risk * 0.6
        probability = min(0.90, base_probability + probability_boost)
        
        # Confidence based on data availability
        if nema_events >= 5:
            confidence = 'high'
        elif nema_events >= 2:
            confidence = 'moderate'
        else:
            confidence = 'low'
        
        # Estimate displacement (typically 20-40% of affected)
        estimated_displacement = int(expected_affected * 0.3)
        
        return {
            'lga': profile['lga'],
            'state': profile['state'],
            'forecast_week': weeks_ahead,
            'expected_affected': expected_affected,
            'expected_displacement': estimated_displacement,
            'probability': round(probability, 2),
            'confidence': confidence,
            'risk_level': profile['risk_level'],
            'in_flood_season': in_flood_season,
            'historical_events': int(nema_events)
        }
    
    def forecast_all_high_risk(self, risk_threshold=40):
        """Forecast all flood-prone LGAs"""
        
        flood_prone = self.db.integrated_lga[
            self.db.integrated_lga['flood_risk'] >= risk_threshold
        ].sort_values('flood_risk', ascending=False)
        
        forecasts = []
        for _, row in flood_prone.iterrows():
            forecast = self.forecast_lga(row['state'], row['lga'])
            if forecast:
                forecasts.append(forecast)
        
        return pd.DataFrame(forecasts)


class MultiHazardForecast:
    """
    Combined multi-hazard forecast
    Integrates conflict and flood forecasts
    """
    
    def __init__(self, database):
        """
        Args:
            database: IBFDatabase instance
        """
        self.db = database
        self.conflict_model = ConflictForecastModel(database)
        self.flood_model = FloodForecastModel(database)
    
    def forecast_all(self):
        """Generate comprehensive forecast for all high-risk LGAs"""
        
        print("="*70)
        print("GENERATING MULTI-HAZARD FORECASTS")
        print("="*70)
        
        # Conflict forecasts
        print("\n🔴 Generating conflict forecasts...")
        conflict_forecasts = self.conflict_model.forecast_all_high_risk(risk_threshold=50)
        print(f"✅ {len(conflict_forecasts)} conflict forecasts generated")
        
        # Flood forecasts
        print("\n🌊 Generating flood forecasts...")
        flood_forecasts = self.flood_model.forecast_all_high_risk(risk_threshold=40)
        print(f"✅ {len(flood_forecasts)} flood forecasts generated")
        
        # Combine
        print("\n🔗 Integrating forecasts...")
        integrated = self._integrate_forecasts(conflict_forecasts, flood_forecasts)
        
        print(f"✅ {len(integrated)} total forecasts")
        print("="*70)
        
        return integrated
    
    def _integrate_forecasts(self, conflict_df, flood_df):
        """Integrate conflict and flood forecasts"""
        
        # Add hazard type
        if len(conflict_df) > 0:
            conflict_df['hazard_type'] = 'conflict'
        if len(flood_df) > 0:
            flood_df['hazard_type'] = 'flood'
        
        # Combine
        all_forecasts = pd.concat([conflict_df, flood_df], ignore_index=True, sort=False)
        
        # Sort by expected impact
        displacement_col = 'expected_displacement'
        all_forecasts = all_forecasts.sort_values(
            displacement_col, ascending=False, na_position='last'
        )
        
        return all_forecasts


def main():
    """Test forecast models"""
    from ibf_database import IBFDatabase
    
    # Load database
    print("\n📊 Loading database...")
    db = IBFDatabase()
    
    # Generate forecasts
    multi_hazard = MultiHazardForecast(db)
    forecasts = multi_hazard.forecast_all()
    
    # Display results
    print("\n" + "="*70)
    print("FORECAST RESULTS")
    print("="*70)
    
    print(f"\n📊 Top 10 Forecasts by Expected Displacement:")
    top10 = forecasts.head(10)
    for _, row in top10.iterrows():
        hazard = row['hazard_type']
        lga = row['lga']
        state = row['state']
        disp = row.get('expected_displacement', 0)
        prob = row.get('probability', 0)
        print(f"   {hazard:8s} {lga:25s} ({state:12s}) "
              f"Disp: {disp:6,.0f} Prob: {prob:.2f}")
    
    # Export
    output_file = config.OUTPUTS_DIR / 'forecasts_latest.csv'
    forecasts.to_csv(output_file, index=False)
    print(f"\n💾 Exported forecasts: {output_file}")
    
    return forecasts


if __name__ == "__main__":
    forecasts = main()
