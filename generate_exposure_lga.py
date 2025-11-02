#!/usr/bin/env python3
"""
Generate LGA-Aggregated CLIMADA Exposure Data from WorldPop
============================================================
This script creates exposure data for Nigeria aggregated by Local Government Areas (LGAs)
using WorldPop population data.

Requirements:
- WorldPop Nigeria population raster (nga_ppp_2020_1km_Aggregated.tif)
- Nigeria LGA boundaries shapefile
- CLIMADA, rasterio, geopandas, rasterstats

Usage:
    python generate_exposure_lga.py
    python generate_exposure_lga.py --output data/exposure --lga-shapefile path/to/lgas.shp
"""

import os
import sys
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, mapping
import warnings

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def download_nigeria_boundaries():
    """
    Download Nigeria LGA boundaries from GADM or other sources.
    """
    logger.info("Attempting to download Nigeria LGA boundaries...")
    
    try:
        import requests
        
        # Try GADM (Global Administrative Areas)
        gadm_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_NGA_2.json"
        
        logger.info(f"Downloading from GADM: {gadm_url}")
        response = requests.get(gadm_url, timeout=60)
        
        if response.status_code == 200:
            output_file = Path.home() / 'worldpop_data' / 'nigeria_lga_boundaries.json'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✓ Downloaded LGA boundaries to: {output_file}")
            return output_file
        else:
            raise Exception(f"Download failed with status code: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Could not download boundaries: {e}")
        logger.info("Please download manually from:")
        logger.info("  - GADM: https://gadm.org/download_country.html (select Nigeria, level 2)")
        logger.info("  - HDX: https://data.humdata.org/dataset/cod-ab-nga")
        return None


