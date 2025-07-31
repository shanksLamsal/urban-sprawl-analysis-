"""
Visualization Module for Urban Sprawl Analysis
"""

import folium
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from settings import VISUALIZATION, CLASSIFICATION, EXPORT

class UrbanSprawlVisualizer:
    """Visualization tools for urban sprawl analysis"""
    
    def __init__(self):
        """Initialize visualizer"""
        # Set matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create output directories
        self._create_output_dirs()
    
    def _create_output_dirs(self):
        """Create output directories if they don't exist"""
        for dir_path in [EXPORT['maps_dir'], EXPORT['charts_dir'], EXPORT['metrics_dir']]:
            os.makedirs(dir_path, exist_ok=True)
    
    def create_interactive_map(self, image: 'ee.Image', title: str = "Land Cover Map",
                             center: List[float] = None, zoom: int = None) -> folium.Map:
        """
        Create interactive Folium map
        
        Args:
            image: ee.Image to display
            title: Map title
            center: Map center coordinates [lat, lon]
            zoom: Zoom level
            
        Returns:
            folium.Map: Interactive map
        """
        if center is None:
            center = VISUALIZATION['map_center']
        if zoom is None:
            zoom = VISUALIZATION['zoom_level']
        
        # Create base map
        m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')
        
        # Add image layer
        image_url = image.getThumbURL({
            'min': 0,
            'max': 4,
            'palette': ['#228B22', '#8B4513', '#4169E1', '#F4A460'],
            'format': 'png'
        })
        
        folium.raster_layers.ImageOverlay(
            image_url,
            bounds=[[27.6, 85.2], [27.8, 85.4]],
            opacity=0.7,
            name=title
        ).add_to(m)
        
        # Add legend
        legend_html = self._create_legend_html()
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_comparison_map(self, image1: 'ee.Image', image2: 'ee.Image',
                            title1: str = "Before", title2: str = "After") -> folium.Map:
        """
        Create side-by-side comparison map
        
        Args:
            image1: ee.Image from earlier time period
            image2: ee.Image from later time period
            title1: Title for first image
            title2: Title for second image
            
        Returns:
            folium.Map: Comparison map
        """
        center = VISUALIZATION['map_center']
        zoom = VISUALIZATION['zoom_level']
        
        # Create base map
        m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')
        
        # Add first image layer
        image1_url = image1.getThumbURL({
            'min': 0,
            'max': 4,
            'palette': ['#228B22', '#8B4513', '#4169E1', '#F4A460'],
            'format': 'png'
        })
        
        folium.raster_layers.ImageOverlay(
            image1_url,
            bounds=[[27.6, 85.2], [27.8, 85.4]],
            opacity=0.7,
            name=title1
        ).add_to(m)
        
        # Add second image layer
        image2_url = image2.getThumbURL({
            'min': 0,
            'max': 4,
            'palette': ['#228B22', '#8B4513', '#4169E1', '#F4A460'],
            'format': 'png'
        })
        
        folium.raster_layers.ImageOverlay(
            image2_url,
            bounds=[[27.6, 85.2], [27.8, 85.4]],
            opacity=0.7,
            name=title2
        ).add_to(m)
        
        # Add legend
        legend_html = self._create_legend_html()
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    
    def _create_legend_html(self) -> str:
        """Create HTML legend for Folium map"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 150px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Land Cover Classes</b></p>
        <p><i class="fa fa-square" style="color:#228B22"></i> Vegetation</p>
        <p><i class="fa fa-square" style="color:#8B4513"></i> Built-up</p>
        <p><i class="fa fa-square" style="color:#4169E1"></i> Water</p>
        <p><i class="fa fa-square" style="color:#F4A460"></i> Bare Soil</p>
        </div>
        '''
        return legend_html
    
    def create_land_cover_chart(self, stats: Dict, title: str = "Land Cover Distribution") -> plt.Figure:
        """
        Create pie chart of land cover distribution
        
        Args:
            stats: Land cover statistics
            title: Chart title
            
        Returns:
            plt.Figure: Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=VISUALIZATION['figure_size'])
        
        # Prepare data
        labels = list(stats.keys())
        sizes = [stats[label]['percentage'] for label in labels]
        colors = [CLASSIFICATION['colors'][label] for label in labels]
        
        # Pie chart
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                          startangle=90)
        ax1.set_title(title)
        
        # Bar chart
        areas = [stats[label]['area_km2'] for label in labels]
        bars = ax2.bar(labels, areas, color=colors)
        ax2.set_title('Land Cover Area (km²)')
        ax2.set_ylabel('Area (km²)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, area in zip(bars, areas):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{area:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_change_analysis_chart(self, change_stats: Dict, 
                                   title: str = "Change Analysis") -> plt.Figure:
        """
        Create charts for change analysis
        
        Args:
            change_stats: Change detection statistics
            title: Chart title
            
        Returns:
            plt.Figure: Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Vegetation changes
        if 'vegetation_changes' in change_stats:
            veg_changes = change_stats['vegetation_changes']
            veg_data = ['Loss', 'Gain', 'No Change']
            veg_values = [
                veg_changes['vegetation_loss_km2'],
                veg_changes['vegetation_gain_km2'],
                veg_changes['no_change_km2']
            ]
            veg_colors = ['#d62728', '#2ca02c', '#7f7f7f']
            
            axes[0, 0].bar(veg_data, veg_values, color=veg_colors)
            axes[0, 0].set_title('Vegetation Changes')
            axes[0, 0].set_ylabel('Area (km²)')
        
        # Urban expansion
        if 'urban_expansion' in change_stats:
            urban_changes = change_stats['urban_expansion']
            urban_data = ['Expansion', 'Decline', 'Stable']
            urban_values = [
                urban_changes['urban_expansion_km2'],
                urban_changes['urban_decline_km2'],
                urban_changes['stable_urban_km2']
            ]
            urban_colors = ['#ff7f0e', '#1f77b4', '#7f7f7f']
            
            axes[0, 1].bar(urban_data, urban_values, color=urban_colors)
            axes[0, 1].set_title('Urban Changes')
            axes[0, 1].set_ylabel('Area (km²)')
        
        # Change matrix heatmap
        if 'change_matrix' in change_stats:
            change_matrix = change_stats['change_matrix']
            sns.heatmap(change_matrix, annot=True, fmt='.2f', cmap='YlOrRd', ax=axes[1, 0])
            axes[1, 0].set_title('Land Cover Change Matrix (km²)')
        
        # Time series plot
        if 'time_series' in change_stats:
            time_data = change_stats['time_series']
            years = list(time_data.keys())
            veg_percentages = [time_data[year]['vegetation_percentage'] for year in years]
            urban_percentages = [time_data[year]['built_up_percentage'] for year in years]
            
            axes[1, 1].plot(years, veg_percentages, 'o-', label='Vegetation', color='#228B22')
            axes[1, 1].plot(years, urban_percentages, 's-', label='Built-up', color='#8B4513')
            axes[1, 1].set_title('Land Cover Trends Over Time')
            axes[1, 1].set_xlabel('Year')
            axes[1, 1].set_ylabel('Percentage (%)')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_elevation_analysis_chart(self, elevation_stats: Dict,
                                      title: str = "Elevation Analysis") -> plt.Figure:
        """
        Create charts for elevation-based analysis
        
        Args:
            elevation_stats: Elevation analysis statistics
            title: Chart title
            
        Returns:
            plt.Figure: Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=VISUALIZATION['figure_size'])
        
        # Elevation zones
        zones = list(elevation_stats.keys())
        veg_changes = [elevation_stats[zone].get('NDVI_mean', 0) for zone in zones]
        
        bars = ax1.bar(zones, veg_changes, color='#228B22', alpha=0.7)
        ax1.set_title('Vegetation Change by Elevation Zone')
        ax1.set_ylabel('NDVI Change')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, veg_changes):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.3f}', ha='center', va='bottom')
        
        # Slope analysis
        if 'slope_analysis' in elevation_stats:
            slope_data = elevation_stats['slope_analysis']
            slope_categories = list(slope_data.keys())
            change_rates = list(slope_data.values())
            
            ax2.bar(slope_categories, change_rates, color='#8B4513', alpha=0.7)
            ax2.set_title('Change Rate by Slope Category')
            ax2.set_ylabel('Change Rate (%)')
            ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def save_map(self, map_obj: folium.Map, filename: str) -> str:
        """
        Save Folium map to HTML file
        
        Args:
            map_obj: folium.Map object
            filename: Output filename
            
        Returns:
            str: Full path to saved file
        """
        filepath = os.path.join(EXPORT['maps_dir'], f"{filename}.html")
        map_obj.save(filepath)
        return filepath
    
    def save_chart(self, fig: plt.Figure, filename: str, dpi: int = None) -> str:
        """
        Save matplotlib chart to file
        
        Args:
            fig: matplotlib Figure object
            filename: Output filename
            dpi: Image resolution
            
        Returns:
            str: Full path to saved file
        """
        if dpi is None:
            dpi = VISUALIZATION['dpi']
        
        filepath = os.path.join(EXPORT['charts_dir'], f"{filename}.{EXPORT['file_format']}")
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)  # Close figure to free memory
        return filepath
    
    def save_metrics_csv(self, data: Dict, filename: str) -> str:
        """
        Save metrics data to CSV file
        
        Args:
            data: Data dictionary
            filename: Output filename
            
        Returns:
            str: Full path to saved file
        """
        filepath = os.path.join(EXPORT['metrics_dir'], f"{filename}.csv")
        
        # Convert nested dictionary to DataFrame
        if isinstance(data, dict):
            # Flatten nested dictionary
            flat_data = self._flatten_dict(data)
            df = pd.DataFrame([flat_data])
        else:
            df = pd.DataFrame(data)
        
        df.to_csv(filepath, index=False, encoding=EXPORT['csv_encoding'])
        return filepath
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def create_summary_dashboard(self, all_stats: Dict) -> str:
        """
        Create a comprehensive summary dashboard
        
        Args:
            all_stats: All analysis statistics
            
        Returns:
            str: HTML dashboard content
        """
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Urban Sprawl Analysis Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; text-align: center; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; }
                .chart { text-align: center; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Urban Sprawl Analysis Dashboard</h1>
                <p>Comprehensive analysis of urban expansion and land cover changes</p>
            </div>
        """
        
        # Add key metrics
        html_content += """
            <div class="section">
                <h2>Key Metrics</h2>
        """
        
        if 'vegetation_changes' in all_stats:
            veg_changes = all_stats['vegetation_changes']
            html_content += f"""
                <div class="metric">
                    <h3>Vegetation Loss</h3>
                    <p>{veg_changes['vegetation_loss_km2']:.2f} km²</p>
                </div>
                <div class="metric">
                    <h3>Vegetation Gain</h3>
                    <p>{veg_changes['vegetation_gain_km2']:.2f} km²</p>
                </div>
            """
        
        if 'urban_expansion' in all_stats:
            urban_changes = all_stats['urban_expansion']
            html_content += f"""
                <div class="metric">
                    <h3>Urban Expansion</h3>
                    <p>{urban_changes['urban_expansion_km2']:.2f} km²</p>
                </div>
                <div class="metric">
                    <h3>Expansion Rate</h3>
                    <p>{urban_changes['expansion_rate_percent']:.1f}%</p>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Save dashboard
        dashboard_path = os.path.join(EXPORT['output_dir'], 'dashboard.html')
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return dashboard_path 