import streamlit as st
import pydeck as pdk
from datetime import date, datetime, timedelta
import geemap
import ee
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit_folium as st_folium
import folium
import requests
import json

# Custom CSS for better aesthetics
st.set_page_config(
    page_title="Urban Sprawl Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .summary-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 2rem 0;
        color: #333;
    }
    .summary-section h2 {
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .summary-section h3 {
        color: #1f77b4;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .summary-section p {
        color: #333;
        line-height: 1.6;
    }
    .summary-section ul {
        color: #333;
    }
    .summary-section strong {
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🌍 Urban Sprawl Analysis Tool</h1>
    <p>Advanced satellite imagery analysis for environmental monitoring and urban development assessment</p>
</div>
""", unsafe_allow_html=True)

# Sidebar styling
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h3>⚙️ Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📅 Timeframe Selection")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Period", value=date(2020, 1, 1), min_value=date(1984, 1, 1), max_value=date.today())
    with col2:
        end_date = st.date_input("End Period", value=date(2023, 1, 1), min_value=date(1984, 1, 1), max_value=date.today())

    if start_date >= end_date:
        st.error("⚠️ Start Period must be before End Period.")

    st.markdown("### 🗺️ Area Selection")
    st.markdown("Draw a rectangle or polygon on the map to select your area of interest.")

# Default map center
map_center = [20.0, 0.0]

m = folium.Map(location=map_center, zoom_start=2, control_scale=True)

# Add drawing tools
draw = folium.plugins.Draw(export=True, draw_options={
    'polyline': False,
    'circle': False,
    'marker': False,
    'circlemarker': False,
    'rectangle': True,
    'polygon': True
})
draw.add_to(m)

# Show map and capture drawing
output = st_folium.st_folium(m, width=700, height=450, returned_objects=["last_active_drawing", "all_drawings"])

# Parse drawn geometry
geometry = None
if output and output.get("last_active_drawing"):
    geometry = output["last_active_drawing"]["geometry"]

# --- Authenticate and Initialize GEE ---
def gee_authenticate():
    try:
        ee.Initialize(project='seraphic-music-467101-s2')
    except Exception as e:
        st.warning("Authenticating with Google Earth Engine...")
        try:
            ee.Authenticate()
            ee.Initialize(project='seraphic-music-467101-s2')
        except Exception as e:
            st.error(f"GEE Authentication failed: {e}")
            return False
    return True

def get_s2_composite(min_lat, max_lat, min_lon, max_lon, start_date, end_date):
    # Define area of interest
    aoi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
    
    # Convert dates to proper format for Earth Engine
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Add some debug info
    st.info(f"Searching for images from {start_date_str} to {end_date_str}")
    
    # Sentinel-2 surface reflectance collection
    collection = (
        ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(aoi)
        .filterDate(start_date_str, end_date_str)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    )
    
    # Check if collection has any images
    count = collection.size().getInfo()
    st.info(f"Found {count} images for the specified date range")
    
    if count == 0:
        # If no images found for exact dates, try a broader date range
        start_date_broad = start_date - timedelta(days=30)
        end_date_broad = end_date + timedelta(days=30)
        start_date_broad_str = start_date_broad.strftime('%Y-%m-%d')
        end_date_broad_str = end_date_broad.strftime('%Y-%m-%d')
        
        st.info(f"No images found for exact dates. Trying broader range: {start_date_broad_str} to {end_date_broad_str}")
        
        collection = (
            ee.ImageCollection('COPERNICUS/S2_SR')
            .filterBounds(aoi)
            .filterDate(start_date_broad_str, end_date_broad_str)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        )
        
        count = collection.size().getInfo()
        st.info(f"Found {count} images for the broader date range")
    
    if count == 0:
        raise Exception(f"No Sentinel-2 images found for the area and date range. Try selecting a different area or time period.")
    
    # Median composite
    composite = collection.median().clip(aoi)
    return composite

def get_s2_url(composite, min_lat, max_lat, min_lon, max_lon):
    vis_params = {
        'bands': ['B4', 'B3', 'B2'],  # RGB
        'min': 0,
        'max': 3000,
        'gamma': 1.2
    }
    url = composite.getThumbURL({
        'min': 0,
        'max': 3000,
        'dimensions': 512,
        'region': [[min_lon, min_lat], [min_lon, max_lat], [max_lon, max_lat], [max_lon, min_lat]],
        'format': 'png',
        'bands': ['B4', 'B3', 'B2'],
        'gamma': 1.2
    })
    return url

def calculate_ndvi(image):
    # NDVI = (NIR - RED) / (NIR + RED)
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return ndvi

def calculate_builtup(image):
    # Simple built-up index: NDBI = (SWIR - NIR) / (SWIR + NIR)
    ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
    return ndbi

def get_mean_stat(image, band, region):
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=30,
        maxPixels=1e9
    )
    return stats.get(band)

# --- GPT-4.1 Summary Section ---
def generate_template_summary(summary_data):
    """Generate a template summary based on analysis results without external API"""
    
    ndvi_change = summary_data.get('ndvi_change', 0)
    ndbi_change = summary_data.get('ndbi_change', 0)
    priority = summary_data.get('conservation_priority', 'Unknown')
    
    # Determine vegetation trend
    if ndvi_change > 0.05:
        veg_trend = "significant vegetation growth"
        veg_reason = "This indicates improved environmental conditions, possibly due to reforestation, better land management, or natural recovery."
    elif ndvi_change > 0:
        veg_trend = "moderate vegetation growth"
        veg_reason = "This suggests slight improvement in vegetation cover, possibly due to seasonal changes or minor land management improvements."
    elif ndvi_change < -0.05:
        veg_trend = "significant vegetation decline"
        veg_reason = "This indicates environmental degradation, possibly due to deforestation, urban expansion, or climate change impacts."
    elif ndvi_change < 0:
        veg_trend = "moderate vegetation decline"
        veg_reason = "This suggests slight reduction in vegetation cover, possibly due to seasonal changes or minor land use changes."
    else:
        veg_trend = "stable vegetation conditions"
        veg_reason = "Vegetation cover has remained relatively stable during the analysis period."
    
    # Determine urban development trend
    if ndbi_change > 0.05:
        urban_trend = "significant urban expansion"
        urban_reason = "This indicates substantial built-up area growth, likely due to urban development, infrastructure projects, or land use changes."
    elif ndbi_change > 0:
        urban_trend = "moderate urban expansion"
        urban_reason = "This suggests some increase in built-up areas, possibly due to gradual urban development or infrastructure improvements."
    elif ndbi_change < -0.05:
        urban_trend = "significant urban decline"
        urban_reason = "This indicates reduction in built-up areas, possibly due to demolition, land restoration, or natural disasters."
    elif ndbi_change < 0:
        urban_trend = "moderate urban decline"
        urban_reason = "This suggests some reduction in built-up areas, possibly due to minor land use changes or seasonal variations."
    else:
        urban_trend = "stable urban conditions"
        urban_reason = "Built-up areas have remained relatively stable during the analysis period."
    
    # Determine problems and solutions
    if priority == "High":
        problems = "High conservation priority indicates significant environmental concerns, including potential habitat loss, biodiversity decline, and ecosystem degradation."
        solutions = "Immediate conservation measures recommended: establish protected areas, implement sustainable land use policies, promote reforestation, and monitor environmental impacts."
    elif priority == "Medium":
        problems = "Medium conservation priority suggests moderate environmental concerns that require attention to prevent further degradation."
        solutions = "Recommended actions: implement sustainable development practices, establish monitoring programs, promote green infrastructure, and engage in community conservation efforts."
    else:
        problems = "Low conservation priority indicates relatively stable environmental conditions, but continued monitoring is important."
        solutions = "Maintain current environmental conditions through sustainable practices, regular monitoring, and community awareness programs."
    
    summary = f"""
## Summary
Analysis of the selected area from {summary_data.get('start_date', 'N/A')} to {summary_data.get('end_date', 'N/A')} reveals {veg_trend} and {urban_trend}. The conservation priority for this area is classified as **{priority}**.

## Key Findings
- **Vegetation Change (NDVI):** {ndvi_change:.3f} ({'increase' if ndvi_change > 0 else 'decrease' if ndvi_change < 0 else 'no change'})
- **Urban Development (NDBI):** {ndbi_change:.3f} ({'increase' if ndbi_change > 0 else 'decrease' if ndbi_change < 0 else 'no change'})
- **Conservation Priority:** {priority}

## Reasons for Changes
**Vegetation:** {veg_reason}

**Urban Development:** {urban_reason}

## Problems Identified
{problems}

## Recommended Solutions
{solutions}

---
*This analysis was generated automatically based on satellite imagery and remote sensing data.*
"""
    
    return summary

# --- Analyze Button ---
if st.button("Analyze", type="primary"):
    if not geometry:
        st.error("Please draw a rectangle or polygon on the map to select your area.")
    else:
        st.success("Area and timeframes selected! Ready for analysis.")
        st.write(f"**Start Period:** {start_date}")
        st.write(f"**End Period:** {end_date}")
        st.write(f"**Selected Area Geometry:**")
        st.json(geometry)

        if gee_authenticate():
            with st.spinner("Fetching satellite images and running analysis..."):
                try:
                    # Convert geometry to bounding box and ee.Geometry
                    if geometry["type"] == "Polygon":
                        coords = geometry["coordinates"][0]
                        lats = [pt[1] for pt in coords]
                        lons = [pt[0] for pt in coords]
                        min_lat, max_lat = min(lats), max(lats)
                        min_lon, max_lon = min(lons), max(lons)
                        ee_geom = ee.Geometry.Polygon([coords])
                    elif geometry["type"] == "Rectangle":
                        coords = geometry["coordinates"][0]
                        lats = [pt[1] for pt in coords]
                        lons = [pt[0] for pt in coords]
                        min_lat, max_lat = min(lats), max(lats)
                        min_lon, max_lon = min(lons), max(lons)
                        ee_geom = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
                    else:
                        st.error("Unsupported geometry type. Please draw a rectangle or polygon.")
                        st.stop()

                    # Fetch composites
                    composite1 = get_s2_composite(min_lat, max_lat, min_lon, max_lon, start_date, start_date + timedelta(days=1))
                    composite2 = get_s2_composite(min_lat, max_lat, min_lon, max_lon, end_date, end_date + timedelta(days=1))
                    url1 = get_s2_url(composite1, min_lat, max_lat, min_lon, max_lon)
                    url2 = get_s2_url(composite2, min_lat, max_lat, min_lon, max_lon)

                    st.markdown("### 🛰️ Satellite Images (Sentinel-2)")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin: 1rem 0;">
                            <h4>📅 {start_date}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.image(url1, caption=f"Start Period: {start_date}")
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin: 1rem 0;">
                            <h4>📅 {end_date}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.image(url2, caption=f"End Period: {end_date}")

                    # --- NDVI Analysis ---
                    ndvi1 = calculate_ndvi(composite1)
                    ndvi2 = calculate_ndvi(composite2)
                    mean_ndvi1 = get_mean_stat(ndvi1, 'NDVI', ee_geom).getInfo()
                    mean_ndvi2 = get_mean_stat(ndvi2, 'NDVI', ee_geom).getInfo()
                    ndvi_diff = mean_ndvi2 - mean_ndvi1 if mean_ndvi1 is not None and mean_ndvi2 is not None else None

                    # --- Built-up Area Analysis (NDBI) ---
                    ndbi1 = calculate_builtup(composite1)
                    ndbi2 = calculate_builtup(composite2)
                    mean_ndbi1 = get_mean_stat(ndbi1, 'NDBI', ee_geom).getInfo()
                    mean_ndbi2 = get_mean_stat(ndbi2, 'NDBI', ee_geom).getInfo()
                    ndbi_diff = mean_ndbi2 - mean_ndbi1 if mean_ndbi1 is not None and mean_ndbi2 is not None else None

                    # --- Conservation Priority ---
                    if ndvi_diff is not None and ndbi_diff is not None:
                        if ndvi_diff < -0.05 and ndbi_diff > 0.05:
                            priority = "High"
                        elif ndvi_diff < 0 and ndbi_diff > 0:
                            priority = "Medium"
                        else:
                            priority = "Low"
                    else:
                        priority = "Unknown"

                    st.markdown("### 📊 Analysis Results")
                    
                    # Create metric cards
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>🌱 Vegetation (NDVI)</h4>
                            <p><strong>Start:</strong> {mean_ndvi1:.3f}</p>
                            <p><strong>End:</strong> {mean_ndvi2:.3f}</p>
                            <p><strong>Change:</strong> {ndvi_diff:.3f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>🏗️ Urban (NDBI)</h4>
                            <p><strong>Start:</strong> {mean_ndbi1:.3f}</p>
                            <p><strong>End:</strong> {mean_ndbi2:.3f}</p>
                            <p><strong>Change:</strong> {ndbi_diff:.3f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        priority_color = "success-card" if priority == "Low" else "warning-card" if priority == "Medium" else "info-card"
                        st.markdown(f"""
                        <div class="{priority_color}">
                            <h4>🛡️ Conservation Priority</h4>
                            <h2>{priority}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    # Prepare summary for GPT-4.1
                    summary_data = {
                        "start_date": str(start_date),
                        "end_date": str(end_date),
                        "mean_ndvi_start": mean_ndvi1,
                        "mean_ndvi_end": mean_ndvi2,
                        "ndvi_change": ndvi_diff,
                        "mean_ndbi_start": mean_ndbi1,
                        "mean_ndbi_end": mean_ndbi2,
                        "ndbi_change": ndbi_diff,
                        "conservation_priority": priority
                    }
                    st.session_state["summary_data"] = summary_data

                    # --- AI Summary Section ---
                    st.markdown("### 🤖 AI-Powered Analysis Summary")
                    gpt_summary = generate_template_summary(summary_data)
                    st.markdown(f"""
                    <div class="summary-section">
                        {gpt_summary}
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>❌ Error</h4>
                        <p>Error fetching images or running analysis: {e}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="warning-card">
                <h4>🔐 Authentication Error</h4>
                <p>Google Earth Engine authentication failed. Please check your credentials.</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="info-card">
        <h4>ℹ️ Ready to Analyze</h4>
        <p>Select area and timeframes, then click Analyze to begin your urban sprawl analysis.</p>
    </div>
    """, unsafe_allow_html=True) 