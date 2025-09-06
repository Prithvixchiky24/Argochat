#!/usr/bin/env python3
"""
Test script for enhanced ARGO visualizations
"""

from src.visualization.enhanced_plots import EnhancedARGOVisualizer
from src.database.database_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)

def main():
    """Test the enhanced visualization capabilities."""
    
    # Initialize visualizer and database
    visualizer = EnhancedARGOVisualizer()
    db = DatabaseManager()
    
    print("Testing Enhanced ARGO Visualizations")
    print("=" * 50)
    
    # Get data summary
    summary = db.get_data_summary()
    print(f"Available data:")
    print(f"- Floats: {summary.get('total_floats', 0)}")
    print(f"- Profiles: {summary.get('total_profiles', 0)}")
    print(f"- Measurements: {summary.get('total_measurements', 0)}")
    
    if summary.get('total_floats', 0) == 0:
        print("❌ No float data available for visualization")
        return
    
    # Get some sample floats
    floats_df = db.get_floats_by_region(-90, 90, -180, 180)
    
    if floats_df.empty:
        print("❌ No float data retrieved")
        return
        
    print(f"\n✅ Retrieved {len(floats_df)} float records")
    
    # Test 1: Create float location map
    print("\n1. Testing float location map...")
    try:
        map_plot = visualizer.create_float_map(floats_df)
        if map_plot:
            map_plot.save("outputs/float_locations_map.html")
            print("   ✅ Float location map saved to outputs/float_locations_map.html")
        else:
            print("   ❌ Failed to create float location map")
    except Exception as e:
        print(f"   ❌ Error creating float map: {e}")
    
    # Test 2: Create data summary dashboard
    print("\n2. Testing data summary dashboard...")
    try:
        summary_fig = visualizer.create_data_summary_dashboard(summary, floats_df)
        if summary_fig:
            summary_fig.write_html("outputs/data_summary_dashboard.html")
            print("   ✅ Data summary dashboard saved to outputs/data_summary_dashboard.html")
        else:
            print("   ❌ Failed to create summary dashboard")
    except Exception as e:
        print(f"   ❌ Error creating summary dashboard: {e}")
    
    # Test 3: Test profile plots if measurements are available
    if summary.get('total_measurements', 0) > 0:
        print("\n3. Testing profile visualizations...")
        
        # Get first float with data
        first_float = floats_df.iloc[0]['float_id']
        measurements_df = db.get_measurements_by_profile(first_float, 1)
        
        if not measurements_df.empty:
            try:
                profile_fig = visualizer.plot_temperature_depth_profile(measurements_df)
                if profile_fig:
                    profile_fig.write_html(f"outputs/temperature_profile_{first_float}.html")
                    print(f"   ✅ Temperature profile saved for float {first_float}")
                else:
                    print("   ❌ Failed to create temperature profile")
            except Exception as e:
                print(f"   ❌ Error creating temperature profile: {e}")
        else:
            print("   ⚠️ No measurement data available for profile visualization")
    else:
        print("\n3. ⚠️ Skipping profile visualizations - no measurement data")
    
    # Test 4: Create geographic coverage plot
    print("\n4. Testing geographic coverage...")
    try:
        bounds = summary.get('geographic_bounds', {})
        if bounds and all(v is not None for v in bounds.values()):
            coverage_fig = visualizer.create_geographic_coverage_plot(floats_df)
            if coverage_fig:
                coverage_fig.write_html("outputs/geographic_coverage.html")
                print("   ✅ Geographic coverage plot saved")
            else:
                print("   ❌ Failed to create coverage plot")
        else:
            print("   ⚠️ No geographic bounds data available")
    except Exception as e:
        print(f"   ❌ Error creating coverage plot: {e}")
    
    print(f"\n✅ Enhanced visualization testing completed!")
    print(f"📁 Check the outputs/ directory for generated plots")

if __name__ == "__main__":
    main()
