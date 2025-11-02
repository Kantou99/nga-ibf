#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process NEMA Flood Data for Nigeria IBF System
Cleans and standardizes NEMA flood event database (2006-2022)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

def process_nema_flood_data(
    input_file='/mnt/user-data/uploads/nema_data.xlsx',
    output_dir='data'
):
    """
    Process NEMA flood data for IBF system
    
    Data source: NEMA (National Emergency Management Agency)
    Coverage: 2006-2022
    Records: 1,030 flood events across Nigeria
    
    Args:
        input_file: Path to NEMA Excel file
        output_dir: Where to save processed files
    """
    
    print("="*70)
    print("PROCESSING NEMA FLOOD DATA")
    print("="*70)
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Load NEMA data
    print(f"\n📂 Loading data from: {input_file}")
    df = pd.read_excel(input_file, sheet_name='_flood_2006-2022')
    
    print(f"✅ Loaded {len(df):,} flood event records")
    print(f"   Years: 2006-2022")
    print(f"   Geographic coverage: {df['STATEs'].nunique()} states, {df['LGA'].nunique()} LGAs")
    
    # ========================================================================
    # Clean and standardize data
    # ========================================================================
    
    print("\n🔧 Cleaning and standardizing data...")
    
    # 1. Standardize column names
    df_clean = df.rename(columns={
        'S/N': 'event_id',
        'STATEs': 'state_raw',
        'LGA': 'lga_raw',
        'COMMUNITITY': 'community',
        'DISASTER TYPE': 'disaster_type',
        'YEAR': 'year',
        'NATURE OF DAMAGE': 'damage_description',
        'NO OF AFFECTED': 'affected_raw',
        'NO OF DEATHS': 'deaths_raw',
        'LATITUDE': 'latitude_raw',
        'LONGITUDE': 'longitude_raw'
    })
    
    # 2. Clean disaster type
    df_clean['disaster_type'] = df_clean['disaster_type'].str.strip().str.title()
    df_clean['is_flood'] = df_clean['disaster_type'].str.contains('Flood', case=False, na=False)
    
    # 3. Clean year
    df_clean['year'] = df_clean['year'].fillna(0).astype(int)
    df_clean = df_clean[df_clean['year'] > 2000]  # Filter invalid years
    
    # 4. Standardize state names
    df_clean['state'] = df_clean['state_raw'].apply(standardize_state_name)
    
    # 5. Clean LGA names
    df_clean['lga'] = df_clean['lga_raw'].apply(standardize_lga_name)
    
    # 6. Clean numeric fields
    df_clean['affected'] = df_clean['affected_raw'].apply(clean_number)
    df_clean['deaths'] = df_clean['deaths_raw'].apply(clean_number)
    
    # 7. Clean coordinates
    df_clean['latitude'] = df_clean['latitude_raw'].apply(clean_coordinate)
    df_clean['longitude'] = df_clean['longitude_raw'].apply(clean_coordinate)
    
    # Validate coordinates (Nigeria bounds: ~4-14°N, ~3-15°E)
    df_clean.loc[
        (df_clean['latitude'] < 4) | (df_clean['latitude'] > 14), 
        'latitude'
    ] = np.nan
    df_clean.loc[
        (df_clean['longitude'] < 3) | (df_clean['longitude'] > 15), 
        'longitude'
    ] = np.nan
    
    # 8. Add derived fields
    df_clean['has_coordinates'] = df_clean['latitude'].notna() & df_clean['longitude'].notna()
    df_clean['has_impact_data'] = df_clean['affected'].notna() | df_clean['deaths'].notna()
    df_clean['severity'] = df_clean.apply(categorize_severity, axis=1)
    
    # 9. Add geopolitical zones
    df_clean['region'] = df_clean['state'].apply(assign_region)
    
    print(f"✅ Cleaned {len(df_clean):,} valid records")
    
    # ========================================================================
    # Create aggregated summaries
    # ========================================================================
    
    print("\n📊 Creating aggregated summaries...")
    
    # State-year aggregation
    state_year = df_clean.groupby(['state', 'year', 'region']).agg({
        'event_id': 'count',
        'affected': 'sum',
        'deaths': 'sum',
        'lga': 'nunique',
        'has_coordinates': 'sum'
    }).reset_index()
    
    state_year = state_year.rename(columns={
        'event_id': 'num_events',
        'lga': 'num_lgas_affected',
        'has_coordinates': 'events_with_coords'
    })
    
    print(f"✅ Created state-year aggregation: {len(state_year)} records")
    
    # LGA summary statistics
    lga_summary = df_clean[df_clean['lga'].notna()].groupby(['state', 'lga']).agg({
        'event_id': 'count',
        'affected': ['sum', 'mean', 'max'],
        'deaths': ['sum', 'mean'],
        'year': ['min', 'max'],
        'has_coordinates': 'sum'
    }).reset_index()
    
    # Flatten columns
    lga_summary.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                           for col in lga_summary.columns.values]
    
    lga_summary = lga_summary.rename(columns={
        'event_id_count': 'total_events',
        'affected_sum': 'total_affected',
        'affected_mean': 'mean_affected_per_event',
        'affected_max': 'max_affected_single_event',
        'deaths_sum': 'total_deaths',
        'deaths_mean': 'mean_deaths_per_event',
        'year_min': 'first_event_year',
        'year_max': 'last_event_year',
        'has_coordinates_sum': 'events_with_coords'
    })
    
    # Calculate risk score
    lga_summary['years_with_events'] = lga_summary['last_event_year'] - lga_summary['first_event_year'] + 1
    lga_summary['events_per_year'] = (
        lga_summary['total_events'] / lga_summary['years_with_events']
    ).round(2)
    
    # Simple flood risk score (0-100)
    lga_summary['flood_risk_score'] = (
        (lga_summary['total_events'].rank(pct=True) * 0.3 +
         lga_summary['events_per_year'].rank(pct=True) * 0.3 +
         lga_summary['total_affected'].fillna(0).rank(pct=True) * 0.4) * 100
    ).round(1)
    
    print(f"✅ Created LGA summary: {len(lga_summary)} LGAs")
    
    # State summary
    state_summary = df_clean.groupby('state').agg({
        'event_id': 'count',
        'affected': 'sum',
        'deaths': 'sum',
        'lga': 'nunique',
        'year': ['min', 'max'],
        'region': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown'
    }).reset_index()
    
    state_summary.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                            for col in state_summary.columns.values]
    
    state_summary = state_summary.rename(columns={
        'event_id_count': 'total_events',
        'affected_sum': 'total_affected',
        'deaths_sum': 'total_deaths',
        'lga_nunique': 'num_lgas_affected',
        'year_min': 'first_event_year',
        'year_max': 'last_event_year',
        'region_<lambda>': 'region'
    })
    
    print(f"✅ Created state summary: {len(state_summary)} states")
    
    # ========================================================================
    # Save processed data
    # ========================================================================
    
    print("\n💾 Saving processed files...")
    
    # 1. Full cleaned dataset
    output_full = f"{output_dir}/nema_flood_data_cleaned.csv"
    df_clean.to_csv(output_full, index=False)
    print(f"✅ Saved: {output_full} ({len(df_clean):,} records)")
    
    # 2. State-year aggregation
    output_state_year = f"{output_dir}/nema_flood_by_state_year.csv"
    state_year.to_csv(output_state_year, index=False)
    print(f"✅ Saved: {output_state_year} ({len(state_year)} records)")
    
    # 3. LGA summary with risk scores
    output_lga = f"{output_dir}/nema_flood_risk_by_lga.csv"
    lga_summary.to_csv(output_lga, index=False)
    print(f"✅ Saved: {output_lga} ({len(lga_summary)} LGAs)")
    
    # 4. State summary
    output_state = f"{output_dir}/nema_flood_summary_by_state.csv"
    state_summary.to_csv(output_state, index=False)
    print(f"✅ Saved: {output_state} ({len(state_summary)} states)")
    
    # 5. Excel with all sheets
    output_excel = f"{output_dir}/nema_flood_processed.xlsx"
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_clean.to_excel(writer, sheet_name='All_Events', index=False)
        state_year.to_excel(writer, sheet_name='State_Year', index=False)
        lga_summary.to_excel(writer, sheet_name='LGA_Risk_Scores', index=False)
        state_summary.to_excel(writer, sheet_name='State_Summary', index=False)
    print(f"✅ Saved: {output_excel}")
    
    # ========================================================================
    # Print summary
    # ========================================================================
    
    print_processing_summary(df_clean, state_summary, lga_summary)
    
    return df_clean, state_year, lga_summary, state_summary


