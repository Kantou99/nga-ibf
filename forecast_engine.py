#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nigeria IBF Forecast Engine
Main operational system for running forecasts and generating alerts
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import config
from ibf_database import IBFDatabase
from forecast_models import MultiHazardForecast
from alert_system import AlertSystem

class IBFForecastEngine:
    """
    Main IBF forecasting engine
    Orchestrates data loading, forecasting, and alert generation
    """
    
    def __init__(self):
        """Initialize the forecast engine"""
        print("="*70)
        print(f"{config.SYSTEM_NAME} v{config.SYSTEM_VERSION}")
        print("="*70)
        print(f"\n🚀 Initializing forecast engine...")
        print(f"   Organization: {config.ORGANIZATION}")
        print(f"   Forecast horizon: Conflict {config.CONFLICT_FORECAST_HORIZON}w, Flood {config.FLOOD_FORECAST_HORIZON}w")
        
        self.database = None
        self.forecasts = None
        self.alerts = None
        self.run_timestamp = datetime.now()
        
    def run_full_forecast(self):
        """Run complete forecast cycle"""
        
        print("\n" + "="*70)
        print("RUNNING FULL FORECAST CYCLE")
        print("="*70)
        
        # Step 1: Load database
        print("\n📊 STEP 1: Loading database...")
        self.database = IBFDatabase()
        
        # Step 2: Generate forecasts
        print("\n🔮 STEP 2: Generating forecasts...")
        multi_hazard = MultiHazardForecast(self.database)
        self.forecasts = multi_hazard.forecast_all()
        
        # Step 3: Generate alerts
        print("\n🚨 STEP 3: Generating alerts...")
        alert_system = AlertSystem(self.forecasts)
        self.alerts = alert_system.generate_alerts(
            displacement_threshold=5000,
            probability_threshold=0.40
        )
        
        # Step 4: Export results
        print("\n💾 STEP 4: Exporting results...")
        self._export_results(alert_system)
        
        # Step 5: Summary
        self._print_summary()
        
        return {
            'forecasts': self.forecasts,
            'alerts': self.alerts,
            'timestamp': self.run_timestamp
        }
    
    def _export_results(self, alert_system):
        """Export all results"""
        
        date_str = self.run_timestamp.strftime("%Y%m%d_%H%M")
        
        # Forecasts
        forecast_file = config.OUTPUTS_DIR / f'forecasts_{date_str}.csv'
        self.forecasts.to_csv(forecast_file, index=False)
        print(f"   ✅ Forecasts: {forecast_file}")
        
        # Alerts
        if self.alerts is not None and len(self.alerts) > 0:
            alert_file = config.OUTPUTS_DIR / f'alerts_{date_str}.csv'
            self.alerts.to_csv(alert_file, index=False)
            print(f"   ✅ Alerts: {alert_file}")
            
            # Alert bulletin
            bulletin_file = alert_system.create_alert_bulletin()
            print(f"   ✅ Bulletin: {bulletin_file}")
        
        # Integrated database
        db_file = self.database.export_integrated_database()
        print(f"   ✅ Database: {db_file}")
        
        # Summary report
        self._create_summary_report(date_str)
    
    def _create_summary_report(self, date_str):
        """Create executive summary report"""
        
        report_file = config.OUTPUTS_DIR / f'summary_report_{date_str}.txt'
        
        with open(report_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write(f"{config.SYSTEM_NAME} - FORECAST SUMMARY\n")
            f.write("="*70 + "\n")
            f.write(f"Generated: {self.run_timestamp.strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Forecast Horizon: {config.CONFLICT_FORECAST_HORIZON} weeks (conflict), ")
            f.write(f"{config.FLOOD_FORECAST_HORIZON} weeks (flood)\n\n")
            
            f.write("OVERVIEW\n")
            f.write("-"*70 + "\n")
            f.write(f"Total LGAs analyzed: {len(self.database.integrated_lga)}\n")
            f.write(f"Forecasts generated: {len(self.forecasts)}\n")
            
            if self.alerts is not None and len(self.alerts) > 0:
                f.write(f"Alerts issued: {len(self.alerts)}\n\n")
                
                f.write("ALERT BREAKDOWN\n")
                f.write("-"*70 + "\n")
                for level in ['critical', 'severe', 'moderate']:
                    count = (self.alerts['alert_level'] == level).sum()
                    f.write(f"{level.upper():10s} {count:3d} alerts\n")
                
                f.write("\nTOP 5 PRIORITY AREAS\n")
                f.write("-"*70 + "\n")
                for i, (_, row) in enumerate(self.alerts.head(5).iterrows(), 1):
                    f.write(f"\n{i}. {row['lga']}, {row['state']}\n")
                    f.write(f"   Hazard: {row['hazard_type']}\n")
                    f.write(f"   Expected Displacement: {row['expected_displacement']:,}\n")
                    f.write(f"   Probability: {row['probability']:.0%}\n")
                    f.write(f"   Alert Level: {row['alert_level'].upper()}\n")
            
            else:
                f.write("Alerts issued: 0\n")
                f.write("Status: All areas below alert thresholds\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*70 + "\n")
        
        print(f"   ✅ Summary: {report_file}")
    
    def _print_summary(self):
        """Print execution summary"""
        
        print("\n" + "="*70)
        print("FORECAST CYCLE COMPLETE")
        print("="*70)
        
        print(f"\n📊 Results:")
        print(f"   Forecasts generated: {len(self.forecasts)}")
        
        if self.alerts is not None and len(self.alerts) > 0:
            print(f"   Alerts issued: {len(self.alerts)}")
            
            critical_count = (self.alerts['alert_level'] == 'critical').sum()
            if critical_count > 0:
                print(f"\n🔴 {critical_count} CRITICAL ALERTS require immediate attention!")
            
            print(f"\n🎯 Top 3 Priority Areas:")
            for i, (_, row) in enumerate(self.alerts.head(3).iterrows(), 1):
                print(f"   {i}. {row['lga']}, {row['state']}")
                print(f"      {row['hazard_type'].upper()}: {row['expected_displacement']:,} displaced")
        else:
            print(f"   Alerts issued: 0")
            print(f"   ✅ All areas below alert thresholds")
        
        print(f"\n⏱️  Runtime: {self.run_timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"📁 Outputs: {config.OUTPUTS_DIR}/")
        
        print("\n" + "="*70)
        print("✅ SYSTEM READY FOR OPERATIONAL USE")
        print("="*70)


def main():
    """Main execution"""
    
    try:
        # Initialize and run
        engine = IBFForecastEngine()
        results = engine.run_full_forecast()
        
        print("\n✅ SUCCESS - Forecast engine executed successfully")
        print(f"\nNext steps:")
        print(f"1. Review alerts in: {config.OUTPUTS_DIR}/alerts_*.csv")
        print(f"2. Check summary: {config.OUTPUTS_DIR}/summary_report_*.txt")
        print(f"3. Share bulletin: {config.OUTPUTS_DIR}/alert_bulletin_*.txt")
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()