def load_lga_boundaries(lga_shapefile=None):
    """
    Load Nigeria LGA boundaries from shapefile or download if not provided.
    """
    logger.info("Loading LGA boundaries...")
    
    # If no shapefile provided, try to find or download
    if lga_shapefile is None:
        # Check common locations
        possible_paths = [
            Path.home() / 'worldpop_data' / 'nigeria_lga_boundaries.json',
            Path.home() / 'worldpop_data' / 'nigeria_lga_boundaries.geojson',
            Path('data') / 'boundaries' / 'nigeria_lgas.shp',
            Path('data') / 'boundaries' / 'nigeria_lgas.geojson',
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found boundaries at: {path}")
                lga_shapefile = path
                break
        
        if lga_shapefile is None:
            logger.info("No LGA boundaries found locally. Attempting download...")
            lga_shapefile = download_nigeria_boundaries()
            
            if lga_shapefile is None:
                raise FileNotFoundError(
                    "Could not find or download LGA boundaries. "
                    "Please download from GADM or HDX and provide path with --lga-shapefile"
                )
    
    # Load the boundaries
    try:
        lgas = gpd.read_file(lga_shapefile)
        logger.info(f"✓ Loaded {len(lgas)} LGA boundaries")
        
        # Standardize column names
        # Look for name columns (different sources use different names)
        name_columns = ['NAME_2', 'name_2', 'ADM2_EN', 'admin2Name', 'LGA', 'lga_name', 'name']
        lga_name_col = None
        
        for col in name_columns:
            if col in lgas.columns:
                lga_name_col = col
                break
        
        if lga_name_col:
            lgas['lga_name'] = lgas[lga_name_col]
        else:
            logger.warning("Could not find LGA name column. Using index as name.")
            lgas['lga_name'] = [f"LGA_{i}" for i in range(len(lgas))]
        
        # Ensure CRS is WGS84
        if lgas.crs is None or lgas.crs.to_epsg() != 4326:
            logger.info("Reprojecting to EPSG:4326...")
            lgas = lgas.to_crs('EPSG:4326')
        
        return lgas
        
    except Exception as e:
        logger.error(f"Error loading LGA boundaries: {e}")
        raise


def generate_lga_exposure(
    worldpop_file=None,
    lga_shapefile=None,
    output_dir='data/exposure',
    min_population=0
):
    """
    Generate CLIMADA exposure data aggregated by LGA.
    
    Parameters
    ----------
    worldpop_file : str or Path, optional
        Path to WorldPop .tif file
    lga_shapefile : str or Path, optional
        Path to LGA boundaries shapefile
    output_dir : str
        Directory to save output files
    min_population : float
        Minimum population threshold for LGA inclusion
    
    Returns
    -------
    exposure : climada.entity.Exposures
        Generated exposure object
    """
    
    try:
        import rasterio
        from rasterio.mask import mask
        from climada.entity import Exposures
    except ImportError as e:
        logger.error(f"Required package not installed: {e}")
        logger.error("Please install: pip install climada rasterio rasterstats")
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("GENERATING LGA-AGGREGATED EXPOSURE DATA")
    logger.info("=" * 70)
    
    # Set default WorldPop file location
    if worldpop_file is None:
        worldpop_file = Path.home() / 'worldpop_data' / 'nga_ppp_2020_1km_Aggregated.tif'
    else:
        worldpop_file = Path(worldpop_file)
    
    # Check if WorldPop file exists
    if not worldpop_file.exists():
        logger.error(f"WorldPop file not found: {worldpop_file}")
        sys.exit(1)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load LGA boundaries
    lgas = load_lga_boundaries(lga_shapefile)
    
    logger.info(f"Reading WorldPop data from: {worldpop_file}")
    logger.info(f"Processing {len(lgas)} LGAs...")
    
    # Process each LGA
    lga_data = []
    
    with rasterio.open(worldpop_file) as src:
        logger.info(f"WorldPop raster CRS: {src.crs}")
        logger.info(f"WorldPop raster bounds: {src.bounds}")
        
        for idx, lga in lgas.iterrows():
            try:
                # Get LGA geometry
                geom = [mapping(lga.geometry)]
                
                # Mask raster with LGA boundary
                out_image, out_transform = mask(src, geom, crop=True, nodata=src.nodata)
                
                # Sum population in LGA
                population = out_image[out_image > 0].sum()
                
                if population > min_population:
                    # Get LGA centroid for coordinates
                    centroid = lga.geometry.centroid
                    
                    lga_data.append({
                        'lga_name': lga['lga_name'],
                        'latitude': centroid.y,
                        'longitude': centroid.x,
                        'value': float(population),
                        'region_id': 566,  # Nigeria ISO code
                        'geometry': lga.geometry
                    })
                    
                    if (idx + 1) % 50 == 0:
                        logger.info(f"  Processed {idx + 1}/{len(lgas)} LGAs...")
                        
            except Exception as e:
                logger.warning(f"  Could not process LGA {lga.get('lga_name', idx)}: {e}")
                continue
    
    logger.info(f"✓ Processed all LGAs")
    logger.info(f"Valid LGAs with population: {len(lga_data)}")
    
    if len(lga_data) == 0:
        logger.error("No LGAs with valid population data found!")
        sys.exit(1)
    
    # Create GeoDataFrame
    logger.info("Creating CLIMADA Exposure object...")
    gdf = gpd.GeoDataFrame(lga_data, crs='EPSG:4326')
    
    # Create Exposures object
    exposure = Exposures(gdf)
    
    # Set metadata
    exposure.ref_year = 2020
    exposure.value_unit = 'people'
    
    try:
        if hasattr(exposure, 'tag'):
            if hasattr(exposure.tag, 'description'):
                exposure.tag.description = 'Nigeria LGA-aggregated population exposure from WorldPop 2020'
    except:
        pass
    
    # Validate
    logger.info("Validating exposure data...")
    try:
        exposure.check()
        logger.info("✓ Exposure data validation passed")
    except Exception as e:
        logger.warning(f"Validation warning: {e}")
    
    # Save outputs
    logger.info("Saving exposure data...")
    
    # Save as HDF5
    output_file_h5 = output_path / 'exposure_nigeria_lga_aggregated.hdf5'
    try:
        exposure.write_hdf5(output_file_h5)
        logger.info(f"✓ HDF5 saved: {output_file_h5}")
    except Exception as e:
        logger.warning(f"Could not save HDF5: {e}")
    
    # Save as CSV
    csv_file = output_path / 'exposure_nigeria_lga_aggregated.csv'
    csv_data = gdf.drop(columns=['geometry']).copy()
    csv_data.to_csv(csv_file, index=False)
    logger.info(f"✓ CSV saved: {csv_file}")
    
    # Save as GeoJSON
    geojson_file = output_path / 'exposure_nigeria_lga_aggregated.geojson'
    gdf.to_file(geojson_file, driver='GeoJSON')
    logger.info(f"✓ GeoJSON saved: {geojson_file}")
    
    # Save summary statistics
    stats_file = output_path / 'exposure_nigeria_lga_aggregated_summary.txt'
    with open(stats_file, 'w') as f:
        f.write("LGA-AGGREGATED EXPOSURE DATA SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Source: WorldPop 2020 Nigeria Population\n")
        f.write(f"Aggregation Level: Local Government Areas (LGAs)\n")
        f.write(f"Reference Year: 2020\n\n")
        
        f.write("COVERAGE\n")
        f.write("-" * 70 + "\n")
        f.write(f"Number of LGAs: {len(gdf)}\n")
        f.write(f"Total population: {gdf['value'].sum():,.0f}\n\n")
        
        f.write("POPULATION STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Mean population per LGA: {gdf['value'].mean():,.1f}\n")
        f.write(f"Median population per LGA: {gdf['value'].median():,.1f}\n")
        f.write(f"Max population (LGA): {gdf['value'].max():,.0f}\n")
        f.write(f"Min population (LGA): {gdf['value'].min():,.0f}\n\n")
        
        f.write("TOP 10 MOST POPULATED LGAs\n")
        f.write("-" * 70 + "\n")
        top10 = gdf.nlargest(10, 'value')[['lga_name', 'value']]
        for i, row in top10.iterrows():
            f.write(f"{row['lga_name']:<40} {row['value']:>15,.0f}\n")
    
    logger.info(f"✓ Summary saved: {stats_file}")
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("LGA-AGGREGATED EXPOSURE GENERATION COMPLETED")
    logger.info("=" * 70)
    logger.info(f"Output directory: {output_path.absolute()}")
    logger.info(f"Number of LGAs: {len(gdf)}")
    logger.info(f"Total population: {gdf['value'].sum():,.0f}")
    logger.info(f"Mean population per LGA: {gdf['value'].mean():,.1f}")
    logger.info("\nTop 5 Most Populated LGAs:")
    for i, row in gdf.nlargest(5, 'value').iterrows():
        logger.info(f"  {row['lga_name']}: {row['value']:,.0f}")
    logger.info("=" * 70)
    
    return exposure


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate LGA-aggregated CLIMADA exposure data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--worldpop-file',
        type=str,
        default=None,
        help='Path to WorldPop .tif file'
    )
    parser.add_argument(
        '--lga-shapefile',
        type=str,
        default=None,
        help='Path to LGA boundaries shapefile/geojson'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/exposure',
        help='Output directory'
    )
    parser.add_argument(
        '--min-population',
        type=float,
        default=0,
        help='Minimum population threshold for LGA inclusion'
    )
    
    args = parser.parse_args()
    
    try:
        exposure = generate_lga_exposure(
            worldpop_file=args.worldpop_file,
            lga_shapefile=args.lga_shapefile,
            output_dir=args.output,
            min_population=args.min_population
        )
        
        print("\n" + "🎉" * 35)
        print("✅ LGA-AGGREGATED EXPOSURE GENERATION COMPLETED!")
        print("🎉" * 35)
        print(f"\n📊 Summary:")
        print(f"   • Number of LGAs: {len(exposure.gdf)}")
        print(f"   • Total population: {exposure.gdf['value'].sum():,.0f}")
        print(f"   • Output location: {args.output}")
        print(f"\n💾 Files created:")
        print(f"   • HDF5: exposure_nigeria_lga_aggregated.hdf5")
        print(f"   • CSV:  exposure_nigeria_lga_aggregated.csv")
        print(f"   • GeoJSON: exposure_nigeria_lga_aggregated.geojson")
        print(f"   • Summary: exposure_nigeria_lga_aggregated_summary.txt")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"LGA exposure generation failed: {e}", exc_info=True)
        print(f"\n❌ LGA exposure generation failed!")
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