# Helper functions

def clean_number(x):
    """Clean and convert to number"""
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float)):
        return x
    try:
        return float(str(x).replace(',', '').strip())
    except:
        return np.nan


def clean_coordinate(x):
    """Clean coordinate values"""
    if pd.isna(x):
        return np.nan
    try:
        return float(str(x).strip())
    except:
        return np.nan


def standardize_state_name(state):
    """Standardize state names"""
    if pd.isna(state):
        return None
    
    state = str(state).strip().title()
    
    # Common variations
    state_mapping = {
        'Fct': 'FCT',
        'Federal Capital Territory': 'FCT',
        'Cross Rivers': 'Cross River',
        'Rivers ': 'Rivers',
        'Akwa Ibom ': 'Akwa Ibom',
    }
    
    return state_mapping.get(state, state)


def standardize_lga_name(lga):
    """Standardize LGA names"""
    if pd.isna(lga):
        return None
    
    lga = str(lga).strip().title()
    
    # Remove common suffixes
    lga = re.sub(r'\s+Lga$', '', lga, flags=re.IGNORECASE)
    
    return lga


def categorize_severity(row):
    """Categorize flood severity"""
    affected = row['affected'] if pd.notna(row['affected']) else 0
    deaths = row['deaths'] if pd.notna(row['deaths']) else 0
    
    if deaths > 50 or affected > 10000:
        return 'catastrophic'
    elif deaths > 10 or affected > 5000:
        return 'severe'
    elif deaths > 0 or affected > 1000:
        return 'moderate'
    else:
        return 'minor'


