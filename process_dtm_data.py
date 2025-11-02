#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Real DTM Displacement Data for Nigeria IBF System
Converts DTM IDP_Admin2 data into format for forecasting model
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def process_dtm_displacement_data(
    input_file='/mnt/user-data/uploads/2017_2024_Nigeria_displacement_events.xlsx',
    output_dir='data'
):
    """
    Process DTM displacement data for IBF system
    
    Data source: DTM Nigeria (IOM)
    Coverage: 2017-2024
    Records: 8,883 displacement events
    Total IDPs: 121+ million (cumulative)
    
    Args:
        input_file: Path to DTM Excel file
        output_dir: Where to save processed files
    """
    
    print("="*70)
    print("PROCESSING DTM DISPLACEMENT DATA")
    print("="*70)
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Load DTM data
    print(f"\n📂 Loading data from: {input_file}")
    df = pd.read_excel(input_file, sheet_name='IDP_Admin2')
    
    print(f"✅ Loaded {len(df):,} records")
    print(f"   Date range: {df['reportingDate'].min()} to {df['reportingDate'].max()}")
    print(f"   Total IDPs: {df['numPresentIdpInd'].sum():,}")
    
    # ========================================================================
    # Clean and standardize data
    # ========================================================================
    
    print("\n🔧 Cleaning and standardizing data...")
    
    # Rename columns to standard names
    df_clean = df.rename(columns={
        'reportingDate': 'date',
        'yearReportingDate': 'year',
        'monthReportingDate': 'month',
        'admin1Name': 'state',
        'admin1Pcode': 'state_pcode',
        'admin2Name': 'lga',
        'admin2Pcode': 'lga_pcode',
        'numPresentIdpInd': 'idps_present',
        'displacementReason': 'displacement_reason',
        'numberMales': 'males',
        'numberFemales': 'females',
        'roundNumber': 'dtm_round',
        'assessmentType': 'assessment_type'
    })
    
    # Add derived fields
    df_clean['total_population'] = df_clean['males'].fillna(0) + df_clean['females'].fillna(0)
    df_clean['has_gender_data'] = df_clean['males'].notna()
    
    # Categorize displacement reasons
    df_clean['primary_hazard'] = df_clean['displacement_reason'].apply(categorize_hazard)
    df_clean['is_conflict'] = df_clean['displacement_reason'].str.contains('Conflict', case=False, na=False)
    df_clean['is_flood'] = df_clean['displacement_reason'].str.contains('Natural disaster', case=False, na=False)
    df_clean['is_insecurity'] = df_clean['displacement_reason'].str.contains('Insecurity', case=False, na=False)
    
    # Add quarter
    df_clean['quarter'] = df_clean['date'].dt.quarter
    
    # ========================================================================
    # Create aggregated event database
    # ========================================================================
    
    print("\n📊 Creating aggregated event database...")
    
    # Aggregate by state, LGA, month for forecasting
    events_monthly = df_clean.groupby([
        'year', 'month', 'quarter', 'state', 'state_pcode', 'lga', 'lga_pcode', 'primary_hazard'
    ]).agg({
        'idps_present': ['sum', 'mean', 'count'],
        'males': 'sum',
        'females': 'sum',
        'dtm_round': 'max'
    }).reset_index()
    
    # Flatten column names
    events_monthly.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                              for col in events_monthly.columns.values]
    
    # Rename aggregated columns
    events_monthly = events_monthly.rename(columns={
        'idps_present_sum': 'total_idps',
        'idps_present_mean': 'mean_idps_per_record',
        'idps_present_count': 'num_records',
        'males_sum': 'total_males',
        'females_sum': 'total_females',
        'dtm_round_max': 'latest_dtm_round'
    })
    
    # Add date column
    events_monthly['date'] = pd.to_datetime(
        events_monthly[['year', 'month']].assign(day=1)
    )
    
    print(f"✅ Created {len(events_monthly):,} monthly aggregated events")
    
    # ========================================================================
    # Create LGA-level summary statistics
    # ========================================================================
    
    print("\n📈 Creating LGA-level statistics...")
    
    lga_stats = df_clean.groupby(['state', 'lga', 'lga_pcode']).agg({
        'idps_present': ['sum', 'mean', 'max', 'count'],
        'date': ['min', 'max'],
        'primary_hazard': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown'
    }).reset_index()
    
    # Flatten columns
    lga_stats.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                         for col in lga_stats.columns.values]
    
    lga_stats = lga_stats.rename(columns={
        'idps_present_sum': 'total_idps_all_time',
        'idps_present_mean': 'mean_idps_per_event',
        'idps_present_max': 'max_idps_single_event',
        'idps_present_count': 'num_events',
        'date_min': 'first_event_date',
        'date_max': 'last_event_date',
        'primary_hazard_<lambda>': 'most_common_hazard'
    })
    
    # Calculate event frequency (events per year)
    lga_stats['years_covered'] = (
        (lga_stats['last_event_date'] - lga_stats['first_event_date']).dt.days / 365.25
    )
    lga_stats['events_per_year'] = (
        lga_stats['num_events'] / lga_stats['years_covered'].clip(lower=1)
    ).round(2)
    
    print(f"✅ Created statistics for {len(lga_stats)} LGAs")
    
    # ========================================================================
    # Create state-level summary
    # ========================================================================
    
    print("\n🗺️  Creating state-level statistics...")
    
    state_stats = df_clean.groupby('state').agg({
        'idps_present': ['sum', 'mean', 'count'],
        'lga': 'nunique',
        'date': ['min', 'max']
    }).reset_index()
    
    state_stats.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                           for col in state_stats.columns.values]
    
    state_stats = state_stats.rename(columns={
        'idps_present_sum': 'total_idps',
        'idps_present_mean': 'mean_idps_per_event',
        'idps_present_count': 'num_events',
        'lga_nunique': 'num_lgas_affected',
        'date_min': 'first_event',
        'date_max': 'last_event'
    })
    
    # ========================================================================
    # Save processed data
    # ========================================================================
    
    print("\n💾 Saving processed files...")
    
    # 1. Full cleaned dataset
    output_full = f"{output_dir}/dtm_displacement_data_cleaned.csv"
    df_clean.to_csv(output_full, index=False)
    print(f"✅ Saved: {output_full} ({len(df_clean):,} records)")
    
    # 2. Monthly aggregated events
    output_monthly = f"{output_dir}/displacement_events_monthly.csv"
    events_monthly.to_csv(output_monthly, index=False)
    print(f"✅ Saved: {output_monthly} ({len(events_monthly):,} events)")
    
    # 3. LGA statistics
    output_lga = f"{output_dir}/displacement_statistics_by_lga.csv"
    lga_stats.to_csv(output_lga, index=False)
    print(f"✅ Saved: {output_lga} ({len(lga_stats)} LGAs)")
    
    # 4. State statistics
    output_state = f"{output_dir}/displacement_statistics_by_state.csv"
    state_stats.to_csv(output_state, index=False)
    print(f"✅ Saved: {output_state} ({len(state_stats)} states)")
    
    # 5. Excel with all sheets
    output_excel = f"{output_dir}/dtm_displacement_processed.xlsx"
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_clean.to_excel(writer, sheet_name='All_Records', index=False)
        events_monthly.to_excel(writer, sheet_name='Monthly_Events', index=False)
        lga_stats.to_excel(writer, sheet_name='LGA_Statistics', index=False)
        state_stats.to_excel(writer, sheet_name='State_Statistics', index=False)
    print(f"✅ Saved: {output_excel}")
    
    # ========================================================================
    # Print summary
    # ========================================================================
    
    print_processing_summary(df_clean, events_monthly, lga_stats, state_stats)
    
    return df_clean, events_monthly, lga_stats, state_stats


