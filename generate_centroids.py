#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Nigeria Centroids at 1km Resolution
Compatible with CLIMADA 6.x API
Creates nigeria_centroids_1km.hdf5 for IBF system
"""

import numpy as np
from pathlib import Path
import logging
from climada.hazard import Centroids

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_nigeria_centroids(
    resolution_km: float = 1.0,
    output_file: str = 'nigeria_centroids_1km.hdf5',
    method: str = 'bbox'
) -> Centroids:
    """
    Generate centroids for Nigeria at specified resolution
    
    Args:
        resolution_km: Spatial resolution in kilometers (default: 1.0)
        output_file: Output HDF5 file path (default: 'nigeria_centroids_1km.hdf5')
        method: Generation method - 'bbox' for bounding box (default: 'bbox')
    
    Returns:
        Centroids object
    """
    logger.info(f"Generating Nigeria centroids at {resolution_km}km resolution...")
    logger.info(f"Method: {method}")
    
    # Nigeria bounding box coordinates
    # Longitude: 2.7°E to 14.7°E
    # Latitude: 4.3°N to 13.9°N
    lon_min, lon_max = 2.5, 15.0
    lat_min, lat_max = 4.0, 14.0
    
    logger.info(f"Bounding box: Lon [{lon_min}, {lon_max}], Lat [{lat_min}, {lat_max}]")
    
    # Convert km to degrees (approximate at Nigeria's latitude ~10°N)
    # 1 degree latitude ≈ 111 km (constant)
    # 1 degree longitude ≈ 109 km at 10°N latitude
    res_lat = resolution_km / 111.0
    res_lon = resolution_km / 109.0
    
    logger.info(f"Grid resolution: {res_lat:.5f}° lat, {res_lon:.5f}° lon")
    
    # Create coordinate arrays
    lat = np.arange(lat_min, lat_max, res_lat)
    lon = np.arange(lon_min, lon_max, res_lon)
    
    # Create 2D meshgrid
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    
    # Flatten to 1D arrays (required for Centroids)
    lat_flat = lat_grid.flatten()
    lon_flat = lon_grid.flatten()
    
    n_points = len(lat_flat)
    logger.info(f"Generated {n_points:,} grid points")
    
    # Create centroids using CLIMADA 6.x API
    # Important: Pass lat and lon as keyword arguments
    centroids = Centroids(lat=lat_flat, lon=lon_flat, crs='EPSG:4326')
    
    # Save to HDF5 format
    logger.info(f"Saving centroids to {output_file}...")
    centroids.write_hdf5(output_file)
    
    # Print summary
    print_summary(centroids, output_file)
    
    return centroids


def print_summary(centroids: Centroids, output_file: str):
    """Print summary of generated centroids"""
    
    # Get file size
    file_path = Path(output_file)
    if file_path.exists():
        file_size = file_path.stat().st_size / (1024 * 1024)  # Convert to MB
    else:
        file_size = 0
    
    # Calculate average spacing (for verification)
    lat_sorted = np.sort(centroids.lat)
    lat_diffs = np.diff(lat_sorted)
    lat_diffs = lat_diffs[lat_diffs > 1e-6]  # Remove zeros
    if len(lat_diffs) > 0:
        avg_spacing_km = np.median(lat_diffs) * 111  # Convert to km
    else:
        avg_spacing_km = 0
    
    print("\n" + "="*70)
    print("CENTROIDS GENERATION SUMMARY")
    print("="*70)
    print(f"Output file:      {output_file}")
    print(f"File size:        {file_size:.2f} MB")
    print(f"Number of points: {len(centroids.lat):,}")
    print(f"Longitude range:  {centroids.lon.min():.2f}° to {centroids.lon.max():.2f}°")
    print(f"Latitude range:   {centroids.lat.min():.2f}° to {centroids.lat.max():.2f}°")
    print(f"Avg spacing:      {avg_spacing_km:.2f} km")
    print(f"CRS:              {centroids.crs}")
    print("="*70)
    print("\n✅ Centroids file generated successfully!")
    print(f"   Location: {file_path.absolute()}")


# ============================================================================
# Command Line Interface
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Nigeria centroids for IBF system (CLIMADA 6.x compatible)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 1km resolution centroids (default, ~30 seconds)
  python generate_centroids.py --method bbox
  
  # Generate 5km resolution (faster, for testing, ~5 seconds)
  python generate_centroids.py --resolution 5.0 --output nigeria_centroids_5km.hdf5
  
  # Generate 10km resolution (very fast, for quick tests)
  python generate_centroids.py --resolution 10.0 --output nigeria_centroids_10km.hdf5
  
Output:
  Creates an HDF5 file containing:
  - Latitude and longitude coordinates
  - Coordinate reference system (EPSG:4326)
  - Ready to use with CLIMADA hazard and impact calculations
  
Next Steps:
  1. Move file to data directory: mkdir -p data && mv nigeria_centroids_1km.hdf5 data/
  2. Verify: python -c "from climada.hazard import Centroids; c = Centroids.from_hdf5('nigeria_centroids_1km.hdf5'); print(f'Loaded {len(c.lat):,} centroids')"
  3. Use in forecasts!
        """
    )
    
    parser.add_argument(
        '--method',
        choices=['bbox'],
        default='bbox',
        help='Generation method: bbox = bounding box (includes some border areas)'
    )
    
    parser.add_argument(
        '--resolution',
        type=float,
        default=1.0,
        help='Resolution in kilometers (default: 1.0). Use 5.0 or 10.0 for faster testing.'
    )
    
    parser.add_argument(
        '--output',
        default='nigeria_centroids_1km.hdf5',
        help='Output file path (default: nigeria_centroids_1km.hdf5)'
    )
    
    args = parser.parse_args()
    
    # Generate centroids
    try:
        centroids = generate_nigeria_centroids(
            resolution_km=args.resolution,
            output_file=args.output,
            method=args.method
        )
        
        print("\n" + "="*70)
        print("SUCCESS! You can now use this file in your IBF system.")
        print("="*70)
        print("\nNext steps:")
        print("1. Move file to data directory:")
        print(f"   mkdir -p data && mv {args.output} data/")
        print("")
        print("2. Verify the file:")
        print(f"   python -c \"from climada.hazard import Centroids; c = Centroids.from_hdf5('{args.output}'); print(f'Loaded {{len(c.lat):,}} centroids')\"")
        print("")
        print("3. Update config.py if needed:")
        print(f"   centroids_file: '{args.output}'")
        print("")
        print("4. You're ready to run forecasts!")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Failed to generate centroids: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70)
        print("ERROR: Centroids generation failed!")
        print("="*70)
        print("\nTroubleshooting:")
        print("1. Make sure CLIMADA is installed: pip install climada")
        print("2. Check you have write permissions in this directory")
        print("3. Verify CLIMADA version: python -c \"import climada; print(climada.__version__)\"")
        print("   (This script requires CLIMADA 6.x)")
        print("="*70)
        exit(1)
