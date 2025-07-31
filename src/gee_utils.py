"""
Google Earth Engine Utilities for Urban Sprawl Analysis
"""

import ee
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from settings import STUDY_AREA, TIME_PERIODS, LANDSAT_COLLECTION, ANALYSIS_PARAMS

class GEEProcessor:
    """Google Earth Engine data processor for urban sprawl analysis"""
    
    def __init__(self):
        """Initialize GEE processor"""
        try:
            ee.Initialize()
            print("Google Earth Engine initialized successfully")
        except Exception as e:
            print(f"Error initializing GEE: {e}")
            print("Please run 'earthengine authenticate' first")
    
    def create_study_area_roi(self) -> ee.Geometry:
        """Create region of interest for study area"""
        coords = STUDY_AREA['coordinates']
        roi = ee.Geometry.Rectangle([
            coords['west'], coords['south'], 
            coords['east'], coords['north']
        ])
        return roi
    
    def get_landsat_collection(self, start_date: str, end_date: str, 
                              cloud_threshold: int = None) -> ee.ImageCollection:
        """
        Get Landsat collection for specified time period
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            cloud_threshold: Maximum cloud cover percentage
            
        Returns:
            ee.ImageCollection: Filtered Landsat collection
        """
        if cloud_threshold is None:
            cloud_threshold = ANALYSIS_PARAMS['cloud_cover_threshold']
        
        # Get Landsat collection
        collection = ee.ImageCollection(LANDSAT_COLLECTION)
        
        # Filter by date and region
        roi = self.create_study_area_roi()
        filtered = collection.filterBounds(roi)\
                            .filterDate(start_date, end_date)\
                            .filter(ee.Filter.lt('CLOUD_COVER', cloud_threshold))
        
        return filtered
    
    def get_composite_image(self, collection: ee.ImageCollection, 
                           method: str = 'median') -> ee.Image:
        """
        Create composite image from collection
        
        Args:
            collection: ee.ImageCollection
            method: Compositing method ('median', 'mean', 'mosaic')
            
        Returns:
            ee.Image: Composite image
        """
        if method == 'median':
            return collection.median()
        elif method == 'mean':
            return collection.mean()
        elif method == 'mosaic':
            return collection.mosaic()
        else:
            raise ValueError(f"Unknown compositing method: {method}")
    
    def apply_cloud_mask(self, image: ee.Image) -> ee.Image:
        """
        Apply cloud mask to Landsat image
        
        Args:
            image: ee.Image to mask
            
        Returns:
            ee.Image: Cloud-masked image
        """
        # Get QA band for cloud masking
        qa = image.select('QA_PIXEL')
        
        # Create cloud mask (bit 3 for cloud, bit 4 for cloud shadow)
        cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)  # Cloud
        shadow_mask = qa.bitwiseAnd(1 << 4).eq(0)  # Cloud shadow
        
        # Combine masks
        mask = cloud_mask.And(shadow_mask)
        
        return image.updateMask(mask)
    
    def calculate_ndvi(self, image: ee.Image) -> ee.Image:
        """
        Calculate Normalized Difference Vegetation Index
        
        Args:
            image: ee.Image with NIR and Red bands
            
        Returns:
            ee.Image: NDVI image
        """
        nir = image.select('SR_B5')  # NIR band
        red = image.select('SR_B4')  # Red band
        
        ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
        return ndvi
    
    def calculate_built_up_index(self, image: ee.Image) -> ee.Image:
        """
        Calculate Built-up Index using NDBI
        
        Args:
            image: ee.Image with SWIR and NIR bands
            
        Returns:
            ee.Image: Built-up index image
        """
        swir = image.select('SR_B6')  # SWIR1 band
        nir = image.select('SR_B5')   # NIR band
        
        ndbi = swir.subtract(nir).divide(swir.add(nir)).rename('NDBI')
        return ndbi
    
    def get_elevation_data(self) -> ee.Image:
        """
        Get SRTM elevation data for study area
        
        Returns:
            ee.Image: Elevation image
        """
        from config.settings import ELEVATION
        
        roi = self.create_study_area_roi()
        elevation = ee.Image(ELEVATION['dataset']).clip(roi)
        return elevation
    
    def calculate_slope_aspect(self, elevation: ee.Image) -> Tuple[ee.Image, ee.Image]:
        """
        Calculate slope and aspect from elevation data
        
        Args:
            elevation: ee.Image elevation data
            
        Returns:
            Tuple[ee.Image, ee.Image]: Slope and aspect images
        """
        # Calculate slope and aspect
        terrain = ee.Terrain.products(elevation)
        slope = terrain.select('slope')
        aspect = terrain.select('aspect')
        
        return slope, aspect
    
    def export_image_to_drive(self, image: ee.Image, filename: str, 
                             scale: int = None, region: ee.Geometry = None) -> str:
        """
        Export image to Google Drive
        
        Args:
            image: ee.Image to export
            filename: Output filename
            scale: Export scale in meters
            region: Export region
            
        Returns:
            str: Export task ID
        """
        if scale is None:
            scale = ANALYSIS_PARAMS['scale']
        if region is None:
            region = self.create_study_area_roi()
        
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=filename,
            scale=scale,
            region=region,
            fileFormat='GeoTIFF',
            maxPixels=1e13
        )
        
        task.start()
        return task.id
    
    def get_image_statistics(self, image: ee.Image, region: ee.Geometry = None) -> Dict:
        """
        Get basic statistics for an image
        
        Args:
            image: ee.Image to analyze
            region: Region for statistics
            
        Returns:
            Dict: Statistics dictionary
        """
        if region is None:
            region = self.create_study_area_roi()
        
        stats = image.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                ee.Reducer.stdDev(), '', True
            ).combine(
                ee.Reducer.minMax(), '', True
            ),
            geometry=region,
            scale=ANALYSIS_PARAMS['scale'],
            maxPixels=1e13
        )
        
        return stats.getInfo()
    
    def create_time_series(self, start_year: int, end_year: int, 
                          months: List[int] = None) -> Dict[int, ee.Image]:
        """
        Create time series of composite images
        
        Args:
            start_year: Start year
            end_year: End year
            months: List of months to include (1-12)
            
        Returns:
            Dict[int, ee.Image]: Dictionary of year: image pairs
        """
        if months is None:
            months = [6, 7, 8]  # Summer months for better vegetation analysis
        
        time_series = {}
        
        for year in range(start_year, end_year + 1):
            try:
                # Create date range for the year
                start_date = f"{year}-{months[0]:02d}-01"
                end_date = f"{year}-{months[-1]:02d}-28"
                
                # Get collection and create composite
                collection = self.get_landsat_collection(start_date, end_date)
                if collection.size().getInfo() > 0:
                    composite = self.get_composite_image(collection)
                    composite = self.apply_cloud_mask(composite)
                    time_series[year] = composite
                    print(f"Created composite for {year}")
                else:
                    print(f"No data available for {year}")
                    
            except Exception as e:
                print(f"Error processing {year}: {e}")
        
        return time_series
    
    def validate_data_availability(self, start_year: int, end_year: int) -> Dict:
        """
        Check data availability for the study period
        
        Args:
            start_year: Start year
            end_year: End year
            
        Returns:
            Dict: Data availability information
        """
        availability = {}
        
        for year in range(start_year, end_year + 1):
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            collection = self.get_landsat_collection(start_date, end_date)
            count = collection.size().getInfo()
            
            availability[year] = {
                'image_count': count,
                'available': count > 0,
                'date_range': f"{start_date} to {end_date}"
            }
        
        return availability 