def categorize_hazard(reason):
    """Categorize displacement reason into primary hazard type"""
    if pd.isna(reason):
        return 'Unknown'
    
    reason_lower = reason.lower()
    
    # Priority order: Natural disaster > Conflict > Insecurity
    if 'natural disaster' in reason_lower:
        return 'Natural Disaster'
    elif 'conflict' in reason_lower:
        return 'Conflict'
    elif 'insecurity' in reason_lower:
        return 'Insecurity'
    else:
        return 'Other'


def print_processing_summary(df_clean, events_monthly, lga_stats, state_stats):
    """Print summary of processed data"""
    
    print("\n" + "="*70)
    print("PROCESSING SUMMARY")
    print("="*70)
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Original records:        {len(df_clean):,}")
    print(f"   Monthly events:          {len(events_monthly):,}")
    print(f"   LGAs with data:          {len(lga_stats)}")
    print(f"   States with data:        {len(state_stats)}")
    
    print(f"\n📅 Temporal Coverage:")
    print(f"   Date range:              {df_clean['date'].min()} to {df_clean['date'].max()}")
    print(f"   Years covered:           {df_clean['year'].nunique()}")
    print(f"   DTM rounds:              {df_clean['dtm_round'].min()} to {df_clean['dtm_round'].max()}")
    
    print(f"\n👥 Displacement Statistics:")
    print(f"   Total IDPs (all time):   {df_clean['idps_present'].sum():,}")
    print(f"   Mean IDPs per record:    {df_clean['idps_present'].mean():,.0f}")
    print(f"   Median IDPs per record:  {df_clean['idps_present'].median():,.0f}")
    print(f"   Max IDPs single event:   {df_clean['idps_present'].max():,}")
    
    print(f"\n🌊 Displacement by Primary Hazard:")
    for hazard, count in df_clean['primary_hazard'].value_counts().items():
        total_idps = df_clean[df_clean['primary_hazard'] == hazard]['idps_present'].sum()
        pct = total_idps / df_clean['idps_present'].sum() * 100
        print(f"   {hazard:20s} {count:5,} records, {total_idps:12,} IDPs ({pct:5.1f}%)")
    
    print(f"\n🏆 Top 5 Most Affected States:")
    top_states = state_stats.nlargest(5, 'total_idps')[['state', 'total_idps', 'num_events', 'num_lgas_affected']]
    for _, row in top_states.iterrows():
        print(f"   {row['state']:15s} {row['total_idps']:12,} IDPs, {row['num_events']:4} events, {row['num_lgas_affected']:3} LGAs")
    
    print(f"\n🎯 Top 5 Most Affected LGAs:")
    top_lgas = lga_stats.nlargest(5, 'total_idps_all_time')[['lga', 'state', 'total_idps_all_time', 'num_events']]
    for _, row in top_lgas.iterrows():
        print(f"   {row['lga']:25s} ({row['state']:10s}) {row['total_idps_all_time']:12,} IDPs, {row['num_events']:4} events")
    
    print(f"\n✅ Data Quality:")
    has_gender = df_clean['has_gender_data'].sum()
    pct_gender = has_gender / len(df_clean) * 100
    print(f"   Records with gender data: {has_gender:,} ({pct_gender:.1f}%)")
    print(f"   LGAs with 10+ events:     {(lga_stats['num_events'] >= 10).sum()}")
    print(f"   LGAs with 100+ events:    {(lga_stats['num_events'] >= 100).sum()}")
    
    print("="*70)


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process DTM displacement data for Nigeria IBF system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script processes real DTM (Displacement Tracking Matrix) data from IOM Nigeria.

