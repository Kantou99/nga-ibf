#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualize Nigeria Centroids
Creates maps and plots of the generated centroids
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from climada.hazard import Centroids

def visualize_centroids(centroids_file='nigeria_centroids_1km.hdf5'):
    """
    Create visualizations of Nigeria centroids
    
    Args:
        centroids_file: Path to centroids HDF5 file
    """
    
    print("="*70)
    print("NIGERIA CENTROIDS VISUALIZATION")
    print("="*70)
    
    # Load centroids
    print(f"\n📂 Loading centroids from: {centroids_file}")
    centroids = Centroids.from_hdf5(centroids_file)
    
    print(f"✅ Loaded {len(centroids.lat):,} centroids")
    print(f"   Latitude range: {centroids.lat.min():.2f}° to {centroids.lat.max():.2f}°")
    print(f"   Longitude range: {centroids.lon.min():.2f}° to {centroids.lon.max():.2f}°")
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # ========================================================================
    # Plot 1: Full Map of Centroids
    # ========================================================================
    ax1 = plt.subplot(2, 2, 1)
    scatter1 = ax1.scatter(centroids.lon, centroids.lat, 
                          c='blue', s=0.5, alpha=0.3)
    ax1.set_xlabel('Longitude (°E)', fontsize=12)
    ax1.set_ylabel('Latitude (°N)', fontsize=12)
    ax1.set_title(f'Nigeria Centroids Map\n{len(centroids.lat):,} points', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal', adjustable='box')
    
    # Add Nigeria outline (approximate)
    nigeria_outline_lon = [2.7, 14.7, 14.7, 2.7, 2.7]
    nigeria_outline_lat = [4.3, 4.3, 13.9, 13.9, 4.3]
    ax1.plot(nigeria_outline_lon, nigeria_outline_lat, 
            'r-', linewidth=2, label='Approx. Nigeria boundary')
    ax1.legend()
    
    # ========================================================================
    # Plot 2: Density Map (Heatmap)
    # ========================================================================
    ax2 = plt.subplot(2, 2, 2)
    
    # Create 2D histogram for density
    H, xedges, yedges = np.histogram2d(
        centroids.lon, centroids.lat, 
        bins=[100, 100]
    )
    
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    im = ax2.imshow(H.T, origin='lower', extent=extent, 
                    cmap='YlOrRd', aspect='auto')
    ax2.set_xlabel('Longitude (°E)', fontsize=12)
    ax2.set_ylabel('Latitude (°N)', fontsize=12)
    ax2.set_title('Point Density Heatmap', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax2, label='Point Count')
    
    # ========================================================================
    # Plot 3: Latitude Distribution
    # ========================================================================
    ax3 = plt.subplot(2, 2, 3)
    ax3.hist(centroids.lat, bins=50, color='green', alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Latitude (°N)', fontsize=12)
    ax3.set_ylabel('Frequency', fontsize=12)
    ax3.set_title('Latitude Distribution', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.axvline(centroids.lat.mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {centroids.lat.mean():.2f}°')
    ax3.legend()
    
    # ========================================================================
    # Plot 4: Longitude Distribution
    # ========================================================================
    ax4 = plt.subplot(2, 2, 4)
    ax4.hist(centroids.lon, bins=50, color='orange', alpha=0.7, edgecolor='black')
    ax4.set_xlabel('Longitude (°E)', fontsize=12)
    ax4.set_ylabel('Frequency', fontsize=12)
    ax4.set_title('Longitude Distribution', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.axvline(centroids.lon.mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {centroids.lon.mean():.2f}°')
    ax4.legend()
    
    # ========================================================================
    # Overall figure adjustments
    # ========================================================================
    plt.suptitle('Nigeria IBF System - Centroids Visualization', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    # Save figure
    output_file = 'nigeria_centroids_visualization.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n💾 Saved visualization to: {output_file}")
    
    # Show statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)
    print(f"Total points:        {len(centroids.lat):,}")
    print(f"Latitude range:      {centroids.lat.min():.4f}° to {centroids.lat.max():.4f}°")
    print(f"Longitude range:     {centroids.lon.min():.4f}° to {centroids.lon.max():.4f}°")
    print(f"Mean latitude:       {centroids.lat.mean():.4f}°")
    print(f"Mean longitude:      {centroids.lon.mean():.4f}°")
    print(f"Std dev latitude:    {centroids.lat.std():.4f}°")
    print(f"Std dev longitude:   {centroids.lon.std():.4f}°")
    
    # Calculate approximate spacing
    lat_sorted = np.sort(centroids.lat)
    lat_diffs = np.diff(lat_sorted)
    lat_diffs = lat_diffs[lat_diffs > 1e-6]
    if len(lat_diffs) > 0:
        avg_spacing = np.median(lat_diffs) * 111  # Convert to km
        print(f"Average spacing:     {avg_spacing:.2f} km")
    
    print("="*70)
    
    # Try to display (won't work in WSL without X server, but will save file)
    try:
        plt.show()
        print("\n✅ Displaying plot...")
    except:
        print("\n⚠️  Cannot display plot in terminal (normal for WSL)")
        print(f"   View the saved image: {output_file}")
    
    return centroids


def create_simple_map(centroids_file='nigeria_centroids_1km.hdf5'):
    """
    Create a simple, clean map of centroids
    """
    
    print("\n📊 Creating simple map...")
    
    # Load centroids
    centroids = Centroids.from_hdf5(centroids_file)
    
    # Create figure
    plt.figure(figsize=(12, 10))
    
    # Plot points
    plt.scatter(centroids.lon, centroids.lat, 
               c='#2E86AB', s=1, alpha=0.5, marker='.')
    
    # Styling
    plt.xlabel('Longitude (°E)', fontsize=14, fontweight='bold')
    plt.ylabel('Latitude (°N)', fontsize=14, fontweight='bold')
    plt.title(f'Nigeria Impact-Based Forecasting System\nCentroids Grid ({len(centroids.lat):,} points)', 
             fontsize=16, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.2, linestyle='--')
    
    # Add Nigeria boundary
    plt.plot([2.7, 14.7, 14.7, 2.7, 2.7],
            [4.3, 4.3, 13.9, 13.9, 4.3],
            'r-', linewidth=2.5, label='Nigeria boundary (approx.)')
    
    # Add major cities (approximate locations)
    cities = {
        'Lagos': (3.4, 6.5),
        'Abuja': (7.5, 9.1),
        'Kano': (8.5, 12.0),
        'Port Harcourt': (7.0, 4.8),
        'Maiduguri': (13.2, 11.8)
    }
    
    for city, (lon, lat) in cities.items():
        plt.plot(lon, lat, 'ro', markersize=8, markeredgecolor='white', markeredgewidth=1)
        plt.text(lon + 0.3, lat, city, fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    plt.legend(loc='upper right', fontsize=12)
    plt.tight_layout()
    
    # Save
    output_file = 'nigeria_centroids_simple_map.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"💾 Saved simple map to: {output_file}")
    
    plt.close()


def create_regional_breakdown(centroids_file='nigeria_centroids_1km.hdf5'):
    """
    Show regional breakdown of centroids
    """
    
    print("\n🗺️  Creating regional breakdown...")
    
    centroids = Centroids.from_hdf5(centroids_file)
    
    # Define Nigerian regions (approximate boundaries)
    regions = {
        'North East': {'lon': (10, 15), 'lat': (9, 14)},
        'North West': {'lon': (3, 10), 'lat': (10, 14)},
        'North Central': {'lon': (5, 10), 'lat': (7, 10)},
        'South West': {'lon': (2.5, 6), 'lat': (6, 9)},
        'South East': {'lon': (6, 9), 'lat': (4.5, 7)},
        'South South': {'lon': (4, 9), 'lat': (4, 7)}
    }
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, (region_name, bounds) in enumerate(regions.items()):
        ax = axes[idx]
        
        # Filter points in region
        mask = ((centroids.lon >= bounds['lon'][0]) & 
                (centroids.lon <= bounds['lon'][1]) &
                (centroids.lat >= bounds['lat'][0]) & 
                (centroids.lat <= bounds['lat'][1]))
        
        region_lon = centroids.lon[mask]
        region_lat = centroids.lat[mask]
        
        # Plot
        ax.scatter(region_lon, region_lat, c='green', s=2, alpha=0.6)
        ax.set_xlabel('Longitude (°E)')
        ax.set_ylabel('Latitude (°N)')
        ax.set_title(f'{region_name}\n{len(region_lon):,} points', 
                    fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(bounds['lon'])
        ax.set_ylim(bounds['lat'])
    
    plt.suptitle('Nigeria Centroids - Regional Breakdown', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    output_file = 'nigeria_centroids_regional.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"💾 Saved regional breakdown to: {output_file}")
    
    plt.close()


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Visualize Nigeria centroids',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic visualization
  python visualize_centroids.py
  
  # Specify centroids file
  python visualize_centroids.py --file data/nigeria_centroids_1km.hdf5
  
  # Create all visualizations
  python visualize_centroids.py --all

Output:
  Creates PNG images:
  - nigeria_centroids_visualization.png (4-panel overview)
  - nigeria_centroids_simple_map.png (clean map)
  - nigeria_centroids_regional.png (regional breakdown)
        """
    )
    
    parser.add_argument(
        '--file',
        default='nigeria_centroids_1km.hdf5',
        help='Path to centroids HDF5 file'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Create all visualization types'
    )
    
    args = parser.parse_args()
    
    # Check file exists
    if not Path(args.file).exists():
        print(f"❌ Error: File not found: {args.file}")
        print("\nAvailable files:")
        for f in Path('.').glob('*.hdf5'):
            print(f"  - {f}")
        exit(1)
    
    try:
        # Main visualization
        print("\n🎨 Creating visualizations...\n")
        centroids = visualize_centroids(args.file)
        
        # Additional visualizations
        if args.all:
            create_simple_map(args.file)
            create_regional_breakdown(args.file)
        
        print("\n" + "="*70)
        print("✅ VISUALIZATION COMPLETE!")
        print("="*70)
        print("\nGenerated files:")
        print("  📊 nigeria_centroids_visualization.png")
        if args.all:
            print("  🗺️  nigeria_centroids_simple_map.png")
            print("  🌍 nigeria_centroids_regional.png")
        
        print("\n💡 Tip: Open these PNG files in Windows to view!")
        print(f"   Location: {Path('.').absolute()}")
        
        # Show path in Windows format
        import os
        current_dir = os.getcwd()
        if '/mnt/c/' in current_dir:
            win_path = current_dir.replace('/mnt/c/', 'C:\\').replace('/', '\\')
            print(f"   Windows: {win_path}")
        
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
