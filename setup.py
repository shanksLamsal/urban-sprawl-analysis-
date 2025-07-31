#!/usr/bin/env python3
"""
Setup script for Urban Sprawl Analysis Project
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_gee_authentication():
    """Check Google Earth Engine authentication"""
    print("\n🌍 Checking Google Earth Engine authentication...")
    try:
        import ee
        ee.Initialize()
        print("✅ Google Earth Engine is authenticated")
        return True
    except ImportError:
        print("❌ Google Earth Engine API not installed")
        print("Please install: pip install earthengine-api")
        return False
    except Exception as e:
        print("❌ Google Earth Engine authentication required")
        print("Please run: earthengine authenticate")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = [
        "results",
        "results/maps",
        "results/charts", 
        "results/metrics"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Checking installed packages...")
    required_packages = [
        "earthengine-api",
        "geopandas", 
        "folium",
        "matplotlib",
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "rasterio",
        "shapely",
        "seaborn",
        "jupyter"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        return False
    return True

def main():
    """Main setup function"""
    print("🚀 Urban Sprawl Analysis Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing packages manually:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check GEE authentication
    if not check_gee_authentication():
        print("\nTo authenticate with Google Earth Engine:")
        print("1. Sign up at https://earthengine.google.com")
        print("2. Run: earthengine authenticate")
        print("3. Follow the authentication process")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Authenticate with Google Earth Engine (if not done)")
    print("2. Open urban_sprawl_analysis.ipynb in Jupyter")
    print("3. Run the analysis cells")
    print("\nFor help, see README.md")

if __name__ == "__main__":
    main() 