Input:
  - DTM IDP_Admin2 Excel file with displacement records
  - 8,883 records from 2017-2024
  - Coverage: 7 states, 113 LGAs, 121M+ IDPs

Output files created in data/:
  - dtm_displacement_data_cleaned.csv (full cleaned dataset)
  - displacement_events_monthly.csv (monthly aggregated events)
  - displacement_statistics_by_lga.csv (LGA-level statistics)
  - displacement_statistics_by_state.csv (state-level statistics)
  - dtm_displacement_processed.xlsx (all sheets in one file)

Usage:
  python process_dtm_data.py
  python process_dtm_data.py --input path/to/dtm_data.xlsx --output data/
        """
    )
    
    parser.add_argument(
        '--input',
        default='/mnt/user-data/uploads/2017_2024_Nigeria_displacement_events.xlsx',
        help='Path to DTM Excel file'
    )
    
    parser.add_argument(
        '--output',
        default='data',
        help='Output directory for processed files'
    )
    
    args = parser.parse_args()
    
    try:
        df_clean, events_monthly, lga_stats, state_stats = process_dtm_displacement_data(
            input_file=args.input,
            output_dir=args.output
        )
        
        print("\n" + "="*70)
        print("✅ PROCESSING COMPLETE!")
        print("="*70)
        print("\nYou now have real historical displacement data ready for:")
        print("• Model calibration and validation")
        print("• Historical trend analysis")
        print("• Vulnerability mapping")
        print("• Forecast model training")
        
        print("\nNext steps:")
        print("1. Link displacement data with hazard data (floods, conflict)")
        print("2. Integrate with exposure data by LGA")
        print("3. Train predictive models")
        print("4. Run forecasts!")
        print("="*70)
        
    except FileNotFoundError:
        print(f"\n❌ Error: Input file not found: {args.input}")
        print("Make sure the DTM data file is in the correct location.")
        exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
