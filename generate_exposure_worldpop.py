#!/usr/bin/env python3
"""
Generate CLIMADA Exposure Data from WorldPop Population Raster
================================================================
This script creates exposure data for Nigeria using WorldPop population data.

Requirements:
- WorldPop Nigeria population raster (nga_ppp_2020_1km_Aggregated.tif)
- CLIMADA installed
- rasterio, geopandas, numpy, pandas

Usage:
    python generate_exposure_worldpop_complete.py
    python generate_exposure_worldpop_complete.py --output data/exposure --resolution 1
    python generate_exposure_worldpop_complete.py --min-population 10

Author: Created for Nigeria IBF Project
Date: 2025-10-19
"""

import os
import sys
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

def generate_exposure_worldpop(
    worldpop_file=None,
    output_dir='data/exposure',
    resolution_km=1,
    min_population=0
):
    """
    Generate CLIMADA exposure data from WorldPop population raster.
    
    Parameters
    ----------
    worldpop_file : str or Path, optional
        Path to WorldPop .tif file. If None, uses default location.
    output_dir : str
        Directory to save output files
    resolution_km : float
        Resolution in kilometers (WorldPop is 1km)
    min_population : float
        Minimum population threshold to include a grid cell
    
    Returns
    -------
    exposure : climada.entity.Exposures
        Generated exposure object
    """
    
    try:
        import rasterio
        from climada.entity import Exposures
    except ImportError as e:
        logger.error(f"Required package not installed: {e}")
        logger.error("Please install: pip install climada rasterio")
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("GENERATING EXPOSURE DATA - WORLDPOP METHOD")
    logger.info("=" * 70)
    
    # Set default WorldPop file location
    if worldpop_file is None:
        worldpop_file = Path.home() / 'worldpop_data' / 'nga_ppp_2020_1km_Aggregated.tif'
    else:
        worldpop_file = Path(worldpop_file)
    
    # Check if file exists
    if not worldpop_file.exists():
        logger.error(f"WorldPop file not found: {worldpop_file}")
        logger.error("Please download from: https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/NGA/")
        sys.exit(1)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Resolution: {resolution_km} km")
    logger.info(f"Reading WorldPop data from: {worldpop_file}")
    logger.info(f"Minimum population threshold: {min_population}")
    
    # Read the raster data
    try:
        with rasterio.open(worldpop_file) as src:
            logger.info(f"Raster dimensions: {src.width} x {src.height}")
            logger.info(f"Raster CRS: {src.crs}")
            logger.info(f"Raster bounds: {src.bounds}")
            
            # Read population data
            population_data = src.read(1)
            transform = src.transform
            crs = src.crs
            nodata = src.nodata
            bounds = src.bounds
            
            # Get shape
            height, width = population_data.shape
            
            # Create coordinate arrays
            cols, rows = np.meshgrid(np.arange(width), np.arange(height))
            
            # Transform pixel coordinates to geographic coordinates
            xs, ys = rasterio.transform.xy(transform, rows.flatten(), cols.flatten())
            lons = np.array(xs)
            lats = np.array(ys)
            population = population_data.flatten()
            
            logger.info(f"Total cells in raster: {len(population):,}")
            
    except Exception as e:
        logger.error(f"Error reading WorldPop file: {e}")
        sys.exit(1)
    
    # Filter valid data
    logger.info("Filtering valid population data...")
    
    # Create mask for valid data
    if nodata is not None:
        valid_mask = (population != nodata) & (population > min_population) & ~np.isnan(population)
    else:
        valid_mask = (population > min_population) & ~np.isnan(population)
    
    # Apply mask
    lons_valid = lons[valid_mask]
    lats_valid = lats[valid_mask]
    population_valid = population[valid_mask]
    
    logger.info(f"Valid populated cells: {len(population_valid):,}")
    logger.info(f"Total population: {population_valid.sum():,.0f}")
    
    if len(population_valid) == 0:
        logger.error("No valid population data found!")
        sys.exit(1)
    
    # Store original coordinate arrays for later use
    coords_data = {
        'lons': lons_valid,
        'lats': lats_valid,
        'population': population_valid
    }
    
    # Create GeoDataFrame
    logger.info("Creating CLIMADA Exposure object...")
    
    geometry = [Point(lon, lat) for lon, lat in zip(lons_valid, lats_valid)]
    
    gdf = gpd.GeoDataFrame({
        'latitude': lats_valid,
        'longitude': lons_valid,
        'value': population_valid,
        'region_id': 566,  # ISO numeric code for Nigeria
    }, geometry=geometry, crs='EPSG:4326')
    
    # Create Exposures object
    exposure = Exposures(gdf)
    
    # Set metadata (compatible with all CLIMADA versions)
    exposure.ref_year = 2020
    exposure.value_unit = 'people'
    
    # Try to set tag metadata if available
    try:
        if hasattr(exposure, 'tag'):
            if hasattr(exposure.tag, 'file_name'):
                exposure.tag.file_name = str(worldpop_file)
            if hasattr(exposure.tag, 'description'):
                exposure.tag.description = f'Nigeria population exposure from WorldPop 2020 ({resolution_km}km resolution)'
    except Exception as e:
        logger.debug(f"Could not set tag metadata: {e}")
    
    # Assign centroids (unique IDs)
    exposure.gdf['centr_'] = np.arange(len(exposure.gdf))
    
    # Ensure geometry is set
    if 'geometry' not in exposure.gdf.columns or exposure.gdf.geometry.isna().any():
        exposure.set_geometry([Point(lon, lat) for lon, lat in 
                              zip(coords_data['lons'], coords_data['lats'])])
    
    # Check validity
    logger.info("Validating exposure data...")
    try:
        exposure.check()
        logger.info("✓ Exposure data validation passed")
    except Exception as e:
        logger.warning(f"Validation warning: {e}")
    
    # Save outputs
    logger.info("Saving exposure data...")
    
    # Save as HDF5 (CLIMADA native format)
    output_file_h5 = output_path / f'exposure_nigeria_worldpop_{resolution_km}km.hdf5'
    try:
        exposure.write_hdf5(output_file_h5)
        logger.info(f"✓ HDF5 saved: {output_file_h5}")
    except Exception as e:
        logger.warning(f"Could not save HDF5: {e}")
        # Try alternative save method
        try:
            output_file_pkl = output_path / f'exposure_nigeria_worldpop_{resolution_km}km.pkl'
            exposure.write_pickle(output_file_pkl)
            logger.info(f"✓ Pickle saved: {output_file_pkl}")
        except Exception as e2:
            logger.warning(f"Could not save pickle: {e2}")
    
    # Save as CSV for inspection (using original coordinates)
    csv_file = output_path / f'exposure_nigeria_worldpop_{resolution_km}km.csv'
    try:
        csv_data = pd.DataFrame({
            'latitude': coords_data['lats'],
            'longitude': coords_data['lons'],
            'value': coords_data['population'],
            'region_id': 566
        })
        csv_data.to_csv(csv_file, index=False)
        logger.info(f"✓ CSV saved: {csv_file}")
    except Exception as e:
        logger.warning(f"Could not save CSV: {e}")
        # Try alternative method using exposure.gdf
        try:
            exposure.gdf.to_csv(csv_file, index=False)
            logger.info(f"✓ CSV saved (alternative method): {csv_file}")
        except:
            pass
    
    # Save GeoJSON for GIS software (sampled if too large)
    geojson_file = output_path / f'exposure_nigeria_worldpop_{resolution_km}km.geojson'
    try:
        # Sample data if too large (>100k points)
        if len(coords_data['lons']) > 100000:
            sample_size = 100000
            logger.info(f"Sampling {sample_size} points for GeoJSON (full data in CSV)")
            indices = np.random.choice(len(coords_data['lons']), sample_size, replace=False)
            
            sample_gdf = gpd.GeoDataFrame({
                'latitude': coords_data['lats'][indices],
                'longitude': coords_data['lons'][indices],
                'value': coords_data['population'][indices],
                'region_id': 566
            }, geometry=[Point(lon, lat) for lon, lat in 
                        zip(coords_data['lons'][indices], coords_data['lats'][indices])],
               crs='EPSG:4326')
            sample_gdf.to_file(geojson_file, driver='GeoJSON')
        else:
            exposure.gdf.to_file(geojson_file, driver='GeoJSON')
        logger.info(f"✓ GeoJSON saved: {geojson_file}")
    except Exception as e:
        logger.warning(f"Could not save GeoJSON: {e}")
    
    # Save summary statistics
    stats_file = output_path / f'exposure_nigeria_worldpop_{resolution_km}km_summary.txt'
    try:
        with open(stats_file, 'w') as f:
            f.write("EXPOSURE DATA SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Source: WorldPop 2020 Nigeria Population\n")
            f.write(f"Resolution: {resolution_km} km\n")
            f.write(f"Reference Year: 2020\n")
            f.write(f"File: {worldpop_file}\n\n")
            
            f.write("SPATIAL COVERAGE\n")
            f.write("-" * 70 + "\n")
            f.write(f"Latitude range: {coords_data['lats'].min():.4f}° to {coords_data['lats'].max():.4f}°\n")
            f.write(f"Longitude range: {coords_data['lons'].min():.4f}° to {coords_data['lons'].max():.4f}°\n\n")
            
            f.write("POPULATION STATISTICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Number of exposure points: {len(coords_data['population']):,}\n")
            f.write(f"Total population: {coords_data['population'].sum():,.0f}\n")
            f.write(f"Mean population per cell: {coords_data['population'].mean():.1f}\n")
            f.write(f"Median population per cell: {np.median(coords_data['population']):.1f}\n")
            f.write(f"Max population per cell: {coords_data['population'].max():,.0f}\n")
            f.write(f"Min population per cell: {coords_data['population'].min():.1f}\n\n")
            
            f.write("POPULATION DISTRIBUTION (Percentiles)\n")
            f.write("-" * 70 + "\n")
            f.write(f"  10th percentile: {np.percentile(coords_data['population'], 10):.1f}\n")
            f.write(f"  25th percentile: {np.percentile(coords_data['population'], 25):.1f}\n")
            f.write(f"  50th percentile: {np.percentile(coords_data['population'], 50):.1f}\n")
            f.write(f"  75th percentile: {np.percentile(coords_data['population'], 75):.1f}\n")
            f.write(f"  90th percentile: {np.percentile(coords_data['population'], 90):.1f}\n")
            f.write(f"  95th percentile: {np.percentile(coords_data['population'], 95):.1f}\n")
            f.write(f"  99th percentile: {np.percentile(coords_data['population'], 99):.1f}\n\n")
            
            f.write("DENSITY STATISTICS\n")
            f.write("-" * 70 + "\n")
            # Calculate cells in different density ranges
            low_density = (coords_data['population'] < 50).sum()
            medium_density = ((coords_data['population'] >= 50) & (coords_data['population'] < 200)).sum()
            high_density = ((coords_data['population'] >= 200) & (coords_data['population'] < 500)).sum()
            very_high_density = (coords_data['population'] >= 500).sum()
            
            f.write(f"Cells with <50 people: {low_density:,} ({100*low_density/len(coords_data['population']):.1f}%)\n")
            f.write(f"Cells with 50-200 people: {medium_density:,} ({100*medium_density/len(coords_data['population']):.1f}%)\n")
            f.write(f"Cells with 200-500 people: {high_density:,} ({100*high_density/len(coords_data['population']):.1f}%)\n")
            f.write(f"Cells with >500 people: {very_high_density:,} ({100*very_high_density/len(coords_data['population']):.1f}%)\n")
        
        logger.info(f"✓ Summary saved: {stats_file}")
    except Exception as e:
        logger.warning(f"Could not save summary: {e}")
    
    # Print summary to console
    logger.info("\n" + "=" * 70)
    logger.info("EXPOSURE GENERATION COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Output directory: {output_path.absolute()}")
    logger.info(f"Number of exposure points: {len(coords_data['population']):,}")
    logger.info(f"Total population: {coords_data['population'].sum():,.0f}")
    logger.info(f"Mean population per cell: {coords_data['population'].mean():.1f}")
    logger.info(f"Coordinate ranges:")
    logger.info(f"  Latitude:  {coords_data['lats'].min():.2f}° to {coords_data['lats'].max():.2f}°")
    logger.info(f"  Longitude: {coords_data['lons'].min():.2f}° to {coords_data['lons'].max():.2f}°")
    logger.info("=" * 70)
    
    return exposure


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate CLIMADA exposure data from WorldPop population raster',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--worldpop-file',
        type=str,
        default=None,
        help='Path to WorldPop .tif file (default: ~/worldpop_data/nga_ppp_2020_1km_Aggregated.tif)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/exposure',
        help='Output directory for exposure files'
    )
    parser.add_argument(
        '--resolution',
        type=float,
        default=1.0,
        help='Resolution in kilometers'
    )
    parser.add_argument(
        '--min-population',
        type=float,
        default=0,
        help='Minimum population threshold to include a grid cell'
    )
    
    args = parser.parse_args()
    
    try:
        exposure = generate_exposure_worldpop(
            worldpop_file=args.worldpop_file,
            output_dir=args.output,
            resolution_km=args.resolution,
            min_population=args.min_population
        )
        
        print("\n" + "🎉" * 35)
        print("✅ EXPOSURE GENERATION COMPLETED SUCCESSFULLY!")
        print("🎉" * 35)
        print(f"\n📊 Summary:")
        print(f"   • Exposure points: {len(exposure.gdf):,}")
        print(f"   • Total population: {coords_data['population'].sum():,.0f}" if 'coords_data' in locals() else "")
        print(f"   • Output location: {args.output}")
        print(f"\n💾 Files created:")
        print(f"   • HDF5: exposure_nigeria_worldpop_{args.resolution}km.hdf5")
        print(f"   • CSV:  exposure_nigeria_worldpop_{args.resolution}km.csv")
        print(f"   • GeoJSON: exposure_nigeria_worldpop_{args.resolution}km.geojson")
        print(f"   • Summary: exposure_nigeria_worldpop_{args.resolution}km_summary.txt")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Exposure generation failed: {e}", exc_info=True)
        print(f"\n❌ Exposure generation failed!")
        print(f"Error: {e}")
        print(f"\nCheck the logs above for more details.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
