#!/usr/bin/env python3
"""
Example usage of Urban Sprawl Analysis modules
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def example_basic_analysis():
    """Example of basic urban sprawl analysis"""
    print("Running basic urban sprawl analysis example...")
    
    try:
        # Import modules
        from gee_utils import GEEProcessor
        from land_cover import LandCoverClassifier
        from change_detection import ChangeDetector
        from visualization import UrbanSprawlVisualizer
        
        # Initialize processors
        gee_processor = GEEProcessor()
        classifier = LandCoverClassifier(gee_processor)
        change_detector = ChangeDetector(gee_processor)
        visualizer = UrbanSprawlVisualizer()
        
        # Get study area
        study_area = gee_processor.create_study_area_roi()
        print(f"Study area created: Kathmandu Valley")
        
        # Example: Get data availability
        availability = gee_processor.validate_data_availability(2010, 2020)
        print(f"Data availability checked for 2010-2020")
        
        # Example: Create sample statistics (mock data for demonstration)
        sample_stats = {
            'vegetation': {'area_km2': 150.5, 'percentage': 45.2},
            'built_up': {'area_km2': 89.3, 'percentage': 26.8},
            'water': {'area_km2': 12.1, 'percentage': 3.6},
            'bare_soil': {'area_km2': 81.1, 'percentage': 24.4}
        }
        
        # Create visualization
        fig = visualizer.create_land_cover_chart(sample_stats, "Sample Land Cover")
        chart_path = visualizer.save_chart(fig, "example_land_cover")
        print(f"Sample chart saved: {chart_path}")
        
        # Save sample metrics
        metrics_path = visualizer.save_metrics_csv(sample_stats, "example_metrics")
        print(f"Sample metrics saved: {metrics_path}")
        
        print("✅ Basic analysis example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in basic analysis: {e}")
        print("Make sure you have authenticated with Google Earth Engine")

def example_change_detection():
    """Example of change detection analysis"""
    print("\nRunning change detection example...")
    
    try:
        from change_detection import ChangeDetector
        from gee_utils import GEEProcessor
        
        # Initialize
        gee_processor = GEEProcessor()
        change_detector = ChangeDetector(gee_processor)
        
        # Example change statistics
        sample_changes = {
            'vegetation_changes': {
                'vegetation_loss_km2': 25.3,
                'vegetation_gain_km2': 8.7,
                'net_change_km2': -16.6,
                'change_percentage': -5.2
            },
            'urban_expansion': {
                'urban_expansion_km2': 18.9,
                'urban_decline_km2': 2.1,
                'net_expansion_km2': 16.8,
                'expansion_rate_percent': 4.8
            }
        }
        
        # Generate change report
        report = change_detector.generate_change_report(
            sample_changes, 
            "Kathmandu", 
            "2010-2020"
        )
        
        # Save report
        with open("results/metrics/example_change_report.txt", "w") as f:
            f.write(report)
        
        print("✅ Change detection example completed!")
        print("Report saved to: results/metrics/example_change_report.txt")
        
    except Exception as e:
        print(f"❌ Error in change detection: {e}")

def example_visualization():
    """Example of visualization features"""
    print("\nRunning visualization example...")
    
    try:
        from visualization import UrbanSprawlVisualizer
        
        visualizer = UrbanSprawlVisualizer()
        
        # Create sample data for visualization
        sample_data = {
            'vegetation': {'area_km2': 120.5, 'percentage': 36.2},
            'built_up': {'area_km2': 95.3, 'percentage': 28.6},
            'water': {'area_km2': 15.1, 'percentage': 4.5},
            'bare_soil': {'area_km2': 102.1, 'percentage': 30.7}
        }
        
        # Create charts
        fig1 = visualizer.create_land_cover_chart(sample_data, "Example Land Cover")
        chart1_path = visualizer.save_chart(fig1, "example_visualization")
        
        # Create sample change data
        change_data = {
            'vegetation_changes': {
                'vegetation_loss_km2': 20.0,
                'vegetation_gain_km2': 5.0,
                'no_change_km2': 95.5
            },
            'urban_expansion': {
                'urban_expansion_km2': 15.0,
                'urban_decline_km2': 1.0,
                'stable_urban_km2': 79.3
            }
        }
        
        fig2 = visualizer.create_change_analysis_chart(change_data, "Example Changes")
        chart2_path = visualizer.save_chart(fig2, "example_changes")
        
        print("✅ Visualization examples completed!")
        print(f"Charts saved: {chart1_path}, {chart2_path}")
        
    except Exception as e:
        print(f"❌ Error in visualization: {e}")

def main():
    """Main example function"""
    print("🌍 Urban Sprawl Analysis - Example Usage")
    print("=" * 50)
    
    # Run examples
    example_basic_analysis()
    example_change_detection()
    example_visualization()
    
    print("\n" + "=" * 50)
    print("📚 Example usage completed!")
    print("\nTo run the full analysis:")
    print("1. Open urban_sprawl_analysis.ipynb in Jupyter")
    print("2. Run all cells to perform complete analysis")
    print("3. Check results/ folder for outputs")

if __name__ == "__main__":
    main() 