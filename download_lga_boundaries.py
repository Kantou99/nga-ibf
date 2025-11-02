#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download Nigeria Administrative Boundaries - LGA Level (ADM2)
Local Government Areas for detailed forecasting
"""

import geopandas as gpd
import requests
import pandas as pd
from pathlib import Path

def download_nigeria_lga_boundaries():
    """
    Download Nigeria LGA-level (Admin 2) boundaries from GeoBoundaries
    Returns detailed boundaries for all 774 LGAs
    """
    
    print("="*70)
    print("DOWNLOADING NIGERIA LGA BOUNDARIES (ADMIN 2)")
    print("="*70)
    
    # Create data directory
    Path('data').mkdir(exist_ok=True)
    
    # GeoBoundaries API for ADM2 (LGA level)
    print("\n📡 Connecting to GeoBoundaries API...")
    api_url = "https://www.geoboundaries.org/api/current/gbOpen/NGA/ADM2/"
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Get download URL
        geojson_url = data['gjDownloadURL']
        print(f"✅ API response received")
        print(f"📥 Downloading from: {geojson_url[:60]}...")
        
        # Download and read GeoJSON
        print("\n⏳ Downloading LGA boundaries (may take 1-2 minutes)...")
        gdf = gpd.read_file(geojson_url)
        
        print(f"✅ Downloaded {len(gdf)} LGA boundaries")
        
    except Exception as e:
        print(f"❌ GeoBoundaries download failed: {e}")
        print("\n🔄 Trying alternative method...")
        
        # Alternative: Try direct download URL
        backup_url = "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/NGA/ADM2/geoBoundaries-NGA-ADM2.geojson"
        try:
            gdf = gpd.read_file(backup_url)
            print(f"✅ Downloaded {len(gdf)} LGA boundaries (backup source)")
        except:
            print("❌ Backup source also failed")
            print("\n💡 Manual download option:")
            print("   1. Go to: https://www.geoboundaries.org/")
            print("   2. Search for 'Nigeria'")
            print("   3. Download ADM2 level in GeoJSON format")
            print("   4. Save as: data/nigeria_lga_boundaries.geojson")
            return None
    
    # Clean and prepare data
    print("\n🔧 Processing boundary data...")
    
    # Rename columns for clarity
    column_mapping = {
        'shapeName': 'lga_name',
        'shapeISO': 'lga_code',
        'shapeID': 'lga_id',
        'shapeGroup': 'state_name',
        'shapeType': 'admin_level'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in gdf.columns:
            gdf = gdf.rename(columns={old_col: new_col})
    
    # Ensure we have essential columns
    if 'lga_name' not in gdf.columns:
        # Try to find LGA name column
        for col in gdf.columns:
            if 'name' in col.lower():
                gdf = gdf.rename(columns={col: 'lga_name'})
                break
    
    # Add state-level information if available
    if 'state_name' not in gdf.columns:
        for col in gdf.columns:
            if 'group' in col.lower() or 'state' in col.lower():
                gdf = gdf.rename(columns={col: 'state_name'})
                break
    
    # Add regional classification (6 geopolitical zones)
    print("🗺️  Adding regional classifications...")
    gdf = add_regional_classification(gdf)
    
    # Add area calculations
    print("📐 Calculating LGA areas...")
    gdf['area_km2'] = gdf.geometry.to_crs('EPSG:3857').area / 1e6  # Convert to km²
    
    # Sort by state and LGA name
    if 'state_name' in gdf.columns and 'lga_name' in gdf.columns:
        gdf = gdf.sort_values(['state_name', 'lga_name'])
    
    # Save in multiple formats
    print("\n💾 Saving files...")
    
    # 1. GeoJSON (primary format)
    output_geojson = 'data/nigeria_lga_boundaries.geojson'
    gdf.to_file(output_geojson, driver='GeoJSON')
    file_size = Path(output_geojson).stat().st_size / (1024*1024)
    print(f"✅ Saved GeoJSON: {output_geojson} ({file_size:.1f} MB)")
    
    # 2. Shapefile (backup format)
    output_shp = 'data/nigeria_lga_boundaries.shp'
    gdf.to_file(output_shp)
    print(f"✅ Saved Shapefile: {output_shp}")
    
    # 3. CSV with LGA metadata (no geometry)
    output_csv = 'data/nigeria_lga_metadata.csv'
    metadata = gdf.drop(columns='geometry')
    metadata.to_csv(output_csv, index=False)
    print(f"✅ Saved metadata: {output_csv}")
    
    # Print summary
    print_summary(gdf)
    
    return gdf


def add_regional_classification(gdf):
    """
    Add geopolitical zone classification to LGAs
    Nigeria has 6 geopolitical zones
    """
    
    # State to region mapping (36 states + FCT)
    state_to_region = {
        # North West (7 states)
        'Jigawa': 'North_West', 'Kaduna': 'North_West', 'Kano': 'North_West',
        'Katsina': 'North_West', 'Kebbi': 'North_West', 'Sokoto': 'North_West',
        'Zamfara': 'North_West',
        
        # North East (6 states)
        'Adamawa': 'North_East', 'Bauchi': 'North_East', 'Borno': 'North_East',
        'Gombe': 'North_East', 'Taraba': 'North_East', 'Yobe': 'North_East',
        
        # North Central (7 states)
        'Benue': 'North_Central', 'Kogi': 'North_Central', 'Kwara': 'North_Central',
        'Nasarawa': 'North_Central', 'Niger': 'North_Central', 'Plateau': 'North_Central',
        'FCT': 'North_Central', 'Federal Capital Territory': 'North_Central',
        
        # South West (6 states)
        'Ekiti': 'South_West', 'Lagos': 'South_West', 'Ogun': 'South_West',
        'Ondo': 'South_West', 'Osun': 'South_West', 'Oyo': 'South_West',
        
        # South East (5 states)
        'Abia': 'South_East', 'Anambra': 'South_East', 'Ebonyi': 'South_East',
        'Enugu': 'South_East', 'Imo': 'South_East',
        
        # South South (6 states)
        'Akwa Ibom': 'South_South', 'Bayelsa': 'South_South', 'Cross River': 'South_South',
        'Delta': 'South_South', 'Edo': 'South_South', 'Rivers': 'South_South'
    }
    
    # Initialize region column
    gdf['region'] = 'Unknown'
    
    # Try to match states
    if 'state_name' in gdf.columns:
        for state, region in state_to_region.items():
            mask = gdf['state_name'].str.contains(state, case=False, na=False)
            gdf.loc[mask, 'region'] = region
    else:
        # Try to extract state from LGA name or other columns
        for col in gdf.columns:
            if 'state' in col.lower() or 'admin' in col.lower():
                for state, region in state_to_region.items():
                    mask = gdf[col].astype(str).str.contains(state, case=False, na=False)
                    gdf.loc[mask, 'region'] = region
    
    return gdf


def print_summary(gdf):
    """Print detailed summary of LGA boundaries"""
    
    print("\n" + "="*70)
    print("SUMMARY - NIGERIA LGA BOUNDARIES")
    print("="*70)
    
    print(f"\n📊 Basic Statistics:")
    print(f"   Total LGAs:          {len(gdf)}")
    print(f"   CRS:                 {gdf.crs}")
    
    if 'state_name' in gdf.columns:
        n_states = gdf['state_name'].nunique()
        print(f"   States:              {n_states}")
    
    if 'area_km2' in gdf.columns:
        total_area = gdf['area_km2'].sum()
        mean_area = gdf['area_km2'].mean()
        print(f"   Total area:          {total_area:,.0f} km²")
        print(f"   Mean LGA area:       {mean_area:,.0f} km²")
        print(f"   Largest LGA:         {gdf['area_km2'].max():,.0f} km²")
        print(f"   Smallest LGA:        {gdf['area_km2'].min():,.0f} km²")
    
    # Regional breakdown
    if 'region' in gdf.columns:
        print(f"\n🗺️  Regional Distribution:")
        region_counts = gdf['region'].value_counts().sort_index()
        for region, count in region_counts.items():
            print(f"   {region:20s} {count:3d} LGAs")
    
    # State breakdown (top 10)
    if 'state_name' in gdf.columns:
        print(f"\n📍 LGAs by State (Top 10):")
        state_counts = gdf['state_name'].value_counts().head(10)
        for state, count in state_counts.items():
            print(f"   {state:20s} {count:3d} LGAs")
    
    # Column information
    print(f"\n📋 Available Columns:")
    for col in gdf.columns:
        if col != 'geometry':
            print(f"   - {col}")
    
    print("="*70)


def verify_lga_boundaries():
    """
    Verify downloaded LGA boundaries
    """
    
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    
    files_to_check = [
        'data/nigeria_lga_boundaries.geojson',
        'data/nigeria_lga_boundaries.shp',
        'data/nigeria_lga_metadata.csv'
    ]
    
    all_present = True
    for filepath in files_to_check:
        if Path(filepath).exists():
            size = Path(filepath).stat().st_size / (1024*1024)
            print(f"✅ {filepath:45s} ({size:.1f} MB)")
        else:
            print(f"❌ {filepath:45s} MISSING")
            all_present = False
    
    if all_present:
        print("\n✅ All files present!")
        
        # Quick load test
        try:
            gdf = gpd.read_file('data/nigeria_lga_boundaries.geojson')
            print(f"✅ GeoJSON loads successfully ({len(gdf)} LGAs)")
            
            # Check for essential columns
            required_cols = ['lga_name', 'geometry']
            missing_cols = [col for col in required_cols if col not in gdf.columns]
            
            if missing_cols:
                print(f"⚠️  Missing columns: {', '.join(missing_cols)}")
            else:
                print("✅ All essential columns present")
                
        except Exception as e:
            print(f"⚠️  Error loading file: {e}")
    else:
        print("\n❌ Some files missing - run download script")
    
    print("="*70)


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download Nigeria LGA-level (Admin 2) boundaries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download LGA boundaries
  python download_lga_boundaries.py
  
  # Verify existing files
  python download_lga_boundaries.py --verify

Output:
  Creates three files in data/ directory:
  - nigeria_lga_boundaries.geojson (primary format, ~2-5 MB)
  - nigeria_lga_boundaries.shp (shapefile format)
  - nigeria_lga_metadata.csv (LGA information without geometry)

Nigeria has 774 LGAs across 36 states + FCT
        """
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify existing boundary files instead of downloading'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verify:
            verify_lga_boundaries()
        else:
            gdf = download_nigeria_lga_boundaries()
            
            if gdf is not None:
                print("\n" + "="*70)
                print("✅ SUCCESS!")
                print("="*70)
                print("\nYou now have detailed LGA-level boundaries!")
                print("\nNext steps:")
                print("1. Use for detailed spatial analysis")
                print("2. Link with population/exposure data at LGA level")
                print("3. Generate LGA-level forecasts and alerts")
                print("\nQuick test:")
                print("  python -c \"import geopandas as gpd; gdf = gpd.read_file('data/nigeria_lga_boundaries.geojson'); print(f'Loaded {len(gdf)} LGAs')\"")
                print("="*70)
            else:
                print("\n❌ Download failed - see messages above")
                exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
        exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
