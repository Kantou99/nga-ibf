#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download Nigeria Administrative Boundaries
LGA (774) and State (37) boundaries from geoBoundaries
"""

import requests
import geopandas as gpd
from pathlib import Path
import time

def download_nigeria_boundaries(output_dir='data'):
    """
    Download Nigeria administrative boundaries from geoBoundaries API
    
    Downloads:
    - ADM1 (States): 37 states + FCT
    - ADM2 (LGAs): 774 Local Government Areas
    
    Args:
        output_dir: Directory to save files
    """
    
    print("="*70)
    print("DOWNLOADING NIGERIA ADMINISTRATIVE BOUNDARIES")
    print("="*70)
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # geoBoundaries API URLs
    base_url = "https://www.geoboundaries.org/api/current/gbOpen"
    
    boundaries = {
        'ADM1': {
            'name': 'States',
            'count': 37,
            'output': f'{output_dir}/nigeria_state_boundaries.geojson'
        },
        'ADM2': {
            'name': 'LGAs',
            'count': 774,
            'output': f'{output_dir}/nigeria_lga_boundaries.geojson'
        }
    }
    
    downloaded_files = []
    
    for adm_level, info in boundaries.items():
        print(f"\n{'='*70}")
        print(f"Downloading {info['name']} ({adm_level})")
        print('='*70)
        
        try:
            # Get metadata
            print(f"\n1. Fetching metadata from geoBoundaries...")
            api_url = f"{base_url}/NGA/{adm_level}/"
            
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            metadata = response.json()
            download_url = metadata['gjDownloadURL']
            
            print(f"✅ Metadata retrieved")
            print(f"   Source: {metadata.get('boundarySourceName', 'geoBoundaries')}")
            print(f"   Year: {metadata.get('boundaryYearRepresented', 'N/A')}")
            print(f"   License: {metadata.get('boundaryLicense', 'Open')}")
            
            # Download GeoJSON
            print(f"\n2. Downloading {info['name']} GeoJSON...")
            gdf = gpd.read_file(download_url)
            
            print(f"✅ Downloaded {len(gdf)} {info['name']}")
            
            # Validate
            if len(gdf) < info['count'] * 0.8:  # Allow some variance
                print(f"⚠️  Warning: Expected ~{info['count']}, got {len(gdf)}")
            
            # Show columns
            print(f"\n3. Data structure:")
            print(f"   Columns: {list(gdf.columns)}")
            print(f"   CRS: {gdf.crs}")
            
            # Save GeoJSON
            print(f"\n4. Saving to: {info['output']}")
            gdf.to_file(info['output'], driver='GeoJSON')
            
            file_size = Path(info['output']).stat().st_size / (1024*1024)
            print(f"✅ Saved successfully ({file_size:.1f} MB)")
            
            # Also save as shapefile for backup
            shp_dir = f"{output_dir}/shapefiles/{adm_level.lower()}"
            Path(shp_dir).mkdir(parents=True, exist_ok=True)
            shp_file = f"{shp_dir}/nigeria_{adm_level.lower()}.shp"
            gdf.to_file(shp_file)
            print(f"✅ Backup shapefile: {shp_file}")
            
            # Sample data
            print(f"\n5. Sample {info['name']}:")
            name_col = [col for col in gdf.columns if 'name' in col.lower()]
            if name_col:
                sample = gdf[name_col[0]].head(5).tolist()
                for i, name in enumerate(sample, 1):
                    print(f"   {i}. {name}")
            
            downloaded_files.append(info['output'])
            
            # Be nice to the API
            time.sleep(2)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error downloading {info['name']}: {e}")
            print(f"   Try manual download from: https://www.geoboundaries.org/")
            continue
        
        except Exception as e:
            print(f"❌ Error processing {info['name']}: {e}")
            continue
    
    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    
    if len(downloaded_files) == 2:
        print("\n✅ SUCCESS! All boundaries downloaded!")
        print(f"\nFiles created:")
        for f in downloaded_files:
            size = Path(f).stat().st_size / (1024*1024)
            print(f"   📄 {f} ({size:.1f} MB)")
        
        print(f"\n📁 Backup shapefiles:")
        print(f"   📁 {output_dir}/shapefiles/adm1/")
        print(f"   📁 {output_dir}/shapefiles/adm2/")
        
        print("\n🎯 Next steps:")
        print("   1. Run: python integrate_data.py")
        print("   2. This will merge boundaries with your risk data")
        print("   3. Then you can create maps and build models!")
        
    elif len(downloaded_files) == 1:
        print(f"\n⚠️  Partial success: {len(downloaded_files)}/2 downloaded")
        print("   Try running again or download manually")
    
    else:
        print("\n❌ Download failed")
        print("   Alternative: Download manually from:")
        print("   https://www.geoboundaries.org/downloadCGAZ.html")
        print("   Select: Nigeria → ADM1 & ADM2 → Download GeoJSON")
    
    print("="*70)
    
    return downloaded_files


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download Nigeria administrative boundaries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Downloads from geoBoundaries (https://www.geoboundaries.org/):
  - ADM1: 37 states + FCT
  - ADM2: 774 Local Government Areas (LGAs)

Saves as:
  - GeoJSON files (main format)
  - Shapefiles (backup)

Usage:
  python download_boundaries.py
  python download_boundaries.py --output data/
        """
    )
    
    parser.add_argument(
        '--output',
        default='data',
        help='Output directory (default: data/)'
    )
    
    args = parser.parse_args()
    
    try:
        files = download_nigeria_boundaries(args.output)
        
        if len(files) == 2:
            print("\n✅ Ready for next step: python integrate_data.py")
            exit(0)
        else:
            exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
