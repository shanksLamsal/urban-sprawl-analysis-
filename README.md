# 🌍 Urban Sprawl Analysis Tool

A powerful web application for analyzing urban development and environmental changes using satellite imagery and AI-powered insights.

## 📋 Overview

This tool provides comprehensive analysis of urban sprawl and environmental changes by comparing satellite imagery from different time periods. It automatically calculates vegetation indices (NDVI), urban development indices (NDBI), and generates intelligent summaries with conservation recommendations.

## ✨ Features

- **🛰️ Satellite Imagery Analysis**: Compare Sentinel-2 satellite images from different time periods
- **🌱 Vegetation Monitoring**: Calculate NDVI (Normalized Difference Vegetation Index) changes
- **🏗️ Urban Development Tracking**: Analyze NDBI (Normalized Difference Built-up Index) changes
- **🛡️ Conservation Priority Assessment**: Automatic classification of environmental conservation needs
- **🤖 AI-Powered Summaries**: Intelligent analysis summaries with recommendations
- **🎨 Modern UI**: Beautiful, responsive interface with gradient designs and styled components
- **🗺️ Interactive Area Selection**: Draw custom areas on an interactive map
- **📊 Visual Metrics**: Professional metric cards with color-coded indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Earth Engine account
- Internet connection for satellite data access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/urban-sprawl-analysis.git
   cd urban-sprawl-analysis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Earth Engine**
   ```bash
   earthengine authenticate
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Configure Analysis Parameters
- **Select Timeframes**: Choose start and end dates for comparison
- **Draw Analysis Area**: Use the interactive map to draw a rectangle or polygon

### Step 2: Run Analysis
- Click the **"Analyze"** button
- Wait for satellite data processing
- View results in the analysis dashboard

### Step 3: Review Results
The application will display:

#### 🛰️ Satellite Images
- Side-by-side comparison of selected time periods
- High-resolution Sentinel-2 imagery

#### 📊 Analysis Metrics
- **Vegetation (NDVI)**: Green cover changes
- **Urban Development (NDBI)**: Built-up area changes
- **Conservation Priority**: Environmental risk assessment

#### 🤖 AI Summary
- **Summary**: Key findings overview
- **Key Findings**: Specific metric changes
- **Reasons**: Analysis of observed changes
- **Problems**: Identified environmental concerns
- **Solutions**: Recommended actions

## 🛠️ Technical Details

### Data Sources
- **Sentinel-2 Satellite**: European Space Agency's Earth observation mission
- **Google Earth Engine**: Cloud-based geospatial analysis platform
- **Streamlit**: Web application framework

### Analysis Methods
- **NDVI Calculation**: `(NIR - RED) / (NIR + RED)`
- **NDBI Calculation**: `(SWIR - NIR) / (SWIR + NIR)`
- **Conservation Priority**: Based on vegetation and urban change thresholds

### Technologies Used
- **Python**: Core programming language
- **Streamlit**: Web application framework
- **Google Earth Engine**: Satellite data processing
- **Folium**: Interactive mapping
- **Geopandas**: Geospatial data handling
- **Custom CSS**: Modern UI styling

## 📁 Project Structure

```
urban-sprawl-analysis/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml      # Configuration file
├── README.md             # This file
└── .gitignore           # Git ignore file
```

## 🔧 Configuration

### Google Earth Engine Setup
1. Sign up at [Google Earth Engine](https://earthengine.google.com/)
2. Authenticate using: `earthengine authenticate`
3. Enable the Earth Engine API for your project

### Environment Variables
Create `.streamlit/secrets.toml`:
```toml
# Optional: Add API keys for additional features
DEEPSEEK_API_KEY = "your-api-key-here"
```

## 🎯 Use Cases

- **Environmental Monitoring**: Track vegetation changes over time
- **Urban Planning**: Analyze development patterns and sprawl
- **Conservation Assessment**: Identify areas needing protection
- **Research Projects**: Academic and scientific studies
- **Policy Making**: Data-driven environmental policy decisions

## 📊 Sample Output

The application generates comprehensive reports including:

- **Satellite imagery comparison**
- **Quantitative metrics** (NDVI, NDBI changes)
- **Qualitative assessments** (conservation priority)
- **AI-generated insights** with actionable recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Earth Engine** for satellite data access
- **European Space Agency** for Sentinel-2 imagery
- **Streamlit** for the web application framework
- **Open Source Community** for various Python libraries

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Contact the development team
- Check the documentation

---

**Made with ❤️ for environmental monitoring and urban planning**

*Last updated: July 2025* 