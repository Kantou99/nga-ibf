#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBF Database Manager
Loads and integrates all data sources (DTM, NEMA, Exposure)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import config

class IBFDatabase:
    """
    Central database manager for IBF system
    Loads and integrates DTM displacement, NEMA floods, and exposure data
    """
    
    def __init__(self):
        """Initialize and load all data"""
        print("="*70)
        print("LOADING IBF DATABASE")
        print("="*70)
        
        self.dtm_monthly = None
        self.dtm_lga_stats = None
        self.nema_lga_risk = None
        self.nema_full = None
        self.exposure = None
        self.integrated_lga = None
        
        self.load_all_data()
        self.create_integrated_database()
        
    def load_all_data(self):
        """Load all data files"""
        print("\n📂 Loading data files...")
        
        try:
            # DTM displacement data
            self.dtm_monthly = pd.read_csv(config.DATA_FILES['dtm_monthly'])
            print(f"✅ DTM monthly events: {len(self.dtm_monthly):,} records")
            
            self.dtm_lga_stats = pd.read_csv(config.DATA_FILES['dtm_lga_stats'])
            print(f"✅ DTM LGA statistics: {len(self.dtm_lga_stats)} LGAs")
            
            # NEMA flood data
            self.nema_lga_risk = pd.read_csv(config.DATA_FILES['nema_lga_risk'])
            print(f"✅ NEMA LGA flood risk: {len(self.nema_lga_risk)} LGAs")
            
            self.nema_full = pd.read_csv(config.DATA_FILES['nema_full'])
            print(f"✅ NEMA flood events: {len(self.nema_full):,} events")
            
            # Exposure data
            self.exposure = pd.read_csv(config.DATA_FILES['exposure_csv'])
            print(f"✅ Exposure data: {len(self.exposure)} LGAs")
            
        except FileNotFoundError as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def create_integrated_database(self):
        """Create integrated LGA-level database"""
        print("\n🔗 Creating integrated LGA database...")
        
        # Check if exposure has state/lga columns
        if 'state' not in self.exposure.columns:
            # Use DTM data as base (has state/lga)
            print("   Using DTM data as base (exposure lacks state/lga columns)")
            integrated = self.dtm_lga_stats[['state', 'lga']].copy()
            
            # Try to add population if available in exposure
            if 'lga_name' in self.exposure.columns or 'name' in self.exposure.columns:
                name_col = 'lga_name' if 'lga_name' in self.exposure.columns else 'name'
                pop_col = 'population' if 'population' in self.exposure.columns else 'value'
                if pop_col in self.exposure.columns:
                    exp_subset = self.exposure[[name_col, pop_col]].rename(columns={name_col: 'lga', pop_col: 'population'})
                    integrated = integrated.merge(exp_subset, on='lga', how='left')
        else:
            # Use exposure data as base
            integrated = self.exposure.copy()
        
        # Ensure we have population column
        if 'population' not in integrated.columns:
            print("   Warning: No population data available, using default values")
            integrated['population'] = 50000  # Default population
        
        # Add DTM statistics
        dtm_cols = ['state', 'lga', 'total_idps_all_time', 'mean_idps_per_event', 
                   'num_events', 'events_per_year', 'most_common_hazard']
        dtm_subset = self.dtm_lga_stats[dtm_cols].copy()
        dtm_subset = dtm_subset.rename(columns={
            'total_idps_all_time': 'dtm_total_idps',
            'mean_idps_per_event': 'dtm_mean_idps',
            'num_events': 'dtm_num_events',
            'events_per_year': 'dtm_events_per_year',
            'most_common_hazard': 'dtm_hazard_type'
        })
        
        integrated = integrated.merge(
            dtm_subset, 
            on=['state', 'lga'], 
            how='outer'  # Changed to outer to keep all LGAs
        )
        
        # Add NEMA flood risk
        nema_cols = ['state', 'lga', 'total_events', 'total_affected', 
                    'events_per_year', 'flood_risk_score']
        nema_subset = self.nema_lga_risk[nema_cols].copy()
        nema_subset = nema_subset.rename(columns={
            'total_events': 'nema_flood_events',
            'total_affected': 'nema_flood_affected',
            'events_per_year': 'nema_events_per_year',
            'flood_risk_score': 'nema_flood_risk'
        })
        
        integrated = integrated.merge(
            nema_subset,
            on=['state', 'lga'],
            how='left'
        )
        
        # Fill NaN values
        integrated['dtm_total_idps'] = integrated['dtm_total_idps'].fillna(0)
        integrated['dtm_num_events'] = integrated['dtm_num_events'].fillna(0)
        integrated['nema_flood_events'] = integrated['nema_flood_events'].fillna(0)
        integrated['nema_flood_risk'] = integrated['nema_flood_risk'].fillna(0)
        
        # Calculate composite risk scores
        integrated['has_conflict_data'] = integrated['dtm_num_events'] > 0
        integrated['has_flood_data'] = integrated['nema_flood_events'] > 0
        
        # Composite risk (0-100 scale)
        integrated['conflict_risk'] = self._calculate_conflict_risk(integrated)
        integrated['flood_risk'] = self._normalize_risk(integrated['nema_flood_risk'])
        integrated['composite_risk'] = integrated[['conflict_risk', 'flood_risk']].max(axis=1)
        
        # Risk categories
        integrated['risk_level'] = integrated['composite_risk'].apply(self._categorize_risk)
        
        self.integrated_lga = integrated
        print(f"✅ Integrated database: {len(self.integrated_lga)} LGAs")
        print(f"   - {integrated['has_conflict_data'].sum()} LGAs with conflict data")
        print(f"   - {integrated['has_flood_data'].sum()} LGAs with flood data")
        
    def _calculate_conflict_risk(self, df):
        """Calculate normalized conflict risk (0-100)"""
        if 'dtm_events_per_year' not in df.columns:
            return pd.Series(0, index=df.index)
        
        risk = df['dtm_events_per_year'].fillna(0).rank(pct=True) * 100
        return risk.round(1)
    
    def _normalize_risk(self, series):
        """Normalize risk to 0-100 scale"""
        return series.fillna(0).clip(0, 100)
    
    def _categorize_risk(self, risk_score):
        """Categorize risk score into levels"""
        if risk_score >= config.RISK_THRESHOLDS['very_high'] * 100:
            return 'very_high'
        elif risk_score >= config.RISK_THRESHOLDS['high'] * 100:
            return 'high'
        elif risk_score >= config.RISK_THRESHOLDS['moderate'] * 100:
            return 'moderate'
        else:
            return 'low'
    
    def get_lga_profile(self, state, lga):
        """Get complete risk profile for an LGA"""
        lga_data = self.integrated_lga[
            (self.integrated_lga['state'] == state) & 
            (self.integrated_lga['lga'] == lga)
        ]
        
        if len(lga_data) == 0:
            return None
        
        return lga_data.iloc[0].to_dict()
    
    def get_high_risk_lgas(self, threshold=60, limit=20):
        """Get high-risk LGAs"""
        high_risk = self.integrated_lga[
            self.integrated_lga['composite_risk'] >= threshold
        ].sort_values('composite_risk', ascending=False).head(limit)
        
        return high_risk[['state', 'lga', 'conflict_risk', 'flood_risk', 
                         'composite_risk', 'risk_level', 'population']]
    
    def get_state_summary(self):
        """Get state-level summary"""
        summary = self.integrated_lga.groupby('state').agg({
            'lga': 'count',
            'population': 'sum',
            'dtm_total_idps': 'sum',
            'nema_flood_affected': 'sum',
            'conflict_risk': 'mean',
            'flood_risk': 'mean',
            'composite_risk': 'mean'
        }).round(1)
        
        summary.columns = ['num_lgas', 'total_pop', 'total_idps', 
                          'flood_affected', 'avg_conflict_risk', 
                          'avg_flood_risk', 'avg_composite_risk']
        
        return summary.sort_values('avg_composite_risk', ascending=False)
    
    def export_integrated_database(self, output_file=None):
        """Export integrated database"""
        if output_file is None:
            output_file = config.DATA_DIR / 'integrated_lga_database.csv'
        
        self.integrated_lga.to_csv(output_file, index=False)
        print(f"\n💾 Exported integrated database: {output_file}")
        
        return output_file


