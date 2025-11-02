#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download Nigeria Administrative Boundaries - Both Levels
State Level (ADM1) and LGA Level (ADM2)
"""

import geopandas as gpd
import requests
from pathlib import Path

def download_all_boundaries():
    """
    Download both state and LGA level boundaries
    """
    
    print("="*70)
    print("DOWNLOADING NIGERIA ADMINISTRATIVE BOUNDARIES")
    print("="*70)
    
    Path('data').mkdir(exist_ok=True)
    
    # Download State Level (ADM1)
    print("\n1️⃣  STATE LEVEL (ADM1) - 36 States + FCT")
    print("-" * 70)
    state_gdf = download_states()
    
    # Download LGA Level (ADM2)
    print("\n2️⃣  LGA LEVEL (ADM2) - 774 Local Government Areas")
    print("-" * 70)
    lga_gdf = download_lgas()
    
    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD COMPLETE!")
    print("="*70)
    
    if state_gdf is not None:
        print(f"✅ State boundaries: {len(state_gdf)} states")
    else:
        print("❌ State boundaries: Failed")
    
    if lga_gdf is not None:
        print(f"✅ LGA boundaries: {len(lga_gdf)} LGAs")
    else:
        print("❌ LGA boundaries: Failed")
    
    print("\n📁 Files created:")
    for f in Path('data').glob('nigeria_*boundaries*'):
        size = f.stat().st_size / (1024*1024)
        print(f"   {f.name:50s} {size:6.1f} MB")
    
    return state_gdf, lga_gdf


def download_states():
    """Download state-level boundaries"""
    
    try:
        # GeoBoundaries API for ADM1 (State level)
        print("📡 Connecting to GeoBoundaries API (ADM1)...")
        api_url = "https://www.geoboundaries.org/api/current/gbOpen/NGA/ADM1/"
        
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        geojson_url = data['gjDownloadURL']
        print(f"📥 Downloading from: {geojson_url[:60]}...")
        
        gdf = gpd.read_file(geojson_url)
        print(f"✅ Downloaded {len(gdf)} states")
        
        # Clean column names
        gdf = gdf.rename(columns={
            'shapeName': 'state_name',
            'shapeISO': 'state_code',
            'shapeID': 'state_id'
        })
        
        # Add regions
        gdf = add_regions_to_states(gdf)
        
        # Calculate area
        gdf['area_km2'] = gdf.geometry.to_crs('EPSG:3857').area / 1e6
        
        # Save
        output_geojson = 'data/nigeria_state_boundaries.geojson'
        gdf.to_file(output_geojson, driver='GeoJSON')
        print(f"💾 Saved: {output_geojson}")
        
        # Also save shapefile
        gdf.to_file('data/nigeria_state_boundaries.shp')
        
        return gdf
        
    except Exception as e:
        print(f"❌ State download failed: {e}")
        return None


def download_lgas():
    """Download LGA-level boundaries"""
    
    try:
        # GeoBoundaries API for ADM2 (LGA level)
        print("📡 Connecting to GeoBoundaries API (ADM2)...")
        api_url = "https://www.geoboundaries.org/api/current/gbOpen/NGA/ADM2/"
        
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        geojson_url = data['gjDownloadURL']
        print(f"📥 Downloading from: {geojson_url[:60]}...")
        print("⏳ This may take 1-2 minutes...")
        
        gdf = gpd.read_file(geojson_url)
        print(f"✅ Downloaded {len(gdf)} LGAs")
        
        # Clean column names
        column_mapping = {
            'shapeName': 'lga_name',
            'shapeISO': 'lga_code',
            'shapeID': 'lga_id',
            'shapeGroup': 'state_name'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in gdf.columns:
                gdf = gdf.rename(columns={old_col: new_col})
        
        # Add regions
        gdf = add_regions_to_lgas(gdf)
        
        # Calculate area
        gdf['area_km2'] = gdf.geometry.to_crs('EPSG:3857').area / 1e6
        
        # Save
        output_geojson = 'data/nigeria_lga_boundaries.geojson'
        gdf.to_file(output_geojson, driver='GeoJSON')
        print(f"💾 Saved: {output_geojson}")
        
        # Also save shapefile and CSV
        gdf.to_file('data/nigeria_lga_boundaries.shp')
        gdf.drop(columns='geometry').to_csv('data/nigeria_lga_metadata.csv', index=False)
        
        return gdf
        
    except Exception as e:
        print(f"❌ LGA download failed: {e}")
        return None


def add_regions_to_states(gdf):
    """Add geopolitical zones to state boundaries"""
    
    regions = {
        'North_West': ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'],
        'North_East': ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'],
        'North_Central': ['Benue', 'Kogi', 'Kwara', 'Nasarawa', 'Niger', 'Plateau', 'FCT'],
        'South_West': ['Ekiti', 'Lagos', 'Ogun', 'Ondo', 'Osun', 'Oyo'],
        'South_East': ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo'],
        'South_South': ['Akwa Ibom', 'Bayelsa', 'Cross River', 'Delta', 'Edo', 'Rivers']
    }
    
    gdf['region'] = 'Unknown'
    
    if 'state_name' in gdf.columns:
        for region, states in regions.items():
            for state in states:
                mask = gdf['state_name'].str.contains(state, case=False, na=False)
                gdf.loc[mask, 'region'] = region
    
    return gdf


def add_regions_to_lgas(gdf):
    """Add geopolitical zones to LGA boundaries"""
    
    state_to_region = {
        'Jigawa': 'North_West', 'Kaduna': 'North_West', 'Kano': 'North_West',
        'Katsina': 'North_West', 'Kebbi': 'North_West', 'Sokoto': 'North_West',
        'Zamfara': 'North_West',
        'Adamawa': 'North_East', 'Bauchi': 'North_East', 'Borno': 'North_East',
        'Gombe': 'North_East', 'Taraba': 'North_East', 'Yobe': 'North_East',
        'Benue': 'North_Central', 'Kogi': 'North_Central', 'Kwara': 'North_Central',
        'Nasarawa': 'North_Central', 'Niger': 'North_Central', 'Plateau': 'North_Central',
        'FCT': 'North_Central', 'Federal Capital Territory': 'North_Central',
        'Ekiti': 'South_West', 'Lagos': 'South_West', 'Ogun': 'South_West',
        'Ondo': 'South_West', 'Osun': 'South_West', 'Oyo': 'South_West',
        'Abia': 'South_East', 'Anambra': 'South_East', 'Ebonyi': 'South_East',
        'Enugu': 'South_East', 'Imo': 'South_East',
        'Akwa Ibom': 'South_South', 'Bayelsa': 'South_South', 'Cross River': 'South_South',
        'Delta': 'South_South', 'Edo': 'South_South', 'Rivers': 'South_South'
    }
    
    gdf['region'] = 'Unknown'
    
    if 'state_name' in gdf.columns:
        for state, region in state_to_region.items():
            mask = gdf['state_name'].str.contains(state, case=False, na=False)
            gdf.loc[mask, 'region'] = region
    
    return gdf


if __name__ == "__main__":
    
    print("\n🌍 Nigeria Administrative Boundaries Downloader")
    print("   This will download both State and LGA level boundaries\n")
    
    try:
        state_gdf, lga_gdf = download_all_boundaries()
        
        print("\n" + "="*70)
        print("✅ ALL DOWNLOADS COMPLETE!")
        print("="*70)
        print("\nQuick verification:")
        print("  python -c \"import geopandas as gpd; print(f'States: {len(gpd.read_file(\"data/nigeria_state_boundaries.geojson\"))}'); print(f'LGAs: {len(gpd.read_file(\"data/nigeria_lga_boundaries.geojson\"))}')\"")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
