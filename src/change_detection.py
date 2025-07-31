"""
Change Detection for Urban Sprawl Analysis
"""

import ee
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from settings import ANALYSIS_PARAMS, CHANGE_DETECTION

class ChangeDetector:
    """Detect and analyze changes in land cover over time"""
    
    def __init__(self, gee_processor):
        """
        Initialize change detector
        
        Args:
            gee_processor: GEEProcessor instance
        """
        self.gee_processor = gee_processor
        self.min_change_area = CHANGE_DETECTION['min_change_area']
        self.confidence_threshold = CHANGE_DETECTION['confidence_threshold']
    
    def detect_land_cover_changes(self, image1: ee.Image, image2: ee.Image) -> ee.Image:
        """
        Detect changes between two classified land cover images
        
        Args:
            image1: ee.Image classified land cover (earlier time)
            image2: ee.Image classified land cover (later time)
            
        Returns:
            ee.Image: Change detection image
        """
        # Get land cover bands
        lc1 = image1.select('land_cover')
        lc2 = image2.select('land_cover')
        
        # Create change image
        change = lc2.subtract(lc1).rename('change')
        
        # Create change mask (where change != 0)
        change_mask = change.neq(0)
        
        # Apply mask to change image
        change_detected = change.updateMask(change_mask)
        
        return change_detected
    
    def analyze_vegetation_changes(self, image1: ee.Image, image2: ee.Image) -> Dict:
        """
        Analyze changes in vegetation cover
        
        Args:
            image1: ee.Image from earlier time period
            image2: ee.Image from later time period
            
        Returns:
            Dict: Vegetation change statistics
        """
        # Calculate NDVI for both images
        ndvi1 = self.gee_processor.calculate_ndvi(image1)
        ndvi2 = self.gee_processor.calculate_ndvi(image2)
        
        # Calculate NDVI difference
        ndvi_change = ndvi2.subtract(ndvi1).rename('ndvi_change')
        
        # Get statistics
        region = self.gee_processor.create_study_area_roi()
        stats = self.gee_processor.get_image_statistics(ndvi_change, region)
        
        # Classify changes
        vegetation_loss = ndvi_change.lt(-0.1)  # Significant decrease
        vegetation_gain = ndvi_change.gt(0.1)   # Significant increase
        no_change = ndvi_change.abs().lt(0.1)   # Minimal change
        
        # Calculate areas
        loss_area = self._calculate_area(vegetation_loss, region)
        gain_area = self._calculate_area(vegetation_gain, region)
        no_change_area = self._calculate_area(no_change, region)
        
        return {
            'ndvi_change_stats': stats,
            'vegetation_loss_km2': loss_area,
            'vegetation_gain_km2': gain_area,
            'no_change_km2': no_change_area,
            'net_change_km2': gain_area - loss_area,
            'change_percentage': ((gain_area - loss_area) / (loss_area + gain_area + no_change_area)) * 100
        }
    
    def analyze_urban_expansion(self, image1: ee.Image, image2: ee.Image) -> Dict:
        """
        Analyze urban expansion patterns
        
        Args:
            image1: ee.Image from earlier time period
            image2: ee.Image from later time period
            
        Returns:
            Dict: Urban expansion statistics
        """
        # Calculate built-up index for both images
        ndbi1 = self.gee_processor.calculate_built_up_index(image1)
        ndbi2 = self.gee_processor.calculate_built_up_index(image2)
        
        # Calculate built-up change
        ndbi_change = ndbi2.subtract(ndbi1).rename('ndbi_change')
        
        # Get statistics
        region = self.gee_processor.create_study_area_roi()
        stats = self.gee_processor.get_image_statistics(ndbi_change, region)
        
        # Classify urban expansion
        urban_expansion = ndbi_change.gt(0.1)  # Significant increase in built-up
        urban_decline = ndbi_change.lt(-0.1)   # Significant decrease in built-up
        stable_urban = ndbi_change.abs().lt(0.1)  # Minimal change
        
        # Calculate areas
        expansion_area = self._calculate_area(urban_expansion, region)
        decline_area = self._calculate_area(urban_decline, region)
        stable_area = self._calculate_area(stable_urban, region)
        
        return {
            'ndbi_change_stats': stats,
            'urban_expansion_km2': expansion_area,
            'urban_decline_km2': decline_area,
            'stable_urban_km2': stable_area,
            'net_expansion_km2': expansion_area - decline_area,
            'expansion_rate_percent': (expansion_area / (expansion_area + decline_area + stable_area)) * 100
        }
    
    def _calculate_area(self, mask: ee.Image, region: ee.Geometry) -> float:
        """
        Calculate area of masked pixels
        
        Args:
            mask: ee.Image boolean mask
            region: Analysis region
            
        Returns:
            float: Area in square kilometers
        """
        area = mask.multiply(ee.Image.pixelArea()).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=ANALYSIS_PARAMS['scale'],
            maxPixels=1e13
        )
        
        # Convert to square kilometers
        area_km2 = area.getInfo().get('land_cover', 0) / 1e6
        return area_km2
    
    def create_change_matrix(self, image1: ee.Image, image2: ee.Image) -> pd.DataFrame:
        """
        Create change matrix showing transitions between land cover classes
        
        Args:
            image1: ee.Image classified land cover (earlier time)
            image2: ee.Image classified land cover (later time)
            
        Returns:
            pd.DataFrame: Change matrix
        """
        # Get land cover bands
        lc1 = image1.select('land_cover')
        lc2 = image2.select('land_cover')
        
        # Create region for analysis
        region = self.gee_processor.create_study_area_roi()
        
        # Get class names
        class_names = ['vegetation', 'built_up', 'water', 'bare_soil']
        
        # Create change matrix
        change_matrix = {}
        
        for i, class1 in enumerate(class_names, 1):
            change_matrix[class1] = {}
            for j, class2 in enumerate(class_names, 1):
                # Count pixels that changed from class1 to class2
                mask = lc1.eq(i).And(lc2.eq(j))
                area = self._calculate_area(mask, region)
                change_matrix[class1][class2] = area
        
        return pd.DataFrame(change_matrix, index=class_names)
    
    def analyze_elevation_changes(self, image1: ee.Image, image2: ee.Image) -> Dict:
        """
        Analyze changes in relation to elevation
        
        Args:
            image1: ee.Image from earlier time period
            image2: ee.Image from later time period
            
        Returns:
            Dict: Elevation-based change analysis
        """
        # Get elevation data
        elevation = self.gee_processor.get_elevation_data()
        slope, aspect = self.gee_processor.calculate_slope_aspect(elevation)
        
        # Calculate vegetation changes
        ndvi1 = self.gee_processor.calculate_ndvi(image1)
        ndvi2 = self.gee_processor.calculate_ndvi(image2)
        ndvi_change = ndvi2.subtract(ndvi1)
        
        # Analyze changes by elevation zones
        elevation_zones = self._create_elevation_zones(elevation)
        
        elevation_analysis = {}
        for zone_name, zone_mask in elevation_zones.items():
            # Calculate change statistics for each elevation zone
            zone_stats = ndvi_change.updateMask(zone_mask).reduceRegion(
                reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), '', True),
                geometry=self.gee_processor.create_study_area_roi(),
                scale=ANALYSIS_PARAMS['scale'],
                maxPixels=1e13
            )
            
            elevation_analysis[zone_name] = zone_stats.getInfo()
        
        return elevation_analysis
    
    def _create_elevation_zones(self, elevation: ee.Image) -> Dict[str, ee.Image]:
        """
        Create elevation zones for analysis
        
        Args:
            elevation: ee.Image elevation data
            
        Returns:
            Dict[str, ee.Image]: Elevation zone masks
        """
        # Get elevation statistics
        region = self.gee_processor.create_study_area_roi()
        stats = elevation.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=region,
            scale=ANALYSIS_PARAMS['scale'],
            maxPixels=1e13
        ).getInfo()
        
        min_elev = stats.get('elevation_min', 0)
        max_elev = stats.get('elevation_max', 1000)
        
        # Create elevation zones
        zone_size = (max_elev - min_elev) / 4
        
        zones = {}
        for i in range(4):
            zone_min = min_elev + i * zone_size
            zone_max = min_elev + (i + 1) * zone_size
            zone_name = f"elevation_{int(zone_min)}-{int(zone_max)}m"
            
            zone_mask = elevation.gte(zone_min).And(elevation.lt(zone_max))
            zones[zone_name] = zone_mask
        
        return zones
    
    def generate_change_report(self, change_stats: Dict, 
                             study_area_name: str, 
                             time_period: str) -> str:
        """
        Generate a comprehensive change analysis report
        
        Args:
            change_stats: Change detection statistics
            study_area_name: Name of the study area
            time_period: Time period of analysis
            
        Returns:
            str: Formatted change report
        """
        report = f"""
URBAN SPRAWL CHANGE ANALYSIS REPORT
===================================
Study Area: {study_area_name}
Time Period: {time_period}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

VEGETATION CHANGES:
"""
        
        if 'vegetation_changes' in change_stats:
            veg_changes = change_stats['vegetation_changes']
            report += f"""
  - Vegetation Loss: {veg_changes['vegetation_loss_km2']:.2f} km²
  - Vegetation Gain: {veg_changes['vegetation_gain_km2']:.2f} km²
  - Net Change: {veg_changes['net_change_km2']:.2f} km²
  - Change Percentage: {veg_changes['change_percentage']:.1f}%
"""
        
        report += f"""
URBAN EXPANSION:
"""
        
        if 'urban_expansion' in change_stats:
            urban_changes = change_stats['urban_expansion']
            report += f"""
  - Urban Expansion: {urban_changes['urban_expansion_km2']:.2f} km²
  - Urban Decline: {urban_changes['urban_decline_km2']:.2f} km²
  - Net Expansion: {urban_changes['net_expansion_km2']:.2f} km²
  - Expansion Rate: {urban_changes['expansion_rate_percent']:.1f}%
"""
        
        report += f"""
KEY FINDINGS:
  - Primary driver of change: {'Urban expansion' if change_stats.get('urban_expansion', {}).get('net_expansion_km2', 0) > 0 else 'Vegetation loss'}
  - Most affected areas: {'Low elevation zones' if 'elevation_analysis' in change_stats else 'Urban fringe areas'}
  - Conservation priority: {'High' if change_stats.get('vegetation_changes', {}).get('vegetation_loss_km2', 0) > 5 else 'Medium'}
"""
        
        return report
    
    def export_change_results(self, change_image: ee.Image, 
                            filename: str) -> str:
        """
        Export change detection results
        
        Args:
            change_image: ee.Image change detection result
            filename: Output filename
            
        Returns:
            str: Export task ID
        """
        return self.gee_processor.export_image_to_drive(
            change_image, 
            filename
        ) 