def main():
    """Load and display database summary"""
    
    # Initialize database
    db = IBFDatabase()
    
    # Print summary
    print("\n" + "="*70)
    print("DATABASE SUMMARY")
    print("="*70)
    
    print(f"\n📊 LGA-Level Data:")
    print(f"   Total LGAs: {len(db.integrated_lga)}")
    print(f"   Total population: {db.integrated_lga['population'].sum():,.0f}")
    print(f"   LGAs with conflict data: {db.integrated_lga['has_conflict_data'].sum()}")
    print(f"   LGAs with flood data: {db.integrated_lga['has_flood_data'].sum()}")
    
    print(f"\n🎯 Risk Distribution:")
    risk_counts = db.integrated_lga['risk_level'].value_counts()
    for level in ['very_high', 'high', 'moderate', 'low']:
        count = risk_counts.get(level, 0)
        pct = count / len(db.integrated_lga) * 100
        print(f"   {level:12s} {count:4d} LGAs ({pct:5.1f}%)")
    
    print(f"\n🏆 Top 10 High-Risk LGAs:")
    high_risk = db.get_high_risk_lgas(threshold=60, limit=10)
    for _, row in high_risk.iterrows():
        print(f"   {row['lga']:25s} ({row['state']:15s}) "
              f"Risk: {row['composite_risk']:5.1f} "
              f"(C:{row['conflict_risk']:5.1f}, F:{row['flood_risk']:5.1f})")
    
    # Export
    db.export_integrated_database()
    
    print("\n" + "="*70)
    print("✅ DATABASE READY FOR FORECASTING")
    print("="*70)
    
    return db


if __name__ == "__main__":
    db = main()
