"""
Land Cover Classification for Urban Sprawl Analysis
"""

import ee
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from settings import ANALYSIS_PARAMS, CLASSIFICATION

class LandCoverClassifier:
    """Land cover classification using spectral indices"""
    
    def __init__(self, gee_processor):
        """
        Initialize land cover classifier
        
        Args:
            gee_processor: GEEProcessor instance
        """
        self.gee_processor = gee_processor
        self.ndvi_threshold = ANALYSIS_PARAMS['ndvi_threshold']
        self.built_up_threshold = ANALYSIS_PARAMS['built_up_threshold']
    
    def classify_land_cover(self, image: ee.Image) -> ee.Image:
        """
        Classify land cover using NDVI and NDBI
        
        Args:
            image: ee.Image with spectral bands
            
        Returns:
            ee.Image: Classified land cover image
        """
        # Calculate indices
        ndvi = self.gee_processor.calculate_ndvi(image)
        ndbi = self.gee_processor.calculate_built_up_index(image)
        
        # Create classification masks
        vegetation_mask = ndvi.gt(self.ndvi_threshold)
        built_up_mask = ndbi.gt(self.built_up_threshold)
        water_mask = self._detect_water(image)
        
        # Create classified image
        classified = ee.Image(0).rename('land_cover')  # Initialize with 0 (unclassified)
        
        # Apply classification
        classified = classified.where(vegetation_mask, CLASSIFICATION['classes']['vegetation'])
        classified = classified.where(built_up_mask, CLASSIFICATION['classes']['built_up'])
        classified = classified.where(water_mask, CLASSIFICATION['classes']['water'])
        
        # Remaining pixels are bare soil
        classified = classified.where(classified.eq(0), CLASSIFICATION['classes']['bare_soil'])
        
        return classified
    
    def _detect_water(self, image: ee.Image) -> ee.Image:
        """
        Detect water bodies using Modified Normalized Difference Water Index (MNDWI)
        
        Args:
            image: ee.Image with spectral bands
            
        Returns:
            ee.Image: Water mask
        """
        green = image.select('SR_B3')  # Green band
        swir = image.select('SR_B6')   # SWIR1 band
        
        mndwi = green.subtract(swir).divide(green.add(swir)).rename('MNDWI')
        
        # Water typically has MNDWI > 0.2
        water_mask = mndwi.gt(0.2)
        
        return water_mask
    
    def calculate_vegetation_fraction(self, image: ee.Image) -> ee.Image:
        """
        Calculate vegetation fraction using NDVI
        
        Args:
            image: ee.Image with spectral bands
            
        Returns:
            ee.Image: Vegetation fraction image
        """
        ndvi = self.gee_processor.calculate_ndvi(image)
        
        # Convert NDVI to vegetation fraction using empirical relationship
        # This is a simplified approach - more sophisticated methods exist
        veg_fraction = ndvi.subtract(0.1).divide(0.6).clamp(0, 1)
        
        return veg_fraction.rename('vegetation_fraction')
    
    def calculate_impervious_fraction(self, image: ee.Image) -> ee.Image:
        """
        Calculate impervious surface fraction using NDBI
        
        Args:
            image: ee.Image with spectral bands
            
        Returns:
            ee.Image: Impervious fraction image
        """
        ndbi = self.gee_processor.calculate_built_up_index(image)
        
        # Convert NDBI to impervious fraction
        # This is a simplified approach
        impervious_fraction = ndbi.add(0.5).divide(0.5).clamp(0, 1)
        
        return impervious_fraction.rename('impervious_fraction')
    
    def get_class_statistics(self, classified_image: ee.Image, 
                           region: ee.Geometry = None) -> Dict:
        """
        Get statistics for each land cover class
        
        Args:
            classified_image: ee.Image classified land cover
            region: Analysis region
            
        Returns:
            Dict: Statistics for each class
        """
        if region is None:
            region = self.gee_processor.create_study_area_roi()
        
        # Get pixel counts for each class
        area_stats = classified_image.reduceRegion(
            reducer=ee.Reducer.frequencyHistogram(),
            geometry=region,
            scale=ANALYSIS_PARAMS['scale'],
            maxPixels=1e13
        )
        
        # Get total area
        total_area = region.area().getInfo()
        
        # Process results
        hist = area_stats.get('land_cover').getInfo()
        
        stats = {}
        for class_id, pixel_count in hist.items():
            class_name = self._get_class_name(int(class_id))
            area_km2 = (pixel_count * ANALYSIS_PARAMS['scale']**2) / 1e6
            percentage = (pixel_count / sum(hist.values())) * 100
            
            stats[class_name] = {
                'class_id': int(class_id),
                'pixel_count': pixel_count,
                'area_km2': area_km2,
                'percentage': percentage
            }
        
        return stats
    
    def _get_class_name(self, class_id: int) -> str:
        """Get class name from class ID"""
        class_names = {v: k for k, v in CLASSIFICATION['classes'].items()}
        return class_names.get(class_id, 'unknown')
    
    def create_classification_legend(self) -> Dict:
        """Create legend information for classification"""
        legend = {}
        for class_name, class_id in CLASSIFICATION['classes'].items():
            legend[class_name] = {
                'id': class_id,
                'color': CLASSIFICATION['colors'][class_name],
                'description': self._get_class_description(class_name)
            }
        return legend
    
    def _get_class_description(self, class_name: str) -> str:
        """Get description for land cover class"""
        descriptions = {
            'vegetation': 'Areas with significant vegetation cover (forests, grasslands, crops)',
            'built_up': 'Urban areas, buildings, roads, and other impervious surfaces',
            'water': 'Water bodies including rivers, lakes, and reservoirs',
            'bare_soil': 'Exposed soil, rock, or areas with minimal vegetation'
        }
        return descriptions.get(class_name, 'Unknown land cover type')
    
    def validate_classification(self, classified_image: ee.Image, 
                              reference_data: ee.FeatureCollection = None) -> Dict:
        """
        Validate classification accuracy (if reference data available)
        
        Args:
            classified_image: ee.Image classified land cover
            reference_data: Reference data for validation
            
        Returns:
            Dict: Validation metrics
        """
        if reference_data is None:
            return {"message": "No reference data provided for validation"}
        
        # This is a placeholder for accuracy assessment
        # In practice, you would need reference data and implement proper validation
        return {
            "message": "Validation requires reference data implementation",
            "reference_points": reference_data.size().getInfo() if reference_data else 0
        }
    
    def export_classification_results(self, classified_image: ee.Image, 
                                    filename: str) -> str:
        """
        Export classification results
        
        Args:
            classified_image: ee.Image classified land cover
            filename: Output filename
            
        Returns:
            str: Export task ID
        """
        return self.gee_processor.export_image_to_drive(
            classified_image, 
            filename
        )
    
    def create_classification_report(self, stats: Dict, 
                                   study_area_name: str) -> str:
        """
        Create a text report of classification results
        
        Args:
            stats: Classification statistics
            study_area_name: Name of the study area
            
        Returns:
            str: Formatted report
        """
        report = f"""
LAND COVER CLASSIFICATION REPORT
===============================
Study Area: {study_area_name}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

CLASSIFICATION RESULTS:
"""
        
        total_area = sum(class_stats['area_km2'] for class_stats in stats.values())
        
        for class_name, class_stats in stats.items():
            report += f"""
{class_name.upper()}:
  - Area: {class_stats['area_km2']:.2f} km²
  - Percentage: {class_stats['percentage']:.1f}%
  - Pixel Count: {class_stats['pixel_count']:,}
"""
        
        report += f"""
SUMMARY:
  - Total Area: {total_area:.2f} km²
  - Dominant Class: {max(stats.items(), key=lambda x: x[1]['percentage'])[0]}
  - Vegetation Coverage: {stats.get('vegetation', {}).get('percentage', 0):.1f}%
  - Built-up Coverage: {stats.get('built_up', {}).get('percentage', 0):.1f}%
"""
        
        return report 