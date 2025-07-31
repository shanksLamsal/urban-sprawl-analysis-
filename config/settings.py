"""
Configuration settings for Urban Sprawl Analysis
"""

# Study Area Configuration (Kathmandu, Nepal)
STUDY_AREA = {
    'name': 'Kathmandu',
    'country': 'Nepal',
    'coordinates': {
        'north': 27.8,
        'south': 27.6,
        'east': 85.4,
        'west': 85.2
    },
    'center_lat': 27.7,
    'center_lon': 85.3
}

# Time Periods for Analysis
TIME_PERIODS = {
    'start_year': 2010,
    'end_year': 2020,
    'start_date': '2010-01-01',
    'end_date': '2020-12-31'
}

# Landsat Collection Settings
LANDSAT_COLLECTION = 'LANDSAT/LC08/C02/T1_L2'  # Landsat 8 Collection 2 Level 2
LANDSAT_BANDS = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']  # Blue, Green, Red, NIR, SWIR1, SWIR2

# Analysis Parameters
ANALYSIS_PARAMS = {
    'cloud_cover_threshold': 20,  # Maximum cloud cover percentage
    'ndvi_threshold': 0.3,  # NDVI threshold for vegetation classification
    'built_up_threshold': 0.2,  # Built-up index threshold
    'resolution': 30,  # Spatial resolution in meters
    'scale': 30  # Analysis scale in meters
}

# Classification Parameters
CLASSIFICATION = {
    'classes': {
        'vegetation': 1,
        'built_up': 2,
        'water': 3,
        'bare_soil': 4
    },
    'colors': {
        'vegetation': '#228B22',  # Forest Green
        'built_up': '#8B4513',    # Saddle Brown
        'water': '#4169E1',       # Royal Blue
        'bare_soil': '#F4A460'    # Sandy Brown
    }
}

# Visualization Settings
VISUALIZATION = {
    'map_center': [27.7, 85.3],
    'zoom_level': 10,
    'figure_size': (12, 8),
    'dpi': 300
}

# Export Settings
EXPORT = {
    'output_dir': 'results',
    'maps_dir': 'results/maps',
    'charts_dir': 'results/charts',
    'metrics_dir': 'results/metrics',
    'file_format': 'png',
    'csv_encoding': 'utf-8'
}

# Elevation Data Settings
ELEVATION = {
    'dataset': 'USGS/SRTMGL1_003',  # SRTM 30m resolution
    'slope_threshold': 15,  # Degrees for slope analysis
    'aspect_bins': 8  # Number of aspect bins for analysis
}

# Change Detection Parameters
CHANGE_DETECTION = {
    'min_change_area': 1000,  # Minimum area in square meters to consider as change
    'confidence_threshold': 0.7,  # Minimum confidence for change detection
    'buffer_distance': 100  # Buffer distance in meters for analysis
}
