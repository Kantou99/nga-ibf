#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBF Alert System
Generates early warning alerts based on forecasts
"""

import pandas as pd
from datetime import datetime
import config

class AlertSystem:
    """Generate and manage early warning alerts"""
    
    def __init__(self, forecasts_df):
        """
        Args:
            forecasts_df: DataFrame with forecasts from MultiHazardForecast
        """
        self.forecasts = forecasts_df
        self.alerts = None
        
    def generate_alerts(self, displacement_threshold=5000, probability_threshold=0.40):
        """
        Generate alerts for high-risk forecasts
        
        Args:
            displacement_threshold: Minimum expected displacement for alert
            probability_threshold: Minimum probability for alert
        """
        print("="*70)
        print("GENERATING ALERTS")
        print("="*70)
        
        # Filter significant forecasts
        significant = self.forecasts[
            (self.forecasts['expected_displacement'] >= displacement_threshold) &
            (self.forecasts['probability'] >= probability_threshold)
        ].copy()
        
        if len(significant) == 0:
            print("\n✅ No alerts - all areas below thresholds")
            return pd.DataFrame()
        
        # Assign alert levels
        significant['alert_level'] = significant.apply(self._assign_alert_level, axis=1)
        significant['alert_priority'] = significant.apply(self._calculate_priority, axis=1)
        
        # Sort by priority
        significant = significant.sort_values('alert_priority', ascending=False)
        
        self.alerts = significant
        
        # Summary
        print(f"\n🚨 {len(significant)} alerts generated")
        for level in ['critical', 'severe', 'moderate']:
            count = (significant['alert_level'] == level).sum()
            if count > 0:
                print(f"   {level.upper():10s} {count:3d} alerts")
        
        return self.alerts
    
    def _assign_alert_level(self, row):
        """Assign alert level based on risk"""
        displacement = row['expected_displacement']
        probability = row['probability']
        
        # Risk score
        risk_score = (displacement / 50000) * probability  # Normalized risk
        
        if risk_score >= 0.80 or displacement >= 50000:
            return 'critical'
        elif risk_score >= 0.60 or displacement >= 20000:
            return 'severe'
        elif risk_score >= 0.40 or displacement >= 10000:
            return 'moderate'
        else:
            return 'low'
    
    def _calculate_priority(self, row):
        """Calculate alert priority score"""
        displacement = row['expected_displacement']
        probability = row['probability']
        
        # Priority = magnitude * probability
        priority = (displacement / 1000) * probability
        
        return round(priority, 2)
    
    def get_critical_alerts(self):
        """Get only critical alerts"""
        if self.alerts is None or len(self.alerts) == 0:
            return pd.DataFrame()
        return self.alerts[self.alerts['alert_level'] == 'critical']
    
    def create_alert_bulletin(self, output_file=None):
        """Create alert bulletin document"""
        
        if self.alerts is None or len(self.alerts) == 0:
            print("No alerts to report")
            return None
        
        if output_file is None:
            date_str = datetime.now().strftime("%Y%m%d")
            output_file = config.OUTPUTS_DIR / f'alert_bulletin_{date_str}.txt'
        
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("NIGERIA IBF SYSTEM - EARLY WARNING BULLETIN\n")
            f.write("="*70 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Total Alerts: {len(self.alerts)}\n\n")
            
            # Critical alerts
            critical = self.get_critical_alerts()
            if len(critical) > 0:
                f.write("🔴 CRITICAL ALERTS\n")
                f.write("-" * 70 + "\n")
                for _, row in critical.iterrows():
                    f.write(f"\n{row['lga']}, {row['state']}\n")
                    f.write(f"  Hazard: {row['hazard_type'].upper()}\n")
                    f.write(f"  Expected Displacement: {row['expected_displacement']:,}\n")
                    f.write(f"  Probability: {row['probability']:.0%}\n")
                    f.write(f"  Priority: {row['alert_priority']:.1f}\n")
                f.write("\n")
            
            # All alerts summary
            f.write("\n" + "="*70 + "\n")
            f.write("ALL ALERTS SUMMARY\n")
            f.write("="*70 + "\n\n")
            
            for _, row in self.alerts.head(20).iterrows():
                f.write(f"{row['lga']:25s} ({row['state']:12s}) ")
                f.write(f"{row['hazard_type']:8s} ")
                f.write(f"Disp: {row['expected_displacement']:6,.0f} ")
                f.write(f"Prob: {row['probability']:.0%} ")
                f.write(f"[{row['alert_level'].upper()}]\n")
        
        print(f"\n💾 Alert bulletin saved: {output_file}")
        return output_file


def main():
    """Generate alerts from latest forecasts"""
    from ibf_database import IBFDatabase
    from forecast_models import MultiHazardForecast
    
    # Load database and generate forecasts
    print("\n📊 Loading database...")
    db = IBFDatabase()
    
    print("\n🔮 Generating forecasts...")
    multi_hazard = MultiHazardForecast(db)
    forecasts = multi_hazard.forecast_all()
    
    # Generate alerts
    alert_system = AlertSystem(forecasts)
    alerts = alert_system.generate_alerts(
        displacement_threshold=5000,
        probability_threshold=0.40
    )
    
    if len(alerts) > 0:
        # Display top alerts
        print("\n" + "="*70)
        print("TOP 10 PRIORITY ALERTS")
        print("="*70 + "\n")
        
        for _, row in alerts.head(10).iterrows():
            print(f"[{row['alert_level'].upper():8s}] "
                  f"{row['lga']:25s} ({row['state']:12s})")
            print(f"            {row['hazard_type']:8s} "
                  f"Displacement: {row['expected_displacement']:,} "
                  f"Probability: {row['probability']:.0%}")
            print()
        
        # Create bulletin
        alert_system.create_alert_bulletin()
        
        # Export alerts
        output_file = config.OUTPUTS_DIR / 'alerts_latest.csv'
        alerts.to_csv(output_file, index=False)
        print(f"\n💾 Alerts exported: {output_file}")
    
    print("\n" + "="*70)
    print("✅ ALERT SYSTEM COMPLETE")
    print("="*70)
    
    return alerts


if __name__ == "__main__":
    alerts = main()
