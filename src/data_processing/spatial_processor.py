"""
Spatial Data Processing Module
Handles geospatial operations and grid-based analysis
"""

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpatialProcessor:
    """Process spatial data and perform spatial joins"""
    
    def __init__(self, centroids: Optional[Dict] = None):
        """
        Initialize spatial processor
        
        Args:
            centroids: Dictionary with 'lat' and 'lon' arrays for grid centroids
        """
        self.centroids = centroids
        self.kdtree = None
        
        if centroids is not None:
            self._build_kdtree()
    
    def _build_kdtree(self):
        """Build KD-tree for fast spatial queries"""
        if self.centroids is None:
            return
        
        lat = self.centroids.get('lat')
        lon = self.centroids.get('lon')
        
        if lat is not None and lon is not None:
            coords = np.column_stack([lat, lon])
            self.kdtree = cKDTree(coords)
            logger.info(f"Built KD-tree with {len(coords)} points")
    
    def find_nearest_grid_point(self, lat: float, lon: float) -> Tuple[int, float]:
        """
        Find nearest grid point to given coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Tuple of (index, distance)
        """
        if self.kdtree is None:
            raise ValueError("KD-tree not initialized")
        
        distance, index = self.kdtree.query([lat, lon])
        return int(index), float(distance)
    
    def map_points_to_grid(self, df: pd.DataFrame,
                          lat_col: str = 'latitude',
                          lon_col: str = 'longitude') -> pd.DataFrame:
        """
        Map point data to nearest grid cells
        
        Args:
            df: DataFrame with point locations
            lat_col: Name of latitude column
            lon_col: Name of longitude column
            
        Returns:
            DataFrame with grid_index column
        """
        if self.kdtree is None:
            raise ValueError("KD-tree not initialized")
        
        logger.info(f"Mapping {len(df)} points to grid...")
        
        df = df.copy()
        
        # Get coordinates
        coords = df[[lat_col, lon_col]].values
        
        # Find nearest grid points
        distances, indices = self.kdtree.query(coords)
        
        df['grid_index'] = indices
        df['grid_distance_km'] = distances * 111  # Approximate km per degree
        
        logger.info(f"Mapped points with mean distance {df['grid_distance_km'].mean():.2f} km")
        
        return df
    
    def aggregate_to_grid(self, df: pd.DataFrame,
                         value_cols: List[str],
                         agg_func: str = 'sum') -> pd.DataFrame:
        """
        Aggregate point data to grid cells
        
        Args:
            df: DataFrame with grid_index column
            value_cols: Columns to aggregate
            agg_func: Aggregation function
            
        Returns:
            Aggregated DataFrame
        """
        if 'grid_index' not in df.columns:
            raise ValueError("DataFrame must have 'grid_index' column. Run map_points_to_grid first.")
        
        logger.info(f"Aggregating {len(value_cols)} variables to grid...")
        
        agg_dict = {col: agg_func for col in value_cols if col in df.columns}
        
        gridded = df.groupby('grid_index', as_index=False).agg(agg_dict)
        
        # Add grid coordinates
        if self.centroids is not None:
            gridded['latitude'] = self.centroids['lat'][gridded['grid_index']]
            gridded['longitude'] = self.centroids['lon'][gridded['grid_index']]
        
        logger.info(f"Aggregated to {len(gridded)} grid cells")
        
        return gridded
    
    def create_spatial_buffer(self, lat: float, lon: float, 
                             radius_km: float) -> List[int]:
        """
        Find all grid points within radius of a location
        
        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Radius in kilometers
            
        Returns:
            List of grid indices within radius
        """
        if self.kdtree is None:
            raise ValueError("KD-tree not initialized")
        
        # Convert km to degrees (approximate)
        radius_deg = radius_km / 111.0
        
        # Query all points within radius
        indices = self.kdtree.query_ball_point([lat, lon], radius_deg)
        
        logger.info(f"Found {len(indices)} grid points within {radius_km} km")
        
        return indices
    
    def calculate_distance_matrix(self, points_df: pd.DataFrame,
                                  lat_col: str = 'latitude',
                                  lon_col: str = 'longitude') -> np.ndarray:
        """
        Calculate pairwise distance matrix between points
        
        Args:
            points_df: DataFrame with point locations
            lat_col: Latitude column name
            lon_col: Longitude column name
            
        Returns:
            Distance matrix (n x n)
        """
        coords = points_df[[lat_col, lon_col]].values
        
        # Calculate Euclidean distances (in degrees)
        from scipy.spatial.distance import cdist
        distances = cdist(coords, coords, metric='euclidean')
        
        # Convert to kilometers (approximate)
        distances_km = distances * 111.0
        
        logger.info(f"Calculated {distances_km.shape[0]}x{distances_km.shape[1]} distance matrix")
        
        return distances_km
    
    def spatial_join_nearest(self, left_df: pd.DataFrame,
                           right_df: pd.DataFrame,
                           left_lat: str = 'latitude',
                           left_lon: str = 'longitude',
                           right_lat: str = 'latitude',
                           right_lon: str = 'longitude',
                           max_distance_km: Optional[float] = None) -> pd.DataFrame:
        """
        Join two DataFrames based on nearest spatial match
        
        Args:
            left_df: Left DataFrame
            right_df: Right DataFrame
            left_lat: Latitude column in left DataFrame
            left_lon: Longitude column in left DataFrame
            right_lat: Latitude column in right DataFrame
            right_lon: Longitude column in right DataFrame
            max_distance_km: Maximum distance for matches (None = no limit)
            
        Returns:
            Joined DataFrame
        """
        logger.info(f"Performing spatial join: {len(left_df)} x {len(right_df)} records...")
        
        # Build KD-tree for right DataFrame
        right_coords = right_df[[right_lat, right_lon]].values
        tree = cKDTree(right_coords)
        
        # Query for left DataFrame
        left_coords = left_df[[left_lat, left_lon]].values
        distances, indices = tree.query(left_coords)
        
        # Create result DataFrame
        result = left_df.copy()
        
        # Add matched data from right DataFrame
        matched_data = right_df.iloc[indices].reset_index(drop=True)
        
        # Add suffix to avoid column name conflicts
        for col in matched_data.columns:
            if col not in [right_lat, right_lon]:
                result[f'{col}_nearest'] = matched_data[col].values
        
        result['match_distance_km'] = distances * 111.0
        
        # Filter by max distance if specified
        if max_distance_km is not None:
            result = result[result['match_distance_km'] <= max_distance_km]
            logger.info(f"Filtered to {len(result)} matches within {max_distance_km} km")
        
        logger.info(f"Spatial join complete: {len(result)} matched records")
        
        return result
    
    def create_hexagonal_grid(self, bounds: Tuple[float, float, float, float],
                            resolution_km: float = 10) -> pd.DataFrame:
        """
        Create hexagonal grid over area
        
        Args:
            bounds: (min_lat, min_lon, max_lat, max_lon)
            resolution_km: Approximate hexagon size in km
            
        Returns:
            DataFrame with hexagon centroids
        """
        min_lat, min_lon, max_lat, max_lon = bounds
        
        # Convert km to degrees
        res_deg = resolution_km / 111.0
        
        # Create hexagonal grid
        lat_points = np.arange(min_lat, max_lat, res_deg * 0.866)  # sqrt(3)/2
        lon_points = np.arange(min_lon, max_lon, res_deg)
        
        hexagons = []
        for i, lat in enumerate(lat_points):
            offset = (res_deg / 2) if i % 2 == 1 else 0
            for lon in lon_points:
                hexagons.append({
                    'latitude': lat,
                    'longitude': lon + offset,
                    'hex_id': len(hexagons)
                })
        
        grid_df = pd.DataFrame(hexagons)
        
        logger.info(f"Created hexagonal grid with {len(grid_df)} cells")
        
        return grid_df


if __name__ == "__main__":
    # Example usage
    processor = SpatialProcessor()
    print("Spatial processor ready")
