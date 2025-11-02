#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Nigeria Exposure Data
Population and asset exposure for impact-based forecasting
Multiple methods: CLIMADA LitPop, WorldPop, or custom aggregation
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_exposure_litpop(resolution_arcsec=30, save_format='both'):
    """
    Generate exposure using CLIMADA LitPop (Lit: Nightlight + Pop: Population)
    This is the recommended method - combines GDP and population data
    
    Args:
        resolution_arcsec: Resolution in arc seconds (30 = ~1km, 150 = ~5km)
        save_format: 'csv', 'hdf5', or 'both'
    
    Returns:
        Exposure dataframe
    """
    
    print("="*70)
    print("GENERATING EXPOSURE DATA - CLIMADA LITPOP METHOD")
    print("="*70)
    
    logger.info(f"Resolution: {resolution_arcsec} arcsec (~{resolution_arcsec/30:.1f} km)")
    
    try:
        from climada.entity import LitPop
        
        logger.info("Generating LitPop exposure for Nigeria...")
        logger.info("This may take 5-15 minutes depending on resolution...")
        
        # Generate exposure
        # fin_mode options: 'income' (default), 'gdp', 'pc', 'pop'
        exposure = LitPop.from_countries(
            countries=['NGA'],
            res_arcsec=resolution_arcsec,
            fin_mode='income'  # Income-based (combines GDP + population)
        )
        
        logger.info(f"Generated exposure for {len(exposure.gdf):,} points")
        
        # Convert to DataFrame
        df = exposure.gdf.copy()
        
        # Rename columns for clarity
        df = df.rename(columns={
            'latitude': 'lat',
            'longitude': 'lon',
            'value': 'exposure_value_usd',
            'region_id': 'admin_region'
        })
        
        # Add metadata
        df['exposure_type'] = 'litpop'
        df['resolution_km'] = resolution_arcsec / 30.0
        df['data_source'] = 'CLIMADA_LitPop'
        df['generated_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Save in requested format(s)
        Path('data').mkdir(exist_ok=True)
        
        if save_format in ['csv', 'both']:
            # Save as CSV (without geometry for smaller file)
            csv_file = 'data/nigeria_exposure.csv'
            df_csv = df.drop(columns='geometry') if 'geometry' in df.columns else df
            df_csv.to_csv(csv_file, index=False)
            file_size = Path(csv_file).stat().st_size / (1024*1024)
            logger.info(f"Saved CSV: {csv_file} ({file_size:.1f} MB)")
        
        if save_format in ['hdf5', 'both']:
            # Save as HDF5 (faster loading, compressed)
            hdf5_file = 'data/nigeria_exposure.hdf5'
            exposure.write_hdf5(hdf5_file)
            file_size = Path(hdf5_file).stat().st_size / (1024*1024)
            logger.info(f"Saved HDF5: {hdf5_file} ({file_size:.1f} MB)")
        
        # Print summary statistics
        print_exposure_summary(df)
        
        return df
        
    except ImportError:
        logger.error("CLIMADA not installed or LitPop not available")
        logger.error("Install with: pip install climada")
        return None
    
    except Exception as e:
        logger.error(f"LitPop generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def aggregate_exposure_by_lga(exposure_df, lga_boundaries_file='data/nigeria_lga_boundaries.geojson'):
    """
    Aggregate exposure data to LGA level
    This creates LGA-level summaries for easier analysis
    
    Args:
        exposure_df: DataFrame with exposure data (lat, lon, exposure_value_usd)
        lga_boundaries_file: Path to LGA boundaries GeoJSON
    
    Returns:
        GeoDataFrame with LGA-level aggregated exposure
    """
    
    print("\n" + "="*70)
    print("AGGREGATING EXPOSURE BY LGA")
    print("="*70)
    
    try:
        # Load LGA boundaries
        logger.info(f"Loading LGA boundaries from {lga_boundaries_file}...")
        lga_gdf = gpd.read_file(lga_boundaries_file)
        logger.info(f"Loaded {len(lga_gdf)} LGAs")
        
        # Convert exposure to GeoDataFrame if not already
        if 'geometry' not in exposure_df.columns:
            from shapely.geometry import Point
            logger.info("Converting exposure points to GeoDataFrame...")
            geometry = [Point(lon, lat) for lon, lat in zip(exposure_df['lon'], exposure_df['lat'])]
            exposure_gdf = gpd.GeoDataFrame(exposure_df, geometry=geometry, crs='EPSG:4326')
        else:
            exposure_gdf = gpd.GeoDataFrame(exposure_df, crs='EPSG:4326')
        
        # Ensure both have same CRS
        if lga_gdf.crs != exposure_gdf.crs:
            lga_gdf = lga_gdf.to_crs(exposure_gdf.crs)
        
        # Spatial join - assign each exposure point to an LGA
        logger.info("Performing spatial join (this may take a few minutes)...")
        joined = gpd.sjoin(exposure_gdf, lga_gdf, how='left', predicate='within')
        
        # Aggregate by LGA
        logger.info("Aggregating statistics by LGA...")
        
        # Group by LGA and calculate statistics
        agg_cols = {}
        if 'exposure_value_usd' in joined.columns:
            agg_cols['exposure_value_usd'] = ['sum', 'mean', 'count']
        
        lga_stats = joined.groupby('lga_name').agg(agg_cols)
        lga_stats.columns = ['_'.join(col).strip() for col in lga_stats.columns.values]
        lga_stats = lga_stats.reset_index()
        
        # Merge with LGA geometries
        lga_exposure = lga_gdf.merge(lga_stats, on='lga_name', how='left')
        
        # Fill NaN with 0 for LGAs with no exposure points
        for col in lga_exposure.columns:
            if 'exposure' in col and lga_exposure[col].dtype in [np.float64, np.int64]:
                lga_exposure[col] = lga_exposure[col].fillna(0)
        
        # Rename columns
        lga_exposure = lga_exposure.rename(columns={
            'exposure_value_usd_sum': 'total_exposure_usd',
            'exposure_value_usd_mean': 'mean_exposure_usd',
            'exposure_value_usd_count': 'n_exposure_points'
        })
        
        # Save
        output_file = 'data/nigeria_exposure_by_lga.geojson'
        lga_exposure.to_file(output_file, driver='GeoJSON')
        file_size = Path(output_file).stat().st_size / (1024*1024)
        logger.info(f"Saved LGA aggregation: {output_file} ({file_size:.1f} MB)")
        
        # Also save CSV
        csv_file = 'data/nigeria_exposure_by_lga.csv'
        lga_exposure.drop(columns='geometry').to_csv(csv_file, index=False)
        
        # Print summary
        print_lga_exposure_summary(lga_exposure)
        
        return lga_exposure
        
    except Exception as e:
        logger.error(f"LGA aggregation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def download_worldpop_data(year=2020, output_file='data/nigeria_population_worldpop.tif'):
    """
    Download population raster from WorldPop
    Alternative to LitPop - pure population data
    
    Args:
        year: Year of population data (2000-2020)
        output_file: Where to save the raster
    
    Returns:
        Path to downloaded file or None
    """
    
    print("\n" + "="*70)
    print("DOWNLOADING WORLDPOP POPULATION DATA")
    print("="*70)
    
    import requests
    
    filename = f"nga_ppp_{year}_1km_Aggregated.tif"
    url = f"https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/{year}/NGA/{filename}"
    
    logger.info(f"Downloading Nigeria population for {year}...")
    logger.info(f"URL: {url}")
    logger.info("File size: ~50 MB, may take 5-10 minutes...")
    
    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        Path(output_file).parent.mkdir(exist_ok=True)
        
        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024  # 1 MB
        downloaded = 0
        
        with open(output_file, 'wb') as f:
            for data in response.iter_content(block_size):
                downloaded += len(data)
                f.write(data)
                if total_size:
                    progress = (downloaded / total_size) * 100
                    print(f"Progress: {progress:.1f}% ({downloaded/(1024*1024):.1f} MB)", end='\r')
        
        print()  # New line after progress
        logger.info(f"Downloaded: {output_file}")
        
        # Verify with rasterio
        try:
            import rasterio
            with rasterio.open(output_file) as src:
                logger.info(f"Shape: {src.shape}")
                logger.info(f"CRS: {src.crs}")
                data = src.read(1)
                total_pop = data[data > 0].sum()
                logger.info(f"Total population: {total_pop:,.0f}")
        except ImportError:
            logger.warning("Install rasterio to verify raster: pip install rasterio")
        
        return output_file
        
    except Exception as e:
        logger.error(f"WorldPop download failed: {e}")
        return None


def create_exposure_from_population_raster(
    raster_file,
    centroids_file='data/nigeria_centroids_1km.hdf5',
    gdp_per_capita=2200
):
    """
    Create exposure from population raster + GDP per capita
    
    Args:
        raster_file: Path to population raster (e.g., from WorldPop)
        centroids_file: Path to centroids file
        gdp_per_capita: GDP per capita in USD (Nigeria ~$2200)
    
    Returns:
        Exposure DataFrame
    """
    
    print("\n" + "="*70)
    print("CREATING EXPOSURE FROM POPULATION RASTER")
    print("="*70)
    
    try:
        import rasterio
        from climada.hazard import Centroids
        
        # Load centroids
        logger.info(f"Loading centroids from {centroids_file}...")
        centroids = Centroids.from_hdf5(centroids_file)
        logger.info(f"Loaded {len(centroids.lat):,} centroids")
        
        # Load population raster
        logger.info(f"Loading population raster from {raster_file}...")
        with rasterio.open(raster_file) as src:
            # Sample population at each centroid
            coords = [(lon, lat) for lon, lat in zip(centroids.lon, centroids.lat)]
            population = np.array([val[0] if val[0] > 0 else 0 for val in src.sample(coords)])
        
        logger.info(f"Sampled population for {len(population):,} points")
        
        # Calculate exposure (population × GDP per capita)
        exposure_value = population * gdp_per_capita
        
        # Create DataFrame
        df = pd.DataFrame({
            'lat': centroids.lat,
            'lon': centroids.lon,
            'population': population,
            'gdp_per_capita_usd': gdp_per_capita,
            'exposure_value_usd': exposure_value,
            'exposure_type': 'population_gdp',
            'data_source': 'WorldPop',
            'generated_date': datetime.now().strftime('%Y-%m-%d')
        })
        
        # Remove zero-population points
        df = df[df['population'] > 0].reset_index(drop=True)
        
        logger.info(f"Created exposure for {len(df):,} populated points")
        
        # Save
        output_file = 'data/nigeria_exposure.csv'
        df.to_csv(output_file, index=False)
        file_size = Path(output_file).stat().st_size / (1024*1024)
        logger.info(f"Saved: {output_file} ({file_size:.1f} MB)")
        
        print_exposure_summary(df)
        
        return df
        
    except ImportError as e:
        logger.error(f"Missing required package: {e}")
        logger.error("Install with: pip install rasterio")
        return None
    
    except Exception as e:
        logger.error(f"Exposure creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_exposure_summary(df):
    """Print summary statistics of exposure data"""
    
    print("\n" + "="*70)
    print("EXPOSURE DATA SUMMARY")
    print("="*70)
    
    print(f"\n📊 Basic Statistics:")
    print(f"   Total points:        {len(df):,}")
    
    if 'lat' in df.columns:
        print(f"   Latitude range:      {df['lat'].min():.2f}° to {df['lat'].max():.2f}°")
    if 'lon' in df.columns:
        print(f"   Longitude range:     {df['lon'].min():.2f}° to {df['lon'].max():.2f}°")
    
    if 'exposure_value_usd' in df.columns:
        total_exp = df['exposure_value_usd'].sum()
        mean_exp = df['exposure_value_usd'].mean()
        median_exp = df['exposure_value_usd'].median()
        max_exp = df['exposure_value_usd'].max()
        
        print(f"\n💰 Exposure Values (USD):")
        print(f"   Total exposure:      ${total_exp:,.0f}")
        print(f"   Mean per point:      ${mean_exp:,.0f}")
        print(f"   Median per point:    ${median_exp:,.0f}")
        print(f"   Max per point:       ${max_exp:,.0f}")
    
    if 'population' in df.columns:
        total_pop = df['population'].sum()
        print(f"\n👥 Population:")
        print(f"   Total population:    {total_pop:,.0f}")
        print(f"   Mean per point:      {df['population'].mean():,.0f}")
    
    if 'exposure_type' in df.columns:
        print(f"\n📋 Metadata:")
        print(f"   Exposure type:       {df['exposure_type'].iloc[0]}")
    if 'data_source' in df.columns:
        print(f"   Data source:         {df['data_source'].iloc[0]}")
    if 'generated_date' in df.columns:
        print(f"   Generated:           {df['generated_date'].iloc[0]}")
    
    print("="*70)


def print_lga_exposure_summary(gdf):
    """Print summary of LGA-aggregated exposure"""
    
    print("\n" + "="*70)
    print("LGA-LEVEL EXPOSURE SUMMARY")
    print("="*70)
    
    print(f"\n📊 Coverage:")
    print(f"   Total LGAs:          {len(gdf)}")
    
    if 'total_exposure_usd' in gdf.columns:
        lgas_with_data = (gdf['total_exposure_usd'] > 0).sum()
        print(f"   LGAs with exposure:  {lgas_with_data}")
        print(f"   LGAs with no data:   {len(gdf) - lgas_with_data}")
        
        print(f"\n💰 Exposure Statistics:")
        print(f"   Total exposure:      ${gdf['total_exposure_usd'].sum():,.0f}")
        print(f"   Mean per LGA:        ${gdf['total_exposure_usd'].mean():,.0f}")
        print(f"   Median per LGA:      ${gdf['total_exposure_usd'].median():,.0f}")
        
        # Top 10 LGAs by exposure
        print(f"\n🏆 Top 10 LGAs by Exposure:")
        top10 = gdf.nlargest(10, 'total_exposure_usd')[['lga_name', 'state_name', 'total_exposure_usd']]
        for idx, row in top10.iterrows():
            print(f"   {row['lga_name']:25s} ({row['state_name']:15s}) ${row['total_exposure_usd']:,.0f}")
    
    print("="*70)


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Nigeria exposure data for IBF system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Methods:
  litpop      - CLIMADA LitPop (GDP + population) [RECOMMENDED]
  worldpop    - WorldPop population raster + GDP calculation
  
Examples:
  # Generate using LitPop (recommended, 5-15 minutes)
  python generate_exposure.py --method litpop --resolution 30
  
  # Generate using LitPop at 5km resolution (faster, for testing)
  python generate_exposure.py --method litpop --resolution 150
  
  # Download WorldPop and generate exposure
  python generate_exposure.py --method worldpop
  
  # Aggregate existing exposure to LGA level
  python generate_exposure.py --aggregate-lga

Output:
  Creates in data/ directory:
  - nigeria_exposure.csv (point-level exposure)
  - nigeria_exposure.hdf5 (HDF5 format, optional)
  - nigeria_exposure_by_lga.geojson (LGA-aggregated)
  - nigeria_exposure_by_lga.csv (LGA-aggregated, no geometry)
        """
    )
    
    parser.add_argument(
        '--method',
        choices=['litpop', 'worldpop'],
        default='litpop',
        help='Method to generate exposure data'
    )
    
    parser.add_argument(
        '--resolution',
        type=int,
        default=30,
        help='Resolution in arc seconds (30≈1km, 150≈5km, 300≈10km)'
    )
    
    parser.add_argument(
        '--aggregate-lga',
        action='store_true',
        help='Aggregate exposure data to LGA level'
    )
    
    parser.add_argument(
        '--year',
        type=int,
        default=2020,
        help='Year for WorldPop data (2000-2020)'
    )
    
    args = parser.parse_args()
    
    try:
        exposure_df = None
        
        if args.method == 'litpop':
            # Generate using CLIMADA LitPop
            exposure_df = generate_exposure_litpop(
                resolution_arcsec=args.resolution,
                save_format='both'
            )
        
        elif args.method == 'worldpop':
            # Download WorldPop and generate exposure
            raster_file = download_worldpop_data(year=args.year)
            if raster_file:
                exposure_df = create_exposure_from_population_raster(raster_file)
        
        # Aggregate to LGA level if requested
        if args.aggregate_lga and exposure_df is not None:
            aggregate_exposure_by_lga(exposure_df)
        
        if exposure_df is not None:
            print("\n" + "="*70)
            print("✅ EXPOSURE GENERATION COMPLETE!")
            print("="*70)
            print("\nGenerated files:")
            for f in Path('data').glob('nigeria_exposure*'):
                size = f.stat().st_size / (1024*1024)
                print(f"   {f.name:45s} {size:6.1f} MB")
            
            print("\nNext steps:")
            print("1. Verify: python -c \"import pandas as pd; df = pd.read_csv('data/nigeria_exposure.csv'); print(f'Loaded {len(df):,} points')\"")
            print("2. Aggregate to LGA: python generate_exposure.py --aggregate-lga")
            print("3. Use in forecasts!")
            print("="*70)
        else:
            print("\n❌ Exposure generation failed")
            exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        exit(1)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