def assign_region(state):
    """Assign geopolitical zone"""
    if pd.isna(state):
        return 'Unknown'
    
    regions = {
        'North_West': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'],
        'North_East': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
        'North_Central': ['Benue', 'FCT', 'Kogi', 'Kwara', 'Nasarawa', 'Niger', 'Plateau'],
        'South_West': ['Ekiti', 'Lagos', 'Ogun', 'Ondo', 'Osun', 'Oyo'],
        'South_East': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
        'South_South': ['Akwa Ibom', 'Bayelsa', 'Cross River', 'Delta', 'Edo', 'Rivers']
    }
    
    for region, states in regions.items():
        if state in states:
            return region
    
    return 'Unknown'


def print_processing_summary(df_clean, state_summary, lga_summary):
    """Print processing summary"""
    
    print("\n" + "="*70)
    print("NEMA FLOOD DATA PROCESSING SUMMARY")
    print("="*70)
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Total events: {len(df_clean):,}")
    print(f"   Years covered: {df_clean['year'].min():.0f} - {df_clean['year'].max():.0f}")
    print(f"   States: {len(state_summary)}")
    print(f"   LGAs: {len(lga_summary)}")
    
    print(f"\n👥 Impact Summary:")
    print(f"   Total affected: {df_clean['affected'].sum():,.0f}")
    print(f"   Total deaths: {df_clean['deaths'].sum():,.0f}")
    print(f"   Mean affected/event: {df_clean['affected'].mean():,.0f}")
    print(f"   Mean deaths/event: {df_clean['deaths'].mean():.1f}")
    
    print(f"\n✅ Data Quality:")
    print(f"   Records with impact data: {df_clean['has_impact_data'].sum():,} ({df_clean['has_impact_data'].sum()/len(df_clean)*100:.1f}%)")
    print(f"   Records with coordinates: {df_clean['has_coordinates'].sum():,} ({df_clean['has_coordinates'].sum()/len(df_clean)*100:.1f}%)")
    print(f"   Records with LGA names: {df_clean['lga'].notna().sum():,} ({df_clean['lga'].notna().sum()/len(df_clean)*100:.1f}%)")
    
    print(f"\n🏆 Top 5 High-Risk LGAs (by flood risk score):")
    top_lgas = lga_summary.nlargest(5, 'flood_risk_score')[
        ['lga', 'state', 'total_events', 'events_per_year', 'total_affected', 'flood_risk_score']
    ]
    for _, row in top_lgas.iterrows():
        print(f"   {row['lga']:25s} ({row['state']:15s}) Score: {row['flood_risk_score']:5.1f}, {row['total_events']:3.0f} events, {row['events_per_year']:.1f}/yr")
    
    print(f"\n🗺️  Top 5 States by Flood Events:")
    top_states = state_summary.nlargest(5, 'total_events')[
        ['state', 'region', 'total_events', 'total_affected', 'total_deaths']
    ]
    for _, row in top_states.iterrows():
        print(f"   {row['state']:15s} ({row['region']:15s}) {row['total_events']:3.0f} events, {row['total_affected']:8,.0f} affected, {row['total_deaths']:4.0f} deaths")
    
    print("="*70)


# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process NEMA flood data for Nigeria IBF system'
    )
    
    parser.add_argument(
        '--input',
        default='/mnt/user-data/uploads/nema_data.xlsx',
        help='Path to NEMA Excel file'
    )
    
    parser.add_argument(
        '--output',
        default='data',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    try:
        df_clean, state_year, lga_summary, state_summary = process_nema_flood_data(
            input_file=args.input,
            output_dir=args.output
        )
        
        print("\n" + "="*70)
        print("✅ PROCESSING COMPLETE!")
        print("="*70)
        print("\nYou now have comprehensive flood event data for:")
        print("• Flood risk mapping (by LGA)")
        print("• Historical flood pattern analysis")
        print("• Training flood impact models")
        print("• Validating flood forecasts")
        print("• Identifying vulnerable areas")
        
        print("\nIntegrate with DTM data for complete picture!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
